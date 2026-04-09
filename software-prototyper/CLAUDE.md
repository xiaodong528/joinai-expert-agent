# CLAUDE.md

This file provides guidance when working with the `software-prototyper` workspace.

## Runtime Intent

`software-prototyper` is a three-role JAS expert agent for software prototype delivery.

- Mayor: intake, planning, goal loop, bead dispatch, escalation
- Polecat: module implementation, testing, debugging, delivery evidence
- Refinery: module review, integration QA, final acceptance

Master control plane: Mayor + Refinery
Parallel execution plane: multiple Polecat sessions

## Input Modes

The runtime supports two entry modes:

- 从零开始，多轮 brainstorm，逐步收敛成类似 `PLAN.md` 的规格与验收标准
- 直接读取现成方案文档，跳过 brainstorm，进入开发执行

## Goal Loop

The goal-driven workflow is embedded inside `software-prototyper-orchestrator`.

- Freeze goal, constraints, module map, and stop conditions
- Dispatch module beads to polecats
- Validate outputs using reviewer evidence
- Re-dispatch, split, downgrade, or escalate when criteria are not met
- Refinery participates in stop-condition adjudication and return decisions

## Source And Runtime Split

- Runtime workspace: `software-prototyper/gt`
- Agent and Skill source: `joinai-expert-agent/software-prototyper`
- Execution workflows and GT helper skills are vendored into the project skill tree.

## Output Contract

The single valid output root is:

```text
Prototype-output/{project_id}/
```

This root should contain specs, plans, workspace code, runbook docs, and QA evidence.
