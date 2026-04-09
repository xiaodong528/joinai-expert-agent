import unittest
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "joinai-expert-agent/construction-aduit"
SCRIPTS_DIR = AUDIT_ROOT / "skills/construction-audit-s4-error-report/scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from report_payload import build_report_payload


class ReportPayloadTests(unittest.TestCase):
    def test_builds_summary_and_sheet_sections_from_multiple_findings_files(self):
        config = {
            "audit_id": "AUDIT-001",
            "audit_type": "budget",
            "audit_date": "2026-04-01",
            "project_info": {"project_name": "测试项目"},
        }
        sheet_results = [
            {
                "sheet_name": "表一",
                "total_cells_checked": 3,
                "findings": [
                    {
                        "finding_id": "F-001",
                        "cell_ref": "C3",
                        "category": "费率",
                        "severity": "critical",
                        "actual_value": "2%",
                        "expected_value": "1.5%",
                        "discrepancy_pct": 0.5,
                        "description": "安全生产费率偏高",
                        "rule_source_anchor": "表一审核规则 > 安全生产费",
                        "rule_source_excerpt": "安全生产费 = 建筑安装工程费 * 1.5%",
                        "auto_fixable": False,
                    }
                ],
                "summary": {
                    "critical": 1,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "pass": 2,
                    "cumulative_deviation_pct": 2.5,
                    "cumulative_deviation_warning": False,
                },
            },
            {
                "sheet_name": "表二",
                "total_cells_checked": 2,
                "findings": [
                    {
                        "finding_id": "F-002",
                        "cell_ref": "D5",
                        "category": "合计",
                        "severity": "medium",
                        "actual_value": "100",
                        "expected_value": "120",
                        "discrepancy_pct": 20.0,
                        "description": "合计不符",
                        "rule_source_anchor": "表二审核规则 > 合计",
                        "rule_source_excerpt": "合计 = 左值 + 右值",
                        "auto_fixable": True,
                    }
                ],
                "summary": {
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "pass": 1,
                    "cumulative_deviation_pct": 1.2,
                    "cumulative_deviation_warning": False,
                },
            },
        ]

        report = build_report_payload(config, sheet_results)

        self.assertEqual(report["audit_id"], "AUDIT-001")
        self.assertEqual(report["summary"]["total_checks"], 5)
        self.assertEqual(report["summary"]["total_findings"], 2)
        self.assertEqual(report["summary"]["severity_totals"]["critical"], 1)
        self.assertEqual(report["summary"]["severity_totals"]["medium"], 1)
        self.assertEqual(len(report["sheets"]), 2)
        self.assertEqual(report["sheets"][0]["sheet_name"], "表一")
        self.assertEqual(report["sheets"][1]["sheet_name"], "表二")


if __name__ == "__main__":
    unittest.main()
