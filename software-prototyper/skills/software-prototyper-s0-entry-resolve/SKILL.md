---
name: software-prototyper-s0-entry-resolve
description: "标准化软件原型任务入口。Triggers on brainstorm intake、plan intake、prototype entry resolve."
---

**用途**

识别当前任务是“从零 brainstorm”还是“读取现成方案”，并把输入材料标准化为统一执行上下文。

## 依赖

- `software-prototyper-using-superpowers`
- `software-prototyper-brainstorming`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `user_request` | string | 是 | 用户当前需求 |
| `plan_path` | string | 否 | 现成方案文档路径 |

## 输出契约

- `Prototype-output/{project_id}/specs/intake-summary.md`
- `Prototype-output/{project_id}/specs/input-mode.txt`
- `Prototype-output/{project_id}/specs/source-plan.md`（若有现成方案）

## 执行流程

1. 判断是否存在可直接读取的方案文档。
2. 若不存在，则进入 `software-prototyper-brainstorming` 流程，收敛出初始规格。
3. 把输入模式、关键约束和初始目标写入 `Prototype-output/{project_id}/specs/`。
4. 输出给 Mayor 继续 S1。

## 验证清单

- [ ] 入口类型已明确
- [ ] 输入材料已标准化
- [ ] 后续 S1 所需上下文已齐备
