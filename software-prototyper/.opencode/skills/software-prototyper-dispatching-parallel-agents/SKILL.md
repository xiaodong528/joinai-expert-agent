---
name: software-prototyper-dispatching-parallel-agents
description: "在 GT 中把软件原型任务拆成多个可并行 Polecat bead。Triggers on wave split、frontend/backend split、parallel bead dispatch."
---

**用途**

把可并行的软件原型工作拆成多个 GT `Polecat` bead，并明确哪些 bead 可以同时执行、哪些必须串行。
这里的“parallel agents”只表示 GT 中的多个 `Polecat` 会话，不表示 Codex / Claude 子代理。
在默认口径下，若同一 Wave 内存在 3 个及以上无阻塞 beads，应默认至少同时拉起 3 个 `Polecat`，优先体现 JAS 的批量并行能力。

## 依赖

- `software-prototyper-s2-module-plan`
- `software-prototyper-gt-cli`
- `software-prototyper-gt-mail-comm`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `module_map` | yaml | 是 | S2 产出的模块依赖图 |
| `wave_plan` | markdown | 是 | 当前 Wave 计划 |

## 输出契约

- `output/{project_id}/plans/parallel-dispatch.md`
- GT bead 拆分建议与派发顺序

## 执行流程

1. 先识别哪些工作必须串行，哪些工作可以并行。
2. 按以下优先维度拆 bead：
   - 前端页面 / UI 流
   - 后端 API / 服务层
   - 测试模块
   - 共享基础设施
   - 数据 / schema / seed
   - 业务模块
   - 集成修复
   - browser-validation bead
3. 为每个 bead 写清：
   - 范围边界
   - 输入与输出
   - 依赖 bead
   - 对应 `Refinery` 验收点
   - 失败后的回退路径
4. 若两个 bead 会修改同一关键区域，则保持串行，不要强行并行。
5. 输出 GT 派发顺序，交由 `Mayor` 使用 `gt sling` 执行。
6. 若同一 Wave 内存在 3 个及以上无阻塞 beads，默认至少同时拉起 3 个 `Polecat`，并把其余 ready beads 继续按一 bead 一 Polecat 扩展到当前可调度上限。

## 验证清单

- [ ] 并行语义只指向 GT `Polecat`
- [ ] 前端 / 后端 / 共享层 / 业务模块拆分明确
- [ ] 每个 bead 都有 reviewer 验收点
- [ ] 存在共享状态冲突的 bead 未被错误并行化
