# AGENTS.md

This file provides guidance to Codex when working with the `construction-review` workspace.

## Project Overview

This workspace hosts the Gas Town runtime, docs, examples, and training data for the construction audit expert agent. The formal runtime workflow always starts from two user-provided files:

- `rule_document.docx`
- `spreadsheet.xlsx` / `spreadsheet.xls`

`examples/` and `train/` are only for local regression and debugging.

## Source of Truth

The construction-audit OpenCode source no longer lives in a project-local `.opencode/` directory.

- Agent source: `joinai-expert-agent/construction-aduit/agents/*.md`
- Skill source: `joinai-expert-agent/construction-aduit/skills/*`
- User-level runtime registration:
  - `~/.config/opencode/agents/`
  - `~/.config/opencode/skills/`

Only these three custom agents are part of the construction-audit mainline:

| GT Role | Agent Config Name | OpenCode `--agent` | Source File |
|---------|-------------------|--------------------|-------------|
| Mayor | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | `joinai-expert-agent/construction-aduit/agents/construction-audit-orchestrator.md` |
| Polecat | `opencode-construction-audit-worker` | `construction-audit-worker` | `joinai-expert-agent/construction-aduit/agents/construction-audit-worker.md` |
| Refinery | `opencode-construction-audit-reviewer` | `construction-audit-reviewer` | `joinai-expert-agent/construction-aduit/agents/construction-audit-reviewer.md` |

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

`gt/` is its own Gas Town repository with runtime state, beads, and configuration.

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

## Runtime Notes

- Run git commands for GT only inside `construction-review/gt/`.
- `gt prime` is the runtime identity source; do not infer agent identity from bead text alone.
- `gt mail check --inject` is the standard mailbox sync hook.
- Gas Town default witness patrol, if enabled, remains managed by GT defaults and should still use `bd mol wisp`, never `bd mol pour`.

## Common Commands

```bash
# GT runtime
cd gt
gt prime
gt mail check --inject
gt config agent list
gt config default-agent

# Validate JSON configs
python3 -m json.tool gt/settings/config.json
python3 -m json.tool gt/data-audit/settings/config.json

# Inspect user-level registration
ls -l ~/.config/opencode/agents/construction-audit-*.md
ls -l ~/.config/opencode/skills/construction-audit-* ~/.config/opencode/skills/gt-*
```

## Constraints

- Do not reintroduce a project-local hidden source tree as the construction-audit source of truth.
- Do not add the retired custom monitor role back into GT role mappings or user-level registration.
- Keep active docs and GT config aligned with the three-role model.
