#!/usr/bin/env python3
"""
extract_rule_rows_from_markdown.py - deterministically parse rule rows from rule_doc.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_HEADERS = ("费用名称", "依据和计算方法")


def parse_pipe_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    inner = stripped[1:-1] if stripped.endswith("|") else stripped[1:]
    return [cell.strip() for cell in inner.split("|")]


def is_separator_row(cells: list[str]) -> bool:
    valid_chars = {"-", ":", " "}
    return bool(cells) and all(cell and set(cell) <= valid_chars for cell in cells)


def normalize_table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        cells = parse_pipe_row(line)
        if not cells or is_separator_row(cells):
            continue
        if not any(cell for cell in cells):
            continue
        rows.append(cells)
    return rows


def extract_rule_rows(markdown_text: str, source_file: str) -> dict[str, Any]:
    lines = markdown_text.splitlines()
    current_anchor: str | None = None
    table_lines: list[str] = []
    table_index = 0
    rule_rows: list[dict[str, Any]] = []

    def flush_table() -> None:
        nonlocal table_lines, table_index, current_anchor
        if not table_lines:
            return
        rows = normalize_table_rows(table_lines)
        table_lines = []
        if len(rows) < 2:
            return
        headers = tuple(rows[0][:2])
        if headers != EXPECTED_HEADERS:
            return
        table_index += 1
        source_anchor = current_anchor or f"table_{table_index}"
        for row_index, row in enumerate(rows[1:], start=1):
            if len(row) < 2:
                continue
            fee_name_raw = row[0].strip()
            calculation_method_raw = row[1].strip()
            if not fee_name_raw and not calculation_method_raw:
                continue
            rule_rows.append(
                {
                    "source_anchor": source_anchor,
                    "source_table_index": table_index,
                    "source_row_index": row_index,
                    "fee_name_raw": fee_name_raw,
                    "calculation_method_raw": calculation_method_raw,
                }
            )

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            flush_table()
            current_anchor = stripped.lstrip("#").strip()
            continue
        if stripped.startswith("|"):
            table_lines.append(line)
            continue
        flush_table()
    flush_table()

    return {
        "source_file": source_file,
        "extracted_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rule_rows": rule_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract raw rule rows from rule_doc.md")
    parser.add_argument("--input", required=True, help="Path to rule_doc.md")
    parser.add_argument("--output", required=True, help="Path to write rule_rows.json")
    return parser.parse_args()


def friendly_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.is_file():
        return friendly_error(f"markdown 文件不存在: {input_path}")
    try:
        markdown_text = input_path.read_text(encoding="utf-8")
    except Exception as exc:
        return friendly_error(f"无法读取 markdown 文件: {exc}")

    payload = extract_rule_rows(markdown_text, str(input_path.resolve()))
    if not payload["rule_rows"]:
        return friendly_error("未从 markdown 中解析到任何规则行")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
