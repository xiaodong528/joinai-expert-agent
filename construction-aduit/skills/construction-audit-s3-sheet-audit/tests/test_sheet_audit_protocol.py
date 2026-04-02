import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
S1_SCRIPT = ROOT / ".opencode/skills/construction-audit-s1-rule-doc-render/scripts/run_rule_doc_render.py"
S2_SCRIPT = ROOT / ".opencode/skills/construction-audit-s2-workbook-render/scripts/run_workbook_render.py"
RULE_DOC = ROOT / "examples/rules-docx/家客预算审核知识库11.9.docx"
SAMPLE_XLS = ROOT / "train/预算-表一（451定额度折前）/东海县海陵家苑三网小区新建工程-预算（表一451定额度折前有错）.xls"
S3_SCRIPTS = ROOT / ".opencode/skills/construction-audit-s3-sheet-audit/scripts"
if str(S3_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(S3_SCRIPTS))

from sheet_audit_protocol import build_sheet_audit_plan, extract_sheet_rule_rows


class SheetAuditProtocolTests(unittest.TestCase):
    def _render_real_sample(self, output_dir: Path) -> tuple[Path, Path]:
        config_path = output_dir / "audit-config.yaml"
        config = {
            "audit_id": "AUDIT-S3-PROTOCOL-001",
            "audit_type": "budget",
            "rule_document": {
                "path": str(RULE_DOC),
                "markdown_path": str(output_dir / "rule_doc.md"),
            },
            "spreadsheet": {
                "path": str(SAMPLE_XLS),
                "sheets": ["表一（451定额折前）"],
            },
            "output_dir": str(output_dir),
        }
        config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")

        s1 = subprocess.run(
            [sys.executable, str(S1_SCRIPT), "--config", str(config_path)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(s1.returncode, 0, s1.stderr)

        s2 = subprocess.run(
            [sys.executable, str(S2_SCRIPT), "--config", str(config_path)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(s2.returncode, 0, s2.stderr)
        return output_dir / "rule_doc.md", output_dir / "sheets" / "表一_451定额折前_.json"

    def test_extracts_nine_budget_rows_in_original_order_from_real_markdown(self):
        if not RULE_DOC.exists():
            self.skipTest(f"Sample rule doc not found: {RULE_DOC}")

        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path, _ = self._render_real_sample(Path(tmpdir))
            fee_names = [
                row["fee_name"]
                for row in extract_sheet_rule_rows(
                    markdown_path.read_text(encoding="utf-8"),
                    "表一（451定额折前）",
                )
            ]
            self.assertEqual(
                fee_names,
                [
                    "建筑安装工程费",
                    "需要安装的设备费",
                    "工程建设其他费",
                    "不需要安装的设备、工具费",
                    "小型建筑工程费",
                    "合计",
                    "预备费",
                    "总计",
                    "企业运营费",
                ],
            )

    def test_builds_report_targets_on_tax_inclusive_cells_only(self):
        if not RULE_DOC.exists() or not SAMPLE_XLS.exists():
            self.skipTest("Real sample assets not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path, sheet_json_path = self._render_real_sample(Path(tmpdir))
            sheet_payload = json.loads(sheet_json_path.read_text(encoding="utf-8"))
            rule_rows = extract_sheet_rule_rows(markdown_path.read_text(encoding="utf-8"), "表一（451定额折前）")

            plan = build_sheet_audit_plan("表一（451定额折前）", rule_rows, sheet_payload)

            reportable_checks = [item for item in plan["checks"] if item["report_as_finding"]]
            support_checks = [item for item in plan["checks"] if not item["report_as_finding"]]
            reportable_cells = {(item["fee_name"], item["target_cell_ref"]) for item in reportable_checks}
            self.assertIn(("建筑安装工程费", "L7"), reportable_cells)
            self.assertIn(("需要安装的设备费", "L8"), reportable_cells)
            self.assertIn(("工程建设其他费", "L9"), reportable_cells)
            self.assertIn(("合计", "L12"), reportable_cells)
            self.assertIn(("预备费", "L13"), reportable_cells)
            self.assertIn(("总计", "L14"), reportable_cells)
            self.assertNotIn(("工程建设其他费", "J9"), reportable_cells)
            self.assertNotIn(("工程建设其他费", "K9"), reportable_cells)
            self.assertTrue(any(item["target_cell_ref"] == "J7" for item in support_checks))
            self.assertTrue(any(item["target_cell_ref"] == "K7" for item in support_checks))
            derived_rows = {item["fee_name"] for item in plan["rows"] if item["row_type"] == "derived_summary"}
            self.assertEqual(derived_rows, {"合计", "预备费", "总计"})
            expected_modes = {item["target_cell_ref"]: item["source_spec"]["mode"] for item in reportable_checks}
            self.assertEqual(expected_modes["L7"], "same_row_sum")
            self.assertEqual(expected_modes["L8"], "same_row_sum")
            self.assertEqual(expected_modes["L9"], "same_row_sum")
            self.assertEqual(expected_modes["L12"], "same_row_sum")
            self.assertEqual(expected_modes["L13"], "same_row_sum")
            self.assertEqual(expected_modes["L14"], "same_row_sum")
            self.assertTrue(all(item["report_rounding"] == 2 for item in reportable_checks))
