---
name: software-prototyper-qa-checklist
description: "软件原型构建的模块级与最终验收清单。Triggers on module review、prototype qa、acceptance review、master validation."
---

**用途**

为 `Refinery` 提供统一的模块级、集成级和最终交付验收清单。
它是独立运行验收的协议，不只是 checklist，也承担终裁输入。
未通过该清单的结果不得进入 merge / landing / final delivery。

## 依赖

- `software-prototyper-verification-before-completion`
- `software-prototyper-gt-mail-comm`
- `software-prototyper-gt-status-report`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `review_scope` | string | 是 | `spec` / `foundation` / `module` / `final` |
| `evidence_dir` | path | 是 | 当前范围对应的证据目录 |

## 输出契约

- `output/{project_id}/evidence/qa/{review_scope}-review.md`
- `output/{project_id}/evidence/qa/{review_scope}-decision.txt`

## 执行流程

1. 核对规格、测试、运行证据和交付物。
2. 针对当前范围独立检查完整测试矩阵：单元测试、模块间集成测试、端到端测试、Playwright 测试。
3. 独立运行关键验收命令，或明确记录不能运行的客观原因。
4. 按模块或最终阶段给出 `pass / warn / fail`。
5. 若缺少证据，拒绝通过并明确缺口。
6. 给出终裁意见、失败分类与退回建议。
7. 把复核结论回传给 `Mayor`。
8. 若任一完成门槛未满足，明确禁止进入 merge / landing / final delivery。

## 验证清单

- [ ] 结论由证据支撑
- [ ] 项目可运行、可演示，不是文档或空壳
- [ ] 核心页面和核心流程都已落地
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 端到端测试全部通过
- [ ] 浏览器测试全部通过
- [ ] 构建、类型检查、测试命令全部成功
- [ ] 最终结论必须基于真实代码、真实测试结果和真实浏览器验证
- [ ] 已检查单元测试、模块间集成测试、端到端测试和 Playwright 测试
- [ ] 关键验收由 Refinery 独立运行或明确受限原因
- [ ] 缺口与失败点可回溯
- [ ] 结论可供 Mayor 做重派或停止判断
- [ ] 已形成终裁输入而不是单次 review 备注
