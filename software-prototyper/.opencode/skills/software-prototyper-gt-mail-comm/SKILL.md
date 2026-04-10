---
name: software-prototyper-gt-mail-comm
description: "Gas Town 邮件通信共享技能：供 Orchestrator、Worker、Reviewer 在当前 rig 内通过 `gt mail send`、`gt mail check --inject`、`gt mail list`、`gt mail read` 协调 S0-S4 阶段任务与 review 请求。Gas Town 默认 witness 巡逻不属于 software-prototyper 自定义通信主链。Triggers on gt mail, send message, check mail, review request, Agent 间通信、邮件通知、阶段回执。"
---

# Skill: software-prototyper-gt-mail-comm

**用途（Purpose）:** software-prototyper 主链三角色共享的 GT 邮件通信技能。在当前 rig 内统一处理任务分派、阶段回执与审查请求。Gas Town 默认 witness 巡逻继续由平台接管，不作为 software-prototyper 自定义邮件通信角色。

## 依赖

- GT 运行时环境：`gt mail` CLI 可用
- 当前 GT 会话环境变量：`GT_ROLE`、`GT_RIG`
- 共享角色：`Orchestrator`、`Worker`、`Reviewer`

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `to` | enum | 否 | `mayor` / `polecat` / `refinery` |
| `subject` | string | 否 | 邮件主题，建议包含阶段标识和动作 |
| `body` | string | 否 | 邮件正文，建议包含状态、摘要、附件路径 |
| `mail_id` | string | 否 | 读取指定邮件时使用 |
| `current_rig` | string | 是 | 当前会话的 rig，所有通信均限定在该 rig 内 |

## 输出契约（Output Contract）

| 输出 | 类型 | 说明 |
|------|------|------|
| 邮件发送确认 | stdout | `gt mail send` 成功后输出邮件 ID |
| 未读邮件注入 | 会话上下文 | `gt mail check --inject` 注入未读邮件 |
| 邮件列表 | stdout | `gt mail list` 列出邮件元信息 |
| 邮件全文 | stdout | `gt mail read <id>` 输出完整邮件内容 |

## 执行流程

### 1. 发送邮件

```bash
gt mail send --to <role> --subject "[Wave 2] Review Request - Module evidence ready" --body "
阶段：Wave 2
状态：需审查
摘要：模块证据与测试结果已生成
附件路径：Prototype-output/{project_id}/evidence/modules/<module>/summary.md, Prototype-output/{project_id}/evidence/modules/<module>/test-results.txt"
```

### 2. 检查与读取邮件

```bash
gt mail check --inject
gt mail list
gt mail read <mail-id>
```

### 3. 典型通信模式

| 发送方 | 接收方 | 场景 |
|--------|--------|------|
| Orchestrator | Worker | S0-S4 阶段任务分派、重试指令、补充上下文 |
| Worker | Orchestrator | S0-S4 完成/失败回执，附当前正式产物路径 |
| Orchestrator | Reviewer | S0、S1、S2、S3、S4 阶段 review 请求 |
| Reviewer | Orchestrator | QA 结论回执，附 `Prototype-output/{project_id}/evidence/qa/<scope>-decision.txt` |
### 4. 邮件主题与正文约定

推荐主题格式：

```text
[S0] Dispatch - Entry resolve
[S1] Done - Spec freeze complete
[Wave 2] Review Request - Module ready
[Wave 2] Alert - Module stalled
[Wave 3] Done - Final acceptance evidence ready
```

推荐正文结构：

```text
阶段：S0 / S1 / S2 / Wave 2 / Wave 3
状态：进行中 / 完成 / 失败 / 需审查 / 告警
摘要：一句话说明
附件路径：只引用当前正式产物，例如 Prototype-output/{project_id}/specs/execution-spec.md、Prototype-output/{project_id}/plans/module-map.yaml、Prototype-output/{project_id}/evidence/modules/<module>/summary.md、Prototype-output/{project_id}/evidence/final-acceptance.md
```

## 补充说明

- Gas Town 默认 witness 若启用，仍由平台按默认 patrol 机制处理；software-prototyper 不再注册 custom witness agent，也不依赖其参与主链邮件通信。

## 验证清单（Validation Checklist）

- [ ] `gt mail send` 返回邮件 ID，且接收方可通过 `gt mail check --inject` 收到
- [ ] `gt mail list` 能列出当前 rig 内邮件元信息
- [ ] `gt mail read` 能读取指定邮件全文
- [ ] 邮件主题包含 `S0`、`S1`、`S2`、`S3` 或 `S4`
- [ ] 典型通信模式覆盖 Orchestrator、Worker、Reviewer
- [ ] 文案明确 Gas Town 默认 witness 不属于 software-prototyper 自定义通信主链
- [ ] 附件路径只引用当前正式产物，不引用历史 JSON 报告或修正版工作簿

## 非职责范围（Non-goals）

- 不替代 `software-prototyper-gt-status-report` 的状态写回
- 不跨 rig 发送消息
- 不要求正式依赖历史 JSON 版报告
- 不要求正式依赖修正版工作簿文件
