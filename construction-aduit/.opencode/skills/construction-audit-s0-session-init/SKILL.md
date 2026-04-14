---
name: construction-audit-s0-session-init
description: "工程审核会话初始化技能：校验用户上传的 `rule_document.docx` 与 `spreadsheet.xls/.xlsx`，识别 Excel 真实格式，区分 `all_sheets/visible_sheets/hidden_sheets`，生成源格式保真的工作副本，并输出包含 `rule_document.markdown_path` 与 `spreadsheet` 元数据的 `audit-config.yaml`。Triggers on audit session init, audit bootstrap, config generation。"
---

# Skill: construction-audit-s0-session-init

**用途（Purpose）:** 会话初始化（Session initialization）。
统一校验用户上传的规则文档与待审表格，识别 Excel 真实格式，读取工作簿可见性信息，并生成后续阶段使用的 `audit-config.yaml`。

当前正式主链中，本技能由 Mayor 直接加载执行，不再要求经由 Polecat 派发。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `spreadsheet_path` | file path (`.xlsx` / `.xls`) | 是 | 待审工程预算或结算表格 |
| `rule_document_path` | file path (`.docx`) | 是 | 用户上传的审核规则文档 |
| `audit_type` | string | 是 | `budget` 或 `settlement` |
| `project_name` | string | 是 | 工程名称，由用户显式提供 |
| `sheet_scope` | string | 否 | 当前正式主链只支持 `visible`；默认 `visible`，用于声明 `spreadsheet.sheets` 只包含直接审查目标 |

---

## 输出契约（Output Contract）

唯一正式输出文件：`audit-config.yaml`

```yaml
audit_id: "AUDIT-20260401-120000"
audit_type: "budget"
audit_date: "2026-04-01"
project_info:
  project_name: "东海县海陵家苑三网小区新建工程"
rule_document:
  path: "/abs/path/to/rule_document.docx"
  markdown_path: "/abs/path/to/output/rule_doc.md"
spreadsheet:
  original_path: "/abs/path/to/source.xls"
  working_path: "/abs/path/to/output/source.xls"
  path: "/abs/path/to/output/source.xls"
  source_format: "xls"
  sheet_scope: "visible"
  sheets: ["工程信息", "表一"]
  all_sheets: ["工程信息", "隐藏费率表", "表一"]
  visible_sheets: ["工程信息", "表一"]
  hidden_sheets: ["隐藏费率表"]
output_dir: "/abs/path/to/output"
```

字段要求：

- `spreadsheet.sheet_scope` 固定记录为 `visible`，表示当前主链只允许直接审查可见目标 sheet。
- `spreadsheet.sheets` 表示当前运行的直接审查目标 sheet 集合，必须等于 `visible_sheets`，不得包含 `hidden_sheets`。
- `rule_document.markdown_path` 只预声明阶段2约定路径，S0 本身不生成 `rule_doc.md`。
- `working_path` 与 `source_format` 的扩展名必须一致。

---

## 执行步骤（Execution Steps）

1. 校验 `rule_document.docx` 存在、扩展名正确、内容可读。
2. 基于文件签名识别 Excel 真实格式，而不是只信文件后缀。
3. 读取工作簿的 `all_sheets`、`visible_sheets`、`hidden_sheets`。
4. 仅允许使用 `sheet_scope=visible`；将 `spreadsheet.sheets` 固定写成 `visible_sheets`，hidden sheet 只能留在 `hidden_sheets` 中作为只读上下文。
5. 按真实格式复制工作副本：`.xlsx` 保持 `.xlsx`，`.xls` 保持 `.xls`。
6. 生成 `audit-config.yaml`，并预写 `rule_document.markdown_path = {output_dir}/rule_doc.md`。
7. 输出简要配置摘要，至少包含 `audit_id`、`source_format`、`target_sheets_count`。

---

## CLI 入口

```bash
python .opencode/skills/construction-audit-s0-session-init/scripts/session_init.py \
  --rule-document /abs/path/rule_document.docx \
  --spreadsheet /abs/path/spreadsheet.xls \
  --audit-type budget \
  --sheet-scope visible \
  --project-name "东海县海陵家苑三网小区新建工程" \
  --output-dir /abs/path/audit-output
```

---

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml` 已生成
- [ ] `audit_id` 格式为 `AUDIT-YYYYMMDD-HHMMSS`
- [ ] `audit_type` 为 `budget` 或 `settlement`
- [ ] `rule_document.path` 指向已存在的 `.docx`
- [ ] `rule_document.markdown_path` 固定指向 `{output_dir}/rule_doc.md`
- [ ] `spreadsheet.path == spreadsheet.working_path`
- [ ] `working_path` 后缀与 `source_format` 一致
- [ ] `spreadsheet.sheet_scope` 固定为 `visible`
- [ ] `spreadsheet.sheets` 非空
- [ ] `spreadsheet.sheets == visible_sheets`
- [ ] `spreadsheet.sheets` 不得包含 `hidden_sheets`
- [ ] `all_sheets = visible_sheets + hidden_sheets`

---

## 失败条件（Failure Conditions）

- 规则文档不存在或不是合法 `.docx`
- 表格文件不存在
- 表格不是可识别的 Excel 文件
- 工作簿未读取到任何 sheet
- 工作簿没有任何可直接审查的可见 sheet
- 工作副本扩展名与真实格式不一致
- `sheet_scope` 不是 `visible`
- `audit-config.yaml` 写入失败

---

## 非职责范围（Non-goals）

本 Skill 不负责以下事项：

- 不渲染 `rule_doc.md`
- 不导出 `workbook.md`
- 不导出 `sheets/*.json`
- 不生成 `rules.json`
- 不执行任何规则校验、sheet 审核或报告生成

---

## 备注（Notes）

- 当前 `v0.1.0` 正式设计以 `docs/v0.1.0/construction-audit-agent-design.md` 为准。
- 当前正式流程仅支持“用户上传规则文档 + 用户上传待审表格”。
- `skills-bak` 中的同名 Skill 仅作为历史参考，不应再被运行时入口或正式测试直接引用。
