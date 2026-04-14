---
name: software-prototyper-s5-integration-qa
description: "完成软件原型集成与最终质量门控。Triggers on integration qa、smoke verification、final delivery."
---

**用途**

整合模块产物，完成集成修复并生成最终集成证据。
这里由 `Polecat` 产出最终集成证据，`Refinery` 独立运行验收命令并做 master 级终裁。
最终完成门槛要求 build、typecheck、单元测试、集成测试、端到端测试与浏览器验证全部成功。

## 依赖

- `software-prototyper-systematic-debugging`
- `software-prototyper-verification-before-completion`
- `software-prototyper-gt-mail-comm`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `workspace_root` | path | 是 | 原型工作区根目录 |
| `module_reports` | dir | 是 | 模块级验收结果目录 |

## 输出契约

- `output/{project_id}/evidence/integration/smoke-results.txt`
- `output/{project_id}/evidence/integration/e2e-results.txt`
- `output/{project_id}/evidence/integration/unit-test-results.txt`
- `output/{project_id}/evidence/integration/integration-test-results.txt`
- `output/{project_id}/evidence/integration/playwright-results.txt`
- `output/{project_id}/evidence/final-acceptance.md`

## 执行流程

1. 汇总模块级产物和 reviewer 结论。
2. 修复接口不一致、联调失败、环境配置缺口等集成问题。
3. 运行并汇总完整测试矩阵：单元测试、模块间集成测试、端到端测试、Playwright 关键用户流测试。
4. 运行启动验证、Smoke、build、typecheck 或集成级检查，生成正式证据。
5. 记录失败点并明确应该退回哪个 bead。
6. 生成最终交付证据。
7. 把证据提交给 `Refinery` 做独立验收与终裁。

## 验证清单

- [ ] 集成证据存在
- [ ] 单元测试、模块间集成测试、端到端测试、Playwright 测试证据齐全
- [ ] build、typecheck、单元测试、集成测试、端到端测试与浏览器验证全部成功
- [ ] 最终验收报告存在
- [ ] 失败点已明确归因或回退
- [ ] Polecat 产出最终集成证据
- [ ] Refinery 独立运行验收并做 master 级终裁
