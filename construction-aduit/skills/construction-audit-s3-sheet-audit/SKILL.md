---
name: construction-audit-s3-sheet-audit
description: "工程审核按表审计技能：每个智能体只审核一个 sheet，直接阅读 `audit-config.yaml`、`rule_doc.md`、`workbook.md` 与目标 `sheets/*.json`，自行识别费用名称和依据计算方法；运行时只调用 `calc_formula.py` 做单元格数值计算，并由智能体自行写出 `findings_sheet-name.json`。Triggers on sheet audit, single-sheet worker audit, findings generation。"
---

# Skill: construction-audit-s3-sheet-audit

**用途（Purpose）:** 按表审计（Sheet audit）。
每个智能体只审核一个目标 sheet。智能体直接阅读 `audit-config.yaml`、阶段2的 `rule_doc.md`、阶段3的 `workbook.md` 与目标 `sheets/<sheet>.json`，先按规则表行枚举费用名称，再按业务行锚点与金额角色列展开目标格，最后调用 `calc_formula.py` 做单元格数值计算，并自行写出 `findings/findings_<sheet>.json`。本技能不提供总控脚本，不单列输出 `rules.json`，不生成报告。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | 包含 `audit_id`、`audit_type`、`rule_document.markdown_path`、`spreadsheet.sheets`、`output_dir` 的配置文件 |
| `sheet_name` | string | 是 | 当前 worker 负责审核的目标 sheet 名称 |

从配置文件与阶段产物中解析的关键输入：

- `audit_id`
- `audit_type`
- `rule_document.markdown_path` -> `rule_doc.md`
- `{output_dir}/workbook.md`
- `{output_dir}/sheets/*.json`

---

## 输出契约（Output Contract）

正式产物固定为：

- `{output_dir}/findings/findings_<sheet_name>.json`

每个 findings 文件至少包含：

- `sheet_name`
- `audit_id`
- `total_cells_checked`
- `findings[]`
- `summary`

其中每条 finding 至少包含：

- `finding_id`
- `rule_id`
- `cell_ref`
- `expected_value`
- `actual_value`
- `severity`
- `description`
- `rule_source_anchor`
- `rule_source_excerpt`

本技能不提供统一总控 CLI 摘要；每个 worker 完成后应由智能体自行汇报：

- `audit_id`
- `sheet_name`
- `output_findings`
- `findings_count`

---

## 执行步骤（Execution Steps）

1. 读取并校验 `audit-config.yaml` 与当前 `sheet_name`
2. 阅读 `rule_doc.md`、`workbook.md` 中对应 sheet 的桥接信息，以及目标 `sheets/<sheet>.json`
3. 先从 `rule_doc.md` 中抽取当前 sheet 的规则表行，并按原文顺序枚举费用名称
4. 以费用名称列做行锚点，再按 `amount_role` 展开目标金额格；不得只抽查个别规则或只检查单列金额
5. 将规则行分为 `source_backed`、`not_applicable`、`derived_summary`
6. 对 `J/K` 一类支撑格只做校验支撑；正式 findings 仅从协议标记为 `report_as_finding=true` 的目标格产出
7. 仅对需要确定性数值复核的目标格调用 `calc_formula.py`
8. 智能体自行比较期望值与实际值，生成 `finding` 结构
9. 智能体自行写出单个 `findings_<sheet>.json`

---

## Python Helper

```bash
python joinai-expert-agent/construction-aduit/skills/construction-audit-s3-sheet-audit/scripts/calc_formula.py \
  --sheet-data /abs/path/sheets/表一_451定额折前_.json \
  --context-sheets-dir /abs/path/sheets \
  --payload-json '{"sheet_name":"表一（451定额折前）","target_cell":"J13","formula":"left + right","operands":[{"sheet":"表一（451定额折前）","cell_ref":"J12"},{"sheet":"表一（451定额折前）","cell_ref":"I13"}]}'
```

---

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml` 可读取
- [ ] `rule_doc.md` 已生成且非空
- [ ] `workbook.md` 已生成且非空
- [ ] `sheets/*.json` 覆盖 `spreadsheet.sheets`
- [ ] 智能体显式只处理一个 `sheet_name`
- [ ] 当前 `sheet_name` 对应的 `sheets/<sheet>.json` 存在
- [ ] 当前 `sheet_name` 的规则表行已被完整枚举
- [ ] 当前 `sheet_name` 的目标格按 `amount_role` 展开，而不是只审单个金额列
- [ ] `calc_formula.py` 能返回 `actual_value`、`expected_value`、`discrepancy`
- [ ] 智能体写出的 `findings_<sheet>.json` 中保留 `rule_source_anchor` 与 `rule_source_excerpt`
- [ ] `output_dir` 中不存在正式 `rules.json`

---

## 失败条件（Failure Conditions）

- 配置文件不存在或无法解析
- 缺少 `rule_document.markdown_path`
- 缺少 `workbook.md`
- 缺少当前目标 sheet 的 JSON
- 智能体无法从桥接产物中判断当前 sheet 的规则
- `calc_formula.py` 计算失败
- 当前 worker 无法生成 `findings_<sheet>.json`

---

## 非职责范围（Non-goals）

本 Skill 不负责以下事项：

- 不单列输出 `rules.json`
- 不单列 validate 阶段产物
- 不生成 `audit-report.docx`
- 不修改原始表格
- 不提供批量总控脚本

---

## 备注（Notes）

- 当前 `v0.1.0` 正式设计以 `docs/v0.1.0/construction-audit-agent-design.md` 为准。
- 本技能对应收敛后的 `v0.1.0` 阶段4（命名为 `construction-audit-s3-sheet-audit`）。
- 正式设计是“每个 sheet 一个智能体 worker”，并行派发由 GT / Mayor 负责，不在本技能内部实现。
- 除 `calc_formula.py` 外，规则阅读、定位、findings 组装和写盘都由智能体完成。
- 推荐结合 `scripts/sheet_audit_protocol.py` 与 `references/row-driven-audit-protocol.md` 使用，优先遵循“规则行驱动 + 行锚点 + 目标格展开”的确定性协议。
