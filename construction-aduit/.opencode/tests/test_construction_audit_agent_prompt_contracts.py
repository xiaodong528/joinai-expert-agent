import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ConstructionAuditAgentPromptContracts(unittest.TestCase):
    def test_orchestrator_requires_rig_url_and_polecat_parallelism(self):
        content = read_text(".opencode/agents/construction-audit-orchestrator.md")

        self.assertIn("项目源目录必须固定为 GT 工作空间同级下的 `output/<project-name>`", content)
        self.assertIn("file:///abs/path", content)
        self.assertIn("gt rig add <rig> <url>", content)
        self.assertIn("gt rig start <rig>", content)
        self.assertIn("gt polecat list <rig>", content)
        self.assertIn("每个 Sheet 必须 sling 给独立 Polecat 并行执行", content)
        self.assertIn("所有涉及文件读写、脚本执行的工作必须 `gt sling` 给 Polecat", content)

    def test_worker_rejects_invalid_url_and_subagent_parallelism(self):
        content = read_text(".opencode/agents/construction-audit-worker.md")

        self.assertIn("若当前 rig 缺少 URL、URL 非法、URL 使用裸路径，或项目源目录不在 GT 工作空间同级下的 `output/<project-name>`，立即回报 `Mayor`", content)
        self.assertIn("本地项目 rig URL 必须是 `file:///abs/path`；远程项目 rig URL 必须是远程 git URL", content)
        self.assertIn("每个 sheet 一个 GT Polecat", content)
        self.assertIn("不接受通用子智能体并行替代", content)

    def test_reviewer_blocks_invalid_rig_url_and_non_polecat_batches(self):
        content = read_text(".opencode/agents/construction-audit-reviewer.md")

        self.assertIn("rig URL 合法性属于 review 前置检查", content)
        self.assertIn("项目源目录不在 GT 工作空间同级下的 `output/<project-name>` 时直接阻塞", content)
        self.assertIn("本地项目 rig URL 必须是 `file:///abs/path`；远程项目 rig URL 必须是远程 git URL", content)
        self.assertIn("并行批次必须来自多个正式 `Polecat` 交付", content)
        self.assertIn("不接受通用子智能体产物冒充并行执行结果", content)


if __name__ == "__main__":
    unittest.main()
