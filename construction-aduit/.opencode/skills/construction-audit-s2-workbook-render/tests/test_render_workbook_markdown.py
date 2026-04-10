import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "construction-aduit"
SCRIPT = AUDIT_ROOT / ".opencode/skills/construction-audit-s2-workbook-render/scripts/render_workbook_markdown.py"


class RenderWorkbookMarkdownTests(unittest.TestCase):
    def _run(self, sheets_dir: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--sheets-dir",
                str(sheets_dir),
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            cwd=WORKSPACE_ROOT,
        )

    def test_renders_workbook_markdown_from_sheet_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            sheets_dir = tmpdir_path / "sheets"
            sheets_dir.mkdir()
            output_path = tmpdir_path / "workbook.md"

            payload = {
                "sheet_name": "表一",
                "dimensions": "A1:B4",
                "row_count": 4,
                "col_count": 2,
                "merged_regions": [],
                "rows": [
                    {"row_num": 1, "cells": [
                        {"cell_ref": "A1", "display_value": "费用名称", "formula": "", "data_type": "string", "row_context": "", "col_context": "费用名称"},
                        {"cell_ref": "B1", "display_value": "金额", "formula": "", "data_type": "string", "row_context": "", "col_context": "金额"},
                    ]},
                    {"row_num": 2, "cells": [
                        {"cell_ref": "A2", "display_value": "人工费", "formula": "", "data_type": "string", "row_context": "人工费", "col_context": "费用名称", "rule_annotations": [{"role": "target", "source_anchor": "表一（451定额折前）审核规则", "source_row_index": 1, "fee_name_raw": "建筑安装工程费", "calculation_method_raw": "安全生产费计算表（表二折前）建筑安装工程费所对应的合计（元）", "matched_sheet": "表一", "matched_cell_ref": "A2"}]},
                        {"cell_ref": "B2", "display_value": 10, "formula": "", "data_type": "number", "row_context": "人工费", "col_context": "金额", "formula_annotation": None, "rule_annotations": [{"role": "operand", "source_anchor": "表一（451定额折前）审核规则", "source_row_index": 6, "fee_name_raw": "合计", "calculation_method_raw": "表一（451定额折前）建筑安装工程费+需要安装的设备费+工程建设其他费+不需要安装的设备、工具费+小型建筑工程费所对应的总价值-除税价(元)求和", "matched_sheet": "表一", "matched_cell_ref": "B2"}]},
                    ]},
                    {"row_num": 3, "cells": [
                        {"cell_ref": "A3", "display_value": "合计", "formula": "", "data_type": "string", "row_context": "合计", "col_context": "费用名称", "rule_annotations": []},
                        {"cell_ref": "B3", "display_value": "", "formula": "=SUM(B2:B2)", "data_type": "empty", "row_context": "合计", "col_context": "金额", "formula_annotation": {"expression": "B3=SUM(B2:B2)", "source": "native", "confidence": "high"}, "rule_annotations": []},
                    ]},
                ],
            }
            (sheets_dir / "表一.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            result = self._run(sheets_dir, output_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("# Workbook View", content)
            self.assertIn("## Sheet: 表一", content)
            self.assertIn("### Sheet Summary", content)
            self.assertIn("### Sheet View", content)
            self.assertIn("| row\\col | A | B |", content)
            self.assertIn("| 2 | 人工费 | 10 |", content)
            self.assertIn("| 3 | 合计 |  |", content)
            self.assertNotIn("[RULE ", content)
            self.assertNotIn("B3=SUM(B2:B2)", content)

    def test_does_not_repeat_covered_merged_cells(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            sheets_dir = tmpdir_path / "sheets"
            sheets_dir.mkdir()
            output_path = tmpdir_path / "workbook.md"

            payload = {
                "sheet_name": "合并测试",
                "dimensions": "A1:C2",
                "row_count": 2,
                "col_count": 3,
                "merged_regions": [{"range_ref": "A1:C2"}],
                "rows": [
                    {"row_num": 1, "cells": [
                        {"cell_ref": "A1", "display_value": "表头", "formula": "", "data_type": "string", "row_context": "表头", "col_context": "表头", "merge": {"range_ref": "A1:C2", "role": "anchor"}, "rule_annotations": []},
                        {"cell_ref": "B1", "display_value": "表头", "formula": "", "data_type": "string", "row_context": "表头", "col_context": "表头", "merge": {"range_ref": "A1:C2", "role": "covered"}, "rule_annotations": []},
                    ]},
                    {"row_num": 2, "cells": [
                        {"cell_ref": "B2", "display_value": "表头", "formula": "", "data_type": "string", "row_context": "表头", "col_context": "表头", "merge": {"range_ref": "A1:C2", "role": "covered"}, "rule_annotations": []},
                    ]},
                ],
            }
            (sheets_dir / "合并测试.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            result = self._run(sheets_dir, output_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("表头 [MERGE A1:C2]", content)
            self.assertNotIn("| 2 |  | 表头", content)


if __name__ == "__main__":
    unittest.main()
