---
name: software-prototyper-s2-module-plan
description: "将执行态规格拆成模块 beads 与依赖图。Triggers on module planning、bead split、wave planning."
---

**用途**

把冻结规格拆成 GT 可执行的 bead 与 Wave 计划。
默认至少覆盖前端、后端、共享基础设施、数据层和业务模块几个执行面，并为每个 bead 附 reviewer 验收点与失败回退路径。

## 依赖

- `software-prototyper-gt-cli`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `execution_spec` | markdown | 是 | S1 冻结的执行态规格 |

## 输出契约

- `output/{project_id}/plans/module-map.yaml`
- `output/{project_id}/plans/bead-matrix.md`
- `output/{project_id}/plans/wave-plan.md`

## 执行流程

1. 先拆出共享基础设施 bead，再拆前端 bead、后端 bead、数据 bead 与业务模块 bead。
2. 给每个 bead 定义输入、输出、依赖、负责人角色和 reviewer 验收点。
3. 明确哪些 bead 可并行，哪些 bead 必须等待前序完成。
4. 为每个 bead 写明失败回退路径、重派条件和回到哪个 bead。
5. 生成 Wave 1 / Wave 2 / Wave 3 的执行顺序与 GT 派发建议。
6. 输出 bead 计划给 GT 配置与 Wave 文档。

## 验证清单

- [ ] 模块边界清晰
- [ ] 并行与串行依赖关系明确
- [ ] 每个模块都有验收点
- [ ] 每个模块都有失败回退路径
- [ ] 前端 / 后端 / 共享基础设施 / 数据层拆分策略明确
