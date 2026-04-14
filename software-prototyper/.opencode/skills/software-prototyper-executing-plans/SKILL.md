---
name: software-prototyper-executing-plans
description: "在 GT 三角色模型下执行已冻结的实施计划。Triggers on bead execution、worker plan run、implementation handoff."
---

# Executing Plans

## Overview

读取 `Mayor` 已冻结的计划，在当前 `Polecat` bead 范围内逐项执行，并把证据提交给 `Refinery`。
这里的执行是 GT 主链执行，不是同会话子代理执行。
执行文档包是当前 bead 的单一真值来源。

## The Process

### Step 1: 读取并复核计划

1. 读取当前 bead 对应的计划片段
2. 仅检查当前 bead 范围是否清晰、依赖是否满足、验证命令是否存在
3. 若计划缺关键上下文，立刻通过 GT 邮件回报 `Mayor`
4. 任何聊天、口头或邮件补充都只能作为待写回真值文档的候选信息，不能绕过执行文档包直接执行

### Step 2: 在当前 bead 范围内执行

1. 标记当前 bead `in_progress`
2. 严格按计划范围实现，不跨 bead 擅自扩展
3. 对代码变更优先执行 TDD
4. 运行计划要求的验证命令
5. 产出正式证据路径并回报
6. 任何失败、缺口、回归、伪实现、未完成模块，都必须继续修复直到全部收敛

### Step 3: 提交给 Reviewer

1. 使用 GT 邮件发送证据路径给 `Mayor` / `Refinery`
2. 等待 `Refinery` 独立验收
3. 若收到退回结论，在当前 bead 范围内修复并重复验证

## When to Stop and Ask for Help

立刻停止并回报 `Mayor`：

- 计划缺关键输入
- 当前 bead 与实际依赖冲突
- 需要跨模块决策
- 验证命令持续失败且超出当前 bead 范围

## Remember

- 只在当前 bead 范围内执行
- 不跳过验证
- 不自报完成
- 通过 GT 主链回传证据，不口头宣告“已完成”
- 持续修复直到全部收敛

## Integration

- `software-prototyper-test-driven-development`
- `software-prototyper-systematic-debugging`
- `software-prototyper-verification-before-completion`
- `software-prototyper-gt-status-report`
- `software-prototyper-gt-mail-comm`
