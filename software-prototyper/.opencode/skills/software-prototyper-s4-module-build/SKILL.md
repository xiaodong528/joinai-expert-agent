---
name: software-prototyper-s4-module-build
description: "按模块实现软件原型。Triggers on module build、feature slice、module delivery."
---

**用途**

指导 Polecat 在模块级 bead 内完成实现、测试、修复和交付证据整理。
模块完成后必须等待 Reviewer 裁定，且不得自报完成。

## 依赖

- `software-prototyper-using-git-worktrees`
- `software-prototyper-test-driven-development`
- `software-prototyper-systematic-debugging`
- `software-prototyper-verification-before-completion`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `module_name` | string | 是 | 模块名称，如 `auth` |
| `module_bead` | markdown | 是 | 当前模块 bead |

## 输出契约

- `output/{project_id}/workspace/`
- `output/{project_id}/evidence/modules/{module_name}/summary.md`
- `output/{project_id}/evidence/modules/{module_name}/test-results.txt`
- `output/{project_id}/evidence/modules/{module_name}/unit-test-results.txt`
- `output/{project_id}/evidence/modules/{module_name}/integration-test-results.txt`

## 执行流程

1. 读取当前模块 bead，确认范围和停止条件。
2. 优先写失败测试，再做最小实现。
3. 至少补齐当前模块的单元测试与模块间集成测试证据。
4. 若失败，先做根因分析，再修复。
5. 保存模块证据，等待 Reviewer 裁定。
6. 未获通过前不得自报完成，也不得并入最终交付。

## 验证清单

- [ ] 模块范围未越界
- [ ] 模块有测试证据
- [ ] 模块单元测试与模块间集成测试证据齐全
- [ ] 模块交付说明已保存
- [ ] 已等待 Reviewer 裁定
