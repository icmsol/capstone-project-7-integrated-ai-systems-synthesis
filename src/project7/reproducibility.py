"""Audit-chain, inventory, checksum, and replay utilities."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .p4_05_pipeline import run_packet_assembly
from .schema_validation import validate_artifact


class ReproducibilityError(RuntimeError):
    """Fail-closed reproducibility error."""

    def __init__(
        self,
        reason_code: str,
        message: str,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = "fail_closed"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        canonical_json_bytes(value)
    ).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


def categorize_artifact(relative_path: str) -> str:
    if relative_path.startswith("audit/"):
        return "audit"
    if relative_path.startswith("config/"):
        return "configuration"
    if relative_path.startswith("data/"):
        return "data"
    if relative_path.startswith("docs/"):
        return "documentation"
    if relative_path.startswith("notebooks/"):
        return "notebook"
    if relative_path.startswith("outputs/"):
        return "output"
    if relative_path.startswith("requirements_p4_"):
        return "requirements"
    if relative_path.startswith("src/"):
        return "source_code"
    if relative_path.startswith("tests/"):
        return "test"
    if relative_path.startswith("models/"):
        return "model_reference"
    raise ReproducibilityError(
        "ARTIFACT_SCOPE_INVALID",
        f"Unrecognized inventory category: {relative_path}",
    )


def inventory_artifacts(
    *,
    repo_root: Path,
    included_prefixes: list[str],
    excluded_patterns: list[str],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in sorted(
        item for item in repo_root.rglob("*")
        if item.is_file()
    ):
        relative = path.relative_to(
            repo_root
        ).as_posix()
        if not any(
            relative.startswith(prefix)
            for prefix in included_prefixes
        ):
            continue
        if any(
            pattern in relative
            for pattern in excluded_patterns
        ):
            continue
        inventory.append(
            {
                "path": relative,
                "category": categorize_artifact(relative),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "required_for_replay": True,
            }
        )
    if not inventory:
        raise ReproducibilityError(
            "ARTIFACT_MISSING",
            "The replay inventory is empty.",
        )
    return inventory


def verify_inventory(
    *,
    repo_root: Path,
    inventory: list[dict[str, Any]],
) -> dict[str, Any]:
    missing: list[str] = []
    mismatched_sizes: list[str] = []
    mismatched_hashes: list[str] = []
    for item in inventory:
        path = repo_root / item["path"]
        if not path.is_file():
            missing.append(item["path"])
            continue
        if path.stat().st_size != item["bytes"]:
            mismatched_sizes.append(item["path"])
        if sha256_file(path) != item["sha256"]:
            mismatched_hashes.append(item["path"])

    if missing:
        raise ReproducibilityError(
            "ARTIFACT_MISSING",
            "Required artifacts are missing: "
            + ", ".join(missing),
        )
    if mismatched_sizes or mismatched_hashes:
        raise ReproducibilityError(
            "ARTIFACT_CHECKSUM_MISMATCH",
            "Artifact integrity failed for: "
            + ", ".join(
                sorted(
                    set(mismatched_sizes)
                    | set(mismatched_hashes)
                )
            ),
        )
    return {
        "status": "PASS",
        "artifact_count": len(inventory),
        "missing_count": 0,
        "size_mismatch_count": 0,
        "hash_mismatch_count": 0,
    }


def recompute_event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json_bytes(
            {
                key: value
                for key, value in event.items()
                if key != "event_hash"
            }
        )
    ).hexdigest()


def verify_audit_chain(
    events: list[dict[str, Any]],
    *,
    expected_sequences: list[int],
) -> dict[str, Any]:
    if len(events) != len(expected_sequences):
        raise ReproducibilityError(
            "AUDIT_CHAIN_INVALID",
            "Audit event count differs from the required sequence.",
        )

    observed_sequences: list[int] = []
    previous_hash: str | None = None
    case_ids = set()
    for event in events:
        try:
            sequence = int(
                event["event_id"].rsplit("-", 1)[1]
            )
        except Exception as exc:
            raise ReproducibilityError(
                "AUDIT_CHAIN_INVALID",
                f"Invalid event ID: {event.get('event_id')}",
            ) from exc

        observed_sequences.append(sequence)
        case_ids.add(event["case_id"])

        if recompute_event_hash(event) != event["event_hash"]:
            raise ReproducibilityError(
                "AUDIT_CHAIN_INVALID",
                f"Event hash mismatch: {event['event_id']}",
            )
        if event["previous_event_hash"] != previous_hash:
            raise ReproducibilityError(
                "AUDIT_CHAIN_INVALID",
                f"Previous-hash mismatch: {event['event_id']}",
            )
        previous_hash = event["event_hash"]

    if observed_sequences != expected_sequences:
        raise ReproducibilityError(
            "AUDIT_CHAIN_INVALID",
            "Audit sequences are not contiguous.",
        )
    if len(case_ids) != 1:
        raise ReproducibilityError(
            "AUDIT_CHAIN_INVALID",
            "Audit events span multiple case IDs.",
        )

    return {
        "event_count": len(events),
        "first_event_id": events[0]["event_id"],
        "last_event_id": events[-1]["event_id"],
        "expected_sequences": expected_sequences,
        "chain_valid": True,
        "first_event_hash": events[0]["event_hash"],
        "last_event_hash": events[-1]["event_hash"],
    }


def deterministic_packet_replay(
    *,
    repo_root: Path,
    preserved_packet_path: Path,
    preserved_case_path: Path,
    event_time: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        temp_root = Path(directory)
        artifacts = run_packet_assembly(
            repo_root=repo_root,
            case_state_path=(
                repo_root
                / "outputs"
                / "p4_04"
                / "updated_case_state.json"
            ),
            output_directory=temp_root / "outputs",
            audit_output_path=temp_root / "audit.jsonl",
            event_time=event_time,
        )
        replayed_packet = artifacts["packet"]
        replayed_case = artifacts["updated_case_state"]

    preserved_packet = read_json(preserved_packet_path)
    preserved_case = read_json(preserved_case_path)

    preserved_packet_hash = canonical_sha256(
        preserved_packet
    )
    replayed_packet_hash = canonical_sha256(
        replayed_packet
    )
    preserved_case_hash = canonical_sha256(
        preserved_case
    )
    replayed_case_hash = canonical_sha256(
        replayed_case
    )

    if preserved_packet_hash != replayed_packet_hash:
        raise ReproducibilityError(
            "REPLAY_OUTPUT_MISMATCH",
            "Replayed decision-support packet differs from the preserved packet.",
        )
    if preserved_case_hash != replayed_case_hash:
        raise ReproducibilityError(
            "REPLAY_OUTPUT_MISMATCH",
            "Replayed final case state differs from the preserved case state.",
        )

    return {
        "status": "PASS",
        "artifact_integrity": "PASS",
        "audit_chain_integrity": "PASS",
        "packet_replay": "PASS",
        "preserved_packet_sha256": preserved_packet_hash,
        "replayed_packet_sha256": replayed_packet_hash,
        "preserved_case_sha256": preserved_case_hash,
        "replayed_case_sha256": replayed_case_hash,
    }


def build_final_routing(
    *,
    packet: dict[str, Any],
    case_state: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_status": case_state["case_status"],
        "packet_status": packet["packet_status"],
        "recommendation_code": packet[
            "recommendation"
        ]["recommendation_code"],
        "recommendation_label": packet[
            "recommendation"
        ]["recommendation_label"],
        "required_reviewer": packet[
            "human_review"
        ]["required_reviewer"],
        "human_disposition": case_state[
            "human_disposition"
        ],
        "final_decision": packet["final_decision"],
    }


def write_checksum_csv(
    path: Path,
    inventory: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "path",
                "category",
                "bytes",
                "sha256",
                "required_for_replay",
            ],
        )
        writer.writeheader()
        writer.writerows(inventory)
