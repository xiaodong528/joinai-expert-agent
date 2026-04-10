---
name: video-generation-qa-checklist
description: "AI 视频生成阶段审查与最终验收清单。Triggers on video QA, review gate, phase review, final acceptance."
---

# Video Generation QA Checklist

**用途**

为 `video-generation-reviewer` 和 `video-generation-orchestrator` 提供统一的阶段审查和终版验收清单，确保视频生成管线满足 JAS 规范、路径契约和交付要求。

## 依赖

- `video-validate-storyboard`：复核 Stage 1 分镜结构和规则
- `video-s10-qa-review`：读取技术 QA 结果
- `gt-status-report`
- `gt-mail-comm`

## 输入契约

| 输入 | 路径 | 说明 |
|------|------|------|
| 创意策划 | `Video-Producer-output/{project_id}/scripts/story.yaml` | S0 产物 |
| 分镜脚本 | `Video-Producer-output/{project_id}/scripts/storyboard.yaml` | S1 产物 |
| 关键帧目录 | `Video-Producer-output/{project_id}/frames/` | S3 产物 |
| 视频片段目录 | `Video-Producer-output/{project_id}/clips/` | S4 产物 |
| 音频目录 | `Video-Producer-output/{project_id}/audio/` | S5 / S6 产物 |
| 字幕目录 | `Video-Producer-output/{project_id}/subtitles/` | S5 / S9 产物 |
| 最终视频 | `Video-Producer-output/{project_id}/videos/final.mp4` | S9 产物 |
| 技术 QA | `Video-Producer-output/{project_id}/qa-report.json` | S10 产物 |

## 输出契约

| 输出 | 说明 |
|------|------|
| review 结论 | `pass` / `warn` / `fail` |
| 分项审查结果 | 输入完整性、结构正确性、产物完整性、业务一致性、最终可交付性 |
| 问题摘要 | 按阶段列出关键缺陷与建议动作 |

## 执行流程

1. 确认当前会话使用 `Video-Producer-output/{project_id}` 作为唯一输出根目录。
2. 检查 `story.yaml` 和 `storyboard.yaml` 是否存在且关键字段齐全。
3. 对 S3 / S4 / S5 / S6 产物做数量与命名自检：
   - 关键帧数量与分镜数量一致
   - 必要视频片段存在
   - 需要的音频、字幕文件存在
4. 若分镜脚本需要复核，调用 `video-validate-storyboard` 的同一套规则。
5. 检查 `videos/final.mp4`、`subtitles/final.srt`、`qa-report.json` 是否相互一致。
6. 额外扫描旧残留：
   - 旧单编排入口
   - 旧隐藏 Skill 路径
   - 非规范输出根目录
   - 旧巡检角色命名
7. 输出 review 结论，并将需要阻塞的项通过 GT mail 回传给编排者。

## 验证清单

- [ ] 所有运行时路径都指向 `Video-Producer-output/{project_id}`
- [ ] Agent / Skill 发现统一依赖项目内 `.opencode` 目录
- [ ] 分镜、关键帧、视频、音频、字幕与 QA 报告链路闭合
- [ ] 无旧单编排入口、旧隐藏 Skill 路径、非规范输出根目录或旧巡检角色残留
- [ ] 最终 review 结论可直接用于继续执行或阻塞交付
