#!/usr/bin/env python3
"""
report_payload.py - pure aggregation helpers for S4 error report.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def aggregate_sheet_results(sheet_results: list[dict[str, Any]]) -> dict[str, Any]:
    total_checks = 0
    total_findings = 0
    severity_totals = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    auto_fixable_items: list[dict[str, Any]] = []
    human_review_items: list[dict[str, Any]] = []
    sheets_summary: list[dict[str, Any]] = []
    cumulative_abs_deviations: list[float] = []

    for sheet_data in sheet_results:
        sheet_name = sheet_data.get("sheet_name", "未知表格")
        checked = sheet_data.get("total_cells_checked", 0)
        findings = sheet_data.get("findings", [])
        sheet_summary = sheet_data.get("summary", {})

        total_checks += checked
        total_findings += len(findings)

        sheet_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            severity = finding.get("severity", "low")
            if severity in severity_totals:
                severity_totals[severity] += 1
                sheet_severity[severity] += 1

            wrapped = {**finding, "sheet_name": sheet_name}
            if finding.get("auto_fixable", False):
                auto_fixable_items.append(wrapped)
            else:
                human_review_items.append(wrapped)

        cumulative_abs_deviations.append(sheet_summary.get("cumulative_deviation_pct", 0.0))
        sheets_summary.append(
            {
                "sheet_name": sheet_name,
                "total_cells_checked": checked,
                "findings_count": len(findings),
                "severity": sheet_severity,
                "findings": findings,
                "cumulative_deviation_pct": sheet_summary.get("cumulative_deviation_pct", 0.0),
                "cumulative_deviation_warning": sheet_summary.get("cumulative_deviation_warning", False),
            }
        )

    pass_count = total_checks - total_findings
    pass_rate = (pass_count / total_checks * 100.0) if total_checks > 0 else 100.0
    total_cum_dev = (
        sum(cumulative_abs_deviations) / len(cumulative_abs_deviations)
        if cumulative_abs_deviations
        else 0.0
    )

    return {
        "total_checks": total_checks,
        "total_findings": total_findings,
        "pass_count": max(0, pass_count),
        "pass_rate": round(pass_rate, 2),
        "severity_totals": severity_totals,
        "auto_fixable_items": auto_fixable_items,
        "human_review_items": human_review_items,
        "sheets_summary": sheets_summary,
        "cumulative_deviation_pct": round(total_cum_dev, 4),
        "cumulative_deviation_warning": total_cum_dev > 5.0,
    }


def build_report_payload(config: dict[str, Any], sheet_results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = aggregate_sheet_results(sheet_results)
    project_info = config.get("project_info", {})
    audit_date = config.get("audit_date") or datetime.now().strftime("%Y-%m-%d")

    return {
        "audit_id": config.get("audit_id", "AUDIT-001"),
        "audit_type": config.get("audit_type", "budget"),
        "project_info": {
            "project_name": project_info.get("project_name", config.get("project_name", "未指定项目")),
            **{key: value for key, value in project_info.items() if key != "project_name"},
        },
        "audit_date": audit_date,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_checks": aggregate["total_checks"],
            "total_findings": aggregate["total_findings"],
            "pass_count": aggregate["pass_count"],
            "pass_rate": aggregate["pass_rate"],
            "severity_totals": aggregate["severity_totals"],
            "auto_fixable_count": len(aggregate["auto_fixable_items"]),
            "human_review_count": len(aggregate["human_review_items"]),
            "cumulative_deviation_pct": aggregate["cumulative_deviation_pct"],
            "cumulative_deviation_warning": aggregate["cumulative_deviation_warning"],
        },
        "sheets": aggregate["sheets_summary"],
        "auto_fixable_items": aggregate["auto_fixable_items"],
        "human_review_items": aggregate["human_review_items"],
    }
