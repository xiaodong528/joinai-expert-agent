---
name: construction-audit-s4-error-report
description: "工程审核错误报告技能：读取 `findings/*.json` 与 `audit-config.yaml`，聚合审计结果并生成正式产物 `audit-report.md` 与 `audit-report.docx`。运行时允许使用临时中间数据，但不得在正式 `output_dir` 中留下 `audit-report.json` 或修正版表格。Triggers on error report, markdown/docx report generation, stage-5 reporting。"
---

# Skill: construction-audit-s4-error-report

**用途（Purpose）:** 错误报告生成（Error report generation）。
读取阶段4产出的 `findings/*.json` 与 `audit-config.yaml`，聚合审计结果并生成正式交付物 `audit-report.md` 与 `audit-report.docx`。本技能不输出 JSON 报告，不生成修正版表格。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | 包含 `audit_id`、`audit_type`、`project_info`、`output_dir` 的配置文件 |

从配置文件与阶段产物中解析的关键输入：

- `audit_id`
- `audit_type`
- `project_info.project_name`
- `{output_dir}/findings/*.json`

---

## 输出契约（Output Contract）

正式产物：

- `{output_dir}/audit-report.md`
- `{output_dir}/audit-report.docx`

成功时输出单行摘要，至少包含：

- `audit_id`
- `findings_files`
- `total_findings`
- `output_markdown`
- `output_docx`

---

## 执行步骤（Execution Steps）

1. 读取并校验 `audit-config.yaml`
2. 校验 `findings/` 目录存在且非空
3. 聚合所有 findings 统计信息
4. 生成 `audit-report.md`
5. 生成 `audit-report.docx`
6. 校验 Markdown 与 DOCX 非空
7. 输出摘要

---

## CLI 入口

```bash
python .opencode/skills/construction-audit-s4-error-report/scripts/run_error_report.py \
  --config /abs/path/audit-config.yaml
```

---

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml` 可读取
- [ ] `findings/` 目录存在且至少包含一个 `findings_*.json`
- [ ] `audit-report.md` 已生成且非空
- [ ] `audit-report.docx` 已生成且非空
- [ ] `output_dir` 中不存在正式 `audit-report.json`
- [ ] `output_dir` 中不存在 `corrected.<ext>`
- [ ] stdout 包含 `audit_id`、`findings_files`、`total_findings`、`output_markdown`、`output_docx`

---

## 失败条件（Failure Conditions）

- 配置文件不存在或无法解析
- 缺少 `findings/` 目录
- `findings/` 目录为空
- Markdown 生成失败
- DOCX 生成失败
- Markdown 或 DOCX 输出为空

---

## 非职责范围（Non-goals）

本 Skill 不负责以下事项：

- 不输出 `audit-report.json`
- 不生成修正版表格
- 不回写工作簿

---

## 备注（Notes）

- 当前 `v0.1.0` 正式设计以 `docs/v0.1.0/construction-audit-agent-design.md` 为准。
- 本技能对应收敛后的 `v0.1.0` 阶段5（命名为 `construction-audit-s4-error-report`）。
- 若运行时需要 JSON 结构给内部 builder 消费，只能作为瞬时临时数据，不能留在正式 `output_dir` 中。
- 当前正式实现为 Python-only 路径，不再依赖 `report_docx_builder.js`。
