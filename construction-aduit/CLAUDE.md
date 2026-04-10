# CLAUDE.md

This file provides guidance to Claude Code when working with the `construction-aduit/` module in this repository.

## Project Overview

This module contains the construction-audit expert-agent source, a local GT runtime snapshot, and ignored local workspace artifacts.

The formal runtime workflow always begins with:

- `rule_document.docx`
- `spreadsheet.xlsx` / `spreadsheet.xls`

For repo-local work, treat `construction-aduit/` as the workspace root. Historical references to an external runtime workspace are not paths to use when editing this repository.

## Source of Truth

Repo-local source of truth:

- Agents: `.opencode/agents/*.md`
- Skills: `.opencode/skills/*`
- GT runtime snapshot: `gt/`

Ignored local workspace content:

- `docs/`
- `examples/`
- `output/`

The construction-audit mainline registers exactly three custom agents:

| GT Role | Agent Config Name | OpenCode `--agent` | Source File |
|---------|-------------------|--------------------|-------------|
| Mayor | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | `.opencode/agents/construction-audit-orchestrator.md` |
| Polecat | `opencode-construction-audit-worker` | `construction-audit-worker` | `.opencode/agents/construction-audit-worker.md` |
| Refinery | `opencode-construction-audit-reviewer` | `construction-audit-reviewer` | `.opencode/agents/construction-audit-reviewer.md` |

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

`gt/` is a nested runtime repository.

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

- Run GT git commands from `construction-aduit/gt/`.
- `gt prime` is the authoritative identity hook.
- `gt mail check --inject` is the standard mailbox sync step.
- `construction-aduit/gt` is a nested Git root, so discovery depends on `construction-aduit/gt/.opencode -> ../.opencode`.
- Gas Town default witness patrol, if enabled, should still use `bd mol wisp` rather than `bd mol pour`.
- Treat `docs/`, `examples/`, and `output/` as ignored local workspace content, not as live configuration sources.

## Common Commands

```bash
cd construction-aduit/gt
gt prime
gt mail check --inject
gt config agent list
gt config default-agent

python3 -m json.tool construction-aduit/gt/settings/config.json
python3 -m json.tool construction-aduit/gt/data-audit/settings/config.json

ls -l construction-aduit/.opencode/agents/construction-audit-*.md
ls -l construction-aduit/.opencode/skills/construction-audit-* construction-aduit/.opencode/skills/gt-*
ls -ld construction-aduit/gt/.opencode
```

## Constraints

- Do not reintroduce user-home OpenCode registration as the primary construction-audit runtime contract.
- Do not re-register the retired custom monitor role as a construction-audit custom role.
- Keep active docs, GT configs, and project-level registration in sync with the three-role model.
- Prefer module-relative repo paths such as `.opencode/...` and `gt/...` in local guidance.
