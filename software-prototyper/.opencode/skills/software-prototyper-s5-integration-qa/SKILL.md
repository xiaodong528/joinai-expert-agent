---
name: software-prototyper-s5-integration-qa
description: "完成软件原型集成与最终质量门控。Triggers on integration qa、smoke verification、final delivery."
---

**用途**

整合模块产物，运行系统级检查，并为最终验收生成证据。
这里由 Polecat 产出最终集成证据，Refinery 做 master 级终裁。

## 依赖

- `software-prototyper-verification-before-completion`
- `software-prototyper-requesting-code-review`
- `software-prototyper-receiving-code-review`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `workspace_root` | path | 是 | 原型工作区根目录 |
| `module_reports` | dir | 是 | 模块级验收结果目录 |

## 输出契约

- `Prototype-output/{project_id}/evidence/integration/smoke-results.txt`
- `Prototype-output/{project_id}/evidence/integration/e2e-results.txt`
- `Prototype-output/{project_id}/evidence/final-acceptance.md`

## 执行流程

1. 汇总模块级产物和 reviewer 结论。
2. 运行启动验证、Smoke 或 E2E。
3. 记录失败点并决定是否退回模块 bead。
4. 生成最终交付证据。
5. 把证据提交给 Refinery 做 master 级终裁。

## 验证清单

- [ ] 集成证据存在
- [ ] 最终验收报告存在
- [ ] 失败点已明确归因或回退
- [ ] Polecat 产出最终集成证据
- [ ] Refinery 做 master 级终裁
