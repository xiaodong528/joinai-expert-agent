import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENTS_DIR = ROOT / "joinai-expert-agent/video-generation/agents"
SKILLS_DIR = ROOT / "joinai-expert-agent/video-generation/skills"
EXPECTED_AGENTS = {
    "video-generation-orchestrator.md",
    "video-generation-worker.md",
    "video-generation-reviewer.md",
}
REQUIRED_SKILL_SECTIONS = [
    "**用途**",
    "## 依赖",
    "## 输入契约",
    "## 输出契约",
    "## 执行流程",
    "## 验证清单",
]


class VideoGenerationJasContractTests(unittest.TestCase):
    def test_agents_use_standard_three_role_names(self):
        actual = {path.name for path in AGENTS_DIR.glob("*.md")}
        self.assertTrue(EXPECTED_AGENTS.issubset(actual), actual)
        self.assertNotIn("video-producer.md", actual)

    def test_orchestrator_frontmatter_and_scope_are_compliant(self):
        path = AGENTS_DIR / "video-generation-orchestrator.md"
        self.assertTrue(path.exists(), f"missing agent file: {path}")
        content = path.read_text(encoding="utf-8")

        self.assertIn("mode: primary", content)
        self.assertIn("temperature: 0.1", content)
        self.assertIn("permission:", content)
        self.assertIn("GT role: `mayor`", content)
        self.assertNotIn(".opencode/skills", content)
        self.assertNotIn("python ~/.config/opencode/skills", content)

    def test_worker_and_reviewer_agents_exist_with_gt_roles(self):
        expectations = {
            "video-generation-worker.md": "GT role: `polecat`",
            "video-generation-reviewer.md": "GT role: `refinery`",
        }
        for filename, marker in expectations.items():
            path = AGENTS_DIR / filename
            self.assertTrue(path.exists(), f"missing agent file: {path}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("mode: primary", content)
            self.assertIn("permission:", content)
            self.assertIn(marker, content)

    def test_skills_have_required_jas_sections_and_runtime_paths(self):
        skill_dirs = [path for path in SKILLS_DIR.iterdir() if path.is_dir()]
        skill_names = {path.name for path in skill_dirs}
        self.assertIn("video-generation-qa-checklist", skill_names)
        self.assertIn("video-validate-storyboard", skill_names)

        for skill_dir in skill_dirs:
            skill_path = skill_dir / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"missing skill file: {skill_path}")
            content = skill_path.read_text(encoding="utf-8")

            for section in REQUIRED_SKILL_SECTIONS:
                self.assertIn(section, content, f"{skill_path} missing {section}")
            self.assertIsNone(re.search(r"(?<!Video-Producer-)output/\{project_id\}", content), skill_path)
            self.assertNotIn(".opencode/skills", content, skill_path)
            self.assertNotIn("video-producer", content, skill_path)


if __name__ == "__main__":
    unittest.main()
