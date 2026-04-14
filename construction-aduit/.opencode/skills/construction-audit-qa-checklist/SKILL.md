---
name: construction-audit-qa-checklist
description: "工程建设审核质量检查清单：供 Reviewer/Refinery 对当前 `v0.1.0` 主链的 S0-S4 产物执行结构化审查，覆盖 `audit-config.yaml`、`rule_doc.md`、`workbook.md`、`sheets/*.json`、`findings/*.json`、`audit-report.md` 与 `audit-report.docx`，并结合正确版/错误版工作簿做 oracle 比对，输出 `qa-report.json`。Triggers on QA checklist, quality review, oracle diff, refinery review, 审核审查、质量检查、qa-report generation。"
---

# Skill: construction-audit-qa-checklist

**用途（Purpose）:** Reviewer（Refinery）专属的审核质量检查清单。对当前 `v0.1.0` 正式主链的 S0-S4 产物执行结构化 QA 检查，必要时结合正确版/错误版工作簿做 oracle 比对，确保每个阶段的输出完整、可追溯、与当前输入一致，并将审查结论沉淀为 `qa-report.json`。

## 依赖

- 当前正式主链产物：`audit-config.yaml`、`rule_doc.md`、`workbook.md`、`sheets/*.json`、`findings/*.json`、`audit-report.md`、`audit-report.docx`
- Oracle 输入（按需）：正确版工作簿与待审工作簿，用于只读比对真实差异集合
- GT 共享技能：`gt-status-report`、`gt-mail-comm`
- Reviewer 自身需要基于当前输入做抽样复核，不依赖历史 `rules.json`、修正版工作簿或旧报告 JSON
- `audit-config.yaml` 中的 `spreadsheet.sheets` 是唯一直接审查目标集合，`spreadsheet.hidden_sheets` 只用于识别只读上下文

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | S0 输出的 `audit-config.yaml` |
| `rule_doc_path` | file path (`.md`) | 是 | S1 输出的 `rule_doc.md` |
| `workbook_markdown_path` | file path (`.md`) | 是 | S2 输出的 `workbook.md` |
| `sheets_dir` | directory path | 是 | S2 输出目录，包含 `sheets/*.json` |
| `findings_dir` | directory path | 是 | S3 输出目录，包含 `findings/*.json` |
| `report_markdown_path` | file path (`.md`) | 是 | S4 输出的 `audit-report.md` |
| `report_docx_path` | file path (`.docx`) | 是 | S4 输出的 `audit-report.docx` |
| `oracle_correct_spreadsheet_path` | file path (`.xls` / `.xlsx`) | 否 | 正确版工作簿；若提供，Reviewer 可做 oracle 比对 |
| `oracle_wrong_spreadsheet_path` | file path (`.xls` / `.xlsx`) | 否 | 待审工作簿；若提供，Reviewer 可做 oracle 比对 |
| `review_stage` | enum | 是 | `s0` / `s1` / `s2` / `s3` / `s4`，表示当前审查阶段 |

从输入中读取并交叉校验的关键字段：

- `audit_id`
- `audit_type`
- `project_info.project_name`
- `rule_document.path`
- `rule_document.markdown_path`
- `spreadsheet.path`
- `spreadsheet.sheets`
- `spreadsheet.hidden_sheets`

## 输出契约（Output Contract）

正式审查产物固定为：

- `{output_dir}/qa-report.json`

输出 JSON 至少包含：

```json
{
  "reviewer": "construction-audit-reviewer",
  "reviewed_at": "2026-04-01T12:00:00+08:00",
  "audit_id": "AUDIT-20260401-120000",
  "review_stage": "s3",
  "stage_scores": {
    "s0_session_init": {"score": 95, "issues": []},
    "s1_rule_doc_render": {"score": 92, "issues": []},
    "s2_workbook_render": {"score": 90, "issues": []},
    "s3_sheet_audit": {"score": 88, "issues": []},
    "s4_error_report": {"score": 91, "issues": []}
  },
  "overall_score": 91,
  "verdict": "pass",
  "blocking_issues": []
}
```

`verdict` 取值：

- `pass`：`overall_score >= 80`
- `conditional_pass`：`60 <= overall_score < 80`
- `fail`：`overall_score < 60`

## 执行流程

1. 读取并校验 `audit-config.yaml`，确认 `audit_id`、`audit_type`、`rule_document.path`、`rule_document.markdown_path`、`spreadsheet.path`、`spreadsheet.sheets`、`spreadsheet.hidden_sheets` 完整。
2. 按 `review_stage` 审查当前阶段必备产物是否存在、非空、命名正确，并核对与 `audit-config.yaml` 的路径约定一致。
3. 对 S1 审查 `rule_doc.md` 的标题层级、表格顺序和原文保真度。
4. 对 S2 审查 `workbook.md` 与 `sheets/*.json` 的覆盖度、上下文字段和桥接质量；确认 `workbook.md` 不展开公式或规则标注文本。
5. 对 S3 审查 `findings/*.json` 的结构完整性、抽样关键命中、跨表引用解释和 `rule_source_anchor` / `rule_source_excerpt` 可追溯性；S3 gate 的目标集合必须严格等于 `spreadsheet.sheets`。
6. hidden sheet 仅允许作为 operand/context 出现在最终 findings 解释中；不得因 hidden sheet 没有 findings 而判失败。
7. 若提供 `oracle_correct_spreadsheet_path` 与 `oracle_wrong_spreadsheet_path`，使用只读 helper 对比真实差异集合，并核对 findings 是否存在漏报/误报。
8. 对 S4 审查 `audit-report.md` 与 `audit-report.docx` 的章节完整性、统计与 `findings/*.json` 一致性，以及工程信息回填是否正确。
9. 汇总评分、阻塞问题和建议，写出 `qa-report.json`，并通过 `gt-mail-comm` 向 Orchestrator 返回结论。

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml`、`rule_doc.md`、`workbook.md`、`sheets/*.json`、`findings/*.json`、`audit-report.md`、`audit-report.docx` 与当前 `review_stage` 的要求一致
- [ ] `qa-report.json` 已生成且包含 `audit_id`、`review_stage`、`stage_scores`、`overall_score`、`verdict`
- [ ] S0 审查覆盖 `rule_document.path`、`spreadsheet.path`、`audit_type`、`spreadsheet.sheets`
- [ ] S1 审查覆盖标题层级、表格顺序、原文片段完整性
- [ ] S2 审查覆盖 `workbook.md`、`sheets/*.json`、`row_context`、`col_context`
- [ ] S3 审查覆盖 `findings/*.json` 结构、关键抽样命中、`rule_source_anchor`、`rule_source_excerpt`
- [ ] S3 gate 校验对象是 `spreadsheet.sheets`，并且每个可见目标 sheet 恰好存在 1 个最终 findings 文件
- [ ] hidden sheet 仅允许作为 operand/context 出现，且不得因 hidden sheet 没有 findings 而判失败
- [ ] 若提供 oracle 工作簿，QA 覆盖真实差异集合与 findings 的漏报/误报检查
- [ ] S4 审查覆盖 `audit-report.md` 与 `audit-report.docx` 的章节完整性和统计一致性
- [ ] 审查结论只基于当前正式主链产物与明确提供的 oracle 工作簿，不依赖历史 `rules.json`、`audit-report.json` 或 `corrected.xlsx/.xls`

## 非职责范围（Non-goals）

- 不生成或要求运行时依赖历史 `rules.json`
- 不生成或要求正式 `audit-report.json`
- 不生成或要求修正版工作簿 `corrected.xlsx` / `corrected.xls`
- 不替代 Worker 的单表审计职责，也不替代 S4 的报告生成职责
