# CLAUDE.md

This file provides guidance when working with the `software-prototyper/` module in this repository.

## Runtime Intent

`software-prototyper` is a three-role JAS expert agent for software prototype delivery.

- Mayor: intake, planning, goal loop, bead dispatch, escalation
- Polecat: module implementation, testing, debugging, delivery evidence
- Refinery: module review, integration QA, final acceptance

Master control plane: Mayor + Refinery
Parallel execution plane: multiple Polecat sessions

## Repo-Local Layout

Within this repository, use these paths directly:

- Agents: `.opencode/agents/*.md`
- Skills: `.opencode/skills/*`
- GT runtime snapshot: `gt/`
- Ignored local docs snapshot: `docs/`
- Ignored local archive directory: `output/`

The ignored repo-local `output/` directory is not the formal runtime contract.

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

- Repo-local source: `.opencode/agents/` and `.opencode/skills/`
- Runtime snapshot: `gt/`
- Formal runtime output root: `Prototype-output/{project_id}/`

Keep using `Prototype-output/{project_id}/` for generated specs, workspace code, runbooks, and QA evidence. Do not replace it with `software-prototyper/output/`, which is only an ignored local archive directory in this repo.

## Output Contract

The single valid runtime output root is:

```text
Prototype-output/{project_id}/
```

This root should contain specs, plans, workspace code, runbook docs, and QA evidence.
