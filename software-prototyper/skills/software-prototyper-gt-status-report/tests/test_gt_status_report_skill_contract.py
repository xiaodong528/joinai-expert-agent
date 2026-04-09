import re
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "joinai-expert-agent/construction-aduit"
SKILL_PATH = AUDIT_ROOT / "skills/gt-status-report/SKILL.md"


class GtStatusReportSkillContractTests(unittest.TestCase):
    def test_skill_exists_and_uses_jas_structure(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: gt-status-report", content)
        self.assertIn("## 依赖", content)
        self.assertIn("## 输入契约（Input Contract）", content)
        self.assertIn("## 输出契约（Output Contract）", content)
        self.assertRegex(content, r"## 执行(流程|步骤)")
        self.assertIn("## 验证清单（Validation Checklist）", content)

    def test_contract_includes_required_gt_commands(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("gt prime", content)
        self.assertIn("bd update", content)
        self.assertIn("bd mol wisp", content)
        self.assertIn("gt done", content)
        self.assertRegex(content, r"(当前 rig|current rig)")

    def test_gt_default_witness_note_keeps_wisp_and_rejects_pour(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Gas Town 默认 witness", content)
        self.assertRegex(
            content,
            r"(禁止|不得|不可).{0,20}bd mol pour|bd mol wisp.{0,30}(非|不是|而非).{0,10}bd mol pour",
        )


if __name__ == "__main__":
    unittest.main()
