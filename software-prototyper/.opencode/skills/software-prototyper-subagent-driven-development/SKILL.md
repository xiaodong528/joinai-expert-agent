---
name: software-prototyper-subagent-driven-development
description: "兼容旧名称：在 GT 中把实现计划拆成多个 Polecat bead 并走 Mayor -> Polecat -> Refinery 闭环。"
---

# Bead-Driven Development

> 历史名称保留兼容。此 skill 在 `software-prototyper` 中不表示 Codex / Claude 子代理，而表示 GT 中的 bead 驱动开发。

## Overview

当一个实施计划包含多个相互独立的任务时，由 `Mayor` 将任务拆成多个 bead，派发给多个 `Polecat`，并在每个 bead 完成后交给 `Refinery` 独立验收。

## The Process

1. `Mayor` 读取完整计划并提取可独立交付的任务块
2. 按前端 / 后端 / 业务模块 / 测试模块拆 bead，再补共享层 / 数据层
3. 使用 `software-prototyper-dispatching-parallel-agents` 确定并行与串行关系
4. 将每个 bead sling 给对应 `Polecat`
5. 每个 `Polecat` 使用 `software-prototyper-executing-plans` 在本 bead 内执行
6. `Refinery` 对每个 bead 独立做 `pass / warn / fail`
7. `Mayor` 根据结论决定推进、重派或拆细

## When to Use

- 计划里有 2 个及以上独立模块
- 前端与后端可以并行
- 某些业务模块彼此独立
- 测试模块需要独立参与 wave
- 集成修复需要等待前序模块完成

## Red Flags

- 不要把同一关键文件的高冲突修改并行派发
- 不要让 `Polecat` 自己决定新的 bead 边界
- 不要用这个 skill 指代通用子代理执行

## Outputs

- `output/{project_id}/plans/parallel-dispatch.md`
- bead 粒度、依赖和验收点说明
