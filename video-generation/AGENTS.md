# AGENTS.md

This file provides guidance when working with the `video-generation/` module in this repository.

## Module Layout

This module keeps the video-generation source and runtime snapshot together under one repo-local root:

- `.opencode/agents/`
  Source-of-truth agent definitions.
- `.opencode/skills/`
  Stage skills and QA guidance.
- `gt/`
  Gas Town configuration, runtime state snapshot, and role overrides.
- `docs/`
  Ignored local docs snapshot and research material.
- `output/`
  Ignored local archive / sample directory inside the repository.

Runtime discovery uses the module-local `.opencode/` tree:

- `.opencode/agents/video-generation-*.md`
- `.opencode/skills/video-*`
- `.opencode/skills/video-generation-qa-checklist`

Do not confuse the ignored repo-local `output/` directory with the formal runtime output root. The runtime contract remains:

```text
Video-Producer-output/{project_id}/
```

## JAS Role Mapping

The video workflow uses the standard three-role JAS layout:

- `video-generation-orchestrator` → Mayor
- `video-generation-worker` → Polecat
- `video-generation-reviewer` → Refinery

GT configuration under `gt/` maps the three GT roles to those three OpenCode agents.

## Running Stage Scripts

Stage source files live in `.opencode/skills/`, and runtime commands should use project-local paths:

```bash
PYTHONPATH=.opencode/skills/video-s2-character-anchor/scripts \
python .opencode/skills/video-s2-character-anchor/scripts/stage2_seedream.py \
  --project-id test-001 \
  --story Video-Producer-output/test-001/scripts/story.yaml
```

All stage scripts accept `--project-id` and default to `Video-Producer-output` as the base output directory.

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

The single valid runtime output root is:

```text
Video-Producer-output/{project_id}/
```

Repo-local `video-generation/output/` is only an ignored archive / sample directory. Do not replace the runtime contract with that path.

## Editing Rules

- If you update a stage skill, also update the corresponding GT bead instructions when runtime commands change.
- Keep all runtime examples pointed at `.opencode/skills/...`.
- Do not reintroduce the retired single-agent entrypoint, hidden in-repo skill paths, or legacy patrol wording into active runtime docs or configs.
- Use `video-generation-qa-checklist` for reviewer-facing acceptance and phase review guidance.
