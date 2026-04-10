import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "construction-aduit"
SCRIPT = AUDIT_ROOT / ".opencode/skills/construction-audit-s3-sheet-audit/scripts/calc_formula.py"


class CalcFormulaCliTests(unittest.TestCase):
    def test_calculates_same_sheet_formula(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            sheet_path = tmpdir_path / "sheet.json"
            sheet_payload = {
                "sheet_name": "表一",
                "rows": [
                    {"row_num": 1, "cells": [{"cell_ref": "D3", "value": 10}]},
                    {"row_num": 2, "cells": [{"cell_ref": "D4", "value": 20}]},
                    {"row_num": 3, "cells": [{"cell_ref": "D5", "value": 25}]},
                ],
            }
            sheet_path.write_text(json.dumps(sheet_payload, ensure_ascii=False), encoding="utf-8")

            payload = {
                "sheet_name": "表一",
                "target_cell": "D5",
                "formula": "left + right",
                "operands": [
                    {"sheet": "表一", "cell_ref": "D3"},
                    {"sheet": "表一", "cell_ref": "D4"},
                ],
            }

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sheet-data",
                    str(sheet_path),
                    "--payload-json",
                    json.dumps(payload, ensure_ascii=False),
                ],
                capture_output=True,
                text=True,
                cwd=WORKSPACE_ROOT,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["actual_value"], 25.0)
            self.assertEqual(data["expected_value"], 30.0)
            self.assertEqual(data["discrepancy"], 5.0)

    def test_calculates_cross_sheet_formula(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            sheet_path = tmpdir_path / "sheet.json"
            context_dir = tmpdir_path / "sheets"
            context_dir.mkdir()

            sheet_payload = {
                "sheet_name": "表一",
                "rows": [
                    {"row_num": 1, "cells": [{"cell_ref": "J12", "value": 110}]},
                ],
            }
            context_payload = {
                "sheet_name": "表二",
                "rows": [
                    {"row_num": 1, "cells": [{"cell_ref": "G6", "value": 100}]},
                ],
            }
            sheet_path.write_text(json.dumps(sheet_payload, ensure_ascii=False), encoding="utf-8")
            (context_dir / "表二.json").write_text(json.dumps(context_payload, ensure_ascii=False), encoding="utf-8")

            payload = {
                "sheet_name": "表一",
                "target_cell": "J12",
                "formula": "source + rate",
                "operands": [
                    {"sheet": "表二", "cell_ref": "G6"},
                    {"value": 10},
                ],
            }

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sheet-data",
                    str(sheet_path),
                    "--context-sheets-dir",
                    str(context_dir),
                    "--payload-json",
                    json.dumps(payload, ensure_ascii=False),
                ],
                capture_output=True,
                text=True,
                cwd=WORKSPACE_ROOT,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["expected_value"], 110.0)
            self.assertEqual(data["actual_value"], 110.0)
            self.assertEqual(data["resolved_operands"][0]["sheet"], "表二")

    def test_fails_when_operand_unresolved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            sheet_path = tmpdir_path / "sheet.json"
            sheet_payload = {
                "sheet_name": "表一",
                "rows": [
                    {"row_num": 1, "cells": [{"cell_ref": "D5", "value": 25}]},
                ],
            }
            sheet_path.write_text(json.dumps(sheet_payload, ensure_ascii=False), encoding="utf-8")

            payload = {
                "sheet_name": "表一",
                "target_cell": "D5",
                "formula": "left + right",
                "operands": [
                    {"sheet": "表一", "cell_ref": "D3"},
                    {"sheet": "表一", "cell_ref": "D4"},
                ],
            }

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sheet-data",
                    str(sheet_path),
                    "--payload-json",
                    json.dumps(payload, ensure_ascii=False),
                ],
                capture_output=True,
                text=True,
                cwd=WORKSPACE_ROOT,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("无法解析操作数", result.stderr)


if __name__ == "__main__":
    unittest.main()
