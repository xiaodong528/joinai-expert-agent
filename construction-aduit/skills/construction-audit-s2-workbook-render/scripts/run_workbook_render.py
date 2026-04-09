#!/usr/bin/env python3
"""
run_workbook_render.py - Stage 3 entrypoint for workbook rendering.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from extract_rule_rows_from_markdown import extract_rule_rows


SUMMARY_SHEET_ALIASES = {
    "表一（451定额折前）审核规则": "表一（451定额折前）",
    "表一（综合工日折后）审核规则": "表一（综合工日折后）",
    "表二（综合工日折扣后）": "表二（综合工日折后）",
}
SUMMARY_VALUE_COLUMN_BY_FEE = {
    "小型建筑工程费": "D",
    "需要安装的设备费": "E",
    "不需要安装的设备、工具费": "F",
    "建筑安装工程费": "G",
    "工程建设其他费": "H",
    "预备费": "I",
    "合计": "J",
    "总计": "J",
}


def friendly_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def load_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"配置文件不存在: {path}")
    if yaml is not None:
        with path.open("r", encoding="utf-8") as file_obj:
            data = yaml.safe_load(file_obj) or {}
    else:  # pragma: no cover
        with path.open("r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    if not isinstance(data, dict):
        raise ValueError(f"配置文件格式不正确: {path}")
    return data


def validate_workbook_config(config: dict[str, Any]) -> tuple[str, Path, list[str], Path]:
    audit_id = str(config.get("audit_id", "")).strip()
    if not audit_id:
        raise ValueError("配置缺少 audit_id")

    spreadsheet = config.get("spreadsheet")
    if not isinstance(spreadsheet, dict):
        raise ValueError("配置缺少 spreadsheet")

    spreadsheet_path = str(spreadsheet.get("path", "")).strip()
    if not spreadsheet_path:
        raise ValueError("配置缺少 spreadsheet.path")

    target_sheets = spreadsheet.get("sheets")
    if not isinstance(target_sheets, list) or not target_sheets:
        raise ValueError("配置缺少 spreadsheet.sheets")

    output_dir = str(config.get("output_dir", "")).strip()
    if not output_dir:
        raise ValueError("配置缺少 output_dir")

    return audit_id, Path(spreadsheet_path), [str(name) for name in target_sheets], Path(output_dir)


def extract_rule_doc_config(config: dict[str, Any]) -> tuple[Path | None, Path | None]:
    rule_document = config.get("rule_document")
    if not isinstance(rule_document, dict):
        return None, None
    rule_doc_path = str(rule_document.get("path", "")).strip() or None
    markdown_path = str(rule_document.get("markdown_path", "")).strip() or None
    return (Path(rule_doc_path) if rule_doc_path else None, Path(markdown_path) if markdown_path else None)


def safe_filename(name: str) -> str:
    safe = "".join(char if char.isalnum() or char in "-_. " else "_" for char in name)
    return safe.strip()


def run_subprocess(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise ValueError((result.stderr or result.stdout).strip() or "子命令执行失败")


def emit_success_summary(audit_id: str, input_workbook: Path, target_sheets: list[str], output_markdown: Path) -> None:
    print(
        f"audit_id={audit_id} "
        f"input_workbook={input_workbook.resolve()} "
        f"target_sheets_count={len(target_sheets)} "
        f"output_markdown={output_markdown.resolve()}"
    )


def load_sheet_payloads(sheets_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    payloads: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    for path in sorted(sheets_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        sheet_name = payload.get("sheet_name")
        if isinstance(sheet_name, str) and sheet_name:
            payloads[sheet_name] = payload
            paths[sheet_name] = path
    return payloads, paths


def resolve_anchor_sheet(anchor: str, payloads: dict[str, dict[str, Any]]) -> str | None:
    if anchor in SUMMARY_SHEET_ALIASES:
        return SUMMARY_SHEET_ALIASES[anchor]
    if anchor.endswith("审核规则"):
        candidate = anchor.removesuffix("审核规则")
        if candidate in payloads:
            return candidate
    if anchor in payloads:
        return anchor
    return None


def find_matching_cell(payload: dict[str, Any], text: str) -> dict[str, Any] | None:
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    for row in payload.get("rows", []):
        for cell in row.get("cells", []):
            value = cell.get("display_value")
            if isinstance(value, str) and value.strip() == text:
                col_letters = re.sub(r"\d", "", cell["cell_ref"])
                score = 0
                if cell.get("row_context") == text:
                    score += 2
                if col_letters in {"A", "B", "C"}:
                    score += 1
                candidates.append((-score, row["row_num"], len(col_letters), cell))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[:3])
    return candidates[0][3]


def cell_by_ref(payload: dict[str, Any], ref: str) -> dict[str, Any] | None:
    for row in payload.get("rows", []):
        for cell in row.get("cells", []):
            if cell["cell_ref"] == ref:
                return cell
    return None


def target_value_cell(payload: dict[str, Any], label_cell: dict[str, Any], fee_name: str) -> dict[str, Any] | None:
    column = SUMMARY_VALUE_COLUMN_BY_FEE.get(fee_name)
    if not column:
        return None
    row_number = int(re.sub(r"[A-Z]+", "", label_cell["cell_ref"]))
    return cell_by_ref(payload, f"{column}{row_number}")


def add_rule_annotation(cell: dict[str, Any], annotation: dict[str, Any]) -> None:
    existing = cell.setdefault("rule_annotations", [])
    if annotation not in existing:
        existing.append(annotation)


def fee_names_by_anchor(rule_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row in rule_rows:
        anchor = row["source_anchor"]
        result.setdefault(anchor, [])
        fee_name = row["fee_name_raw"]
        if fee_name not in result[anchor]:
            result[anchor].append(fee_name)
    return result


def same_anchor_fee_refs(calc_text: str, current_fee: str, anchor_fees: list[str], target_sheet: str) -> list[str]:
    if target_sheet not in calc_text:
        return []
    refs: list[str] = []
    for fee_name in anchor_fees:
        if fee_name == current_fee:
            continue
        if fee_name in calc_text:
            refs.append(fee_name)
    return refs


def sheet_mentions(calc_text: str, payloads: dict[str, dict[str, Any]]) -> list[str]:
    mentions: list[str] = []
    for sheet_name in payloads:
        if sheet_name in calc_text:
            mentions.append(sheet_name)
    return mentions


def ensure_rule_doc_markdown(config: dict[str, Any], construction_audit_root: Path, workdir: Path) -> Path | None:
    rule_doc_path, markdown_path = extract_rule_doc_config(config)
    if not rule_doc_path or not markdown_path:
        return None
    if markdown_path.is_file() and markdown_path.stat().st_size > 0:
        return markdown_path
    render_script = (
        construction_audit_root / "skills/construction-audit-s1-rule-doc-render/scripts/render_rule_doc_markdown.sh"
    )
    run_subprocess([str(render_script), str(rule_doc_path), str(markdown_path)], cwd=workdir)
    return markdown_path


def annotate_payloads(payloads: dict[str, dict[str, Any]], rule_rows: list[dict[str, Any]]) -> None:
    fees_by_anchor = fee_names_by_anchor(rule_rows)
    for rule in rule_rows:
        anchor = rule["source_anchor"]
        fee_name = rule["fee_name_raw"]
        calc_text = rule["calculation_method_raw"]
        row_index = rule["source_row_index"]
        target_sheet = resolve_anchor_sheet(anchor, payloads)
        if not target_sheet:
            continue
        target_payload = payloads[target_sheet]
        target_label_cell = find_matching_cell(target_payload, fee_name)
        if not target_label_cell:
            continue

        target_annotation = {
            "role": "target",
            "source_anchor": anchor,
            "source_row_index": row_index,
            "fee_name_raw": fee_name,
            "calculation_method_raw": calc_text,
            "matched_sheet": target_sheet,
            "matched_cell_ref": target_label_cell["cell_ref"],
        }
        add_rule_annotation(target_label_cell, target_annotation)

        target_value = target_value_cell(target_payload, target_label_cell, fee_name)
        if target_value:
            add_rule_annotation(
                target_value,
                {
                    **target_annotation,
                    "matched_cell_ref": target_value["cell_ref"],
                },
            )

        operand_fee_names = same_anchor_fee_refs(calc_text, fee_name, fees_by_anchor.get(anchor, []), target_sheet)
        for operand_fee in operand_fee_names:
            operand_label = find_matching_cell(target_payload, operand_fee)
            if operand_label:
                operand_value = target_value_cell(target_payload, operand_label, operand_fee)
                if operand_value:
                    add_rule_annotation(
                        operand_value,
                        {
                            "role": "operand",
                            "source_anchor": anchor,
                            "source_row_index": row_index,
                            "fee_name_raw": fee_name,
                            "calculation_method_raw": calc_text,
                            "matched_sheet": target_sheet,
                            "matched_cell_ref": operand_value["cell_ref"],
                        },
                    )
                else:
                    add_rule_annotation(
                        operand_label,
                        {
                            "role": "operand",
                            "source_anchor": anchor,
                            "source_row_index": row_index,
                            "fee_name_raw": fee_name,
                            "calculation_method_raw": calc_text,
                            "matched_sheet": target_sheet,
                            "matched_cell_ref": operand_label["cell_ref"],
                        },
                    )

        for mentioned_sheet in sheet_mentions(calc_text, payloads):
            if mentioned_sheet == target_sheet:
                continue
            matched_operand = find_matching_cell(payloads[mentioned_sheet], fee_name)
            if matched_operand:
                matched_operand_value = target_value_cell(payloads[mentioned_sheet], matched_operand, fee_name)
                destination_cell = matched_operand_value or matched_operand
                add_rule_annotation(
                    destination_cell,
                    {
                        "role": "operand",
                        "source_anchor": anchor,
                        "source_row_index": row_index,
                        "fee_name_raw": fee_name,
                        "calculation_method_raw": calc_text,
                        "matched_sheet": mentioned_sheet,
                        "matched_cell_ref": destination_cell["cell_ref"],
                    },
                )
            elif target_value:
                add_rule_annotation(
                    target_value,
                    {
                        "role": "operand",
                        "source_anchor": anchor,
                        "source_row_index": row_index,
                        "fee_name_raw": fee_name,
                        "calculation_method_raw": calc_text,
                        "matched_sheet": mentioned_sheet,
                        "matched_cell_ref": None,
                    },
                )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render workbook.md and sheets/*.json from audit-config.yaml")
    parser.add_argument("--config", required=True, help="Path to audit-config.yaml")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(Path(args.config))
        audit_id, spreadsheet_path, target_sheets, output_dir = validate_workbook_config(config)
        if not spreadsheet_path.is_file():
            return friendly_error(f"工作簿不存在: {spreadsheet_path}")

        scripts_dir = Path(__file__).resolve().parent
        construction_audit_root = Path(__file__).resolve().parents[3]
        workspace_root = construction_audit_root.parent.parent
        sheets_dir = output_dir / "sheets"
        workbook_md = output_dir / "workbook.md"

        output_dir.mkdir(parents=True, exist_ok=True)
        run_subprocess(
            [
                sys.executable,
                str(scripts_dir / "spreadsheet_reader.py"),
                "--input",
                str(spreadsheet_path),
                "--all-sheets",
                "--output-dir",
                str(sheets_dir),
            ],
            cwd=workspace_root,
        )

        for sheet_name in target_sheets:
            expected_path = sheets_dir / f"{safe_filename(sheet_name)}.json"
            if not expected_path.is_file():
                raise ValueError(f"未导出目标 sheet JSON: {sheet_name}")

        rule_doc_markdown = ensure_rule_doc_markdown(config, construction_audit_root, workspace_root)
        if rule_doc_markdown:
            payloads, payload_paths = load_sheet_payloads(sheets_dir)
            rule_rows_payload = extract_rule_rows(rule_doc_markdown.read_text(encoding="utf-8"), str(rule_doc_markdown.resolve()))
            annotate_payloads(payloads, rule_rows_payload["rule_rows"])
            for sheet_name, payload in payloads.items():
                payload_paths[sheet_name].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        render_command = [
            sys.executable,
            str(scripts_dir / "render_workbook_markdown.py"),
            "--sheets-dir",
            str(sheets_dir),
            "--output",
            str(workbook_md),
        ]
        for sheet_name in target_sheets:
            render_command.extend(["--sheet-name", sheet_name])
        run_subprocess(render_command, cwd=workspace_root)

        if not workbook_md.is_file() or workbook_md.stat().st_size == 0:
            return friendly_error(f"workbook.md 输出为空: {workbook_md}")

        emit_success_summary(audit_id, spreadsheet_path, target_sheets, workbook_md)
        return 0
    except ValueError as exc:
        return friendly_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
