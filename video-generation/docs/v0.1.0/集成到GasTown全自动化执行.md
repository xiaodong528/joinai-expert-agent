# AI 视频生成接入 Gas Town

> 状态：已按三角色 JAS 口径整理
> 更新：2026-04-07

## 1. 目录与发现链路

本项目保留双目录分工：

- `ai-video-generation/`
  - GT Town / Rig 配置
  - 运行文档
  - `Video-Producer-output/`
- `joinai-expert-agent/video-generation/`
  - Agent 源文件
  - Skill 源文件

运行时通过用户级软链接发现 Agent 与 Skill：

```text
~/.config/opencode/agents/video-generation-orchestrator.md
~/.config/opencode/agents/video-generation-worker.md
~/.config/opencode/agents/video-generation-reviewer.md
~/.config/opencode/skills/video-*
~/.config/opencode/skills/video-generation-qa-checklist
```

## 2. 三角色映射

| GT 角色 | OpenCode Agent |
|---------|----------------|
| mayor | `video-generation-orchestrator` |
| polecat | `video-generation-worker` |
| refinery | `video-generation-reviewer` |

Town 配置位于：

- `ai-video-generation/gt/settings/config.json`

Rig 配置位于：

- `ai-video-generation/gt/gastown/settings/config.json`

Role TOML override 位于：

- `ai-video-generation/gt/roles/mayor.toml`
- `ai-video-generation/gt/roles/polecat.toml`
- `ai-video-generation/gt/roles/refinery.toml`

## 3. 运行链路

GT 负责角色解析和会话编排，具体启动命令由 Role TOML 固定为三角色 Agent：

```text
Mayor    -> opencode --agent video-generation-orchestrator
Polecat  -> opencode --agent video-generation-worker
Refinery -> opencode --agent video-generation-reviewer
```

阶段脚本运行不再引用仓库内隐藏 Skill 目录，统一使用：

```bash
PYTHONPATH=~/.config/opencode/skills/video-s3-keyframe-gen/scripts \
python ~/.config/opencode/skills/video-s3-keyframe-gen/scripts/stage3_keyframe_chain.py \
  --project-id <project_id> \
  --storyboard Video-Producer-output/<project_id>/scripts/storyboard.yaml
```

## 4. Wave 分工

| Wave / 阶段 | 责任角色 | 说明 |
|-------------|----------|------|
| Stage 0 | orchestrator | 创意策划与冻结规则 |
| Wave 1 | worker + reviewer | 分镜脚本、角色锚定、分镜 gate |
| Wave 2 | worker + reviewer | 关键帧生成与连续性抽查 |
| Wave 3 | worker + reviewer | 视频、TTS、BGM 并行生成 |
| Stage 7-10 | worker + reviewer + orchestrator | 拼接、对口型、字幕、技术 QA、最终验收 |

Reviewer 统一使用 `video-generation-qa-checklist` 做阶段审查和最终验收。

## 5. 当前约束

- 唯一合法输出根目录：`Video-Producer-output/{project_id}`
- 不再使用旧的单编排入口
- 不再依赖仓库内隐藏 Agent / Skill 目录做发现
- 不保留旧巡检扩展角色残留

## 6. 验证命令

```bash
python3 -m json.tool ai-video-generation/gt/settings/config.json
python3 -m json.tool ai-video-generation/gt/gastown/settings/config.json
ls ai-video-generation/gt/roles/{mayor,polecat,refinery}.toml
gt config default-agent
gt config agent list | grep video-generation
opencode agent list | grep video-generation
ls -la ~/.config/opencode/agents/video-generation-*.md
find ~/.config/opencode/skills -maxdepth 1 -type l | grep 'video-'
```
