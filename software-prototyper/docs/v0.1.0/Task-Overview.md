# software-prototyper 任务总览

## 1. 定位

`software-prototyper` 是一个三角色 JAS 专家智能体：

- `software-prototyper-orchestrator`：Mayor
- `software-prototyper-worker`：Polecat
- `software-prototyper-reviewer`：Refinery

Mayor 与 Refinery 共同组成 master 控制面（Mayor + Refinery）。
Polecat 是多个并行 subagent 执行单元。

## 2. 双目录分工

- `joinai-expert-agent/software-prototyper/`
  - Agent 源文件
  - Skill 源文件（含项目内置的本地化工作法技能包）
- `software-prototyper/gt/`
  - Town / Rig 配置
  - Role TOML override
  - Wave beads
  - 运行文档与交付证据

## 3. 双入口

支持两种任务入口：

1. 从零开始，多轮 brainstorm，逐步收敛成类似 `PLAN.md` 的规格与验收标准
2. 直接读取现成方案文档，跳过 brainstorm，进入开发执行

## 4. 6 段主流程

1. `S0` 入口判定
2. `S1` 规格冻结
3. `S2` 模块拆解与 bead 生成
4. `Wave 1` 项目底座
5. `Wave 2` 模块并行开发
6. `Wave 3` 集成与收尾

## 5. 默认技术栈策略

- 用户指定技术栈时，以用户指定为准
- 未指定时，默认使用 `Next.js + Node + SQLite`

## 6. 并行策略

Mayor 按业务模块派发并行 polecat / OpenCode 进程。
这里的并行语义来自 GT，不是 Codex 子代理派发。
Refinery 逐模块裁定，Mayor 负责重派或停止。

## 7. 交付证据

统一输出根目录：

```text
Prototype-output/{project_id}/
```

至少包含：

- `specs/`
- `plans/`
- `workspace/`
- `docs/`
- `evidence/`

## 8. 完成标准

- 原型可启动
- 核心用户流 smoke / E2E 通过
- 模块级测试通过
- `Refinery` 模块级与最终验收通过
- Mayor 与 Refinery 基于证据共同决定停止，而不是接受口头完成声明
