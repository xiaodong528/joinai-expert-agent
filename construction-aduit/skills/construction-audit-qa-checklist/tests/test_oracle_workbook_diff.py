import sys
import tempfile
import unittest
from pathlib import Path

import xlwt


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "joinai-expert-agent/construction-aduit"
CONSTRUCTION_REVIEW_ROOT = WORKSPACE_ROOT / "construction-review"
SCRIPTS_DIR = AUDIT_ROOT / "skills/construction-audit-qa-checklist/scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from oracle_workbook_diff import diff_sheet_cells


CORRECT_XLS = CONSTRUCTION_REVIEW_ROOT / "examples/original-xlsx/原-东海县海陵家苑三网小区新建工程-预算（无错误）.xls"
WRONG_XLS = CONSTRUCTION_REVIEW_ROOT / "train/预算-表一（451定额度折前）/东海县海陵家苑三网小区新建工程-预算（表一451定额度折前有错）.xls"


class OracleWorkbookDiffTests(unittest.TestCase):
    def _write_xls(self, path: Path, values: dict[str, str | float]) -> None:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("表一（451定额折前）")
        for cell_ref, value in values.items():
            column = 0
            for char in cell_ref.rstrip("0123456789"):
                column = column * 26 + (ord(char) - 64)
            row = int(cell_ref[len(cell_ref.rstrip("0123456789")) :]) - 1
            sheet.write(row, column - 1, value)
        workbook.save(str(path))

    def test_diff_sheet_cells_returns_only_changed_cells(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            correct = tmpdir_path / "correct.xls"
            wrong = tmpdir_path / "wrong.xls"
            self._write_xls(correct, {"L7": 1, "L8": 2, "L9": 3})
            self._write_xls(wrong, {"L7": 9, "L8": 2, "L9": 8})

            diffs = diff_sheet_cells(correct, wrong, "表一（451定额折前）")

            self.assertEqual(
                diffs,
                [
                    {"cell_ref": "L7", "correct_value": 1.0, "wrong_value": 9.0},
                    {"cell_ref": "L9", "correct_value": 3.0, "wrong_value": 8.0},
                ],
            )

    def test_real_sample_diff_matches_expected_oracle_cells(self):
        if not CORRECT_XLS.exists() or not WRONG_XLS.exists():
            self.skipTest("Real oracle sample workbooks not found")

        diffs = diff_sheet_cells(CORRECT_XLS, WRONG_XLS, "表一（451定额折前）")

        self.assertEqual(
            [item["cell_ref"] for item in diffs],
            ["L7", "L8", "L9", "L12", "L13", "L14"],
        )
