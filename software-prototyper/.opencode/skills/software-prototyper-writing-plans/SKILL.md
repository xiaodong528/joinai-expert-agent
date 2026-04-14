---
name: software-prototyper-writing-plans
description: "在 GT 三角色模型下编写可派发的实施计划。Triggers on implementation planning、bead plan、wave execution plan."
---

# Writing Plans

## Overview

为 `software-prototyper` 主链编写可执行计划，供 `Mayor` 拆 bead、`Polecat` 执行、`Refinery` 验收。
计划必须天然适配 GT 三角色，而不是假设同会话实现者或通用子代理。
计划必须以执行文档包为单一真值来源展开，不得让聊天或口头补充凌驾于文档之上。

## Plan Requirements

- 计划先按 Wave 组织，再按 bead 组织
- 执行文档包是计划展开与验收判断的单一真值来源
- 每个 bead 必须包含：
  - 范围
  - 依赖
  - 目标输出
  - 验证命令
  - 单元测试、模块间集成测试、端到端测试、Playwright 测试要求
  - reviewer 验收点
  - 失败回退路径
- 优先拆成可独立派发的前端 / 后端 / 业务模块 / 测试模块任务，再补共享基础设施 / 数据层
- 测试模块是独立 bead 类型，可出现 `integration-test bead`、`e2e-test bead`、`browser-validation bead`

## Plan Header

```markdown
# [Feature Name] Execution Plan

**Goal:** [一句话目标]

**GT Flow:** Mayor 规划与派发 -> Polecat 执行 -> Refinery 独立验收

**Wave Strategy:** [Wave 1 / Wave 2 / Wave 3 的职责摘要]
```

## Task Structure

````markdown
### Wave 2 / Bead: frontend-checkout

**Owner:** Polecat
**Depends on:** foundation-routing, backend-cart-api
**Reviewer Gate:** checkout flow smoke + contract review

- [ ] 读取 bead 范围与冻结规格
- [ ] 写失败测试或失败用例
- [ ] 做最小实现
- [ ] 运行单元测试、模块间集成测试、端到端测试与 Playwright 测试
- [ ] 输出证据到 `output/{project_id}/evidence/modules/checkout/`
- [ ] 通过 GT 邮件提交给 Refinery
````

## Execution Handoff

计划完成后：

1. `Mayor` 使用 `software-prototyper-dispatching-parallel-agents` 确定并行拆分
2. 将具体 bead sling 给 `Polecat`
3. `Polecat` 使用 `software-prototyper-executing-plans` 执行
4. `Refinery` 使用 `software-prototyper-qa-checklist` 独立验收

## Remember

- 不写“让实现者自己决定”
- 不依赖通用子代理补足缺口
- 所有计划步骤都要能落到 GT 主链角色上
