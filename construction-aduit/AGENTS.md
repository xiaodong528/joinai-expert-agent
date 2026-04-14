# AGENTS.md

This file provides guidance to Codex when working with the `construction-aduit/` module in this repository.

## Module Overview

This module stores the construction-audit expert-agent source, a local Gas Town runtime snapshot, and ignored local workspace artifacts.

The formal runtime workflow always starts from two user-provided files:

- `rule_document.docx`
- `spreadsheet.xlsx` / `spreadsheet.xls`

Within this repository, treat `construction-aduit/` as the local module root. Historical docs may still mention an external runtime workspace; do not use those paths for repo-local editing.

## Source of Truth

Repo-local source of truth:

- Agent source: `.opencode/agents/*.md`
- Skill source: `.opencode/skills/*`
- GT runtime snapshot and config: `gt/`

Local ignored workspace content:

- `docs/`
- `examples/`
- `output/`

Only these three custom agents are part of the active construction-audit mainline:

| GT Role | Agent Config Name | OpenCode `--agent` | Source File |
|---------|-------------------|--------------------|-------------|
| Mayor | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | `.opencode/agents/construction-audit-orchestrator.md` |
| Polecat | `opencode-construction-audit-worker` | `construction-audit-worker` | `.opencode/agents/construction-audit-worker.md` |
| Refinery | `opencode-construction-audit-reviewer` | `construction-audit-reviewer` | `.opencode/agents/construction-audit-reviewer.md` |

Gas Town default witness patrol may still exist at the platform level, but it is not a construction-audit custom agent and is not registered through the construction-audit role map.

## Active Skill Chain

The current construction-audit mainline uses these eight skills:

- `construction-audit-s0-session-init`
- `construction-audit-s1-rule-doc-render`
- `construction-audit-s2-workbook-render`
- `construction-audit-s3-sheet-audit`
- `construction-audit-s4-error-report`
- `construction-audit-qa-checklist`
- `gt-mail-comm`
- `gt-status-report`

## Gas Town Workspace

`gt/` is a nested Gas Town runtime repository. When operating on GT state, use paths under `construction-aduit/gt/`.

Important paths:

- Town config: `gt/settings/config.json`
- Mayor override config: `gt/mayor/settings/config.json`
- Main rig config: `gt/data-audit/settings/config.json`
- Focused rig config: `gt/budget_table4_1to8_review/settings/config.json`
- Active beads:
  - `gt/data-audit/beads/wave-1-rule-extraction.md`
  - `gt/data-audit/beads/wave-2-sheet-audit.md`
  - `gt/data-audit/beads/wave-3-report-generation.md`
  - `gt/budget_table4_1to8_review/beads/wave-table4-focused-review.md`

Current construction-audit GT mapping is three-role only:

- `mayor -> opencode-construction-audit-orchestrator`
- `polecat -> opencode-construction-audit-worker`
- `refinery -> opencode-construction-audit-reviewer`

This round intentionally does **not** modify `gt/roles/*.toml`. Keep that assumption unless the user asks otherwise.

Rig preparation follows one active rule:

- On every new project or new review session, Mayor creates or confirms the rig first.
- The project source directory must be `output/<project-name>` next to `gt/`, not another sibling and not a child inside `gt/`.
- Local projects must register rig URLs as `file:///abs/path`.
- Remote projects must register rig URLs as remote git URLs.
- Parallel execution always means GT-managed `Polecat` sessions; for S3, one sheet maps to one `Polecat`.

## Runtime Notes

- Run GT git commands only inside `construction-aduit/gt/`.
- `gt prime` is the runtime identity source; do not infer agent identity from bead text alone.
- `gt mail check --inject` is the standard mailbox sync hook.
- Gas Town default witness patrol, if enabled, remains managed by GT defaults and should still use `bd mol wisp`, never `bd mol pour`.
- Do not treat `docs/`, `examples/`, or `output/` as source-of-truth configuration. They are local archived inputs, notes, and evidence.

## Common Commands

```bash
# GT runtime
cd construction-aduit/gt
gt prime
gt mail check --inject
gt config agent list
gt config default-agent

# Validate JSON configs
python3 -m json.tool construction-aduit/gt/settings/config.json
python3 -m json.tool construction-aduit/gt/data-audit/settings/config.json

# Inspect project-local registration
ls -l construction-aduit/.opencode/agents/construction-audit-*.md
find construction-aduit/.opencode/skills -maxdepth 1 -mindepth 1 -type d | sort
```

## Constraints

- Keep project-local `.opencode/agents` and `.opencode/skills` as the construction-audit source of truth.
- Do not add the retired custom monitor role back into GT role mappings or `.opencode/agents/`.
- Keep active docs and GT config aligned with the three-role model.
- When writing repo-local guidance, prefer module-relative paths such as `.opencode/agents/...`, `.opencode/skills/...`, and `gt/...`.
