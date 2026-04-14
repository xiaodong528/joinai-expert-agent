import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ConstructionAuditAgentPromptContracts(unittest.TestCase):
    def test_orchestrator_direct_executes_non_parallel_stages_and_keeps_s3_parallel(self):
        content = read_text(".opencode/agents/construction-audit-orchestrator.md")

        self.assertIn("项目源目录必须固定为 GT 工作空间同级下的 `output/<project-name>`", content)
        self.assertIn("file:///abs/path", content)
        self.assertIn("gt rig add <rig> <url>", content)
        self.assertIn("gt rig start <rig>", content)
        self.assertIn("gt polecat list <rig>", content)
        self.assertIn("snake_case 风格 rig 名", content)
        self.assertIn("rig 名只能包含小写字母、数字、下划线", content)
        self.assertIn("budget_table4_1to8_review", content)
        self.assertNotIn("连字符", content)
        self.assertNotIn("budget-table4-1to8-review", content)
        self.assertIn("只有 S3 通过 `gt sling` 派发给 Polecat", content)
        self.assertIn("S0 文件处理、S1、S2、S4 必须由 Mayor 直接加载技能执行", content)
        stage_order = [
            "`construction-audit-s0-session-init`",
            "`construction-audit-s1-rule-doc-render`",
            "`construction-audit-s2-workbook-render`",
            "`construction-audit-s3-sheet-audit`",
            "`construction-audit-s4-error-report`",
        ]
        positions = [content.index(stage_name) for stage_name in stage_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("审查目标只能来自 `audit-config.yaml.spreadsheet.sheets`", content)
        self.assertIn("`hidden_sheets` 只能作为跨表计算的只读上下文", content)
        self.assertIn("固定拆成 3 个子批次", content)
        self.assertIn("每个 sheet 的 3 个子批次完成后，必须先合并成单个 `findings_<sheet>.json`", content)
        self.assertIn("`gt sling` × (可见 sheet 数 × 3 + 可见 sheet 数)", content)
        self.assertIn("`mode=shard_audit`", content)
        self.assertIn("`mode=merge_sheet_findings`", content)
        self.assertIn("`findings/parts/<sheet>/findings_<sheet>__part_{1..3}.json`", content)
        self.assertIn("Mayor 直接执行 S0 文件处理", content)
        self.assertIn("Mayor 直接执行 S1 文档渲染", content)
        self.assertIn("Mayor 直接执行 S2 工作簿渲染", content)
        self.assertIn("Mayor 直接执行 S4 报告生成", content)

    def test_worker_only_handles_s3_parallel_modes(self):
        content = read_text(".opencode/agents/construction-audit-worker.md")

        self.assertIn("若当前 rig 缺少 URL、URL 非法、URL 使用裸路径，或项目源目录不在 GT 工作空间同级下的 `output/<project-name>`，立即回报 `Mayor`", content)
        self.assertIn("本地项目 rig URL 必须是 `file:///abs/path`；远程项目 rig URL 必须是远程 git URL", content)
        self.assertIn("每个可见 sheet 固定 3 路 GT Polecat", content)
        self.assertIn("不接受通用子智能体并行替代", content)
        self.assertIn("`mode=shard_audit`", content)
        self.assertIn("`mode=merge_sheet_findings`", content)
        self.assertIn("`batch_count=3`", content)
        self.assertIn("`assigned_rule_rows`", content)
        self.assertIn("`partial_output_path`", content)
        self.assertIn("`partial_findings_paths`", content)
        self.assertIn("hidden sheet 只能作为 `calc_formula.py --context-sheets-dir` 的只读上下文", content)
        self.assertIn("Polecat 只执行 S3 双层并行审查", content)
        self.assertNotIn("| `/construction-audit-s0-session-init` |", content)
        self.assertNotIn("| `/construction-audit-s1-rule-doc-render` |", content)
        self.assertNotIn("| `/construction-audit-s2-workbook-render` |", content)
        self.assertNotIn("| `/construction-audit-s4-error-report` |", content)

    def test_reviewer_reviews_stage_outputs_and_keeps_s3_polecat_constraint(self):
        content = read_text(".opencode/agents/construction-audit-reviewer.md")

        self.assertIn("rig URL 合法性属于 review 前置检查", content)
        self.assertIn("项目源目录不在 GT 工作空间同级下的 `output/<project-name>` 时直接阻塞", content)
        self.assertIn("本地项目 rig URL 必须是 `file:///abs/path`；远程项目 rig URL 必须是远程 git URL", content)
        self.assertIn("并行批次必须来自多个正式 `Polecat` 交付", content)
        self.assertIn("不接受通用子智能体产物冒充并行执行结果", content)
        self.assertIn("S3/S4 只以可见目标 sheet 的最终合并 findings 为审查对象", content)
        self.assertIn("不对 hidden sheet 要求独立 findings", content)
        self.assertIn("每个可见目标 sheet 恰好 1 个最终 `findings_<sheet>.json`", content)
        self.assertIn("每阶段产物完成后，Mayor 通知 Refinery 执行 review", content)
        self.assertIn("S0 Mayor 产物完成后", content)
        self.assertIn("S1 Mayor 产物完成后", content)
        self.assertIn("S2 Mayor 产物完成后", content)
        self.assertIn("S4 Mayor 产物完成后", content)


if __name__ == "__main__":
    unittest.main()
