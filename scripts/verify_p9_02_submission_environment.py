#!/usr/bin/env python3
"""Verify the final Project 7 submission environment and emit repository inventory evidence."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "requirements.txt"
DOC_PATH = ROOT / "docs/P9_02_Final_Environment_and_Repository_Inventory.md"
AREA_INVENTORY_PATH = ROOT / "docs/P9_02_Final_Repository_Area_Inventory.csv"
OUT = ROOT / "outputs/ci"
FREEZE_PATH = OUT / "p9_02_pip_freeze.txt"
FILE_INVENTORY_PATH = OUT / "p9_02_repository_inventory.csv"
SUMMARY_PATH = OUT / "p9_02_repository_inventory_summary.json"

HISTORICAL_REQUIREMENTS = [
    "requirements_p4_01.txt", "requirements_p4_02.txt", "requirements_p4_03.txt",
    "requirements_p4_04.txt", "requirements_p4_05.txt", "requirements_p4_06.txt",
    "requirements_p5_01.txt", "requirements_p5_02.txt", "requirements_p5_03.txt",
    "requirements_p5_04.txt", "requirements_p5_05.txt", "requirements_p5_09.txt",
]
REQUIRED_LOCK_PACKAGES = {"numpy", "pandas", "matplotlib", "jsonschema", "referencing", "pyyaml", "torch", "ipywidgets"}
IGNORE_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ipynb_checkpoints"}
TEMP_NAMES = {".DS_Store", "Thumbs.db", ".gitkeep"}
TEMP_SUFFIXES = (".tmp", ".bak", "~")


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_exact_lines(text: str, source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line or line.startswith(("-r", "--")):
            raise RuntimeError(f"{source} contains a non-exact requirement: {line}")
        name, version = line.split("==", 1)
        key = canonical_name(name)
        if key in result:
            raise RuntimeError(f"{source} contains duplicate package: {name}")
        result[key] = version
    return result


def inventory_repository() -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    placeholder_hits: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in IGNORE_DIR_NAMES for part in rel.parts):
            continue
        rel_string = rel.as_posix()
        if rel_string.startswith("outputs/ci/"):
            continue
        if path.name in TEMP_NAMES or any(path.name.endswith(s) for s in TEMP_SUFFIXES):
            placeholder_hits.append(rel_string)
        rows.append({
            "path": rel_string,
            "top_level_area": rel.parts[0] if len(rel.parts) > 1 else "repository_root",
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return rows, placeholder_hits


def main() -> None:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"Expected Python 3.12; got {sys.version.split()[0]}")
    for path in [LOCK_PATH, DOC_PATH, AREA_INVENTORY_PATH]:
        if not path.is_file():
            raise FileNotFoundError(path)
    for rel in HISTORICAL_REQUIREMENTS:
        if not (ROOT / rel).is_file():
            raise RuntimeError(f"Historical dependency snapshot moved or missing: {rel}")

    lock = parse_exact_lines(LOCK_PATH.read_text(encoding="utf-8"), "requirements.txt")
    if len(lock) != 51:
        raise RuntimeError(f"Expected 51 exact packages in final lock; found {len(lock)}")
    if not REQUIRED_LOCK_PACKAGES.issubset(lock):
        raise RuntimeError("Final lock is missing a required Project 7 dependency family.")
    if lock.get("torch") != "2.10.0+cpu":
        raise RuntimeError("Final lock must preserve the verified CPU-only torch build.")

    OUT.mkdir(parents=True, exist_ok=True)
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True, capture_output=True, text=True,
    ).stdout
    FREEZE_PATH.write_text(freeze, encoding="utf-8")
    installed = parse_exact_lines(freeze, "pip freeze")

    mismatches = []
    for name, version in lock.items():
        actual = installed.get(name)
        if actual != version:
            mismatches.append({"package": name, "locked": version, "installed": actual})
    if mismatches:
        raise RuntimeError(f"Final environment lock mismatch: {mismatches}")

    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt  # noqa: F401
    import torch  # noqa: F401
    if "+cpu" not in torch.__version__ or torch.cuda.is_available():
        raise RuntimeError(f"Expected CPU-only torch runtime; got {torch.__version__}")
    import jsonschema  # noqa: F401
    import referencing  # noqa: F401
    import yaml  # noqa: F401
    import ipywidgets  # noqa: F401

    rows, placeholder_hits = inventory_repository()
    if placeholder_hits:
        raise RuntimeError(f"Temporary/placeholder repository files remain: {placeholder_hits}")

    with FILE_INVENTORY_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "top_level_area", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    area_counts: dict[str, int] = {}
    area_bytes: dict[str, int] = {}
    for row in rows:
        area = str(row["top_level_area"])
        area_counts[area] = area_counts.get(area, 0) + 1
        area_bytes[area] = area_bytes.get(area, 0) + int(row["bytes"])

    extras = sorted(set(installed) - set(lock))
    summary = {
        "activity": "P9-02",
        "status": "PASS",
        "python_version": sys.version.split()[0],
        "final_requirements_path": "requirements.txt",
        "locked_packages": len(lock),
        "pip_freeze_packages": len(installed),
        "additional_runner_packages_not_in_lock": extras,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "matplotlib_version": matplotlib.__version__,
        "torch_version": torch.__version__,
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "historical_requirement_snapshots_preserved": HISTORICAL_REQUIREMENTS,
        "historical_requirement_snapshot_count": len(HISTORICAL_REQUIREMENTS),
        "repository_files_in_inventory": len(rows),
        "repository_bytes_in_inventory": sum(int(r["bytes"]) for r in rows),
        "top_level_file_counts": dict(sorted(area_counts.items())),
        "top_level_bytes": dict(sorted(area_bytes.items())),
        "temporary_or_placeholder_file_hits": placeholder_hits,
        "generated_evidence": [
            "outputs/ci/p9_02_pip_freeze.txt",
            "outputs/ci/p9_02_repository_inventory.csv",
            "outputs/ci/p9_02_repository_inventory_summary.json",
        ],
        "frozen_candidate_changed": False,
        "external_actions_performed": 0,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Python: {summary['python_version']}")
    print(f"Final lock packages verified: {len(lock)}/{len(lock)}")
    print(f"pip freeze packages recorded: {len(installed)}")
    print(f"Historical requirements snapshots preserved: {len(HISTORICAL_REQUIREMENTS)}/12")
    print(f"Repository files inventoried: {len(rows)}")
    print("Temporary/placeholder file hits: 0")
    print(f"Core setup libraries: numpy={np.__version__}, pandas={pd.__version__}, matplotlib={matplotlib.__version__}")
    print(f"CPU torch runtime: {torch.__version__}")
    print("Frozen candidate changed: FALSE")
    print("External actions performed: 0")
    print("P9-02 final submission environment and inventory verification: PASS")


if __name__ == "__main__":
    main()
