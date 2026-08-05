"""Deterministic registered-corpus evidence retrieval."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


class EvidenceToolError(RuntimeError):
    """Deterministic evidence tool failure."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(value).lower())


class RegisteredEvidenceCorpus:
    """Checksum-verified representative FAR evidence subset."""

    def __init__(
        self,
        *,
        repo_root: Path,
        registry_path: Path,
    ) -> None:
        self.repo_root = repo_root
        self.registry = _load_json(registry_path)
        corpus_path = repo_root / self.registry["corpus_path"]
        if not corpus_path.exists():
            raise EvidenceToolError(
                "TOOL_FAILURE",
                f"Registered corpus is missing: {corpus_path}",
                "fail_closed",
            )
        if _sha256_file(corpus_path) != self.registry["corpus_sha256"]:
            raise EvidenceToolError(
                "SOURCE_CHECKSUM_MISMATCH",
                "Registered corpus checksum does not match.",
                "fail_closed",
            )

        self.corpus = _load_json(corpus_path)
        if (
            self.corpus["fac_number"] != self.registry["fac_number"]
            or self.corpus["fac_effective_date"]
            != self.registry["fac_effective_date"]
        ):
            raise EvidenceToolError(
                "SOURCE_VERSION_UNVERIFIED",
                "FAC number or effective date does not match the registry.",
                "fail_closed",
            )

        self.records = self.corpus["records"]
        self.by_clause = {
            record["clause_number"]: record
            for record in self.records
        }
        self._verify_snapshot_files()

    def _verify_snapshot_files(self) -> None:
        for record in self.records:
            snapshot_path = self.repo_root / record["snapshot_path"]
            if (
                not snapshot_path.exists()
                or _sha256_file(snapshot_path)
                != record["snapshot_sha256"]
            ):
                raise EvidenceToolError(
                    "SOURCE_CHECKSUM_MISMATCH",
                    f"Snapshot integrity failed for {record['clause_number']}.",
                    "fail_closed",
                )

    def exact_lookup(
        self,
        clause_number: str,
    ) -> dict[str, Any] | None:
        normalized = str(clause_number).strip()
        return self.by_clause.get(normalized)

    def semantic_search(
        self,
        query: str,
        *,
        top_k: int,
        minimum_score: float,
    ) -> list[dict[str, Any]]:
        query_tokens = _tokens(query)
        if not query_tokens:
            return []

        document_tokens = [
            _tokens(record["searchable_text"])
            for record in self.records
        ]
        document_count = len(document_tokens)
        document_frequency: Counter[str] = Counter()
        for tokens in document_tokens:
            document_frequency.update(set(tokens))

        def vector(tokens: list[str]) -> dict[str, float]:
            term_counts = Counter(tokens)
            total = max(1, len(tokens))
            output: dict[str, float] = {}
            for term, count in term_counts.items():
                inverse_document_frequency = math.log(
                    (1 + document_count)
                    / (1 + document_frequency.get(term, 0))
                ) + 1.0
                output[term] = (
                    count / total
                ) * inverse_document_frequency
            return output

        query_vector = vector(query_tokens)

        def cosine(
            left: dict[str, float],
            right: dict[str, float],
        ) -> float:
            common = set(left) & set(right)
            numerator = sum(left[key] * right[key] for key in common)
            left_norm = math.sqrt(sum(value * value for value in left.values()))
            right_norm = math.sqrt(sum(value * value for value in right.values()))
            if left_norm == 0.0 or right_norm == 0.0:
                return 0.0
            return numerator / (left_norm * right_norm)

        scored = []
        for record, tokens in zip(self.records, document_tokens):
            score = cosine(query_vector, vector(tokens))
            if score >= minimum_score:
                scored.append(
                    {
                        "record": record,
                        "relevance_score": round(score, 6),
                    }
                )

        scored.sort(
            key=lambda item: (
                item["relevance_score"],
                item["record"]["clause_number"],
            ),
            reverse=True,
        )
        return scored[:top_k]
