---
name: construction-audit-s1-rule-doc-render
description: "工程审核规则文档渲染技能：读取 `audit-config.yaml` 中的 `rule_document.path` 与 `rule_document.markdown_path`，将 `rule_document.docx` 稳定渲染为 `rule_doc.md`，保留标题层级、原表格行顺序和修订痕迹，并输出包含 `audit_id`、输入路径和输出路径的摘要。Triggers on rule doc render, docx to markdown, rule_doc.md generation。"
---

# Skill: construction-audit-s1-rule-doc-render

**用途（Purpose）:** 规则文档渲染（Rule document rendering）。
读取 `audit-config.yaml` 与 `rule_document.docx`，生成后续规则抽取阶段使用的 `rule_doc.md`。本技能只负责文档渲染与最小输出校验，不负责规则抽取、sheet 导出、定位或 review。

---

## 输入契约（Input Contract）

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_config_path` | file path (`.yaml` / `.json`) | 是 | 包含 `rule_document.path` 与 `rule_document.markdown_path` 的配置文件 |

从配置文件中解析的关键字段：

- `audit_id`
- `rule_document.path`
- `rule_document.markdown_path`

---

## 输出契约（Output Contract）

唯一正式输出文件：`rule_doc.md`

要求：

- 输出文件路径固定使用 `audit-config.yaml.rule_document.markdown_path`
- 输出必须非空
- 输出应尽量保留：
  - 标题层级
  - 原表格行顺序
  - 原文表格文本
  - 修订痕迹

本技能成功时打印单行摘要，至少包含：

- `audit_id`
- `input_docx`
- `output_markdown`

---

## 执行步骤（Execution Steps）

1. 读取并校验 `audit-config.yaml`
2. 校验 `rule_document.path`
3. 校验 `rule_document.markdown_path`
4. 调用低层脚本 `render_rule_doc_markdown.sh` 生成 `rule_doc.md`
5. 校验输出文件存在且非空
6. 输出摘要

---

## CLI 入口

```bash
python joinai-expert-agent/construction-aduit/skills/construction-audit-s1-rule-doc-render/scripts/run_rule_doc_render.py \
  --config /abs/path/audit-config.yaml
```

低层脚本：

```bash
joinai-expert-agent/construction-aduit/skills/construction-audit-s1-rule-doc-render/scripts/render_rule_doc_markdown.sh \
  /abs/path/rule_document.docx \
  /abs/path/rule_doc.md
```

---

## 验证清单（Validation Checklist）

- [ ] `audit-config.yaml` 可读取
- [ ] `rule_document.path` 指向已存在的 `.docx`
- [ ] `rule_document.markdown_path` 已声明
- [ ] `rule_doc.md` 已生成且非空
- [ ] 输出中保留标题与表格
- [ ] stdout 包含 `audit_id`、`input_docx`、`output_markdown`

---

## 失败条件（Failure Conditions）

- 配置文件不存在或无法解析
- 缺少 `rule_document.path`
- 缺少 `rule_document.markdown_path`
- 输入文档不存在或不是 `.docx`
- `pandoc` 不可用
- Markdown 输出为空

---

## 非职责范围（Non-goals）

本 Skill 不负责以下事项：

- 不生成 `rules_draft.json`
- 不生成 `rules.json`
- 不导出 `sheets/*.json`
- 不做 sheet 定位
- 不做规则 review
- 不做 gate 校验

---

## 备注（Notes）

- 当前 `v0.1.0` 正式设计以 `docs/v0.1.0/construction-audit-agent-design.md` 为准。
- 本技能只对应 `v0.1.0` 的阶段2，不与阶段3、阶段4合并。
- 阶段2的正式下游是 `construction-audit-s3-sheet-audit`，运行时主链应将这里生成的 `rule_doc.md` 直接交给该阶段消费。
- “行级锚点 ID”不通过新增 sidecar 产物实现，而由后续阶段基于标题路径和表格体 1-based 行号确定性推导。
- 历史备份技能目录仅供参考，不应再被本技能的运行时入口或正式测试直接引用。
