import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALL_SKILLS = [
    "software-prototyper-agent-browser",
    "software-prototyper-brainstorming",
    "software-prototyper-dispatching-parallel-agents",
    "software-prototyper-executing-plans",
    "software-prototyper-finishing-a-development-branch",
    "software-prototyper-gt-cli",
    "software-prototyper-gt-mail-comm",
    "software-prototyper-gt-status-report",
    "software-prototyper-qa-checklist",
    "software-prototyper-receiving-code-review",
    "software-prototyper-requesting-code-review",
    "software-prototyper-s0-entry-resolve",
    "software-prototyper-s1-spec-freeze",
    "software-prototyper-s2-module-plan",
    "software-prototyper-s3-foundation-bootstrap",
    "software-prototyper-s4-module-build",
    "software-prototyper-s5-integration-qa",
    "software-prototyper-subagent-driven-development",
    "software-prototyper-systematic-debugging",
    "software-prototyper-test-driven-development",
    "software-prototyper-using-git-worktrees",
    "software-prototyper-using-superpowers",
    "software-prototyper-verification-before-completion",
    "software-prototyper-writing-plans",
]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    parts = text.split("---")
    if len(parts) < 3:
        raise AssertionError("missing frontmatter")
    return parts[1]


class AgentContractTests(unittest.TestCase):
    def test_all_agents_reference_all_project_skills(self):
        for relative_path in (
            ".opencode/agents/software-prototyper-orchestrator.md",
            ".opencode/agents/software-prototyper-worker.md",
            ".opencode/agents/software-prototyper-reviewer.md",
        ):
            content = read_text(relative_path)
            self.assertIn("## Skill Matrix", content)
            self.assertIn("直接使用", content)
            self.assertIn("协调交接", content)
            self.assertIn("禁止越权", content)
            self.assertIn("首次合法、且不越权", content)
            self.assertIn("首次合法节点显式触发", content)
            self.assertIn("执行文档包", content)
            self.assertIn("单一真值来源", content)
            self.assertIn("不要等待人工分配细项", content)
            self.assertIn("持续推进直到完成", content)
            self.assertIn("任何失败、缺口、回归、伪实现、未完成模块，都必须继续修复直到全部收敛", content)
            for skill in ALL_SKILLS:
                self.assertIn(skill, content, f"{skill} missing from {relative_path}")

    def test_orchestrator_permissions_and_boundaries(self):
        content = read_text(".opencode/agents/software-prototyper-orchestrator.md")
        fm = frontmatter(content)

        self.assertNotIn('"software-prototyper-*": allow', fm)
        self.assertIn("software-prototyper-subagent-driven-development", fm)
        self.assertNotIn("software-prototyper-s3-foundation-bootstrap", fm)
        self.assertNotIn("software-prototyper-s4-module-build", fm)
        self.assertNotIn("software-prototyper-s5-integration-qa", fm)
        self.assertNotIn("software-prototyper-test-driven-development", fm)
        self.assertNotIn("software-prototyper-agent-browser", fm)
        self.assertNotIn("software-prototyper-requesting-code-review", fm)
        self.assertNotIn("software-prototyper-receiving-code-review", fm)
        self.assertNotIn("software-prototyper-finishing-a-development-branch", fm)
        self.assertIn("不得写业务代码", content)
        self.assertIn("不得自行跑开发测试", content)
        self.assertIn("必须优先加载并使用对应的 `software-prototyper-*` 项目技能", content)
        self.assertIn("默认且优先使用 `software-prototyper-gt-cli` 驱动 GT `Polecat`", content)
        self.assertIn("不得使用 `Task` 创建子智能体完成项目任务；若需要新增执行面，默认优先派发 `Polecat` 完成。", content)
        self.assertIn("优先走 `gt sling <bead> <rig>`、`gt sling <bead> <rig>/<polecat>`", content)
        self.assertIn("不得把当前会话自己的通用子智能体当作默认执行面", content)
        self.assertIn("即使当前环境支持 `Task` 或其他子智能体能力，也不得把它们当作默认执行面替代 `Polecat`。", content)
        self.assertIn("完成项目任务前，先创建或确认 rig 已存在并可用；没有有效 rig，不进入项目任务，不进入 S0-S5。", content)
        self.assertIn("单元测试、模块间集成测试、端到端测试、Playwright 测试缺一不可", content)
        self.assertIn("默认把单模块作为最小执行单元", content)
        self.assertIn("默认遵循“一模块一 bead、一 bead 一 Polecat、同一 Wave 多 Polecat 并行”", content)
        self.assertIn("同一 Wave 内对无阻塞模块同时 dispatch 到多个 `Polecat`。", content)
        self.assertIn("优先把同一 Wave 中所有 ready beads 批量 sling 给多个 `Polecat`", content)
        self.assertIn("Wave 2 若存在 3 个及以上无阻塞模块 bead，默认至少同时维持 3 个活跃 `Polecat`", content)
        self.assertIn("JAS 的并行能力默认通过多 `Polecat` 批量 dispatch 来体现，而不是串行排队等待单个执行单元", content)
        self.assertIn("先完整理解执行文档包，再自行拆分全部任务", content)
        self.assertIn("后续所有派发、执行、验收都只能以执行文档包为单一真值来源", content)
        self.assertIn("默认先按 `前端 / 后端 / 业务模块 / 测试模块` 四类拆分", content)
        self.assertIn("测试模块是独立 bead 类型", content)
        self.assertIn("可出现专门的 `integration-test bead`、`e2e-test bead`、`browser-validation bead`", content)
        self.assertIn("不要等待人工分配细项", content)
        self.assertIn("默认持续推进 wave，不因普通失败或缺口中途停下来要方案确认", content)
        self.assertIn("只有在不可恢复的外部阻塞、权限或凭证缺失、或高风险破坏性操作时才允许回流人工", content)
        self.assertIn("完成门槛", content)
        self.assertIn("项目可运行、可演示，不是文档或空壳", content)
        self.assertIn("核心页面和核心流程都已落地", content)
        self.assertIn("单元测试全部通过", content)
        self.assertIn("集成测试全部通过", content)
        self.assertIn("端到端测试全部通过", content)
        self.assertIn("浏览器测试全部通过", content)
        self.assertIn("构建、类型检查、测试命令全部成功", content)
        self.assertIn("最终结论必须基于真实代码、真实测试结果和真实浏览器验证", content)
        self.assertIn(
            "`software-prototyper-agent-browser` | 协调交接 | 当模块或最终验收需要浏览器自动化测试时，Mayor 负责把浏览器自动化测试节点交接给 `Polecat` 或 `Refinery`",
            content,
        )
        self.assertIn("gt rig list", content)
        self.assertIn("gt rig status <rig>", content)
        self.assertNotIn("gt rig add <rig> --adopt --force", content)
        self.assertNotIn("gt init", content)
        self.assertIn("gt rig add <rig> <url>", content)
        self.assertIn("标准创建链路是：`gt rig add <rig> <url>` → `gt rig start <rig>`", content)
        self.assertIn("file:///abs/path", content)
        self.assertIn("禁止裸路径", content)
        self.assertIn("项目源目录必须固定为 GT 工作空间同级下的 `output/<project-name>`", content)
        self.assertIn("不要把“当前还没有 GitHub 仓库”误判成“不能创建 rig”", content)
        self.assertIn("gt rig start <rig>", content)
        self.assertIn("新项目默认先建 rig、再绑定 URL、再进入任何 S0-S5 项目阶段。", content)
        self.assertIn("本地项目 URL 必须是 `file:///abs/path`；远程项目必须是远程 git URL；禁止裸路径。", content)
        self.assertIn("`Mayor`: `intake -> spec freeze -> module plan -> dispatch -> acceptance coordination`", content)
        self.assertIn("| Rig 前置 | `software-prototyper-gt-cli` | check/create/start rig before any project task | Mayor 直接执行 |", content)
        self.assertIn(
            "Mayor 在 S2 必须按 `software-prototyper-writing-plans -> software-prototyper-subagent-driven-development -> software-prototyper-s2-module-plan -> software-prototyper-dispatching-parallel-agents` 的顺序推进。",
            content,
        )
        self.assertIn("`software-prototyper-subagent-driven-development` | 直接使用 | 作为 Mayor 在 S2 的显式 bead-driven 编排步骤", content)
        self.assertIn(
            "`software-prototyper-requesting-code-review` | 协调交接 | 若 `Refinery` 或外部结论要求额外代码审查，由 Mayor 把 review 节点交接给 `Polecat` 触发",
            content,
        )
        self.assertIn(
            "`software-prototyper-finishing-a-development-branch` | 协调交接 | 只有当 `Refinery` 已放行且需进入收尾节点时，Mayor 才通知 `Polecat` 触发",
            content,
        )
        for stage in ("S0", "S1", "S2", "S3", "S4", "S5"):
            self.assertIn(stage, content)
        self.assertIn(
            "| S3 | `software-prototyper-s3-foundation-bootstrap` | dispatch / tracking / evidence collection / acceptance coordination |",
            content,
        )
        self.assertIn(
            "| S4 | `software-prototyper-s4-module-build` | dispatch / tracking / evidence collection / acceptance coordination |",
            content,
        )
        self.assertIn(
            "| S5 | `software-prototyper-s5-integration-qa` | dispatch / tracking / evidence collection / acceptance coordination |",
            content,
        )

    def test_worker_permissions_and_boundaries(self):
        content = read_text(".opencode/agents/software-prototyper-worker.md")
        fm = frontmatter(content)

        self.assertNotIn('"software-prototyper-*": allow', fm)
        self.assertIn("software-prototyper-s3-foundation-bootstrap", fm)
        self.assertIn("software-prototyper-s4-module-build", fm)
        self.assertIn("software-prototyper-s5-integration-qa", fm)
        self.assertIn("software-prototyper-test-driven-development", fm)
        self.assertIn("software-prototyper-agent-browser", fm)
        self.assertIn("software-prototyper-requesting-code-review", fm)
        self.assertIn("software-prototyper-receiving-code-review", fm)
        self.assertIn("software-prototyper-finishing-a-development-branch", fm)
        self.assertIn("软件原型执行任务时，必须优先加载并使用对应的 `software-prototyper-*` 项目技能", content)
        self.assertIn("rig 是执行前置依赖", content)
        self.assertNotIn("rig 可能来自本地初始化或本地 adopt", content)
        self.assertIn("file:///abs/path", content)
        self.assertIn("rig 必须带有可追溯 URL", content)
        self.assertIn("项目源目录必须固定为 GT 工作空间同级下的 `output/<project-name>`", content)
        self.assertIn("当前 bead 执行前默认假定 rig 已由 `Mayor` 创建并启动。", content)
        self.assertIn("实现型 bead 开始时默认先加载 `software-prototyper-test-driven-development`", content)
        self.assertIn("每个 `Polecat` 默认只负责一个明确模块 bead。", content)
        self.assertIn("不同时吃多个模块 bead；同 Wave 中其他模块由其他 `Polecat` 并行处理。", content)
        self.assertIn("你是 JAS 并行执行池中的一个活跃 `Polecat`", content)
        self.assertIn("默认预期同一 Wave 中会并发存在多个活跃 `Polecat`", content)
        self.assertIn("当 `Mayor` 批量派发 ready beads 时，你必须把自己的交付视为并行批次的一部分", content)
        self.assertIn("涉及页面交互、浏览器自动化 smoke、真实 Web 流程验证时，必须优先使用 `software-prototyper-agent-browser`", content)
        self.assertIn("执行文档包是当前 bead 唯一真值来源", content)
        self.assertIn("收到口头、邮件或聊天补充时，只能把它当作待写回真值文档的候选信息，不能绕过文档直接执行", content)
        self.assertIn("只负责一个明确方向", content)
        self.assertIn("不接受由 `Task` 创建的子智能体替代正式 GT `Polecat` 执行面", content)
        self.assertIn("不要等待人工分配细项", content)
        self.assertIn("默认收到 bead 就持续执行、修复、回归、再验证，直到当前 bead 真正满足验收门槛", content)
        self.assertIn("不得把“代码已写完”“页面能打开”或“局部测试过了”当成完成", content)
        self.assertIn("若发现伪实现、缺口、回归、未落地模块，必须继续修复直到全部收敛", content)
        self.assertIn("项目可运行、可演示，不是文档或空壳", content)
        self.assertIn("核心页面和核心流程都已落地", content)
        self.assertIn("单元测试全部通过", content)
        self.assertIn("集成测试全部通过", content)
        self.assertIn("端到端测试全部通过", content)
        self.assertIn("浏览器测试全部通过", content)
        self.assertIn("构建、类型检查、测试命令全部成功", content)
        self.assertIn("最终结论必须基于真实代码、真实测试结果和真实浏览器验证", content)
        self.assertIn("按 `RED -> GREEN -> REFACTOR` 推进当前模块 bead", content)
        self.assertIn("单元测试、模块间集成测试、端到端测试、Playwright 测试", content)
        self.assertIn("不自行创建或注册 rig", content)
        self.assertIn("商品目录 / 搜索筛选", content)
        self.assertIn("结算 / 模拟支付", content)
        self.assertIn("不得自报“系统已完成”", content)
        self.assertIn(
            "默认 bead 生命周期必须按 `software-prototyper-using-superpowers -> software-prototyper-using-git-worktrees（如适用） -> software-prototyper-executing-plans -> software-prototyper-test-driven-development -> 阶段 skill -> software-prototyper-systematic-debugging（如失败） -> software-prototyper-requesting-code-review（达到可审查结果时） -> software-prototyper-receiving-code-review（收到反馈时） -> software-prototyper-verification-before-completion -> software-prototyper-gt-status-report -> software-prototyper-gt-mail-comm -> software-prototyper-finishing-a-development-branch（仅在放行后）` 的顺序推进。",
            content,
        )
        self.assertIn(
            "`software-prototyper-agent-browser` | 直接使用 | 开发阶段的浏览器自动化 smoke、关键页面交互验证和真实 Web 流程测试统一走这个 skill",
            content,
        )
        self.assertIn(
            "`software-prototyper-requesting-code-review` | 直接使用 | 当前 bead 达到“可审查结果”时立即触发，请求额外代码审查以提前发现问题",
            content,
        )
        self.assertIn(
            "`software-prototyper-receiving-code-review` | 直接使用 | 收到 `Refinery`、外部 reviewer 或人工反馈后，先验证意见再在当前 bead 范围内返工",
            content,
        )
        self.assertIn(
            "`software-prototyper-finishing-a-development-branch` | 直接使用 | 仅在 `Mayor` 或 `Refinery` 已明确放行进入收尾节点后，按条件型收尾流程执行",
            content,
        )
        for stage in ("S0", "S1", "S2", "S3", "S4", "S5"):
            self.assertIn(stage, content)

    def test_reviewer_permissions_and_independent_validation(self):
        content = read_text(".opencode/agents/software-prototyper-reviewer.md")
        fm = frontmatter(content)

        self.assertNotIn('"software-prototyper-*": allow', fm)
        self.assertIn("software-prototyper-qa-checklist", fm)
        self.assertIn("software-prototyper-agent-browser", fm)
        self.assertNotIn("software-prototyper-s5-integration-qa", fm)
        self.assertNotIn("software-prototyper-requesting-code-review", fm)
        self.assertNotIn("software-prototyper-receiving-code-review", fm)
        self.assertNotIn("software-prototyper-finishing-a-development-branch", fm)
        self.assertIn("必须独立运行关键验证命令", content)
        self.assertIn("rig 是验收前置依赖", content)
        self.assertNotIn("rig 可能来自本地初始化或本地 adopt", content)
        self.assertIn("file:///abs/path", content)
        self.assertIn("rig 必须带有可追溯 URL", content)
        self.assertIn("项目源目录必须固定为 GT 工作空间同级下的 `output/<project-name>`", content)
        self.assertIn("若 rig 未创建、未启动或会话缺失，输出 `warn/fail` 并回流 `Mayor`。", content)
        self.assertIn("若 rig 缺 URL、URL 非法、URL 使用裸路径、或项目源目录不在 GT 工作空间同级下的 `output/<project-name>`，也必须把它当作阻塞条件回流给 `Mayor`。", content)
        self.assertIn("每个模块 bead 完成后，至少检查 TDD 证据是否覆盖 `RED -> GREEN -> REFACTOR` 的最小闭环。", content)
        self.assertIn("并行 Wave 下，每个 `Polecat` 只应交付自己负责的模块 bead", content)
        self.assertIn("不接受 `Task` 创建的子智能体产物替代正式 GT `Polecat` 执行结果", content)
        self.assertIn("对并行批次中的多个 `Polecat` 结果按 wave 统一做 gate 判断", content)
        self.assertIn("当同一 Wave 同时回流多个模块结果时，优先执行批量验收与批量退回判断", content)
        self.assertIn("需要独立运行浏览器自动化验收、关键页面 walkthrough 或真实 Web 用户流复核时，必须优先使用 `software-prototyper-agent-browser`", content)
        self.assertIn("执行文档包是验收判断的单一真值来源", content)
        self.assertIn("不接受“聊天里说过”“代码里大概有了”这种非文档证据", content)
        self.assertIn("持续审查、持续验收、持续 gate，直到结果真正收敛", content)
        self.assertIn("Refinery 是唯一的 merge / landing 放行 owner", content)
        self.assertIn("未通过 `Refinery` 的结果不得并入下一 wave、并入集成结果、进入最终交付、或进入 finishing / merge queue / landing 节点", content)
        self.assertIn("浏览器验证失败即整体 `warn` 或 `fail`", content)
        self.assertIn("项目可运行、可演示，不是文档或空壳", content)
        self.assertIn("核心页面和核心流程都已落地", content)
        self.assertIn("单元测试全部通过", content)
        self.assertIn("集成测试全部通过", content)
        self.assertIn("端到端测试全部通过", content)
        self.assertIn("浏览器测试全部通过", content)
        self.assertIn("构建、类型检查、测试命令全部成功", content)
        self.assertIn("最终结论必须基于真实代码、真实测试结果和真实浏览器验证", content)
        self.assertIn("单元测试", content)
        self.assertIn("模块间集成测试", content)
        self.assertIn("端到端测试", content)
        self.assertIn("Playwright 测试", content)
        self.assertIn("`pass / warn / fail`", content)
        self.assertIn("`Refinery`: `independent verification -> QA decision -> stop-condition adjudication input`", content)
        self.assertIn(
            "`software-prototyper-agent-browser` | 直接使用 | 独立浏览器自动化验收、关键页面 walkthrough 和真实 Web 用户流复核统一走这个 skill",
            content,
        )
        self.assertIn(
            "验收主链默认按 `software-prototyper-using-superpowers -> 读取 S0/S1/S2 上下文 -> software-prototyper-qa-checklist -> software-prototyper-verification-before-completion -> software-prototyper-gt-status-report -> software-prototyper-gt-mail-comm` 的顺序推进。",
            content,
        )
        self.assertIn(
            "若发现代码层缺口需要额外 code review，必须把“需 code review / 已收到 code review 反馈需返工”作为 gate 结论回流给 `Mayor`，不得由 `Refinery` 直接触发或处理。",
            content,
        )
        self.assertIn(
            "若进入分支收尾判断，`Refinery` 只给出“允许进入 finishing 节点 / 不允许”的证据化结论，不直接执行 `software-prototyper-finishing-a-development-branch`。",
            content,
        )
        for stage in ("S0", "S1", "S2", "S3", "S4", "S5"):
            self.assertIn(stage, content)


class WorkflowSkillContractTests(unittest.TestCase):
    def test_gt_semantic_workflow_skills(self):
        targets = [
            ".opencode/skills/software-prototyper-dispatching-parallel-agents/SKILL.md",
            ".opencode/skills/software-prototyper-executing-plans/SKILL.md",
            ".opencode/skills/software-prototyper-subagent-driven-development/SKILL.md",
            ".opencode/skills/software-prototyper-writing-plans/SKILL.md",
        ]

        banned_phrases = [
            "fresh subagent",
            "same-session subagent",
            "Task tool",
            "code quality reviewer subagent",
            "spec reviewer subagent",
            "implementer subagent",
            "Claude Code or Codex",
        ]

        for target in targets:
            content = read_text(target)
            for phrase in banned_phrases:
                self.assertNotIn(phrase, content, f"{phrase} leaked into {target}")

        self.assertIn("GT `Polecat`", read_text(".opencode/skills/software-prototyper-dispatching-parallel-agents/SKILL.md"))
        self.assertIn("GT 主链执行", read_text(".opencode/skills/software-prototyper-executing-plans/SKILL.md"))
        self.assertIn("历史名称保留兼容", read_text(".opencode/skills/software-prototyper-subagent-driven-development/SKILL.md"))
        self.assertIn("Mayor 规划与派发 -> Polecat 执行 -> Refinery 独立验收", read_text(".opencode/skills/software-prototyper-writing-plans/SKILL.md"))
        self.assertIn("默认至少同时拉起 3 个 `Polecat`", read_text(".opencode/skills/software-prototyper-dispatching-parallel-agents/SKILL.md"))
        self.assertIn("name: software-prototyper-agent-browser", read_text(".opencode/skills/software-prototyper-agent-browser/SKILL.md"))
        self.assertIn("当前 bead 达到“可审查结果”时触发", read_text(".opencode/skills/software-prototyper-requesting-code-review/SKILL.md"))
        self.assertIn("反馈来源可以是 `Refinery`、外部 reviewer、或人工 review", read_text(".opencode/skills/software-prototyper-receiving-code-review/SKILL.md"))
        self.assertIn("只能发生在验收放行之后", read_text(".opencode/skills/software-prototyper-finishing-a-development-branch/SKILL.md"))
        self.assertIn("执行文档包", read_text(".opencode/skills/software-prototyper-writing-plans/SKILL.md"))
        self.assertIn("测试模块", read_text(".opencode/skills/software-prototyper-writing-plans/SKILL.md"))
        self.assertIn("browser-validation bead", read_text(".opencode/skills/software-prototyper-dispatching-parallel-agents/SKILL.md"))
        self.assertIn("持续修复直到全部收敛", read_text(".opencode/skills/software-prototyper-executing-plans/SKILL.md"))
        self.assertIn("持续修复直到全部收敛", read_text(".opencode/skills/software-prototyper-systematic-debugging/SKILL.md"))
        self.assertIn("构建、类型检查、测试命令全部成功", read_text(".opencode/skills/software-prototyper-qa-checklist/SKILL.md"))
        self.assertIn("浏览器测试全部通过", read_text(".opencode/skills/software-prototyper-qa-checklist/SKILL.md"))
        self.assertIn("build、typecheck、单元测试、集成测试、端到端测试与浏览器验证全部成功", read_text(".opencode/skills/software-prototyper-s5-integration-qa/SKILL.md"))
        self.assertIn("开发侧 smoke", read_text(".opencode/skills/software-prototyper-agent-browser/SKILL.md"))
        self.assertIn("验收侧独立 walkthrough", read_text(".opencode/skills/software-prototyper-agent-browser/SKILL.md"))
        self.assertIn("失败时必须回流并继续修复", read_text(".opencode/skills/software-prototyper-agent-browser/SKILL.md"))

    def test_stage_and_acceptance_contracts(self):
        s2 = read_text(".opencode/skills/software-prototyper-s2-module-plan/SKILL.md")
        s4 = read_text(".opencode/skills/software-prototyper-s4-module-build/SKILL.md")
        s5 = read_text(".opencode/skills/software-prototyper-s5-integration-qa/SKILL.md")
        qa = read_text(".opencode/skills/software-prototyper-qa-checklist/SKILL.md")
        mail = read_text(".opencode/skills/software-prototyper-gt-mail-comm/SKILL.md")
        status = read_text(".opencode/skills/software-prototyper-gt-status-report/SKILL.md")
        plans = read_text(".opencode/skills/software-prototyper-writing-plans/SKILL.md")
        gt_cli = read_text(".opencode/skills/software-prototyper-gt-cli/SKILL.md")
        workspace_ref = read_text(".opencode/skills/software-prototyper-gt-cli/references/commands-workspace.md")

        for phrase in ("前端", "后端", "共享基础设施", "数据层"):
            self.assertIn(phrase, s2)

        self.assertIn("单元测试与模块间集成测试证据", s4)
        self.assertIn("单元测试、模块间集成测试、端到端测试、Playwright 测试证据齐全", s5)
        self.assertIn("已检查单元测试、模块间集成测试、端到端测试和 Playwright 测试", qa)
        self.assertIn("单元测试、模块间集成测试、端到端测试、Playwright 测试要求", plans)
        self.assertIn("Refinery` 独立运行验收命令", s5)
        self.assertIn("关键验收由 Refinery 独立运行或明确受限原因", qa)
        self.assertIn("默认采用**本地优先**口径", gt_cli)
        self.assertIn("不要把“先建 GitHub 仓库”当成技术前置", gt_cli)
        self.assertIn("file:///Users/me/src/repo", gt_cli)
        self.assertIn("invalid git URL \"/abs/path\"", gt_cli)
        self.assertIn("gt rig add <rig> --adopt --force", workspace_ref)
        self.assertIn("file:///abs/path", workspace_ref)
        self.assertIn("does not require GitHub first", workspace_ref)

        for stage in ("S0", "S1", "S2", "Wave 1", "Wave 2", "Wave 3"):
            self.assertIn(stage, mail)
            self.assertIn(stage, status)


if __name__ == "__main__":
    unittest.main()
