import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl
import xlwt


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / ".opencode/skills/construction-audit-s2-workbook-render/scripts/spreadsheet_reader.py"
SAMPLE_XLS = ROOT / "train/预算-表一（451定额度折前）/东海县海陵家苑三网小区新建工程-预算（表一451定额度折前有错）.xls"


class SpreadsheetReaderCliTests(unittest.TestCase):
    def _run_all_sheets(self, workbook_path: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(workbook_path),
                "--all-sheets",
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

    def _load_sheet_json(self, output_dir: Path, filename: str) -> dict:
        return json.loads((output_dir / filename).read_text(encoding="utf-8"))

    def _cell_by_ref(self, payload: dict, ref: str) -> dict:
        for row in payload["rows"]:
            for cell in row["cells"]:
                if cell["cell_ref"] == ref:
                    return cell
        raise AssertionError(f"Cell {ref} not found")

    def test_exports_formula_display_value_and_context_for_xlsx(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            workbook_path = tmpdir_path / "formula.xlsx"
            output_dir = tmpdir_path / "sheets"

            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "预算"
            sheet["A1"] = "费用名称"
            sheet["B1"] = "金额"
            sheet["A2"] = "人工费"
            sheet["B2"] = 10
            sheet["A3"] = "材料费"
            sheet["B3"] = 20
            sheet["A4"] = "合计"
            sheet["B4"] = "=SUM(B2:B3)"
            workbook.save(workbook_path)

            result = self._run_all_sheets(workbook_path, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = self._load_sheet_json(output_dir, "预算.json")
            formula_cell = self._cell_by_ref(payload, "B4")
            label_cell = self._cell_by_ref(payload, "A4")
            self.assertIn("display_value", formula_cell)
            self.assertIn("formula", formula_cell)
            self.assertIn("formula_annotation", formula_cell)
            self.assertIn("rule_annotations", formula_cell)
            self.assertEqual(formula_cell["formula"], "=SUM(B2:B3)")
            self.assertEqual(formula_cell["formula_annotation"]["source"], "native")
            self.assertEqual(formula_cell["formula_annotation"]["expression"], "B4=SUM(B2:B3)")
            self.assertEqual(formula_cell["rule_annotations"], [])
            self.assertIn("row_context", formula_cell)
            self.assertIn("col_context", formula_cell)
            self.assertEqual(label_cell["row_context"], "合计")
            self.assertEqual(formula_cell["col_context"], "金额")

    def test_exports_merge_metadata_and_context_for_xls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            workbook_path = tmpdir_path / "merged.xls"
            output_dir = tmpdir_path / "sheets"

            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet("合并测试")
            sheet.write_merge(0, 0, 3, 4, "总价值")
            sheet.write(1, 3, "除税价")
            sheet.write(1, 4, "含税价")
            sheet.write(2, 0, "人工费")
            sheet.write(2, 3, 10)
            sheet.write(2, 4, 11)
            workbook.save(str(workbook_path))

            result = self._run_all_sheets(workbook_path, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = self._load_sheet_json(output_dir, "合并测试.json")
            anchor = self._cell_by_ref(payload, "D1")
            covered = self._cell_by_ref(payload, "E1")
            value_cell = self._cell_by_ref(payload, "D3")
            taxed_cell = self._cell_by_ref(payload, "E3")

            self.assertEqual(anchor["merge"]["role"], "anchor")
            self.assertEqual(covered["merge"]["role"], "covered")
            self.assertEqual(value_cell["formula"], "")
            self.assertIn("display_value", value_cell)
            self.assertIn("formula_annotation", value_cell)
            self.assertIn("rule_annotations", value_cell)
            self.assertIsNone(value_cell["formula_annotation"])
            self.assertEqual(value_cell["row_context"], "人工费")
            self.assertEqual(value_cell["col_context"], "总价值 / 除税价")
            self.assertEqual(taxed_cell["col_context"], "总价值 / 含税价")

    def test_trims_real_xls_to_effective_business_range(self):
        if not SAMPLE_XLS.exists():
            self.skipTest(f"Sample workbook not found: {SAMPLE_XLS}")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "sheets"
            result = self._run_all_sheets(SAMPLE_XLS, output_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = self._load_sheet_json(output_dir, "表一_451定额折前_.json")
            self.assertEqual(payload["dimensions"], "A1:M15")
            self.assertEqual(payload["row_count"], 15)
            self.assertEqual(payload["col_count"], 13)
            self.assertFalse(any(cell["cell_ref"] == "IV1" for row in payload["rows"] for cell in row["cells"]))


if __name__ == "__main__":
    unittest.main()
