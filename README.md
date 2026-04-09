# JAS Expert Agents

这是 JAS（JoinAI Swarm Factory）的专家智能体资产仓库。

仓库当前已经收敛出 3 条真实存在的专家智能体主线：

- `video-generation`：AI 视频生成专家智能体
- `construction-aduit`：工程建设审核专家智能体
- `software-prototyper`：软件原型构建专家智能体

这里沉淀的不是某个业务系统本身，而是专家智能体的 3 类核心资产：

- `agents/`：角色智能体定义
- `skills/`：阶段能力与工作法技能
- `gt/`：Gas Town 运行时接入配置

部分目录还保留了 `docs/`、`output/`、`examples/`，用来承载说明文档、运行证据和样例输入。

## JAS 架构定位

JAS 采用 `OpenCode + Gas Town` 的双层架构：

- OpenCode 层负责专家知识表达
  这里定义领域 Agent、Skills、阶段边界、约束和执行协议。
- Gas Town 层负责运行时编排
  这里定义 Mayor / Polecat / Refinery 的角色映射、任务派发、状态观测和运行控制。

可以把它理解为：

- OpenCode 回答“这个专家智能体要做什么、按什么流程做”
- Gas Town 回答“谁来做、如何并行、如何验收、何时停止”

在当前仓库里，三个方向都已经按三角色主线组织：

- `Mayor`：编排、门禁、对用户交互
- `Polecat`：执行具体阶段技能
- `Refinery`：审查阶段产物和最终结论

`Witness` 仍可能在平台侧作为默认运行时巡检能力存在，但不是这三个方向当前 README 应强调的自定义主角色。

## 当前能力矩阵

| 方向 | 当前状态 | 角色结构 | 核心链路 | 当前证据形态 |
| --- | --- | --- | --- | --- |
| `video-generation` | 最成熟，主流程和阶段文档较完整 | Mayor / Polecat / Refinery | S0-S10 共 11 阶段视频生成，含 Wave 并行和最终 QA | `docs/v0.1.0/PROJECT-OVERVIEW.md`、GT 配置、`output/` 中已有样例 QA 与产物 |
| `construction-aduit` | 已完成三角色主线对齐并保留近期审计产物 | Mayor / Polecat / Refinery | S0 会话初始化 → S1 规则文档渲染 → S2 工作簿桥接 → S3 按 Sheet 审核 → S4 报告生成 | `docs/v0.1.0/Task-Overview.md`、GT 配置、`output/20260408-archive-oracle-verify/` |
| `software-prototyper` | 新增方向，骨架和技能包已成型，运行证据仍在补齐 | Mayor / Polecat / Refinery | 双入口接入 → S0-S2 规格与模块规划 → Wave 1 底座 → Wave 2 并行模块开发 → Wave 3 集成验收 | `docs/v0.1.0/Task-Overview.md`、`docs/v0.1.0/PLAN.md`、GT 配置，`output/` 目录已预留 |

这 3 条线的成熟度并不相同。根 README 的作用不是把它们写成同一完成度，而是明确说明“哪些已经跑出证据、哪些已经建好骨架、哪些还在继续补实战沉淀”。

## 当前目录结构

```text
.
├── construction-aduit/
│   ├── agents/
│   ├── docs/
│   ├── examples/
│   ├── gt/
│   ├── output/
│   └── skills/
├── software-prototyper/
│   ├── agents/
│   ├── docs/
│   ├── gt/
│   ├── output/
│   └── skills/
└── video-generation/
    ├── agents/
    ├── docs/
    ├── gt/
    ├── output/
    └── skills/
```

各层职责如下：

- `agents/`
  存放角色智能体定义，通常对应 Mayor、Polecat、Refinery 三个角色。
- `skills/`
  存放阶段技能或工作法技能，约定输入输出、执行步骤、验证清单和失败条件。
- `docs/`
  存放该方向的项目概览、阶段说明、验证记录、方案文档等。
  当前三个方向的主说明文档都位于各自的 `docs/v0.1.0/` 目录下。
- `gt/`
  存放 Gas Town 侧的 rig、role_agents、town settings、beads 或运行态配置。
- `output/`
  存放该方向的运行产物、验收证据或样例结果。
- `examples/`
  存放样例输入，目前主要出现在 `construction-aduit/`。

需要注意：

- 目录名 `construction-aduit` 保留了当前仓库中的真实路径命名。
- 其业务语义对应的是 `construction-audit`，也就是工程建设审核方向。

## 三个方向分别在做什么

### 1. `video-generation`

`video-generation` 面向 AI 视频制作的长链路编排，已经形成了较完整的阶段资产。

它当前覆盖：

- 创意策划与故事冻结
- 分镜脚本生成与角色锚定
- 关键帧生成、图生视频、TTS、BGM
- 拼接、对口型、字幕、最终 QA

它的重点不是单个脚本，而是“如何把一个多模型、多模态、可并行的视频生成流程拆成可调度的阶段技能，并交给 GT 做 Wave 编排”。

推荐入口文档：

- `video-generation/docs/v0.1.0/PROJECT-OVERVIEW.md`

### 2. `construction-aduit`

`construction-aduit` 面向工程预算 / 结算审核场景，强调强约束输入契约、按阶段门控、按 Sheet 并行审核和最终报告收口。

它当前覆盖：

- 会话初始化与审核配置生成
- 规则文档渲染
- 工作簿桥接与结构化导出
- 单 Sheet 审核并行执行
- Findings 聚合与报告生成

它的重点是“如何把高可靠、强追溯的审核流程交给三角色智能体协作执行”，并把阶段产物保留为可复核证据。

推荐入口文档：

- `construction-aduit/docs/v0.1.0/Task-Overview.md`

### 3. `software-prototyper`

`software-prototyper` 是仓库中新加入的通用软件原型构建专家智能体。

它当前覆盖：

- 从零开始 brainstorm 收敛需求
- 直接读取现成规格文档作为输入
- 规格冻结、模块拆解、Wave 规划
- 底座搭建、模块并行开发、集成验收

它的重点是“如何把一个软件原型从需求收敛一路推进到可运行交付”，并把开发工作法也沉淀成技能包，而不只是沉淀某一个垂直业务流程。

推荐入口文档：

- `software-prototyper/docs/v0.1.0/Task-Overview.md`
- `software-prototyper/docs/v0.1.0/PLAN.md`

## 如何阅读这个仓库

如果你是第一次进入这个仓库，建议按下面顺序阅读：

1. 先看本 README
   建立对三条主线、成熟度差异和通用目录分层的整体认知。
2. 再看各方向的总览文档
   根据你关心的方向进入对应 `docs/`，先理解目标、角色模型和主流程。
3. 再进入 `agents/` 和 `skills/`
   当你要改编排逻辑或某个阶段能力时，再看对应 Agent / Skill 定义。
4. 最后看 `gt/` 与 `output/`
   当你要接入运行时、复核产物或对照交付证据时，再看 GT 配置与输出目录。

如果你的目标是：

- 理解视频生成主线：从 `video-generation/docs/v0.1.0/PROJECT-OVERVIEW.md` 开始
- 理解工程审核主线：从 `construction-aduit/docs/v0.1.0/Task-Overview.md` 开始
- 理解软件原型构建主线：从 `software-prototyper/docs/v0.1.0/Task-Overview.md` 开始

## 后续路线图

仓库下一阶段的重点不是再回到“是否存在第三个方向”的讨论，而是继续把现有 3 条主线做实：

- 为 `software-prototyper` 补齐更多运行证据、验收样例和稳定的交付路径
- 继续沉淀三条线之间可复用的编排、验证、审查工作法
- 在现有模式稳定后，再扩展新的领域专家智能体

换句话说，当前仓库已经不再是“两条成熟主线 + 一个未来想法”，而是“3 条已落地但成熟度不同的专家智能体主线”。

## 总结

这个仓库承载的是 JAS 的专家智能体资产层：

- 用 `agents/` 表达角色职责和协作结构
- 用 `skills/` 表达阶段能力和执行契约
- 用 `gt/` 对接 Gas Town 运行时
- 用 `docs/` 与 `output/` 保存说明、证据和结果

当前最重要的阅读结论是：

- `video-generation`、`construction-aduit`、`software-prototyper` 都已经是仓库中的真实模块
- 三者都已采用三角色主线组织
- 它们的成熟度不同，README 需要忠实反映这种差异，而不是把仓库写成静态不变的“完成态展板”
