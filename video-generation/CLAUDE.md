# CLAUDE.md

This file provides guidance when working with the `ai-video-generation` workspace.

## Workspace Layout

This project intentionally uses a **dual-directory** layout:

- `ai-video-generation/`
  Holds Gas Town configuration, runtime documentation, and generated outputs.
- `joinai-expert-agent/video-generation/`
  Holds the source-of-truth Agent and Skill Markdown files.

Runtime discovery does **not** depend on an in-repo `.opencode/` folder. Agent and Skill discovery is provided through user-level symlinks:

- `~/.config/opencode/agents/video-generation-*.md`
- `~/.config/opencode/skills/video-*`
- `~/.config/opencode/skills/video-generation-qa-checklist`

## JAS Role Mapping

The video workflow now uses the standard three-role JAS layout:

- `video-generation-orchestrator` → Mayor
- `video-generation-worker` → Polecat
- `video-generation-reviewer` → Refinery

GT configuration under `ai-video-generation/gt/` maps the three GT roles to those three OpenCode agents.

## Running Stage Scripts

Stage source files live in `joinai-expert-agent/video-generation/skills/`, but runtime commands should use the user-level symlink contract:

```bash
PYTHONPATH=~/.config/opencode/skills/video-s2-character-anchor/scripts \
python ~/.config/opencode/skills/video-s2-character-anchor/scripts/stage2_seedream.py \
  --project-id test-001 \
  --story Video-Producer-output/test-001/scripts/story.yaml
```

All stage scripts accept `--project-id` and default to `Video-Producer-output` as the output root.

## Pipeline Overview

```text
Stage 0  创意策划                     → scripts/story.yaml
Stage 1  分镜脚本                     → scripts/storyboard.yaml
Stage 2  角色锚定                     → characters/{name}-ref.png
Stage 3  关键帧生成                   → frames/scene-{01..N}-first.png + -last.png
Stage 4  图生视频                     → clips/scene-{01..N}.mp4
Stage 5  TTS 语音 + 逐场景字幕        → audio/tts-{01..N}.mp3 + subtitles/scene-{01..N}.srt
Stage 6  BGM 音乐                     → audio/bgm.mp3
Stage 7  视频拼接 + 音频混合          → videos/concat-final.mp4
Stage 8  对口型                       → videos/lipsync.mp4
Stage 9  字幕生成 / 烧录              → subtitles/final.srt + videos/final.mp4
Stage 10 技术 QA + Reviewer 复核      → qa-report.json
```

唯一合法输出根目录是：

```text
Video-Producer-output/{project_id}/
```

Do not reintroduce the retired nonstandard output root.

## Editing Rules

- If you update a Stage Skill, also update the corresponding GT bead instructions when runtime commands change.
- Keep all runtime examples pointed at `~/.config/opencode/skills/...`.
- Do not reintroduce the retired single-agent entrypoint, hidden in-repo skill paths, or legacy patrol wording into active runtime docs or configs.
- Use `video-generation-qa-checklist` for reviewer-facing acceptance and phase review guidance.
