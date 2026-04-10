---
name: software-prototyper-s3-foundation-bootstrap
description: "搭建软件原型底座。Triggers on foundation bootstrap、prototype scaffold、workspace init."
---

**用途**

为原型生成统一的项目底座，建立默认技术栈骨架、目录结构、依赖安装方式和运行说明。

## 依赖

- `software-prototyper-using-superpowers`
- `software-prototyper-test-driven-development`
- `software-prototyper-verification-before-completion`

## 输入契约

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_id` | string | 是 | 原型任务标识 |
| `project_config` | yaml | 是 | S1 冻结后的项目配置 |
| `wave_plan` | markdown | 是 | S2 生成的 Wave 计划 |

## 输出契约

- `Prototype-output/{project_id}/workspace/`
- `Prototype-output/{project_id}/docs/runbook.md`
- `Prototype-output/{project_id}/evidence/foundation-check.txt`

## 执行流程

1. 按用户指定技术栈或默认 `Next.js + Node + SQLite` 建立底座。
2. 生成目录结构、环境变量模板、测试命令和运行说明。
3. 用最小 Smoke 验证底座可启动。
4. 把基建证据写入 `Prototype-output/{project_id}/evidence/`。

## 验证清单

- [ ] 工作区目录已生成
- [ ] 默认命令和运行说明可用
- [ ] Foundation 证据已保存
