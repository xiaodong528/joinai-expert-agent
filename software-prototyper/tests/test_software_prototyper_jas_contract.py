import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENTS_DIR = ROOT / "joinai-expert-agent/software-prototyper/agents"
SKILLS_DIR = ROOT / "joinai-expert-agent/software-prototyper/skills"
EXPECTED_AGENTS = {
    "software-prototyper-orchestrator.md",
    "software-prototyper-worker.md",
    "software-prototyper-reviewer.md",
}
EXPECTED_SKILLS = {
    "software-prototyper-s0-entry-resolve",
    "software-prototyper-s1-spec-freeze",
    "software-prototyper-s2-module-plan",
    "software-prototyper-s3-foundation-bootstrap",
    "software-prototyper-s4-module-build",
    "software-prototyper-s5-integration-qa",
    "software-prototyper-qa-checklist",
}
EXPECTED_VENDORED_SKILLS = {
    "software-prototyper-using-superpowers",
    "software-prototyper-brainstorming",
    "software-prototyper-writing-plans",
    "software-prototyper-using-git-worktrees",
    "software-prototyper-test-driven-development",
    "software-prototyper-systematic-debugging",
    "software-prototyper-verification-before-completion",
    "software-prototyper-requesting-code-review",
    "software-prototyper-receiving-code-review",
    "software-prototyper-executing-plans",
    "software-prototyper-subagent-driven-development",
    "software-prototyper-finishing-a-development-branch",
    "software-prototyper-dispatching-parallel-agents",
    "software-prototyper-gt-cli",
    "software-prototyper-gt-status-report",
    "software-prototyper-gt-mail-comm",
}
REQUIRED_SKILL_SECTIONS = [
    "**用途**",
    "## 依赖",
    "## 输入契约",
    "## 输出契约",
    "## 执行流程",
    "## 验证清单",
]


class SoftwarePrototyperJasContractTests(unittest.TestCase):
    def test_agents_use_standard_three_role_names(self):
        actual = {path.name for path in AGENTS_DIR.glob("*.md")}
        self.assertEqual(EXPECTED_AGENTS, actual)

    def test_orchestrator_declares_dual_entry_and_goal_driven_loop(self):
        path = AGENTS_DIR / "software-prototyper-orchestrator.md"
        self.assertTrue(path.exists(), f"missing agent file: {path}")
        content = path.read_text(encoding="utf-8")

        self.assertIn("mode: primary", content)
        self.assertIn("temperature: 0.1", content)
        self.assertIn('GT role: `mayor`', content)
        self.assertIn("brainstorming", content)
        self.assertIn("从零开始，多轮 brainstorm", content)
        self.assertIn("直接读取现成方案文档", content)
        self.assertIn("不满足标准就重派、降级、拆细或人工升级", content)
        self.assertIn("并行 polecat / OpenCode 进程", content)
        self.assertNotIn("spawn_agent", content)
        self.assertNotIn("goal-driven-development", content)
        self.assertIn("与 Refinery 共同组成 master 控制面", content)
        self.assertIn("Goal", content)
        self.assertIn("Criteria for Success", content)
        self.assertIn("Verification Loop", content)

    def test_worker_and_reviewer_capture_required_skill_chains(self):
        expectations = {
            "software-prototyper-worker.md": [
                'GT role: `polecat`',
                "using-git-worktrees",
                "test-driven-development",
                "systematic-debugging",
                "verification-before-completion",
                "多个并行执行单元",
                "不得自报完成",
            ],
            "software-prototyper-reviewer.md": [
                'GT role: `refinery`',
                "verification-before-completion",
                "requesting-code-review",
                "receiving-code-review",
                "参与停止条件裁定",
                "退回建议",
                "失败分类",
            ],
        }
        for filename, markers in expectations.items():
            path = AGENTS_DIR / filename
            self.assertTrue(path.exists(), f"missing agent file: {path}")
            content = path.read_text(encoding="utf-8")
            self.assertIn("mode: primary", content)
            self.assertIn("permission:", content)
            for marker in markers:
                self.assertIn(marker, content, f"{path} missing {marker}")

    def test_skills_exist_with_required_sections_and_output_root(self):
        actual = {path.name for path in SKILLS_DIR.iterdir() if path.is_dir()}
        self.assertEqual(EXPECTED_SKILLS | EXPECTED_VENDORED_SKILLS, actual)
        self.assertNotIn("software-prototyper-goal-driven-development", actual)

        for skill_name in EXPECTED_SKILLS:
            skill_path = SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"missing skill file: {skill_path}")
            content = skill_path.read_text(encoding="utf-8")
            for section in REQUIRED_SKILL_SECTIONS:
                self.assertIn(section, content, f"{skill_path} missing {section}")
            self.assertIn("Prototype-output/{project_id}", content)
            self.assertNotIn(".opencode/skills", content)
            self.assertNotIn("goal-driven-development", content)

    def test_vendored_skills_have_key_artifacts(self):
        required_paths = [
            "software-prototyper-using-superpowers/SKILL.md",
            "software-prototyper-using-superpowers/references/codex-tools.md",
            "software-prototyper-brainstorming/SKILL.md",
            "software-prototyper-brainstorming/scripts/start-server.sh",
            "software-prototyper-writing-plans/plan-document-reviewer-prompt.md",
            "software-prototyper-systematic-debugging/root-cause-tracing.md",
            "software-prototyper-requesting-code-review/code-reviewer.md",
            "software-prototyper-subagent-driven-development/implementer-prompt.md",
            "software-prototyper-gt-cli/references/commands-work.md",
            "software-prototyper-gt-status-report/SKILL.md",
            "software-prototyper-gt-mail-comm/SKILL.md",
        ]
        for rel_path in required_paths:
            path = SKILLS_DIR / rel_path
            self.assertTrue(path.exists(), f"missing vendored artifact: {path}")

    def test_stage_skills_capture_master_and_reviewer_contracts(self):
        expectations = {
            "software-prototyper-s1-spec-freeze": [
                "master 级成功标准",
                "裁定接口",
            ],
            "software-prototyper-s2-module-plan": [
                "reviewer 验收点",
                "失败回退路径",
            ],
            "software-prototyper-s4-module-build": [
                "等待 Reviewer 裁定",
                "不得自报完成",
            ],
            "software-prototyper-s5-integration-qa": [
                "Polecat 产出最终集成证据",
                "Refinery 做 master 级终裁",
            ],
            "software-prototyper-qa-checklist": [
                "Refinery 的验证协议",
                "终裁",
            ],
        }
        for skill_name, markers in expectations.items():
            content = (SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8")
            for marker in markers:
                self.assertIn(marker, content, f"{skill_name} missing {marker}")

    def test_agents_and_runtime_skills_use_local_prefixed_dependencies(self):
        target_files = list(AGENTS_DIR.glob("*.md")) + list((SKILLS_DIR).glob("software-prototyper-*/SKILL.md"))
        forbidden = [
            "`using-superpowers`",
            "`brainstorming`",
            "`writing-plans`",
            "`using-git-worktrees`",
            "`test-driven-development`",
            "`systematic-debugging`",
            "`verification-before-completion`",
            "`requesting-code-review`",
            "`receiving-code-review`",
            "`executing-plans`",
            "`subagent-driven-development`",
            "`finishing-a-development-branch`",
            "`dispatching-parallel-agents`",
            "`gt-cli`",
            "`gt-status-report`",
            "`gt-mail-comm`",
            "`goal-driven-development`",
        ]
        for path in target_files:
            content = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, content, f"{path} still references external skill {marker}")

    def test_review_workflow_is_self_contained_and_supports_workspace_mode(self):
        review_skill = (SKILLS_DIR / "software-prototyper-requesting-code-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        reviewer_prompt = (
            SKILLS_DIR / "software-prototyper-subagent-driven-development/code-quality-reviewer-prompt.md"
        ).read_text(encoding="utf-8")
        reviewer_template = (
            SKILLS_DIR / "software-prototyper-requesting-code-review/code-reviewer.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("superpowers:code-reviewer", review_skill)
        self.assertNotIn("superpowers:code-reviewer", reviewer_prompt)
        self.assertIn("code-reviewer.md", review_skill)
        self.assertIn("code-reviewer.md", reviewer_prompt)
        self.assertIn("工作区", review_skill)
        self.assertIn("git status --short", review_skill)
        self.assertIn("WORKSPACE_PATHS", reviewer_template)
        self.assertIn("WORKSPACE_STATUS", reviewer_template)

    def test_gt_shared_skills_use_software_prototyper_language(self):
        status_skill = (SKILLS_DIR / "software-prototyper-gt-status-report/SKILL.md").read_text(
            encoding="utf-8"
        )
        mail_skill = (SKILLS_DIR / "software-prototyper-gt-mail-comm/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("construction-audit", status_skill)
        self.assertNotIn("construction-audit", mail_skill)
        self.assertNotIn("audit-config.yaml", mail_skill)
        self.assertNotIn("workbook.md", mail_skill)
        self.assertNotIn("findings/*.json", mail_skill)
        self.assertNotIn("qa-report.json", mail_skill)
        self.assertIn("Prototype-output/{project_id}", mail_skill)


if __name__ == "__main__":
    unittest.main()
