#!/usr/bin/env python3
"""
render_workbook_markdown.py - Render workbook.md from sheets/*.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def friendly_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def load_sheet_payloads(sheets_dir: Path) -> dict[str, dict[str, Any]]:
    if not sheets_dir.is_dir():
        raise ValueError(f"sheets 目录不存在: {sheets_dir}")
    payloads: dict[str, dict[str, Any]] = {}
    for path in sorted(sheets_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        sheet_name = payload.get("sheet_name")
        if isinstance(sheet_name, str) and sheet_name:
            payloads[sheet_name] = payload
    if not payloads:
        raise ValueError(f"sheets 目录中没有可用 JSON: {sheets_dir}")
    return payloads


def escape_markdown(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def should_render_cell(cell: dict[str, Any]) -> bool:
    merge = cell.get("merge")
    if isinstance(merge, dict) and merge.get("role") == "covered":
        return False
    display_value = cell.get("display_value", "")
    formula = str(cell.get("formula", "") or "")
    if formula:
        return True
    if display_value not in ("", None):
        return True
    if isinstance(merge, dict) and merge.get("role") == "anchor":
        return True
    return False


def format_cell_for_sheet_view(cell: dict[str, Any]) -> str:
    merge = cell.get("merge") or {}
    display_value = escape_markdown(cell.get("display_value", ""))
    if isinstance(merge, dict) and merge.get("role") == "anchor":
        range_ref = merge.get("range_ref", "")
        if range_ref:
            display_value = f"{display_value} [MERGE {range_ref}]".strip()
    return display_value


def sheet_view_rows(payload: dict[str, Any]) -> list[str]:
    rows = payload.get("rows", [])
    if not rows:
        return []

    col_count = payload.get("col_count", 0)
    header = "| row\\col | " + " | ".join(chr(ord("A") + i) if i < 26 else "" for i in range(col_count)) + " |"
    separator = "|---|" + "|".join(["---"] * col_count) + "|"
    lines = [header, separator]

    for row in rows:
        rendered_cells = []
        for cell in row.get("cells", []):
            merge = cell.get("merge")
            if isinstance(merge, dict) and merge.get("role") == "covered":
                rendered_cells.append("")
            else:
                rendered_cells.append(format_cell_for_sheet_view(cell))
        lines.append("| " + str(row["row_num"]) + " | " + " | ".join(rendered_cells) + " |")
    return lines


def render_sheet_markdown(payload: dict[str, Any]) -> str:
    sheet_name = payload["sheet_name"]
    merged_regions = payload.get("merged_regions", [])
    merged_region_refs = ", ".join(region.get("range_ref", "") for region in merged_regions if region.get("range_ref")) or "-"
    lines = [
        f"## Sheet: {sheet_name}",
        "",
        "### Sheet Summary",
        f"- used_range: {payload.get('dimensions', 'A1:A1')}",
        f"- row_count: {payload.get('row_count', 0)}",
        f"- col_count: {payload.get('col_count', 0)}",
        f"- merged_regions: {merged_region_refs}",
        "",
        "### Sheet View",
    ]

    lines.extend(sheet_view_rows(payload))

    lines.append("")
    return "\n".join(lines)


def render_workbook(payloads: dict[str, dict[str, Any]], target_sheet_names: list[str] | None = None) -> str:
    ordered_names = target_sheet_names or sorted(payloads)
    lines = ["# Workbook View", ""]
    for sheet_name in ordered_names:
        if sheet_name not in payloads:
            raise ValueError(f"找不到目标 sheet JSON: {sheet_name}")
        lines.append(render_sheet_markdown(payloads[sheet_name]))
    return "\n".join(lines).strip() + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render workbook.md from sheets/*.json")
    parser.add_argument("--sheets-dir", required=True, help="Directory containing sheets/*.json")
    parser.add_argument("--output", required=True, help="Output path for workbook.md")
    parser.add_argument("--sheet-name", action="append", default=[], help="Optional target sheet names in output order")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payloads = load_sheet_payloads(Path(args.sheets_dir))
        markdown = render_workbook(payloads, args.sheet_name or None)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        if not output_path.is_file() or output_path.stat().st_size == 0:
            return friendly_error(f"workbook.md 输出为空: {output_path}")
        print(f"Wrote {output_path}")
        return 0
    except ValueError as exc:
        return friendly_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
