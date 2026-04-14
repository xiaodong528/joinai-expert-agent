import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SKILL_PATH = WORKSPACE_ROOT / ".opencode/skills/software-prototyper-gt-mail-comm/SKILL.md"


class GtMailCommSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        self.content = SKILL_PATH.read_text(encoding="utf-8")

    def test_skill_exists_and_uses_jas_structure(self):
        self.assertIn("name: software-prototyper-gt-mail-comm", self.content)
        self.assertIn("## 依赖", self.content)
        self.assertIn("## 输入契约（Input Contract）", self.content)
        self.assertIn("## 输出契约（Output Contract）", self.content)
        self.assertIn("## 执行流程", self.content)
        self.assertIn("## 验证清单（Validation Checklist）", self.content)

    def test_contract_includes_required_gt_mail_commands(self):
        self.assertIn("gt mail send", self.content)
        self.assertIn("gt mail check --inject", self.content)
        self.assertIn("gt mail list", self.content)
        self.assertIn("gt mail read", self.content)

    def test_contract_covers_roles_and_current_stage_names(self):
        for role in ("Orchestrator", "Worker", "Reviewer"):
            self.assertIn(role, self.content)

        for stage in ("S0", "S1", "S2", "Wave 1", "Wave 2", "Wave 3"):
            self.assertIn(stage, self.content)

        self.assertIn("Gas Town 默认 witness", self.content)
        self.assertNotIn("audit-report.json", self.content)
        self.assertNotIn("corrected.xlsx", self.content)
        self.assertNotIn("corrected.xls", self.content)


if __name__ == "__main__":
    unittest.main()
