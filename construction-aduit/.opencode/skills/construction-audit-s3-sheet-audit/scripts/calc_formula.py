#!/usr/bin/env python3
"""
calc_formula.py - deterministic cell value calculation helper for S3 sheet workers.

The agent is responsible for:
- reading rule_doc.md / workbook.md / sheets/*.json
- deciding which fee item or formula to audit
- composing the payload for this script
- writing findings_<sheet>.json

This script only resolves operand values and performs numeric calculation.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def friendly_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise ValueError(f"文件不存在: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 无法解析: {path}: {exc}") from exc


def build_cell_map(sheet_payload: dict[str, Any]) -> dict[str, Any]:
    cell_map: dict[str, Any] = {}
    for row in sheet_payload.get("rows", []):
        for cell in row.get("cells", []):
            ref = cell.get("cell_ref")
            if isinstance(ref, str) and ref:
                cell_map[ref] = cell.get("value")
    return cell_map


def load_context_sheets(context_dir: Path | None) -> dict[str, dict[str, Any]]:
    if context_dir is None or not context_dir.is_dir():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for json_path in sorted(context_dir.glob("*.json")):
        payload = load_json(json_path)
        if not isinstance(payload, dict):
            continue
        sheet_name = payload.get("sheet_name")
        if isinstance(sheet_name, str) and sheet_name:
            result[sheet_name] = build_cell_map(payload)
    return result


def to_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if math.isnan(value) or math.isinf(value):
            return None
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").strip())
        except ValueError:
            return None
    return None


def resolve_value(
    operand: dict[str, Any],
    current_sheet_name: str,
    current_sheet_map: dict[str, Any],
    context_sheets: dict[str, dict[str, Any]],
) -> tuple[float | None, dict[str, Any]]:
    if "value" in operand:
        value = to_float(operand.get("value"))
        return value, {"kind": "literal", "value": value}

    cell_ref = str(operand.get("cell_ref", "")).strip()
    if not cell_ref:
        return None, {"kind": "reference", "error": "missing cell_ref"}

    sheet_name = str(operand.get("sheet", current_sheet_name)).strip() or current_sheet_name
    if sheet_name == current_sheet_name:
        raw = current_sheet_map.get(cell_ref)
    else:
        raw = context_sheets.get(sheet_name, {}).get(cell_ref)
    value = to_float(raw)
    return value, {"kind": "reference", "sheet": sheet_name, "cell_ref": cell_ref, "value": value}


def extract_operators(formula: str) -> list[str]:
    operators = {"+", "-", "*", "/", "%"}
    return [token for token in formula.split() if token in operators]


def eval_formula(formula: str, values: list[float]) -> float | None:
    if not values:
        return None
    result = values[0]
    for index, operator in enumerate(extract_operators(formula)):
        if index + 1 >= len(values):
            break
        right = values[index + 1]
        if operator == "+":
            result += right
        elif operator == "-":
            result -= right
        elif operator == "*":
            result *= right
        elif operator == "/":
            if right == 0:
                return None
            result /= right
        elif operator == "%":
            if right == 0:
                return None
            result %= right
    return result


def eval_conditional_formula(
    condition: dict[str, Any],
    current_sheet_name: str,
    current_sheet_map: dict[str, Any],
    context_sheets: dict[str, dict[str, Any]],
) -> tuple[float | None, list[dict[str, Any]], str | None]:
    context_source = str(condition.get("context_source", "")).strip()
    if not context_source:
        return None, [], "missing condition.context_source"

    if "!" in context_source:
        sheet_name, cell_ref = context_source.split("!", 1)
        current_value = context_sheets.get(sheet_name, {}).get(cell_ref)
    else:
        current_value = current_sheet_map.get(context_source)

    branches = condition.get("branches", [])
    selected = None
    for branch in branches:
        if not isinstance(branch, dict):
            continue
        match = branch.get("match")
        if match is None or str(match).strip() == str(current_value).strip():
            selected = branch
            break

    if selected is None:
        selected = condition.get("default")
    if not isinstance(selected, dict):
        return None, [], "no matching condition branch"

    resolved_operands: list[dict[str, Any]] = []
    values: list[float] = []
    for operand in selected.get("operands", []):
        value, resolved = resolve_value(operand, current_sheet_name, current_sheet_map, context_sheets)
        resolved_operands.append(resolved)
        if value is None:
            return None, resolved_operands, "unresolved operand"
        values.append(value)

    return eval_formula(str(selected.get("formula", "")), values), resolved_operands, None


def calculate(payload: dict[str, Any], current_sheet_map: dict[str, Any], context_sheets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    current_sheet_name = str(payload.get("sheet_name", "")).strip()
    if not current_sheet_name:
        raise ValueError("payload 缺少 sheet_name")

    target_cell = str(payload.get("target_cell", "")).strip()
    if not target_cell:
        raise ValueError("payload 缺少 target_cell")

    actual_value = to_float(current_sheet_map.get(target_cell))
    resolved_operands: list[dict[str, Any]] = []

    rule_type = str(payload.get("type", "formula")).strip() or "formula"
    if rule_type == "conditional_formula":
        condition = payload.get("condition")
        if not isinstance(condition, dict):
            raise ValueError("conditional_formula 缺少 condition")
        expected_value, resolved_operands, error = eval_conditional_formula(
            condition,
            current_sheet_name,
            current_sheet_map,
            context_sheets,
        )
        if error:
            raise ValueError(error)
    else:
        formula = str(payload.get("formula", "")).strip()
        if not formula:
            raise ValueError("payload 缺少 formula")
        values: list[float] = []
        for operand in payload.get("operands", []):
            value, resolved = resolve_value(operand, current_sheet_name, current_sheet_map, context_sheets)
            resolved_operands.append(resolved)
            if value is None:
                raise ValueError(f"无法解析操作数: {resolved}")
            values.append(value)
        expected_value = eval_formula(formula, values)

    if expected_value is None:
        raise ValueError("公式计算失败")

    discrepancy = None if actual_value is None else expected_value - actual_value
    discrepancy_pct = None
    if discrepancy is not None:
        if expected_value == 0:
            discrepancy_pct = 100.0 if abs(discrepancy) > 0 else 0.0
        else:
            discrepancy_pct = abs(discrepancy) / abs(expected_value) * 100.0

    return {
        "sheet_name": current_sheet_name,
        "target_cell": target_cell,
        "actual_value": actual_value,
        "expected_value": round(expected_value, 6),
        "discrepancy": None if discrepancy is None else round(discrepancy, 6),
        "discrepancy_pct": None if discrepancy_pct is None else round(discrepancy_pct, 4),
        "resolved_operands": resolved_operands,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministically calculate expected value for one target cell")
    parser.add_argument("--sheet-data", required=True, help="Path to current sheet JSON")
    parser.add_argument("--payload-json", required=True, help="JSON payload describing target cell, formula and operands")
    parser.add_argument("--context-sheets-dir", help="Directory containing context sheet JSON files")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        sheet_payload = load_json(Path(args.sheet_data))
        if not isinstance(sheet_payload, dict):
            raise ValueError("sheet-data 根节点必须是对象")
        payload = json.loads(args.payload_json)
        if not isinstance(payload, dict):
            raise ValueError("payload-json 根节点必须是对象")

        sheet_map = build_cell_map(sheet_payload)
        context_sheets = load_context_sheets(Path(args.context_sheets_dir) if args.context_sheets_dir else None)
        result = calculate(payload, sheet_map, context_sheets)
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
        return 0
    except (ValueError, json.JSONDecodeError) as exc:
        return friendly_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
