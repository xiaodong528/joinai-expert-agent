# Construction Audit Agent Design v0.1.0

## 1. Design Goal

The construction audit agent reviews telecom construction budget and settlement spreadsheets against a user-provided rule document. The current formal runtime contract is:

- Input 1: `rule_document.docx`
- Input 2: `spreadsheet.xlsx` / `spreadsheet.xls`

The repo-local runtime workspace is `construction-aduit/gt/`, and the OpenCode source of truth lives in this module:

- Agents: `construction-aduit/.opencode/agents/*.md`
- Skills: `construction-aduit/.opencode/skills/*`

## 2. Runtime Roles

### 2.1 Construction-Audit Custom Roles

| Role | Agent | Responsibility |
|------|-------|----------------|
| Mayor | `construction-audit-orchestrator` | 会话编排、阶段调度、GT bead 派发、门禁决策 |
| Polecat | `construction-audit-worker` | 执行技能、运行脚本、生成中间产物与最终报告 |
| Refinery | `construction-audit-reviewer` | 审查阶段产物、输出 QA 结论 |

### 2.2 Gas Town Default Witness

Gas Town default witness patrol may still exist at the platform layer. It is not a construction-audit custom role, is not registered through the construction-audit role map, and is not treated as an OpenCode source file that the construction-audit project owns.

### 2.3 Rig URL Contract

- Mayor must create or confirm a new rig before entering S0-S4 for a new project or new review session.
- The project source directory must be `output/<project-name>` next to `gt/`, not another sibling and not a child inside `gt/`.
- Local project sources must register rig URLs as `file:///abs/path`.
- Remote project sources must register rig URLs as remote git URLs.
- Parallel execution always means GT-managed `Polecat` sessions, with one target sheet mapped to one `Polecat`.

## 3. Stage Design

| Stage | Skill | Input | Output |
|------|-------|-------|--------|
| S0 | `construction-audit-s0-session-init` | `rule_document.docx` + `spreadsheet.xls/.xlsx` | `audit-config.yaml` |
| S1 | `construction-audit-s1-rule-doc-render` | `audit-config.yaml` | `rule_doc.md` |
| S2 | `construction-audit-s2-workbook-render` | `audit-config.yaml` | `workbook.md` + `sheets/*.json` |
| S3 | `construction-audit-s3-sheet-audit` | `audit-config.yaml` + `rule_doc.md` + `workbook.md` + `sheets/<sheet>.json` | `findings/findings_<sheet>.json` |
| S4 | `construction-audit-s4-error-report` | `audit-config.yaml` + `findings/*.json` | `audit-report.md` + `audit-report.docx` |

## 4. Stage Contracts

### 4.1 S0 Session Init

Responsibilities:

- Validate the uploaded rule document and spreadsheet
- Detect real workbook format
- Derive visible/all sheet lists
- Produce `audit-config.yaml`

Formal output:

```yaml
audit_id: AUDIT-...
audit_type: budget | settlement
rule_document:
  path: /abs/path/to/rule_document.docx
  markdown_path: /abs/path/to/output/rule_doc.md
spreadsheet:
  path: /abs/path/to/working.xls
  source_format: xls | xlsx
  sheets: [...]
  all_sheets: [...]
  visible_sheets: [...]
  hidden_sheets: [...]
output_dir: /abs/path/to/output
```

### 4.2 S1 Rule Doc Render

Responsibilities:

- Render the uploaded rule document to `rule_doc.md`
- Preserve heading hierarchy and table ordering
- Avoid introducing retired `rules.json`/validate side outputs into the mainline

### 4.3 S2 Workbook Render

Responsibilities:

- Export structured `sheets/*.json`
- Produce `workbook.md`
- Preserve `row_context`, `col_context`, `formula`, `formula_annotation`, and rule annotations needed by S3

### 4.4 S3 Sheet Audit

Responsibilities:

- One worker handles one target sheet
- Read `rule_doc.md`, `workbook.md`, and the corresponding sheet JSON
- Use `calc_formula.py` only for deterministic numeric checking
- Write `findings/findings_<sheet>.json`

### 4.5 S4 Error Report

Responsibilities:

- Aggregate all findings
- Generate `audit-report.md`
- Generate `audit-report.docx`
- Avoid formal `audit-report.json`

## 5. GT Mapping

### 5.1 Active Config Targets

- `construction-aduit/gt/settings/config.json`
- `construction-aduit/gt/mayor/settings/config.json`
- `construction-aduit/gt/data-audit/settings/config.json`
- `construction-aduit/gt/budget_table4_1to8_review/settings/config.json`
- `construction-aduit/gt/budget_table4_1to8_review/polecats/rust/budget_table4_1to8_review/settings/config.json`

Each active construction-audit config should map only:

```json
{
  "role_agents": {
    "mayor": "opencode-construction-audit-orchestrator",
    "polecat": "opencode-construction-audit-worker",
    "refinery": "opencode-construction-audit-reviewer"
  }
}
```

### 5.2 Bead Flow

The active beads are:

- `wave-1-rule-extraction.md` for S0 + S1
- `wave-2-sheet-audit.md` for parallel S3 per-sheet work
- `wave-3-report-generation.md` for S4
- `wave-table4-focused-review.md` for the focused table-4 review scenario

These bead definitions must reference only the active S0-S4 skill names and the three custom roles.

## 6. Runtime Registration

User-level runtime registration must point to the sibling source repository:

### Agents

- `.opencode/agents/construction-audit-orchestrator.md`
- `.opencode/agents/construction-audit-worker.md`
- `.opencode/agents/construction-audit-reviewer.md`

### Skills

- `construction-audit-s0-session-init`
- `construction-audit-s1-rule-doc-render`
- `construction-audit-s2-workbook-render`
- `construction-audit-s3-sheet-audit`
- `construction-audit-s4-error-report`
- `construction-audit-qa-checklist`
- `gt-mail-comm`
- `gt-status-report`

Broken links to retired top-level `agents/` / `skills/` directories are obsolete and should not remain in the active runtime chain.

## 7. Non-Goals in This Round

- Do not rename `construction-aduit/` in this repository.
- Do not modify `gt/roles/*.toml`.
- Keep `.opencode/agents/` and `.opencode/skills/` as the project-local source of truth.
- Do not reintroduce the retired custom monitor role into GT custom role mappings.

## 8. Verification

### Static checks

- No active document should point source agents or skills back to retired top-level `agents/` / `skills/` directories.
- No active construction-audit config should include a custom witness-to-monitor mapping.
- No active bead should invoke retired skill names.

### Validation commands

```bash
python3 -m json.tool construction-aduit/gt/settings/config.json
python3 -m json.tool construction-aduit/gt/data-audit/settings/config.json
python3 -m json.tool construction-aduit/gt/budget_table4_1to8_review/settings/config.json

gt config agent list
ls -l .opencode/agents/construction-audit-*.md
ls -l .opencode/skills/construction-audit-* .opencode/skills/gt-*
```

### Expected result

- The runtime chain is fully aligned on the three-role model.
- Project-local registration points to `construction-aduit/.opencode/...`.
- Gas Town default witness remains a platform-level patrol concern only.
