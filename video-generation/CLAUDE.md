# CLAUDE.md

This file provides guidance when working with the `video-generation/` module in this repository.

## Module Layout

Within this repository, use these paths directly:

- Agents: `.opencode/agents/*.md`
- Skills: `.opencode/skills/*`
- GT runtime snapshot: `gt/`
- Ignored local docs snapshot: `docs/`
- Ignored local archive directory: `output/`

Runtime discovery uses the module-local `.opencode/` tree:

- `.opencode/agents/video-generation-*.md`
- `.opencode/skills/video-*`
- `.opencode/skills/video-generation-qa-checklist`

The ignored repo-local `output/` directory is not the formal runtime contract.

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

## Output Contract

The single valid runtime output root is:

```text
Video-Producer-output/{project_id}/
```

Keep using `Video-Producer-output/{project_id}/` for intermediate assets, final videos, subtitles, and QA evidence. Do not replace it with `video-generation/output/`, which is only an ignored local archive directory in this repo.

## Editing Rules

- If you update a stage skill, also update the corresponding GT bead instructions when runtime commands change.
- Keep all runtime examples pointed at `.opencode/skills/...`.
- Do not reintroduce the retired single-agent entrypoint, hidden in-repo skill paths, or legacy patrol wording into active runtime docs or configs.
- Use `video-generation-qa-checklist` for reviewer-facing acceptance and phase review guidance.
