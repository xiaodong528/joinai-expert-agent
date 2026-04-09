# JAS 工程建设审核智能体能力与价值报告

> **JoinAI Swarm Factory** | 版本 v1.0 |
>
> 基于 JAS 多智能体并行架构的双层审核系统。单项目审核时间从 **30 分钟**压缩至 **数分钟**，支持**家客电信建设工程**预算/结算全自动审核。

---

## 1. 执行摘要

JAS（JoinAI Swarm Factory）工程建设审核智能体是一套端到端全自动化的建设工程造价审核系统。它将传统人工审核中的规则解析、表格审查、交叉验证、报告生成等环节，整合为 4 个自动化阶段（Stage 0–3），由多个 AI 智能体协同并行执行，实现从"上传工程表格"到"审核报告+修正文件"的全自动交付。

系统采用 **OpenCode + Gas Town 双层架构**，当前正式流程统一为“用户上传 `rule_document.docx` + `spreadsheet.xlsx/.xls`”，由 S1 从规则文档提取结构化规则，再驱动后续审核与报告生成。

### 核心指标一览

| 指标             | 数值                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------ |
| 管线阶段数       | 4（Stage 0–3，覆盖会话初始化→规则提取→表格审查→报告生成全流程）                  |
| 样例验证规则数   | **47 条**（预算 23 条 + 结算 24 条）                                           |
| 峰值并行智能体数 | **N+2 个**（N = Sheet 数量，每个 Sheet 独立 Polecat）                          |
| 支持审核类型     | 预算审核、结算审核（家客电信工程）                                                   |
| 端到端验证项目   | 2 个：① 东海县海陵家苑预算审核（23 条规则）；② 东海县海陵家苑结算审核（24 条规则） |
| 关键问题发现     | **6 个**（预算 4 个 critical + 结算 2 个 critical）                            |

---

## 2. 系统架构总览

![系统架构总览](illustrations/jas-construction-audit-report/01-framework-system-architecture.png)

*图 2-1：双层架构图——OpenCode 智能体层与 Gas Town 运维层的分层关系*

### 2.1 双层架构

JAS 工程建设审核智能体采用**双层分离架构**，将智能体行为定义与运维基础设施各司其职：

```
┌─────────────────────────────────────────────────────────────┐
│  OpenCode Layer                    智能体行为定义层          │
│  ── Agent 定义（四角色）、Skill 封装、I/O 契约               │
├─────────────────────────────────────────────────────────────┤
│  Gas Town Layer                    运维编排层                │
│  ── Mayor 调度、Polecat 执行、Refinery 审查、Witness 监控    │
│  ── Wave 并行分发、Dolt 持久化、巡逻与升级路由               │
└─────────────────────────────────────────────────────────────┘
```

- **智能体层（OpenCode）**：定义四角色 Agent、Stage Skill、数据 Schema。职责清晰、边界明确。
- **运维层（Gas Town）**：提供 Mayor-Polecat 主从架构、Wave 并行调度、质量门控、状态持久化。

### 2.2 四角色智能体架构

系统采用 **ADR-001 标准四角色架构**（与 ai-video-generation 项目一致）：

| GT 角色                      | Agent Config 名称                            | OpenCode `--agent`                | 核心职责                               |
| ---------------------------- | -------------------------------------------- | ----------------------------------- | -------------------------------------- |
| **Mayor（编排者）**    | `opencode-construction-audit-orchestrator` | `construction-audit-orchestrator` | 调度、Wave 编排、质量门控、与用户对话  |
| **Polecat（执行者）**  | `opencode-construction-audit-worker`       | `construction-audit-worker`       | 执行 S0-S3 具体任务（除 Mayor 对话外） |
| **Refinery（审查者）** | `opencode-construction-audit-reviewer`     | `construction-audit-reviewer`     | QA 检查、质量评分、端到端验证          |
| **Witness（监控者）**  | `opencode-construction-audit-monitor`      | `construction-audit-monitor`      | 心跳监控、超时检测、升级路由           |

**设计哲学**：

- Mayor 仅处理用户对话和编排调度，**所有文件 I/O 和脚本执行必须 `gt sling` 给 Polecat**
- Polecat 完全无状态，通过共享文件系统传递数据，支持弹性扩展
- Refinery 在每阶段后审查产出质量，确保规则覆盖度和数值准确性
- Witness 监控流水线健康状态，异常时通过 escalation 机制上报

![四角色智能体架构](illustrations/jas-construction-audit-report/02-framework-four-roles.png)

*图 2-2：四角色智能体架构——Mayor、Polecat、Refinery、Witness 的职责与交互关系*

### 2.3 四阶段审核流水线

| Stage | 名称       | 属性 | 执行者          | 核心产出                                 |
| ----- | ---------- | ---- | --------------- | ---------------------------------------- |
| 0     | 会话初始化 | 必选 | Mayor（交互式） | `audit-config.yaml`（含 `rule_document.path`） |
| 1     | 规则提取   | 必选 | Polecat x 1-2   | `rules/rules.json`（23-24 条规则）     |
| 2     | 表格审查   | 必选 | Polecat x N     | `findings/*.json`（每 Sheet 一个）     |
| 3     | 报告生成   | 必选 | Polecat x 1     | `audit-report.md` + `corrected.xlsx` |

**关键约束**：

- S1 必须消费用户上传的 `rule_document.docx`，不得跳过
- S2 必须按 Sheet **并行执行**，每个 Sheet 独立 Polecat
- S3 必须先通过 **Two-Phase Gate**（验证所有 findings 存在）才能执行

---

## 3. 多智能体并行架构 — Wave 调度模型

![Wave 调度模型](illustrations/jas-construction-audit-report/03-flowchart-wave-scheduling.png)

*图 3-1：Wave 调度模型——三阶段并行处理流程，S0→S1→S2→S3 分 Wave 执行*

Wave 调度模型是 JAS Construction-Review 智能体的核心架构创新。它将 4 个阶段组织为**三个并行波浪（Wave）**，最大化利用多智能体并行处理能力。

### 3.1 Wave 并行化流程

```
                    ┌───────────────────┐
                    │      Stage 0      │  Mayor 与用户交互式对话
                    │    会话初始化      │  输出: audit-config.yaml
                    └─────────┬─────────┘
                              ▼
              ┌───────────────────────────────┐
    Wave 1    │  S0 文件处理（Sling → Polecat）│  1 个 Polecat
              │  S1 规则提取（条件执行）       │  1-2 个 Polecat
              │  Validate 质量门控            │  1 个 Polecat
              └───────────────┬───────────────┘
                    质量门控 ▼ 规则 JSON 验证
              ┌───────────────────────────────┐
    Wave 2    │     Stage 2 表格审查          │  N 个 Polecat
              │   每 Sheet 独立并行执行        │  （N = Sheet 数量）
              └───────────────┬───────────────┘
                    质量门控 ▼ Two-Phase Gate
              ┌───────────────────────────────┐
    Wave 3    │     Stage 3 报告生成          │  1 个 Polecat
              │  Report Builder + XLSX Fixer  │
              └───────────────────────────────┘
```

**设计哲学**：

- 耗时的规则提取和表格审查全部并行化
- Mayor 仅负责编排和对话，不执行具体计算
- Wave 之间设置同步屏障和质量门控，确保上游输出质量后再启动下游

### 3.2 并行度扩展能力

随着 Sheet 数量增加，系统的并行度**线性扩展**：

| Sheet 数 N | Wave 2 Polecat 数 | 总 Polecat 数 | 说明             |
| ---------- | ----------------- | ------------- | ---------------- |
| 5          | 5                 | 7             | 小规模项目       |
| 10         | 10                | 12            | 中等规模项目     |
| 20         | 20                | 22            | 大型项目         |
| 24         | 24                | 26            | 当前验证项目规模 |

> 峰值并行度出现在 Wave 2（表格审查阶段）。东海县海陵家苑项目有 24 个 Sheet，最高有 **24 个 Polecat 同时工作**。

### 3.3 GT Sling 调度协议

**核心规则**：Mayor 仅处理用户对话。所有文件 I/O 和脚本执行必须 `gt sling` 给 Polecat。

| Stage             | Mayor 职责                  | Polecat 执行（必须加载对应 Skill）               | Refinery 审查             |
| ----------------- | --------------------------- | ------------------------------------------------ | ------------------------- |
| S0 交互           | 与用户对话收集文件路径      | —                                               | —                        |
| S0 文件处理       | `gt sling` 派发           | `/construction-audit-s0-session-init`          | config 完整性             |
| S1 规则提取       | `gt sling` 派发           | `/construction-audit-s1-rule-extraction`       | 规则覆盖度                |
| validate          | `gt sling` 派发           | `/construction-audit-validate-rules`           | —                        |
| **S2 审核** | **`gt sling` × N** | **`/construction-audit-s2-sheet-audit`** | **findings 合理性** |
| S3 报告           | `gt sling` 派发           | `/construction-audit-s3-report-generation`     | 最终 review               |

### 3.4 质量门控机制

管线设置 **3 个质量检查点**，确保每个 Wave 的输出质量：

| 检查时机      | 检查内容                                         | 不通过处理   |
| ------------- | ------------------------------------------------ | ------------ |
| Wave 1 完成后 | 规则 JSON schema 验证、cell_ref 解析率 > 95%     | 返回重新提取 |
| Wave 2 完成后 | Two-Phase Gate：所有 findings 文件存在且格式合法 | 等待缺失文件 |
| S3 完成后     | 报告格式、数值一致性、修正文件完整性             | 生成修复建议 |

---

## 4. 审核输入契约

### 4.1 当前正式输入

系统当前正式流程要求用户一次性提供两类输入：

| 输入 | 说明 | 用途 |
| ---- | ---- | ---- |
| `rule_document.docx` | 用户上传的审核规则文档 | S1 解析并提取结构化规则 |
| `spreadsheet.xlsx/.xls` | 工程造价表格 | S2 逐 Sheet 审核与 S3 修正 |

### 4.2 规则提取链路

```
用户上传 rule_document.docx
    │
    ▼
render_rule_doc_markdown.sh
    │
    ▼
LLM 规则解释 / reviewer subagent
    │
    ▼
rules/rules.json
```

### 4.3 配置落盘

`audit-config.yaml` 记录当前会话的正式输入契约，关键字段如下：

```yaml
rule_document:
  path: "/abs/path/to/rule_document.docx"
spreadsheet:
  path: "/abs/path/to/预算表.xlsx"
```

---

## 5. 端到端验证成果

![验证成果信息图](illustrations/jas-construction-audit-report/05-infographic-validation-results.png)

*图 5-1：端到端验证成果——历史样例规则集验证中发现 6 个 Critical Findings（预算 4 个 + 结算 2 个）*

### 5.1 验证项目概况

系统已完成完整的端到端验证，项目代号 **东海县海陵家苑三网小区新建工程**：

| 属性       | 预算审核                                | 结算审核                                           |
| ---------- | --------------------------------------- | -------------------------------------------------- |
| 审核类型   | 预算审核                                | 结算审核                                           |
| 工程名称   | 东海县海陵家苑三网小区新建工程          | 同上                                               |
| 表格文件   | 东海县海陵家苑三网小区新建工程-预算.xls | 东海县海陵家苑三网小区新建工程-施工单位结算书.xlsx |
| Sheet 数量 | 24 个                                   | 20+ 个                                             |
| 输入契约   | `rule_document.docx` + spreadsheet     | `rule_document.docx` + spreadsheet                 |
| 规则数量   | 23 条                                   | 24 条                                              |
| 验证方式   | 真实 API 调用（非 mock/dry-run）        | 真实 API 调用                                      |

### 预算审核验证结果

| # | 位置          | 规则                        | 预期值 | 实际值 | 偏差   | 严重度             |
| - | ------------- | --------------------------- | ------ | ------ | ------ | ------------------ |
| 1 | 表五（甲）D13 | 安全生产费 = 建安费 × 1.5% | 150.40 | 200.53 | +33.3% | **Critical** |
| 2 | 三费取费 N3   | 安全生产费 = 建安费 × 1.5% | 150.40 | 200.53 | +33.3% | **Critical** |
| 3 | 表一折前 I13  | 预备费 = 合计 × 0.4%       | 54.14  | 541.44 | +900%  | **Critical** |
| 4 | 三费取费 I3   | 预备费 = 总投资 × 0.4%     | 56.31  | 541.44 | +862%  | **Critical** |

**根因分析**：

- **安全生产费率错误**：使用了结算费率 2% 而非预算费率 1.5%
- **预备费率错误**：使用了 4% 而非知识库规定的 0.4%（10 倍差异）

### 结算审核验证结果

| # | 位置      | 问题描述                                 | 严重度             |
| - | --------- | ---------------------------------------- | ------------------ |
| 1 | 表一 J13  | 综合工日施工费折扣后**未扣材料费** | **Critical** |
| 2 | 表五甲 D7 | 总计**缺监理费**                   | **Critical** |

### 5.4 已知校验点验证

以下数值用于端到端验证审核结果的正确性：

| 指标                            | 期望值                   | 验证结果 |
| ------------------------------- | ------------------------ | -------- |
| 人工费合计 (labor_cost)         | 2532.76                  | ✅ 通过  |
| 安全文明施工费费率 (safety_fee) | 2%（结算）/ 1.5%（预算） | ✅ 通过  |
| 优惠折扣系数 (discount)         | 0.54（东海区域）         | ✅ 通过  |

### 5.5 验证历程（Phase 8）

| 轮次   | 模式            | 规则数 | Findings                | 关键问题                    |
| ------ | --------------- | ------ | ----------------------- | --------------------------- |
| 第一轮 | user_provided   | 5 条   | 0 个                    | S1 规则提取不足（Issue #7） |
| 第二轮 | 预算规则文档 | 23 条  | **4 个 critical** | 费率错误检出                |
| 第三轮 | 结算规则文档 | 24 条  | **2 个 critical** | 计算遗漏检出                |

---

## 6. 成本与效率分析

![效率对比](illustrations/jas-construction-audit-report/06-comparison-efficiency-boost.png)

*图 6-1：审核效率对比——传统人工 vs JAS AI 审核，单项目耗时从 30 分钟降至数分钟，5-10 倍效率提升*

### 6.1 审核效率对比

| 维度                 | 传统人工审核           | JAS AI 审核              | 提升               |
| -------------------- | ---------------------- | ------------------------ | ------------------ |
| **单项目耗时** | 30 分钟以上            | 数分钟                   | **5-10 倍**  |
| **遗漏率**     | 15-50%                 | 接近 0%（全量覆盖）      | **质的飞跃** |
| **跨表验证**   | 容易出错               | 自动交叉验证             | 准确性保障         |
| **规则一致性** | 依赖人员经验           | 用户上传规则文档 + 统一提取链路 | 标准化             |
| **并发能力**   | 线性增长（需叠加人头） | 弹性扩展（增加 Polecat） | 可扩展性           |

### 6.2 审核质量保障

| 保障机制             | 说明                                                  |
| -------------------- | ----------------------------------------------------- |
| **规则唯一性** | 审核规则是唯一依据，不得擅自添加、修改或忽略          |
| **计算复核**   | Decimal 二次验证 +`calculation_verified` 标记       |
| **零值跳过**   | 目标值为 0 或操作数全为 0 时自动跳过，避免误报        |
| **容差可配置** | 默认误差容差 0.1，支持 per-rule 覆盖                  |
| **反欺诈意识** | Agent Prompt 内置：施工单位可能高估冒算，保持审慎怀疑 |

### 6.3 规模化预测

| 审核规模 | 月处理量      | 人工审核人力     | JAS AI 成本 |
| -------- | ------------- | ---------------- | ----------- |
| 小规模   | 100 项目/月   | 1-2 名专职审核员 | 计算资源    |
| 中规模   | 1000 项目/月  | 5-10 名审核团队  | 计算资源    |
| 大规模   | 10000 项目/月 | 大型审核部门     | 计算资源    |

> JAS AI 审核的边际成本极低，大规模场景下优势更加明显。

---

## 7. 技术栈与依赖

### 7.1 Python 依赖

| 库          | 版本  | 用途                           |
| ----------- | ----- | ------------------------------ |
| openpyxl    | 3.1+  | 读写 .xlsx 文件                |
| xlrd        | 1.2.x | 读取 .xls 文件（旧二进制格式） |
| python-docx | 1.x   | 解析 .docx 知识库文档          |
| pyyaml      | 6.x   | audit-config.yaml 读写         |

### 7.2 Claude Code Skills

| Skill                     | 触发条件             | 用途             |
| ------------------------- | -------------------- | ---------------- |
| `/document-skills:docx` | 涉及 .docx 文件      | 解析知识库文档   |
| `/document-skills:xlsx` | 涉及 .xlsx/.xls 文件 | 读取工程造价表格 |

### 7.3 OpenCode 组件

| 组件               | 路径                                                                       | 说明         |
| ------------------ | -------------------------------------------------------------------------- | ------------ |
| Orchestrator Agent | `.opencode/agents/construction-audit-orchestrator.md`                    | Mayor        |
| Worker Agent       | `.opencode/agents/construction-audit-worker.md`                          | Polecat      |
| Reviewer Agent     | `.opencode/agents/construction-audit-reviewer.md`                        | Refinery     |
| Monitor Agent      | `.opencode/agents/construction-audit-monitor.md`                         | Witness      |
| Skill S0-S3        | `.opencode/skills/construction-audit-s{0-3}-*/`                          | 四阶段技能   |
| Rule Document Path | `audit-config.yaml -> rule_document.path`                              | 当前正式规则输入 |

### 7.4 Gas Town 组件

| 组件       | 路径                                      | 说明              |
| ---------- | ----------------------------------------- | ----------------- |
| Rig        | `gt/data-audit/`                        | 审核编排 rig      |
| Wave Beads | `gt/data-audit/beads/wave-{1,2,3}-*.md` | Polecat 任务定义  |
| Dolt DB    | `127.0.0.1:3307`, database `hq`       | 会话状态持久化    |
| Rig Config | `gt/data-audit/settings/config.json`    | 四角色 agent 映射 |

---

## 8. 核心数据 Schema

### 8.1 Rule JSON（Stage 1 输出）

```json
{
  "audit_type": "budget",
  "source_file": "家客预算审核知识库11.9.docx",
  "extracted_at": "2026-03-27T10:00:00Z",
  "rule_categories": [
    {
      "category_id": "table_2_pre_discount",
      "category_name": "表二-折扣前",
      "rules": [
        {
          "rule_id": "T2-R05",
          "description": "人工费 = 技工费 + 普工费",
          "type": "formula",
          "formula": "skilled_labor + unskilled_labor",
          "source_cells": {
            "result": { "sheet": "表二-折扣前", "hint": "人工费合计", "cell_ref": "D15" },
            "operands": [
              { "sheet": "表二-折扣前", "hint": "技工费", "cell_ref": "D13" },
              { "sheet": "表二-折扣前", "hint": "普工费", "cell_ref": "D14" }
            ]
          },
          "tolerance": 0.1,
          "severity": "critical",
          "auto_fixable": true
        }
      ]
    }
  ]
}
```

### 8.2 Finding JSON（Stage 2 输出）

```json
{
  "sheet_name": "表二-折扣前",
  "audit_id": "AUDIT-20260327-001",
  "total_cells_checked": 45,
  "total_rules_in_file": 25,
  "rules_applied": 20,
  "rules_skipped": { "no_cell_ref": 1, "zero_target": 1, "zero_operands": 1 },
  "findings": [
    {
      "finding_id": "F-表二-001",
      "rule_id": "T2-R14",
      "cell_ref": "D20",
      "expected_value": 37.99,
      "actual_value": 38.50,
      "discrepancy": 0.51,
      "discrepancy_pct": 1.34,
      "severity": "high",
      "category": "formula_error",
      "calculation_verified": true,
      "description": "文明施工费计算错误：应为37.99，实际为38.50",
      "auto_fixable": true,
      "fix_action": { "type": "replace_value", "target_cell": "D20", "new_value": 37.99 }
    }
  ],
  "summary": { "critical": 0, "high": 1, "medium": 2, "low": 0, "pass": 42 }
}
```

### 8.3 Audit Config YAML（Stage 0 输出）

```yaml
audit_id: "AUDIT-20260327-150943"
audit_type: "budget"
audit_date: "2026-03-27"
project_info:
  project_name: "东海县海陵家苑三网小区新建工程"
  contract_type: "家客"
rule_document:
  path: "/abs/path/to/rule_document.docx"
spreadsheet:
  path: "/abs/path/to/预算表.xlsx"
  sheets: ["表一", "表二-折扣前", "表二-综合工日折后", "表五甲", ...]
output_dir: "./audit-output/AUDIT-20260327-150943"
tolerance: 0.1
```

## 9. 验证策略

### 9.1 已知验证点

| 验证项           | 期望值                             | 来源           |
| ---------------- | ---------------------------------- | -------------- |
| 表二折前-人工费  | 2532.76 (技工2265.06 + 普工267.70) | 结算书.xlsx    |
| 安全生产费率     | 2%（结算）vs 1.5%（预算）          | 知识库差异     |
| 施工折扣         | 0.54（东海区域，山东永川科技）     | 工程信息       |
| 综合工日单价     | 74.24 x 施工折扣                   | 知识库规则     |
| 技工费(折后)     | 总工日 x 74.24 x 0.54 = 796.54     | 结算书表二折后 |
| 甲供材合计(除税) | 635.39                             | 结算书表四     |

---

## 10. 技术风险与缓解

| 风险                   | 影响             | 缓解措施                                           |
| ---------------------- | ---------------- | -------------------------------------------------- |
| .xls 格式无公式信息    | 无法对比实际公式 | xlrd 只读值，依赖规则推导期望值                    |
| 合并单元格             | 数据提取遗漏     | spreadsheet_reader 将合并值传播到所有覆盖单元格    |
| 规则->单元格的模糊映射 | 审核遗漏或误报   | LLM 解读表格结构 + 验证门控二次确认                |
| 跨表公式依赖           | Stage 2 需预加载 | cell_validator --context-sheets 预加载依赖表       |
| 大表格（表三甲254行）  | 单 Agent 超时    | 按 Sheet 并行，每个子智能体处理一个 Sheet          |
| LLM 规则提取幻觉       | 生成错误规则     | rule_extractor.py 验证 + audit-validate-rules 门控 |

---
