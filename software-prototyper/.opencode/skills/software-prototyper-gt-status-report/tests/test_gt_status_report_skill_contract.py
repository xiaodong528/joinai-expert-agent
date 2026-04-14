import re
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SKILL_PATH = WORKSPACE_ROOT / ".opencode/skills/software-prototyper-gt-status-report/SKILL.md"


class GtStatusReportSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        self.content = SKILL_PATH.read_text(encoding="utf-8")

    def test_skill_exists_and_uses_jas_structure(self):
        self.assertIn("name: software-prototyper-gt-status-report", self.content)
        self.assertIn("## 依赖", self.content)
        self.assertIn("## 输入契约（Input Contract）", self.content)
        self.assertIn("## 输出契约（Output Contract）", self.content)
        self.assertIn("## 执行流程", self.content)
        self.assertIn("## 验证清单（Validation Checklist）", self.content)

    def test_contract_includes_required_gt_commands(self):
        self.assertIn("gt prime", self.content)
        self.assertIn("bd update", self.content)
        self.assertIn("bd mol wisp", self.content)
        self.assertIn("gt done", self.content)
        self.assertRegex(self.content, r"(当前 rig|current rig)")

    def test_contract_uses_current_stage_language_and_witness_rules(self):
        for stage in ("S0", "S1", "S2", "Wave 1", "Wave 2", "Wave 3"):
            self.assertIn(stage, self.content)

        self.assertIn("Gas Town 默认 witness", self.content)
        self.assertRegex(
            self.content,
            r"(禁止|不得|不可).{0,20}bd mol pour|bd mol wisp.{0,30}(非|不是|而非).{0,10}bd mol pour",
        )


if __name__ == "__main__":
    unittest.main()
