#!/usr/bin/env python3
"""Fast repository-integrity checks for the Project 7 CI quality gate."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
MAX_BYTES = 100 * 1024 * 1024
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".csv", ".txt", ".yml", ".yaml", ".ipynb"}
SECRET_PATTERNS = [
    re.compile("github_pat_" + r"[A-Za-z0-9_]{20,}"),
    re.compile("ghp_" + r"[A-Za-z0-9]{30,}"),
    re.compile("sk-" + r"[A-Za-z0-9]{20,}"),
    re.compile("AKIA" + r"[0-9A-Z]{16}"),
    re.compile("-----BEGIN " + r"(?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
]


def main() -> None:
    large_files = []
    secret_hits = []
    conflict_hits = []
    notebook_tracebacks = []
    checked = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        checked += 1
        if path.stat().st_size > MAX_BYTES:
            large_files.append(path.relative_to(ROOT).as_posix())
        if path.resolve() == SELF or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append(path.relative_to(ROOT).as_posix())
                break
        if "<<<<<<< " in text or "=======" in text and ">>>>>>> " in text:
            conflict_hits.append(path.relative_to(ROOT).as_posix())
        if path.suffix.lower() == ".ipynb" and '"traceback": [' in text and '"traceback": []' not in text:
            notebook_tracebacks.append(path.relative_to(ROOT).as_posix())

    required = [
        ".github/workflows/project7-quality-gate.yml",
        "config/system/p5_04_refinement_policy.json",
        "outputs/evaluation/p5_04/refined_run_manifest.json",
        "outputs/evaluation/p5_04/portability/portability_comparison.json",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if large_files or secret_hits or conflict_hits or notebook_tracebacks or missing:
        raise RuntimeError(
            f"CI repository checks failed: large={large_files}, secrets={secret_hits}, "
            f"conflicts={conflict_hits}, notebook_tracebacks={notebook_tracebacks}, missing={missing}"
        )
    print(f"Repository files checked: {checked}")
    print("Credential-pattern hits: 0")
    print("Files over 100 MB: 0")
    print("Merge-conflict markers: 0")
    print("Notebook traceback outputs: 0")
    print("Required final-baseline files present: PASS")
    print("CI repository checks: PASS")


if __name__ == "__main__":
    main()
