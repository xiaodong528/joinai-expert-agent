---
name: software-prototyper-qa-checklist
description: "软件原型构建的模块级与最终验收清单。Triggers on module review、prototype qa、acceptance review、master validation."
---

**用途**

为 Refinery 提供统一的模块级、集成级和最终交付验收清单。
它是 Refinery 的验证协议，不只是 checklist，也承担终裁输入。

## 依赖

- `software-prototyper-verification-before-completion`
- `software-prototyper-requesting-code-review`
- `software-prototyper-receiving-code-review`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `review_scope` | string | 是 | `spec` / `foundation` / `module` / `final` |
| `evidence_dir` | path | 是 | 当前范围对应的证据目录 |

## 输出契约

- `Prototype-output/{project_id}/evidence/qa/{review_scope}-review.md`
- `Prototype-output/{project_id}/evidence/qa/{review_scope}-decision.txt`

## 执行流程

1. 核对规格、测试、运行证据和交付物。
2. 按模块或最终阶段给出 pass / warn / fail。
3. 若缺少证据，拒绝通过并明确缺口。
4. 给出终裁意见、失败分类与退回建议。
5. 把复核结论回传给 Mayor。

## 验证清单

- [ ] 结论由证据支撑
- [ ] 缺口与失败点可回溯
- [ ] 结论可供 Mayor 做重派或停止判断
- [ ] 已形成终裁输入而不是单次 review 备注
