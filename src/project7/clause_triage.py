"""Bounded Project 4 clause-theme inference for Project 7."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from .schema_validation import validate_artifact


class ClauseTriageError(RuntimeError):
    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str = "fail_closed",
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


@dataclass(frozen=True)
class TransformerModelConfig:
    vocab_size: int
    num_classes: int
    max_length: int
    embedding_dim: int
    num_heads: int
    num_layers: int
    feedforward_dim: int
    dropout: float
    pad_index: int


class TransformerClauseClassifier(nn.Module):
    def __init__(self, config: TransformerModelConfig) -> None:
        super().__init__()
        if config.embedding_dim % config.num_heads != 0:
            raise ValueError(
                "embedding_dim must be divisible by num_heads."
            )
        self.config = config
        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.embedding_dim,
            padding_idx=config.pad_index,
        )
        self.position_embedding = nn.Embedding(
            config.max_length,
            config.embedding_dim,
        )
        layer = nn.TransformerEncoderLayer(
            d_model=config.embedding_dim,
            nhead=config.num_heads,
            dim_feedforward=config.feedforward_dim,
            dropout=config.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )
        self.encoder = nn.TransformerEncoder(
            layer,
            num_layers=config.num_layers,
            norm=nn.LayerNorm(config.embedding_dim),
        )
        self.output_dropout = nn.Dropout(config.dropout)
        self.classifier = nn.Linear(
            config.embedding_dim,
            config.num_classes,
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        batch_size, sequence_length = input_ids.shape
        if sequence_length > self.config.max_length:
            raise ValueError("Input exceeds configured maximum length.")
        position_ids = (
            torch.arange(
                sequence_length,
                device=input_ids.device,
            )
            .unsqueeze(0)
            .expand(batch_size, -1)
        )
        hidden = (
            self.token_embedding(input_ids)
            + self.position_embedding(position_ids)
        )
        encoded = self.encoder(
            hidden,
            src_key_padding_mask=~attention_mask.bool(),
        )
        mask = attention_mask.unsqueeze(-1).to(encoded.dtype)
        pooled = (
            (encoded * mask).sum(dim=1)
            / mask.sum(dim=1).clamp(min=1.0)
        )
        return self.classifier(self.output_dropout(pooled))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class Project4InferencePackage:
    model: TransformerClauseClassifier
    model_config: dict[str, Any]
    tokenizer_config: dict[str, Any]
    token_to_index: dict[str, int]
    label_id_to_category: dict[int, str]
    checkpoint_sha256: str
    model_artifact_id: str
    model_version: str
    device: str = "cpu"

    @classmethod
    def load(
        cls,
        model_dir: Path,
        *,
        registry: dict[str, Any] | None = None,
        device: str = "cpu",
    ) -> "Project4InferencePackage":
        required = [
            "selected_clause_classifier.pt",
            "model_config.json",
            "tokenizer_config.json",
            "token_to_index.json",
            "label_id_to_category.json",
        ]
        missing = [
            name for name in required
            if not (model_dir / name).is_file()
        ]
        if missing:
            raise ClauseTriageError(
                "MODEL_PACKAGE_INVALID",
                "Missing model files: " + ", ".join(missing),
            )

        checkpoint_path = (
            model_dir / "selected_clause_classifier.pt"
        )
        observed_sha = _sha256_file(checkpoint_path)
        if registry and registry.get("checkpoint_sha256"):
            if observed_sha != registry["checkpoint_sha256"]:
                raise ClauseTriageError(
                    "MODEL_PACKAGE_INVALID",
                    "Checkpoint SHA-256 does not match the registry.",
                )

        model_config = _load_json(
            model_dir / "model_config.json"
        )
        tokenizer_config = _load_json(
            model_dir / "tokenizer_config.json"
        )
        token_to_index = {
            str(token): int(index)
            for token, index in _load_json(
                model_dir / "token_to_index.json"
            ).items()
        }
        labels = {
            int(label_id): str(category)
            for label_id, category in _load_json(
                model_dir / "label_id_to_category.json"
            ).items()
        }

        if len(token_to_index) != model_config["vocab_size"]:
            raise ClauseTriageError(
                "MODEL_PACKAGE_INVALID",
                "Vocabulary size does not match model config.",
            )
        if len(labels) != model_config["num_classes"]:
            raise ClauseTriageError(
                "MODEL_PACKAGE_INVALID",
                "Label count does not match model config.",
            )
        if (
            tokenizer_config["maximum_sequence_length"]
            != model_config["max_length"]
        ):
            raise ClauseTriageError(
                "MODEL_PACKAGE_INVALID",
                "Tokenizer and model maximum lengths differ.",
            )

        model = TransformerClauseClassifier(
            TransformerModelConfig(**model_config)
        )
        state = torch.load(
            checkpoint_path,
            map_location=device,
            weights_only=True,
        )
        model.load_state_dict(state)
        model.eval()

        return cls(
            model=model,
            model_config=model_config,
            tokenizer_config=tokenizer_config,
            token_to_index=token_to_index,
            label_id_to_category=labels,
            checkpoint_sha256=observed_sha,
            model_artifact_id=(
                registry.get(
                    "model_artifact_id",
                    "PROJECT4-CLAUSE-CLASSIFIER-INFERENCE",
                )
                if registry
                else "PROJECT4-CLAUSE-CLASSIFIER-INFERENCE"
            ),
            model_version=(
                registry.get("model_version", "1.0.0")
                if registry
                else "1.0.0"
            ),
            device=device,
        )

    def encode(self, passage_text: str) -> dict[str, Any]:
        if not isinstance(passage_text, str):
            raise ClauseTriageError(
                "MODEL_INPUT_INVALID",
                "Passage must be a string.",
            )
        normalized = passage_text.strip()
        if not normalized:
            raise ClauseTriageError(
                "MODEL_INPUT_INVALID",
                "Passage is empty.",
            )

        token_pattern = re.compile(
            self.tokenizer_config["pattern"]
        )
        text = (
            normalized.lower()
            if self.tokenizer_config.get("lowercase", True)
            else normalized
        )
        tokens = token_pattern.findall(text)
        if not tokens:
            raise ClauseTriageError(
                "MODEL_INPUT_INVALID",
                "Tokenizer produced no tokens.",
            )

        max_length = int(
            self.tokenizer_config[
                "maximum_sequence_length"
            ]
        )
        original_count = len(tokens)
        retained = tokens[:max_length]
        truncated = original_count > max_length
        unk_index = int(
            self.tokenizer_config["unk_index"]
        )
        pad_index = int(
            self.tokenizer_config["pad_index"]
        )
        ids = [
            int(self.token_to_index.get(token, unk_index))
            for token in retained
        ]
        unknown_count = sum(
            token_id == unk_index for token_id in ids
        )
        oov_ratio = (
            unknown_count / len(ids)
            if ids else 1.0
        )
        attention = [True] * len(ids)
        padding = max_length - len(ids)
        ids.extend([pad_index] * padding)
        attention.extend([False] * padding)

        return {
            "input_ids": torch.tensor(
                [ids],
                dtype=torch.long,
                device=self.device,
            ),
            "attention_mask": torch.tensor(
                [attention],
                dtype=torch.bool,
                device=self.device,
            ),
            "original_token_count": original_count,
            "retained_token_count": len(retained),
            "truncated": truncated,
            "oov_count": unknown_count,
            "oov_ratio": oov_ratio,
            "passage_text_hash": _sha256_text(normalized),
        }

    def predict_probabilities(
        self,
        passage_text: str,
    ) -> dict[str, Any]:
        encoded = self.encode(passage_text)
        with torch.inference_mode():
            logits = self.model(
                encoded["input_ids"],
                encoded["attention_mask"],
            )
            probabilities = torch.softmax(logits, dim=-1)

        expected_shape = (
            1,
            int(self.model_config["num_classes"]),
        )
        if tuple(logits.shape) != expected_shape:
            raise ClauseTriageError(
                "MODEL_INFERENCE_INVALID",
                f"Unexpected output shape: {tuple(logits.shape)}",
            )
        if not torch.isfinite(probabilities).all():
            raise ClauseTriageError(
                "MODEL_INFERENCE_INVALID",
                "Nonfinite probability detected.",
            )
        probability_sum = float(
            probabilities.sum().item()
        )
        if abs(probability_sum - 1.0) > 1e-5:
            raise ClauseTriageError(
                "MODEL_INFERENCE_INVALID",
                "Probabilities do not sum to one.",
            )

        vector = [
            float(value)
            for value in probabilities[0].tolist()
        ]
        label_id = int(
            probabilities.argmax(dim=-1).item()
        )
        return {
            **encoded,
            "probabilities": vector,
            "predicted_label_id": label_id,
            "predicted_category": (
                self.label_id_to_category[label_id]
            ),
            "confidence": vector[label_id],
            "probability_sum": probability_sum,
        }


def build_clause_prediction(
    *,
    case_id: str,
    passage_id: str,
    probability_result: dict[str, Any],
    model_artifact_id: str,
    model_version: str,
    model_sha256: str,
    policy: dict[str, Any],
    source_domain: str,
    consequential_use: bool,
    schema_dir: Path,
) -> dict[str, Any]:
    confidence = float(probability_result["confidence"])
    truncated = bool(probability_result["truncated"])
    public_sector = (
        source_domain.strip().lower() == "public_sector"
    )
    domain_warning = (
        public_sector
        or float(probability_result["oov_ratio"])
        > policy[
            "maximum_oov_ratio_without_domain_warning"
        ]
    )

    decision = "classify"
    priority = policy["default_review_priority"]
    reason_codes: list[str] = []

    if (
        policy["low_confidence_abstains"]
        and confidence
        < policy["minimum_classification_confidence"]
    ):
        decision = "abstain"
        priority = "high"
        reason_codes.append("MODEL_CONFIDENCE_LOW")

    if policy["truncation_escalates"] and truncated:
        decision = "escalate"
        priority = "critical"
        reason_codes.append("MODEL_INPUT_TRUNCATED")

    if (
        public_sector
        and consequential_use
        and policy[
            "public_sector_consequential_use_escalates"
        ]
    ):
        decision = "escalate"
        if priority != "critical":
            priority = "high"
        reason_codes.append("MODEL_DOMAIN_SHIFT")

    if not reason_codes:
        reason_codes.append(
            "MODEL_CLASSIFICATION_PRODUCED"
        )

    limitations = [
        {
            "code": "MODEL_THEME_ONLY",
            "description": (
                "The output is a clause-theme triage label, not legal "
                "meaning, enforceability, compliance, acceptability, or "
                "required contractual action."
            ),
            "material": True,
            "mitigation": (
                "Route consequential interpretation to an authorized "
                "contracts or legal reviewer."
            ),
        },
        {
            "code": "MODEL_TEN_CLASS_LIMIT",
            "description": (
                "The classifier recognizes only ten CUAD-derived "
                "commercial-contract categories."
            ),
            "material": True,
            "mitigation": (
                "Do not treat the label set as a complete contract taxonomy."
            ),
        },
        {
            "code": "MODEL_CONFIDENCE_NOT_CERTAINTY",
            "description": (
                "Confidence is not legal certainty or evidence of "
                "correctness on public-sector language."
            ),
            "material": True,
            "mitigation": (
                "Use confidence only for review prioritization."
            ),
        },
    ]
    if domain_warning:
        limitations.append(
            {
                "code": "MODEL_DOMAIN_SHIFT",
                "description": (
                    "The model was trained on commercial-contract language; "
                    "this passage is public-sector or exhibits vocabulary shift."
                ),
                "material": True,
                "mitigation": (
                    "Require qualified human review and do not use the "
                    "label as authoritative evidence."
                ),
            }
        )
    if truncated:
        limitations.append(
            {
                "code": "MODEL_INPUT_TRUNCATED",
                "description": (
                    "The passage exceeded the configured maximum length "
                    "and was truncated before inference."
                ),
                "material": True,
                "mitigation": (
                    "Review the complete passage and surrounding context."
                ),
            }
        )

    prediction = {
        "prediction_schema_version": "1.0.0",
        "case_id": case_id,
        "passage_id": passage_id,
        "passage_text_hash": (
            probability_result["passage_text_hash"]
        ),
        "model_artifact_id": model_artifact_id,
        "model_version": model_version,
        "model_sha256": model_sha256,
        "predicted_label_id": int(
            probability_result["predicted_label_id"]
        ),
        "predicted_category": str(
            probability_result["predicted_category"]
        ),
        "confidence": confidence,
        "decision": decision,
        "review_priority": priority,
        "required_reviewer_role": (
            policy["required_reviewer_role"]
        ),
        "domain_warning": domain_warning,
        "truncated": truncated,
        "token_count": int(
            probability_result["original_token_count"]
        ),
        "reason_codes": sorted(set(reason_codes)),
        "limitations": limitations,
    }
    validate_artifact(
        prediction,
        "clause_prediction.schema.json",
        schema_dir,
    )
    return prediction


def triage_passage(
    *,
    inference_package: Project4InferencePackage,
    case_id: str,
    passage_id: str,
    passage_text: str,
    policy: dict[str, Any],
    source_domain: str,
    consequential_use: bool,
    schema_dir: Path,
) -> dict[str, Any]:
    result = inference_package.predict_probabilities(
        passage_text
    )
    return build_clause_prediction(
        case_id=case_id,
        passage_id=passage_id,
        probability_result=result,
        model_artifact_id=(
            inference_package.model_artifact_id
        ),
        model_version=inference_package.model_version,
        model_sha256=(
            inference_package.checkpoint_sha256
        ),
        policy=policy,
        source_domain=source_domain,
        consequential_use=consequential_use,
        schema_dir=schema_dir,
    )
