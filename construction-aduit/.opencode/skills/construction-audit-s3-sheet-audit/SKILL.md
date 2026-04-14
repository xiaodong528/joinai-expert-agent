---
name: construction-audit-s3-sheet-audit
description: "工程审核按表审计技能：供 Mayor 在 S3 以双层并行方式调用。每个可见目标 sheet 固定拆成 3 个 `mode=shard_audit` 分片 Polecat，再由 1 个 `mode=merge_sheet_findings` Polecat 合并成最终 `findings_<sheet>.json`；hidden sheet 只保留为跨表计算上下文。Triggers on sheet audit, shard audit, findings merge, visible-sheet review。"
---

# Skill: construction-audit-s3-sheet-audit

**用途（Purpose）:** 按表审计（Sheet audit）。
本技能是当前正式主链中唯一保留给 Polecat 派发执行的阶段技能，供 Mayor 在 S3 双层并行链路中复用，不新增阶段 skill。运行模式固定为两类：

- `mode=shard_audit`：每个 Polecat 只审核当前可见目标 sheet 的一个固定分片
- `mode=merge_sheet_findings`：每个 Polecat 只负责把同一可见目标 sheet 的 3 份分片 findings 合并成最终 `findings_<sheet>.json`

直接审查目标只能来自 `audit-config.yaml.spreadsheet.sheets`。`hidden_sheets` 只能保留在 `sheets/*.json` 中供 `calc_formula.py --context-sheets-dir` 做跨表取数，不得把 hidden sheet 当作 `sheet_name` 直接审，也不得为 hidden sheet 生成独立 findings。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | 包含 `audit_id`、`audit_type`、`rule_document.markdown_path`、`spreadsheet.sheets`、`spreadsheet.hidden_sheets`、`output_dir` 的配置文件 |
| `mode` | string | 是 | `shard_audit` 或 `merge_sheet_findings` |
| `sheet_name` | string | 是 | 当前 worker 负责处理的可见目标 sheet 名称 |
| `batch_index` | integer | `mode=shard_audit` 时必填 | 当前分片序号，固定取值 `1..3` |
| `batch_count=3` | integer | `mode=shard_audit` / `mode=merge_sheet_findings` 时必填 | 固定 fanout，必须为 3 |
| `assigned_rule_rows` | list / description | `mode=shard_audit` 时必填 | 当前分片负责的规则行；必须按原始顺序平均切成 3 段 |
| `partial_output_path` | file path (`.json`) | `mode=shard_audit` 时必填 | 分片 findings 输出路径 |
| `partial_findings_paths` | list[file path] | `mode=merge_sheet_findings` 时必填 | 3 个分片 findings 路径 |
| `merged_output_path` | file path (`.json`) | `mode=merge_sheet_findings` 时必填 | 最终 findings 输出路径 |

从配置文件与阶段产物中解析的关键输入：

- `audit_id`
- `audit_type`
- `rule_document.markdown_path` -> `rule_doc.md`
- `{output_dir}/workbook.md`
- `{output_dir}/sheets/*.json`
- `spreadsheet.sheets`（唯一直接审查目标集合）
- `spreadsheet.hidden_sheets`（只读上下文集合）

---

## 输出契约（Output Contract）

正式产物分两类：

- `mode=shard_audit`：`{output_dir}/findings/parts/<sheet>/findings_<sheet>__part_{1..3}.json`
- `mode=merge_sheet_findings`：`{output_dir}/findings/findings_<sheet_name>.json`

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
- `mode`
- `sheet_name`
- `output_findings`
- `findings_count`

---

## 执行步骤（Execution Steps）

1. 读取并校验 `audit-config.yaml`、`mode` 与当前 `sheet_name`
2. 确认 `sheet_name` 来自 `spreadsheet.sheets`，不得把 hidden sheet 当作 `sheet_name` 直接审
3. `mode=shard_audit` 时：
   - 阅读 `rule_doc.md`、`workbook.md` 与 `sheets/<sheet>.json`
   - 从 `rule_doc.md` 中抽取当前 sheet 的规则表行
   - 按原始顺序将规则行平均切成固定 3 段，并且当前 worker 只处理 `assigned_rule_rows`
   - 以费用名称列做行锚点，再按 `amount_role` 展开目标金额格
   - 仅对当前分片需要确定性数值复核的目标格调用 `calc_formula.py`
   - 写出当前分片的 `partial_output_path`
4. `mode=merge_sheet_findings` 时：
   - 读取当前 `sheet_name` 的 3 份 `partial_findings_paths`
   - 校验 `batch_count=3`、`batch_index` 连续且无缺失
   - 合并为单个最终 `merged_output_path`
5. 无论哪种模式，都不得生成 `rules.json`、报告文件或 hidden sheet 的独立 findings

---

## Python Helper

```bash
python .opencode/skills/construction-audit-s3-sheet-audit/scripts/calc_formula.py \
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
- [ ] 智能体显式只处理一个来自 `spreadsheet.sheets` 的 `sheet_name`
- [ ] hidden sheet 只能作为上下文，不得把 hidden sheet 当作 `sheet_name` 直接审
- [ ] `mode=shard_audit` 与 `mode=merge_sheet_findings` 至少命中其一
- [ ] `mode=shard_audit` 时显式传入 `batch_index`、`batch_count=3`、`assigned_rule_rows`、`partial_output_path`
- [ ] `mode=merge_sheet_findings` 时显式传入 `batch_count=3`、`partial_findings_paths`、`merged_output_path`
- [ ] 当前 `sheet_name` 对应的 `sheets/<sheet>.json` 存在
- [ ] 当前 `sheet_name` 的规则表行能被稳定平均切成固定 3 段，且 3 个分片无重复、无遗漏
- [ ] 当前 `sheet_name` 的目标格按 `amount_role` 展开，而不是只审单个金额列
- [ ] `calc_formula.py` 能返回 `actual_value`、`expected_value`、`discrepancy`
- [ ] 分片产物路径固定为 `findings/parts/<sheet>/findings_<sheet>__part_{1..3}.json`
- [ ] 最终产物路径固定为 `findings/findings_<sheet>.json`
- [ ] 智能体写出的最终 `findings_<sheet>.json` 中保留 `rule_source_anchor` 与 `rule_source_excerpt`
- [ ] `output_dir` 中不存在正式 `rules.json`

---

## 失败条件（Failure Conditions）

- 配置文件不存在或无法解析
- 缺少 `rule_document.markdown_path`
- 缺少 `workbook.md`
- 缺少当前目标 sheet 的 JSON
- `sheet_name` 不在 `spreadsheet.sheets` 中，或 `sheet_name` 命中 hidden sheet
- `batch_count` 不等于 3
- 当前分片或最终合并缺少要求的输入字段
- 智能体无法从桥接产物中判断当前 sheet 的规则
- `calc_formula.py` 计算失败
- 当前 worker 无法生成分片 findings 或最终 `findings_<sheet>.json`

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
- 正式设计是“双层并行”：先按可见目标 sheet 并行，再对每个可见目标 sheet 固定拆成 3 个分片 worker，并由第 4 个 worker 合并。
- 除 `calc_formula.py` 外，规则阅读、定位、findings 组装和写盘都由智能体完成。
- 推荐结合 `scripts/sheet_audit_protocol.py` 与 `references/row-driven-audit-protocol.md` 使用，优先遵循“规则行驱动 + 行锚点 + 固定三段分片 + 最终合并”的确定性协议。
