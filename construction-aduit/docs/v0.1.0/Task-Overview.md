# Construction Review Task Overview

## 1. Current Goal

`construction-aduit/` is the repo-local module root for the construction audit expert agent. Its nested `gt/` directory is the Gas Town runtime workspace, and the active source of truth is:

- Agents: `construction-aduit/.opencode/agents/*.md`
- Skills: `construction-aduit/.opencode/skills/*`

Runtime discovery is provided by the module-local `.opencode/` tree:

- `.opencode/agents/`
- `.opencode/skills/`

## 2. Three-Role Runtime Model

The construction-audit mainline is now a three-role system:

| Role | GT Mapping | OpenCode Agent | Responsibility |
|------|------------|----------------|----------------|
| Mayor | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | 会话编排、阶段门禁、rig 内调度 |
| Polecat | `opencode-construction-audit-worker` | `construction-audit-worker` | 执行 S0-S4 具体技能和脚本 |
| Refinery | `opencode-construction-audit-reviewer` | `construction-audit-reviewer` | 阶段审查、QA 评分、最终复核 |

Gas Town default witness patrol may still be enabled at the platform level, but it is not a construction-audit custom role and is not registered through the construction-audit GT config.

## 2.1 Rig URL Rules

- Mayor must create or confirm a new rig before entering S0-S4 for a new project or new review session.
- The project source directory must be `output/<project-name>` next to `gt/`, not another sibling and not a child inside `gt/`.
- Local project sources must register rig URLs as `file:///abs/path`.
- Remote project sources must register rig URLs as remote git URLs.
- S3 parallel execution always means GT-managed `Polecat` sessions, one sheet per `Polecat`.

## 3. Active Skill Chain

The active skill set is:

| Stage | Skill | Formal Output |
|------|-------|---------------|
| S0 | `construction-audit-s0-session-init` | `audit-config.yaml` |
| S1 | `construction-audit-s1-rule-doc-render` | `rule_doc.md` |
| S2 | `construction-audit-s2-workbook-render` | `workbook.md` + `sheets/*.json` |
| S3 | `construction-audit-s3-sheet-audit` | `findings/findings_<sheet>.json` |
| S4 | `construction-audit-s4-error-report` | `audit-report.md` + `audit-report.docx` |
| QA | `construction-audit-qa-checklist` | `qa-report.json` |
| Shared | `gt-mail-comm` | GT 邮件通信 |
| Shared | `gt-status-report` | GT 状态上报 |

## 4. GT Integration

### 4.1 Active Config Files

- Town config: `gt/settings/config.json`
- Mayor overlay: `gt/mayor/settings/config.json`
- Main rig config: `gt/data-audit/settings/config.json`
- Focused rig config: `gt/budget_table4_1to8_review/settings/config.json`
- Nested runtime rig snapshot: `gt/budget_table4_1to8_review/polecats/rust/budget_table4_1to8_review/settings/config.json`

All active construction-audit role maps should contain only:

```json
{
  "role_agents": {
    "mayor": "opencode-construction-audit-orchestrator",
    "polecat": "opencode-construction-audit-worker",
    "refinery": "opencode-construction-audit-reviewer"
  }
}
```

### 4.2 Active Beads

- `gt/data-audit/beads/wave-1-rule-extraction.md`
- `gt/data-audit/beads/wave-2-sheet-audit.md`
- `gt/data-audit/beads/wave-3-report-generation.md`
- `gt/budget_table4_1to8_review/beads/wave-table4-focused-review.md`

These beads should reference only the active S0-S4 skill names and the three custom roles above.

## 5. Project-Local Registration

The construction-audit runtime should expose only these project-local entries:

### Agents

- `construction-audit-orchestrator.md`
- `construction-audit-worker.md`
- `construction-audit-reviewer.md`

### Skills

- `construction-audit-s0-session-init`
- `construction-audit-s1-rule-doc-render`
- `construction-audit-s2-workbook-render`
- `construction-audit-s3-sheet-audit`
- `construction-audit-s4-error-report`
- `construction-audit-qa-checklist`
- `gt-mail-comm`
- `gt-status-report`

Broken links pointing to retired top-level `agents/` / `skills/` directories are obsolete and should be replaced with `.opencode/...` paths.

## 6. Verification Checklist

### Static checks

- No active document or bead should mention retired custom roles or retired skill names.
- No active document should point construction-audit source files back to retired top-level `agents/` / `skills/` directories.

### Runtime checks

```bash
python3 -m json.tool gt/settings/config.json
python3 -m json.tool gt/data-audit/settings/config.json
python3 -m json.tool gt/budget_table4_1to8_review/settings/config.json

gt config agent list
gt config default-agent

ls -l .opencode/agents/construction-audit-*.md
ls -l .opencode/skills/construction-audit-* .opencode/skills/gt-*
```

### Expected state

- Exactly 3 construction-audit custom agents are registered in GT.
- Exactly 3 construction-audit agent files exist in `.opencode/agents/`.
- Exactly 8 construction-audit / GT skill directories exist in `.opencode/skills/`.
- Active docs, GT configs, project-local paths, and GT custom agent registry all point to the same three-role model.
