---
name: gt-status-report
description: "Gas Town 状态上报共享技能：供 Orchestrator、Worker、Reviewer、Monitor 在 GT 会话中执行 `gt prime`、`bd update`、`bd mol wisp` 与 `gt done`，同步当前 rig 下的角色身份、任务状态、巡逻记录和完成信号。Triggers on gt status, status report, bead update, worker done, witness patrol, 会话初始化、状态上报、巡逻记录。"
---

# Skill: gt-status-report

**用途（Purpose）:** 所有角色共享的 GT 状态上报技能。在 Gas Town 会话中统一处理角色身份注入、Bead 状态更新、Witness 巡逻记录和 Worker 完成信号。所有状态都以当前 rig 为唯一真值来源。

## 依赖

- GT 运行时环境：`gt`、`bd` CLI 可用
- 当前 GT 会话环境变量：`GT_ROLE`、`GT_RIG`、`GT_AGENT`、`BD_ACTOR`
- Witness 巡逻必须使用 `bd mol wisp`；禁止使用 `bd mol pour`

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `current_rig` | string | 是 | 当前会话激活的 rig，必须与 GT 注入上下文一致 |
| `role` | enum | 是 | `mayor` / `polecat` / `refinery` / `witness` |
| `bead_id` | string | 否 | 使用 `bd update` 时的任务 ID |
| `status` | enum | 否 | `in_progress` / `blocked` / `done` / `failed` |
| `mol_id` | string | 否 | Witness 巡逻记录的 molecule / wisp ID |
| `reason` | string | 否 | 状态变更原因或补充说明 |

## 输出契约（Output Contract）

| 输出 | 类型 | 说明 |
|------|------|------|
| Agent 身份注入 | 会话上下文 | `gt prime` 将当前角色身份注入到当前会话 |
| Bead 状态更新 | GT / Dolt 记录 | `bd update` 写入当前任务状态 |
| 巡逻执行记录 | GT / Dolt 记录 | `bd mol wisp` 记录 Witness 巡逻 |
| 完成信号 | GT 事件 | `gt done` 通知 Orchestrator 当前 sling 任务已结束 |

## 执行流程

### 1. 会话初始化

```bash
gt prime
gt prime --hook
```

用途：

- 初始化当前角色身份
- 确认当前 rig 与当前角色已注入会话
- 任何后续状态上报都以当前 rig 为唯一真值来源

### 2. Bead 状态更新

```bash
bd update <bead-id> --status in_progress
bd update <bead-id> --status blocked
bd update <bead-id> --status done
bd update <bead-id> --status failed
```

典型场景：

- Orchestrator 标记阶段开始或等待依赖
- Worker 标记任务开始、阻塞或失败
- Reviewer 标记 review 完成

### 3. Witness 巡逻记录

```bash
bd mol wisp <mol-id>
```

约束：

- Witness 只记录当前 rig 下的巡逻执行
- 禁止把 Witness 巡逻写成 `bd mol pour`
- 若需要在状态说明中提到命令差异，必须明确 `bd mol wisp` 而非 `bd mol pour`

### 4. Worker 完成信号

```bash
gt done
```

用途：

- Worker 完成 sling 任务后向 Orchestrator 发出完成信号
- Orchestrator 再决定是否进入下一阶段或触发 Reviewer / Monitor

## 验证清单（Validation Checklist）

- [ ] `gt prime` 执行后，当前会话已注入正确角色与当前 rig
- [ ] `bd update` 仅更新当前 rig 下对应 bead 的状态
- [ ] 状态值仅使用 `in_progress`、`blocked`、`done`、`failed`
- [ ] Witness 巡逻使用 `bd mol wisp`，不得使用 `bd mol pour`
- [ ] `gt done` 仅在 Worker 完成当前 sling 任务后触发
- [ ] 状态说明中明确“当前 rig 是唯一真值来源”

## 非职责范围（Non-goals）

- 不负责跨 rig 迁移或切换旧 rig
- 不负责定义业务阶段产物内容
- 不替代 `gt-mail-comm` 的结构化消息传递

