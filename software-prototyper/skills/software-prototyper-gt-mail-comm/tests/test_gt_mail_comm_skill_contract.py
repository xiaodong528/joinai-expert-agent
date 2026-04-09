import re
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "joinai-expert-agent/construction-aduit"
SKILL_PATH = AUDIT_ROOT / "skills/gt-mail-comm/SKILL.md"


class GtMailCommSkillContractTests(unittest.TestCase):
    def test_skill_exists_and_uses_jas_structure(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: gt-mail-comm", content)
        self.assertIn("## 依赖", content)
        self.assertIn("## 输入契约（Input Contract）", content)
        self.assertIn("## 输出契约（Output Contract）", content)
        self.assertRegex(content, r"## 执行(流程|步骤)")
        self.assertIn("## 验证清单（Validation Checklist）", content)

    def test_contract_includes_required_gt_mail_commands(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("gt mail send", content)
        self.assertIn("gt mail check --inject", content)
        self.assertIn("gt mail list", content)
        self.assertIn("gt mail read", content)

    def test_contract_covers_roles_and_current_stage_names(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        for role in ("Orchestrator", "Worker", "Reviewer"):
            self.assertIn(role, content)

        for stage in ("S0", "S1", "S2", "S3", "S4"):
            self.assertIn(stage, content)

        self.assertIn("Gas Town 默认 witness", content)
        self.assertNotIn("audit-report.json", content)
        self.assertNotRegex(content, r"corrected\.(xlsx|xls)")


if __name__ == "__main__":
    unittest.main()
