import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "construction-aduit"
SKILL_PATH = AUDIT_ROOT / ".opencode/skills/construction-audit-s3-sheet-audit/SKILL.md"


class ConstructionAuditS3SheetAuditSkillContractTests(unittest.TestCase):
    def test_skill_contract_supports_shard_and_merge_modes(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("`mode=shard_audit`", content)
        self.assertIn("`mode=merge_sheet_findings`", content)
        self.assertIn("`batch_index`", content)
        self.assertIn("`batch_count=3`", content)
        self.assertIn("`assigned_rule_rows`", content)
        self.assertIn("`partial_output_path`", content)
        self.assertIn("`partial_findings_paths`", content)
        self.assertIn("`merged_output_path`", content)

    def test_skill_contract_limits_direct_audit_targets_to_visible_sheets(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("`spreadsheet.sheets`", content)
        self.assertIn("hidden sheet", content)
        self.assertIn("不得把 hidden sheet 当作 `sheet_name` 直接审", content)
        self.assertIn("`findings/parts/<sheet>/findings_<sheet>__part_{1..3}.json`", content)
        self.assertIn("`findings/findings_<sheet>.json`", content)


if __name__ == "__main__":
    unittest.main()
