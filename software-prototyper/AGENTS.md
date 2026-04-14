# AGENTS.md

This file provides guidance when working with the `software-prototyper/` module in this repository.

## Module Layout

This module keeps the software-prototyper source and runtime snapshot together under one repo-local root:

- `.opencode/agents/`
  Source-of-truth agent definitions.
- `.opencode/skills/`
  Stage skills and working-method skills.
- `gt/`
  Gas Town runtime config, rigs, beads, and role overrides.
- `docs/`
  Ignored local docs snapshot and planning notes.
- `output/`
  Formal runtime delivery root inside the repository (gitignored).

The formal runtime output root is:

```text
output/{project_id}/
```

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
Polecat sessions are the parallel execution plane.

GT configuration under `gt/` maps the three GT roles to those three agents.

Rig preparation follows one active rule:

- On every new project, Mayor creates or confirms the project source directory first.
- The project source directory must be `output/<project-name>` next to `gt/`, not another sibling and not a child inside `gt/`.
- Local projects must register rig URLs as `file:///abs/path`.
- Remote projects must register rig URLs as remote git URLs.
- Parallel execution always means GT-managed `Polecat` sessions, not Codex subagents.

## Source Of Truth

- Agent source: `.opencode/agents/*.md`
- Skill source: `.opencode/skills/*`
- GT runtime snapshot: `gt/`

The project includes vendored local skills for execution workflows and GT operations directly under `.opencode/skills/`.

## Output Contract

All formal delivery evidence is collected under:

```text
output/{project_id}/
```

Recommended runtime structure:

- `specs/`
- `plans/`
- `workspace/`
- `docs/`
- `evidence/`

This output root remains gitignored, but it is the formal location for runtime code, runbooks, and acceptance evidence in this module.

## GT Notes

- Town config: `gt/settings/config.json`
- Rig config: `gt/software-prototyper/settings/config.json`
- Role TOML override: `gt/roles/{mayor,polecat,refinery}.toml`
- Wave beads:
  - `gt/software-prototyper/beads/wave-1-foundation-bootstrap.md`
  - `gt/software-prototyper/beads/wave-2-module-build.md`
  - `gt/software-prototyper/beads/wave-3-integration-qa.md`

## Parallel Dispatch Meaning

In this project, “parallel agents” means GT-managed parallel polecat / OpenCode sessions.
It does not mean Codex subagent dispatch.
