# CLAUDE.md

This file provides guidance to Claude Code when working with the `construction-review` workspace.

## Project Overview

This workspace contains the Gas Town runtime, active docs, examples, and training data for the construction audit expert agent. The formal runtime workflow always begins with:

- `rule_document.docx`
- `spreadsheet.xlsx` / `spreadsheet.xls`

The binary files under `examples/` and `train/` are local samples only.

## Source of Truth

The construction-audit OpenCode assets are sourced from the sibling repository, not from a local `.opencode/` directory.

- Agent source: `joinai-expert-agent/construction-aduit/agents/*.md`
- Skill source: `joinai-expert-agent/construction-aduit/skills/*`
- Runtime registration happens via:
  - `~/.config/opencode/agents/`
  - `~/.config/opencode/skills/`

The construction-audit mainline registers exactly three custom agents:

| GT Role | Agent Config Name | OpenCode `--agent` | Source File |
|---------|-------------------|--------------------|-------------|
| Mayor | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | `joinai-expert-agent/construction-aduit/agents/construction-audit-orchestrator.md` |
| Polecat | `opencode-construction-audit-worker` | `construction-audit-worker` | `joinai-expert-agent/construction-aduit/agents/construction-audit-worker.md` |
| Refinery | `opencode-construction-audit-reviewer` | `construction-audit-reviewer` | `joinai-expert-agent/construction-aduit/agents/construction-audit-reviewer.md` |

Gas Town default witness patrol remains a platform concern and is not part of the construction-audit custom role map.

## Active Skill Chain

The current construction-audit mainline uses:

- `construction-audit-s0-session-init`
- `construction-audit-s1-rule-doc-render`
- `construction-audit-s2-workbook-render`
- `construction-audit-s3-sheet-audit`
- `construction-audit-s4-error-report`
- `construction-audit-qa-checklist`
- `gt-mail-comm`
- `gt-status-report`

## Gas Town Workspace

`gt/` is its own runtime repository.

Important files:

- Town config: `gt/settings/config.json`
- Mayor config: `gt/mayor/settings/config.json`
- Main rig: `gt/data-audit/settings/config.json`
- Focused rig: `gt/budget_table4_1to8_review/settings/config.json`
- Active beads:
  - `gt/data-audit/beads/wave-1-rule-extraction.md`
  - `gt/data-audit/beads/wave-2-sheet-audit.md`
  - `gt/data-audit/beads/wave-3-report-generation.md`
  - `gt/budget_table4_1to8_review/beads/wave-table4-focused-review.md`

The active construction-audit role map is:

- `mayor -> opencode-construction-audit-orchestrator`
- `polecat -> opencode-construction-audit-worker`
- `refinery -> opencode-construction-audit-reviewer`

This round intentionally leaves `gt/roles/*.toml` unchanged.

## Runtime Notes

- Run GT git commands from `construction-review/gt/`.
- `gt prime` is the authoritative identity hook.
- `gt mail check --inject` is the standard mailbox sync step.
- Gas Town default witness patrol, if enabled, should still use `bd mol wisp` rather than `bd mol pour`.

## Common Commands

```bash
cd gt
gt prime
gt mail check --inject
gt config agent list
gt config default-agent

python3 -m json.tool gt/settings/config.json
python3 -m json.tool gt/data-audit/settings/config.json

ls -l ~/.config/opencode/agents/construction-audit-*.md
ls -l ~/.config/opencode/skills/construction-audit-* ~/.config/opencode/skills/gt-*
```

## Constraints

- Do not treat a local hidden source directory as the construction-audit source of truth.
- Do not re-register the retired custom monitor role as a construction-audit custom role.
- Keep active docs, GT configs, and user-level registration in sync with the three-role model.
