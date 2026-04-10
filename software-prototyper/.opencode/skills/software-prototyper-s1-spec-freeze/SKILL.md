---
name: software-prototyper-s1-spec-freeze
description: "冻结软件原型的执行态规格。Triggers on spec freeze、prototype constraints、acceptance criteria."
---

**用途**

把已收敛的需求冻结成可执行规格，明确目标、范围、技术栈、模块清单和验收标准。
同时补齐 master 级成功标准 与 裁定接口，供 Mayor 与 Refinery 共用。

## 依赖

- `software-prototyper-writing-plans`
- `software-prototyper-verification-before-completion`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `intake_summary` | markdown | 是 | S0 生成的入口摘要 |
| `stack_policy` | string | 是 | 用户指定优先，未指定时默认栈 |

## 输出契约

- `Prototype-output/{project_id}/specs/execution-spec.md`
- `Prototype-output/{project_id}/specs/acceptance-criteria.md`
- `Prototype-output/{project_id}/specs/project-config.yaml`
- `Prototype-output/{project_id}/specs/master-decision-interface.md`

## 执行流程

1. 汇总目标、约束、技术栈与模块范围。
2. 明确停止条件，禁止模糊表述。
3. 写出 master 级成功标准、失败分类入口和裁定接口。
4. 固化为执行态规格与项目配置。
5. 交给 Mayor 做 S1 Gate，并供 Refinery 后续引用。

## 验证清单

- [ ] 规格可供后续模块拆解直接使用
- [ ] 停止条件为可验证标准
- [ ] 默认栈策略已明确写入
- [ ] master 级成功标准已固化
- [ ] 裁定接口可供 Mayor 与 Refinery 复用
