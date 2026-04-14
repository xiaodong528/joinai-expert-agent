#!/usr/bin/env python3
"""
sheet_audit_protocol.py - deterministic helpers for S3 row-driven sheet audit.
"""

from __future__ import annotations

from typing import Any


EXPECTED_HEADERS = ("费用名称", "依据和计算方法")
SOURCE_BACKED_FEES = frozenset({"建筑安装工程费", "需要安装的设备费", "工程建设其他费"})
NOT_APPLICABLE_FEES = frozenset({"不需要安装的设备、工具费", "小型建筑工程费", "企业运营费"})
DERIVED_SUMMARY_FEES = frozenset({"合计", "预备费", "总计"})
TARGET_AMOUNT_ROLES = ("pre_tax", "tax", "tax_inclusive")

SOURCE_SPECS = {
    ("表一（451定额折前）", "建筑安装工程费", "pre_tax"): {
        "mode": "reference",
        "source_sheet": "安全生产费计算表（表二折前）",
        "source_cell_ref": "D6",
    },
    ("表一（451定额折前）", "建筑安装工程费", "tax"): {
        "mode": "difference",
        "left": {"sheet": "安全生产费计算表（表二折前）", "cell_ref": "D5"},
        "right": {"sheet": "安全生产费计算表（表二折前）", "cell_ref": "D6"},
    },
    ("表一（451定额折前）", "需要安装的设备费", "pre_tax"): {
        "mode": "reference",
        "source_sheet": "表四-需安装设备",
        "source_cell_ref": "I19",
    },
    ("表一（451定额折前）", "需要安装的设备费", "tax"): {
        "mode": "reference",
        "source_sheet": "表四-需安装设备",
        "source_cell_ref": "J19",
    },
    ("表一（451定额折前）", "工程建设其他费", "pre_tax"): {
        "mode": "reference",
        "source_sheet": "表五（甲）",
        "source_cell_ref": "D20",
    },
    ("表一（451定额折前）", "工程建设其他费", "tax"): {
        "mode": "reference",
        "source_sheet": "表五（甲）",
        "source_cell_ref": "E20",
    },
}


def split_rule_rows_into_fixed_batches(
    rule_rows: list[dict[str, Any]],
    batch_count: int = 3,
) -> list[list[dict[str, Any]]]:
    if batch_count <= 0:
        raise ValueError("batch_count 必须大于 0")

    total_rows = len(rule_rows)
    base_size, remainder = divmod(total_rows, batch_count)
    batches: list[list[dict[str, Any]]] = []
    start_index = 0

    for batch_offset in range(batch_count):
        current_size = base_size + (1 if batch_offset < remainder else 0)
        end_index = start_index + current_size
        batches.append([dict(row) for row in rule_rows[start_index:end_index]])
        start_index = end_index

    return batches


def merge_partial_findings(
    sheet_name: str,
    partial_results: list[dict[str, Any]],
    expected_batch_count: int = 3,
) -> dict[str, Any]:
    if expected_batch_count <= 0:
        raise ValueError("expected_batch_count 必须大于 0")
    if not partial_results:
        raise ValueError("partial_results 不能为空")

    ordered_results = sorted(
        partial_results,
        key=lambda item: int(item.get("batch_index", 0)),
    )
    batch_indexes = [int(item.get("batch_index", 0)) for item in ordered_results]
    if batch_indexes != list(range(1, expected_batch_count + 1)):
        raise ValueError("partial_results 缺少完整且连续的 batch_index")

    audit_ids = {
        str(item.get("audit_id", "")).strip()
        for item in ordered_results
        if str(item.get("audit_id", "")).strip()
    }
    if len(audit_ids) != 1:
        raise ValueError("partial_results 的 audit_id 必须唯一")

    severity_totals = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_cells_checked = 0
    total_pass = 0
    merged_findings: list[dict[str, Any]] = []
    cumulative_deviation_values: list[float] = []
    deviation_warning = False

    for result in ordered_results:
        current_sheet_name = str(result.get("sheet_name", "")).strip()
        if current_sheet_name != sheet_name:
            raise ValueError("partial_results 中存在不属于当前 sheet 的结果")

        total_cells_checked += int(result.get("total_cells_checked", 0) or 0)
        merged_findings.extend([dict(finding) for finding in result.get("findings", [])])

        summary = result.get("summary", {})
        if isinstance(summary, dict):
            for severity in severity_totals:
                severity_totals[severity] += int(summary.get(severity, 0) or 0)
            total_pass += int(summary.get("pass", 0) or 0)
            cumulative_deviation_values.append(
                float(summary.get("cumulative_deviation_pct", 0.0) or 0.0)
            )
            deviation_warning = deviation_warning or bool(
                summary.get("cumulative_deviation_warning", False)
            )

    average_cumulative_deviation = (
        sum(cumulative_deviation_values) / len(cumulative_deviation_values)
        if cumulative_deviation_values
        else 0.0
    )
    deviation_warning = deviation_warning or average_cumulative_deviation > 5.0

    return {
        "sheet_name": sheet_name,
        "audit_id": audit_ids.pop(),
        "total_cells_checked": total_cells_checked,
        "findings": merged_findings,
        "summary": {
            **severity_totals,
            "pass": total_pass,
            "cumulative_deviation_pct": round(average_cumulative_deviation, 4),
            "cumulative_deviation_warning": deviation_warning,
            "completed_batches": len(ordered_results),
            "batch_count": expected_batch_count,
        },
    }


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


def extract_sheet_rule_rows(markdown_text: str, sheet_name: str) -> list[dict[str, Any]]:
    anchor = f"{sheet_name}审核规则"
    lines = markdown_text.splitlines()
    in_section = False
    table_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if in_section and heading != anchor:
                break
            in_section = heading == anchor
            continue
        if in_section and stripped.startswith("|"):
            table_lines.append(line)
        elif in_section and table_lines:
            break

    rows = normalize_table_rows(table_lines)
    if len(rows) < 2 or tuple(rows[0][:2]) != EXPECTED_HEADERS:
        return []

    extracted: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows[1:], start=1):
        if len(row) < 2:
            continue
        fee_name = row[0].strip()
        calculation_method = row[1].strip()
        if not fee_name:
            continue
        extracted.append(
            {
                "fee_name": fee_name,
                "calculation_method": calculation_method,
                "source_anchor": f"{anchor}/{fee_name}",
                "source_row_index": row_index,
            }
        )
    return extracted


def build_sheet_audit_plan(
    sheet_name: str,
    rule_rows: list[dict[str, Any]],
    sheet_payload: dict[str, Any],
) -> dict[str, Any]:
    grouped_targets: dict[str, dict[str, str]] = {}
    for row in sheet_payload.get("rows", []):
        for cell in row.get("cells", []):
            fee_name = str(cell.get("row_business_label", "") or "").strip()
            amount_role = cell.get("amount_role")
            if not fee_name or amount_role not in TARGET_AMOUNT_ROLES:
                continue
            grouped_targets.setdefault(fee_name, {})[str(amount_role)] = cell["cell_ref"]

    rows: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for rule in rule_rows:
        fee_name = rule["fee_name"]
        if fee_name in SOURCE_BACKED_FEES:
            row_type = "source_backed"
        elif fee_name in NOT_APPLICABLE_FEES:
            row_type = "not_applicable"
        elif fee_name in DERIVED_SUMMARY_FEES:
            row_type = "derived_summary"
        else:
            row_type = "unsupported"

        report_amount_roles: list[str] = []
        if row_type in {"source_backed", "derived_summary"}:
            report_amount_roles = ["tax_inclusive"]

        row_entry = {
            "fee_name": fee_name,
            "row_type": row_type,
            "source_anchor": rule["source_anchor"],
            "source_row_index": rule["source_row_index"],
            "calculation_method": rule["calculation_method"],
            "report_amount_roles": report_amount_roles,
        }

        current_targets = grouped_targets.get(fee_name, {})
        for amount_role in TARGET_AMOUNT_ROLES:
            target_cell_ref = current_targets.get(amount_role)
            if not target_cell_ref:
                continue
            check = {
                "fee_name": fee_name,
                "row_type": row_type,
                "amount_role": amount_role,
                "target_cell_ref": target_cell_ref,
                "rule_source_anchor": rule["source_anchor"],
                "rule_source_excerpt": rule["calculation_method"],
                "report_as_finding": amount_role in report_amount_roles,
                "report_rounding": 2 if amount_role in report_amount_roles else None,
            }
            source_spec = SOURCE_SPECS.get((sheet_name, fee_name, amount_role))
            if source_spec:
                check["source_spec"] = source_spec
            elif amount_role == "tax_inclusive" and row_type in {"source_backed", "derived_summary"}:
                pre_tax_ref = current_targets.get("pre_tax")
                tax_ref = current_targets.get("tax")
                if pre_tax_ref and tax_ref:
                    check["source_spec"] = {
                        "mode": "same_row_sum",
                        "left": {"sheet": sheet_name, "cell_ref": pre_tax_ref},
                        "right": {"sheet": sheet_name, "cell_ref": tax_ref},
                    }
            checks.append(check)

        rows.append(row_entry)

    return {
        "sheet_name": sheet_name,
        "rows": rows,
        "checks": checks,
    }
