import re
import unittest
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
AUDIT_ROOT = WORKSPACE_ROOT / "joinai-expert-agent/construction-aduit"
SKILL_PATH = AUDIT_ROOT / "skills/construction-audit-qa-checklist/SKILL.md"


def extract_section(markdown: str, title: str) -> str:
    pattern = rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


class ConstructionAuditQaChecklistSkillContractTests(unittest.TestCase):
    def test_skill_exists_and_uses_jas_structure(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("name: construction-audit-qa-checklist", content)
        self.assertIn("## 依赖", content)
        self.assertIn("## 输入契约（Input Contract）", content)
        self.assertIn("## 输出契约（Output Contract）", content)
        self.assertRegex(content, r"## 执行(流程|步骤)")
        self.assertIn("## 验证清单（Validation Checklist）", content)

    def test_formal_contract_targets_current_s0_to_s4_outputs(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("audit-config.yaml", content)
        self.assertIn("rule_doc.md", content)
        self.assertIn("workbook.md", content)
        self.assertIn("sheets/*.json", content)
        self.assertIn("findings/*.json", content)
        self.assertIn("audit-report.md", content)
        self.assertIn("audit-report.docx", content)
        self.assertIn("qa-report.json", content)
        self.assertIn("oracle_correct_spreadsheet_path", content)
        self.assertIn("oracle_wrong_spreadsheet_path", content)

    def test_input_output_contracts_do_not_depend_on_retired_outputs(self):
        self.assertTrue(SKILL_PATH.exists(), f"missing skill file: {SKILL_PATH}")
        content = SKILL_PATH.read_text(encoding="utf-8")

        input_contract = extract_section(content, "输入契约（Input Contract）")
        output_contract = extract_section(content, "输出契约（Output Contract）")
        formal_contract = f"{input_contract}\n{output_contract}"

        self.assertNotIn("rules.json", formal_contract)
        self.assertNotIn("audit-report.json", formal_contract)
        self.assertNotRegex(formal_contract, r"corrected\.(xlsx|xls)")


if __name__ == "__main__":
    unittest.main()
