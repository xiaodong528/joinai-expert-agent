---
name: construction-audit-s2-workbook-render
description: "工程审核工作簿渲染技能：读取 `audit-config.yaml` 中的 `spreadsheet.path`、`spreadsheet.sheets` 与可选 `rule_document` 信息，按真实业务有效区域导出目标工作簿的 `sheets/*.json` 与桥接文档 `workbook.md`。JSON 保留 display_value、formula、仅原生公式来源的 formula_annotation、merge、row_context、基于表头识别的 col_context，以及规则名称与原文依据标注；`workbook.md` 仅输出值与 merge 视图，不展开公式或规则标注。Triggers on workbook render, spreadsheet to markdown/json, workbook.md generation。"
---

# Skill: construction-audit-s2-workbook-render

**用途（Purpose）:** 工作簿渲染（Workbook rendering）。
读取 `audit-config.yaml` 与工作簿文件，导出后续规则抽取阶段使用的 `workbook.md` 与 `sheets/*.json`。本技能只负责结构化表达与桥接视图，不负责规则抽取、rule candidate 标记、sheet 审核或 findings 输出。

当前正式主链中，本技能由 Mayor 直接加载执行，不再要求经由 Polecat 派发。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | 包含 `spreadsheet.path`、`spreadsheet.sheets`、`output_dir` 的配置文件 |

从配置文件中解析的关键字段：

- `audit_id`
- `spreadsheet.path`
- `spreadsheet.sheets`
- `output_dir`

---

## 输出契约（Output Contract）

正式产物固定为：

- `{output_dir}/workbook.md`
- `{output_dir}/sheets/{sheet_name}.json`

其中 `sheets/*.json` 中每个单元格至少包含：

- `cell_ref`
- `value`
- `display_value`
- `data_type`
- `formula`
- `formula_annotation`（仅原生公式来源）
- `rule_annotations`
- `merge`（可选）
- `row_context`
- `col_context`
- `row_business_label`
- `amount_role`

`workbook.md` 必须：

- 为每个目标 sheet 输出一个 `## Sheet: <sheet_name>` 小节
- 包含 `Sheet Summary`
- 包含 `Sheet View`
- 使用按有效业务区域裁剪后的二维 Markdown 表格语义复刻原 sheet
- merge anchor 内容附加 ` [MERGE A1:C2]` 之类的范围标记
- 不展开公式文本
- 不展开规则标注文本

`dimensions`、`row_count`、`col_count` 表示有效业务区域，而不是工作簿物理边界。

成功时输出单行摘要，至少包含：

- `audit_id`
- `input_workbook`
- `target_sheets_count`
- `output_markdown`

---

## 执行步骤（Execution Steps）

1. 读取并校验 `audit-config.yaml`
2. 校验 `spreadsheet.path`
3. 校验 `spreadsheet.sheets`
4. 调用 `spreadsheet_reader.py` 导出 `sheets/*.json`
5. 若存在 `rule_document.path`，确保 `rule_doc.md` 可用，并提取规则表行
6. 将规则名称与原文依据补充回 `sheets/*.json`，并仅保留原生公式说明
7. 校验所有目标 sheet 都已导出 JSON
8. 调用 `render_workbook_markdown.py` 生成 `workbook.md`
9. 校验 `workbook.md` 与 `sheets/*.json` 非空
10. 输出摘要

---

## CLI 入口

```bash
python .opencode/skills/construction-audit-s2-workbook-render/scripts/run_workbook_render.py \
  --config /abs/path/audit-config.yaml
```

低层脚本：

```bash
python .opencode/skills/construction-audit-s2-workbook-render/scripts/spreadsheet_reader.py \
  --input /abs/path/spreadsheet.xls \
  --all-sheets \
  --output-dir /abs/path/output/sheets

python .opencode/skills/construction-audit-s2-workbook-render/scripts/render_workbook_markdown.py \
  --sheets-dir /abs/path/output/sheets \
  --output /abs/path/output/workbook.md
```

---

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml` 可读取
- [ ] `spreadsheet.path` 指向已存在的工作簿
- [ ] `spreadsheet.sheets` 非空
- [ ] `sheets/*.json` 已导出
- [ ] 每个 cell 包含 `display_value`、`formula`、`formula_annotation`、`row_context`、`col_context`
- [ ] 金额目标格具备稳定的 `row_business_label`
- [ ] 金额目标格具备 `amount_role`（如 `pre_tax` / `tax` / `tax_inclusive`）
- [ ] 目标格和已解析操作数格具备 `rule_annotations`
- [ ] `workbook.md` 已生成且非空
- [ ] `workbook.md` 未展开公式或规则标注文本
- [ ] 合并单元格 anchor/covered 信息已保留
- [ ] `dimensions/row_count/col_count` 已收敛到真实业务区域
- [ ] stdout 包含 `audit_id`、`input_workbook`、`target_sheets_count`、`output_markdown`

---

## 失败条件（Failure Conditions）

- 配置文件不存在或无法解析
- 缺少 `spreadsheet.path`
- 缺少 `spreadsheet.sheets`
- 工作簿不存在或不可读
- 规则文档存在但 `rule_doc.md` 无法生成或无法提取规则表行
- 任一目标 sheet 无法导出 JSON
- `workbook.md` 输出为空

---

## 非职责范围（Non-goals）

本 Skill 不负责以下事项：

- 不生成 `rules_draft.json`
- 不生成 `rules.json`
- 不做 `[RULE_*]` 重点标记
- 不做 sheet 审核
- 不生成 findings
- 不生成 report
- 不引入 LLM 到运行时主链

---

## 备注（Notes）

- 当前 `v0.1.0` 正式设计以 `docs/v0.1.0/construction-audit-agent-design.md` 为准。
- 本技能只对应 `v0.1.0` 的阶段3，不与阶段4、阶段6合并。
- 阶段3的正式下游是 `construction-audit-s3-sheet-audit`，运行时主链应将这里生成的 `workbook.md` 与 `sheets/*.json` 直接交给该阶段消费。
- `.xls` 公式提取在当前版本允许降级为空字符串；若无法直接读取原生公式，不做任何结构或规则推断。
- `col_context` 采用稳定表头识别与继承，不再使用单纯“最近向上文本”。
- `row_business_label` 用于给同一业务行的金额格补上统一费用名称，避免值格只保留表格编号等弱上下文。
- `amount_role` 用于标识金额格语义角色，供 S3 将 `J/K/L` 等列展开为可审目标格。
- 若 `rule_document` 信息可用，本技能会复用阶段2的 `rule_doc.md` 或懒生成它，然后基于确定性规则行提取为单元格补充规则标注。
- `workbook.md` 是简化桥接视图，只展示值与 merge 语义；结构化公式与规则信息保留在 `sheets/*.json` 中。
- 除工作簿原生可读公式外，本技能不额外推断新公式表达。
- 历史备份技能目录仅供参考，不应再被本技能运行时入口或正式测试直接引用。
