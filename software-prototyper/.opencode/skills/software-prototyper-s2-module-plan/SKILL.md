---
name: software-prototyper-s2-module-plan
description: "将执行态规格拆成模块 beads 与依赖图。Triggers on module planning、bead split、wave planning."
---

**用途**

把冻结规格拆成模块级执行单元，形成可并行的 bead 计划和 Wave 顺序。
每个模块都必须带 reviewer 验收点 和 失败回退路径。

## 依赖

- `software-prototyper-gt-cli`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `execution_spec` | markdown | 是 | S1 冻结的执行态规格 |

## 输出契约

- `Prototype-output/{project_id}/plans/module-map.yaml`
- `Prototype-output/{project_id}/plans/bead-matrix.md`
- `Prototype-output/{project_id}/plans/wave-plan.md`

## 执行流程

1. 标记基础设施模块与业务模块边界。
2. 给每个模块定义输入、输出、依赖和 reviewer 验收点。
3. 为每个模块写明失败回退路径、重派条件和回到哪个 bead。
4. 生成 Wave 1 / Wave 2 / Wave 3 的执行顺序。
5. 输出 bead 计划给 GT 配置与 Wave 文档。

## 验证清单

- [ ] 模块边界清晰
- [ ] 并行与串行依赖关系明确
- [ ] 每个模块都有验收点
- [ ] 每个模块都有失败回退路径
