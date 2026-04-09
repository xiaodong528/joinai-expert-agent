# AGENTS.md

This file provides guidance when working with the `software-prototyper` workspace.

## Workspace Layout

This workspace uses a dual-directory layout:

- `software-prototyper/`
  Holds GT runtime assets, runtime docs, `Prototype-output/{project_id}`, and acceptance evidence.
- `joinai-expert-agent/software-prototyper/`
  Holds the source-of-truth Agent and Skill Markdown files.

## Dual Entry Workflow

`software-prototyper-orchestrator` supports two entry modes:

- 从零开始，多轮 brainstorm，逐步收敛成类似 `PLAN.md` 的规格与验收标准
- 直接读取现成方案文档，跳过 brainstorm，进入开发执行

Mayor owns the internal goal loop. There is no fourth role and no outer master agent.
The master control plane is `Mayor + Refinery`.

## JAS Role Mapping

- `software-prototyper-orchestrator` → Mayor
- `software-prototyper-worker` → Polecat
- `software-prototyper-reviewer` → Refinery

Mayor + Refinery act as the master control plane.
Polecat sessions are the parallel subagent execution plane.

GT configuration under `software-prototyper/gt/` maps the three GT roles to those three agents.

## Source Of Truth

- Agent source: `joinai-expert-agent/software-prototyper/agents/*.md`
- Skill source: `joinai-expert-agent/software-prototyper/skills/*`
- The project now includes a vendored local skill pack for execution workflows and GT operations.

## Output Root

All delivery evidence is collected under:

```text
Prototype-output/{project_id}/
```

Recommended structure:

- `specs/`
- `plans/`
- `workspace/`
- `docs/`
- `evidence/`

## GT Notes

- Town config: `software-prototyper/gt/settings/config.json`
- Rig config: `software-prototyper/gt/software-prototyper/settings/config.json`
- Role TOML override: `software-prototyper/gt/roles/{mayor,polecat,refinery}.toml`
- Wave beads:
  - `software-prototyper/gt/software-prototyper/beads/wave-1-foundation-bootstrap.md`
  - `software-prototyper/gt/software-prototyper/beads/wave-2-module-build.md`
  - `software-prototyper/gt/software-prototyper/beads/wave-3-integration-qa.md`

## Parallel Dispatch Meaning

In this project, “parallel agents” means GT-managed parallel polecat / OpenCode sessions.
It does not mean Codex subagent dispatch.
