#!/usr/bin/env python3
"""
report_inputs.py - input loading helpers for S4 error report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_yaml(path: str) -> dict[str, Any]:
    if yaml is not None:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return load_json(path)


def load_findings(findings_dir: str) -> list[dict[str, Any]]:
    base = Path(findings_dir)
    if not base.is_dir():
        raise FileNotFoundError(f"Findings directory not found: {findings_dir}")

    results: list[dict[str, Any]] = []
    for json_path in sorted(base.glob("*.json")):
        payload = load_json(str(json_path))
        if isinstance(payload, dict):
            results.append(payload)
    return results
