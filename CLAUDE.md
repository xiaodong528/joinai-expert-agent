# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库定位

JAS（JoinAI Swarm Factory）专家智能体资产仓库。存放三条领域专家智能体主线的定义资产，不是可运行的应用程序。

三条主线（成熟度递减）：
- `video-generation/` — AI 视频生成（最成熟，S0-S10 共 11 阶段）
- `construction-aduit/` — 工程建设审核（三角色主线已完成对齐）
- `software-prototyper/` — 软件原型构建（骨架成型，运行证据在补齐）

## 架构：OpenCode + Gas Town 双层

- **OpenCode 层**（本仓库）：定义领域 Agent、Skills、阶段边界、约束和执行协议
- **Gas Town 层**（`gt/` 目录 + 外部运行时）：负责角色映射、任务派发（`gt sling`）、状态观测、Wave 编排

每个领域模块都采用**三角色主线**：

| GT 角色 | 职责 | 对应文件命名 |
|---------|------|-------------|
| Mayor (编排) | 门控、调度、用户交互、Wave 管理 | `*-orchestrator.md` |
| Polecat (执行) | 具体阶段技能执行 | `*-worker.md` |
| Refinery (审查) | 阶段产物和最终结论审查 | `*-reviewer.md` |

## 目录约定

每个领域模块统一包含：
- `.opencode/agents/` — 角色智能体定义（`.md`，含 YAML frontmatter）
- `.opencode/skills/` — 阶段技能和工作法技能
- `gt/` — Gas Town 运行时配置（rigs.json、config.json、beads/）
- `docs/` — 项目概览和阶段说明
- `output/` — 运行产物和验收证据

运行时发现以各模块根目录下的 `.opencode/agents/` 与 `.opencode/skills/` 为准。`construction-aduit/gt` 因为是嵌套 Git 仓库，额外通过 `construction-aduit/gt/.opencode -> ../.opencode` bridge 继承同一份项目级定义。

## 常用命令

```bash
# 运行 Python 测试
python -m pytest -q --import-mode=importlib

# 运行单个 skill 的测试
pytest construction-aduit/.opencode/skills/<skill-name>/tests -q

# 验证 GT JSON 配置
python3 -m json.tool construction-aduit/gt/settings/config.json

# Gas Town 运行时（在各模块 gt/ 目录下执行）
cd gt && gt prime
gt mail check --inject
gt config agent list

# 查看模块级注册
find construction-aduit video-generation software-prototyper -maxdepth 2 -path '*/.opencode/agents' -o -path '*/.opencode/skills'
```

## Agent 定义格式

Agent 文件使用 Markdown + YAML frontmatter：

```yaml
---
description: 角色描述和触发词
mode: primary
color: "#2E86AB"
temperature: 0.1
permission:
  skill:
    "domain-*": allow
    "gt-*": allow
---
```

关键结构：角色与职责 → 阶段调度表 → GT Sling 调度协议 → 约束。

## 编码约定

- Agent 和 Skill 用 Markdown 书写，保持标题简短、步骤明确
- Python 辅助脚本：4 空格缩进、`snake_case`、测试文件 `test_*.py`
- 测试放在对应 skill 旁：`*/.opencode/skills/<skill>/tests/`
- 提交格式：`feat: ...`、`fix: ...`、`docs: ...`、`chore: ...`

## 约束

- 不提交 secrets、`.env*`、`output/` 内容和 GT 运行态生成的 `.opencode/` 产物
- 不恢复已退役的单角色入口或隐藏源路径
- 改了 Stage Skill 要同步更新对应的 GT bead 指令
- `gt/` 和 output 目录的运行态文件不应作为源码编辑
- 各模块的本地 `AGENTS.md` 和 `CLAUDE.md` 优先于根级指导
- 目录名 `construction-aduit` 保留原始拼写，业务语义对应 `construction-audit`
