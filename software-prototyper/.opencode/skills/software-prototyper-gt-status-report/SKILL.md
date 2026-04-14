---
name: software-prototyper-gt-status-report
description: "Gas Town 状态上报共享技能：供 Orchestrator、Worker、Reviewer 在 GT 会话中执行 `gt prime`、`bd update` 与 `gt done`，同步当前 rig 下的角色身份、Wave / bead 状态和完成信号。Gas Town 默认 witness 巡逻若启用，仍应使用 `bd mol wisp`，不得使用 `bd mol pour`。Triggers on gt status, status report, bead update, worker done, 会话初始化、状态上报、巡逻记录。"
---

# Skill: software-prototyper-gt-status-report

**用途（Purpose）:** software-prototyper 主链三角色共享的 GT 状态上报技能。在 Gas Town 会话中统一处理角色身份注入、Wave / bead 状态更新和完成信号。Gas Town 默认 witness 巡逻若启用，仍由平台默认机制负责。所有状态都以当前 rig 为唯一真值来源。

## 依赖

- GT 运行时环境：`gt`、`bd` CLI 可用
- 当前 GT 会话环境变量：`GT_ROLE`、`GT_RIG`、`GT_AGENT`、`BD_ACTOR`
- Gas Town 默认 witness 巡逻若启用，必须使用 `bd mol wisp`；禁止使用 `bd mol pour`

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `current_rig` | string | 是 | 当前会话激活的 rig，必须与 GT 注入上下文一致 |
| `role` | enum | 是 | `mayor` / `polecat` / `refinery` |
| `bead_id` | string | 否 | 使用 `bd update` 时的任务 ID |
| `status` | enum | 否 | `in_progress` / `blocked` / `done` / `failed` |
| `reason` | string | 否 | 状态变更原因或补充说明 |

## 输出契约（Output Contract）

| 输出 | 类型 | 说明 |
|------|------|------|
| Agent 身份注入 | 会话上下文 | `gt prime` 将当前角色身份注入到当前会话 |
| Bead 状态更新 | GT / Dolt 记录 | `bd update` 写入当前任务状态 |
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

- Orchestrator 标记 S0 / S1 / S2 或 Wave 启动与等待依赖
- Worker 标记 bead 开始、阻塞、完成或失败
- Reviewer 标记独立验收完成并回写结论

### 3. Gas Town 默认 witness 巡逻说明

```bash
bd mol wisp <mol-id>
```

约束：

- Gas Town 默认 witness 若启用，只记录当前 rig 下的巡逻执行
- software-prototyper 不再注册 custom witness agent
- 禁止把默认 witness 巡逻写成 `bd mol pour`
- 若需要在状态说明中提到命令差异，必须明确 `bd mol wisp` 而非 `bd mol pour`

### 4. Worker 完成信号

```bash
gt done
```

用途：

- Worker 完成 bead 后向 Orchestrator 发出完成信号
- Reviewer 完成独立验收后也可配合状态写回
- Orchestrator 再决定是否进入下一阶段或触发下一轮 review

## 验证清单（Validation Checklist）

- [ ] `gt prime` 执行后，当前会话已注入正确角色与当前 rig
- [ ] `bd update` 仅更新当前 rig 下对应 bead 的状态
- [ ] 状态值仅使用 `in_progress`、`blocked`、`done`、`failed`
- [ ] 文案明确当前主链围绕 S0 / S1 / S2 / Wave 1 / Wave 2 / Wave 3
- [ ] 文案明确 Gas Town 默认 witness 不属于 software-prototyper 自定义角色注册
- [ ] Gas Town 默认 witness 巡逻若启用，使用 `bd mol wisp`，不得使用 `bd mol pour`
- [ ] `gt done` 用于 bead 或验收结论完成后的正式完成信号
- [ ] 状态说明中明确“当前 rig 是唯一真值来源”

## 非职责范围（Non-goals）

- 不负责跨 rig 迁移或切换旧 rig
- 不负责定义业务阶段产物内容
- 不替代 `software-prototyper-gt-mail-comm` 的结构化消息传递
