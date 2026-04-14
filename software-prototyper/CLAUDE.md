# CLAUDE.md

This file provides guidance when working with the `software-prototyper/` module in this repository.

## Runtime Intent

`software-prototyper` is a three-role JAS expert agent for software prototype delivery.

- Mayor: intake, planning, goal loop, bead dispatch, escalation
- Polecat: module implementation, testing, debugging, delivery evidence
- Refinery: module review, integration QA, final acceptance

Master control plane: Mayor + Refinery
Parallel execution plane: multiple Polecat sessions

Rig preparation follows one active rule:

- On every new project, Mayor creates or confirms the project source directory first.
- The project source directory must be `output/<project-name>` next to `gt/`, not another sibling and not a child inside `gt/`.
- Local projects must register rig URLs as `file:///abs/path`.
- Remote projects must register rig URLs as remote git URLs.
- Parallel execution always means GT-managed `Polecat` sessions, not Codex subagents.

## Repo-Local Layout

Within this repository, use these paths directly:

- Agents: `.opencode/agents/*.md`
- Skills: `.opencode/skills/*`
- GT runtime snapshot: `gt/`
- Ignored local docs snapshot: `docs/`
- Formal runtime delivery root (gitignored): `output/`

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
- Formal runtime output root: `output/{project_id}/`

Use `output/{project_id}/` for generated specs, workspace code, runbooks, and QA evidence.

## Output Contract

The single valid runtime output root is:

```text
output/{project_id}/
```

This root should contain specs, plans, workspace code, runbook docs, and QA evidence.
