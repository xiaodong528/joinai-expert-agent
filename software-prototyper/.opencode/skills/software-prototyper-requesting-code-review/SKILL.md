---
name: software-prototyper-requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch a reviewer using the project-local `code-reviewer.md` template to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

在 `software-prototyper` 主链里，这个 skill 由 `Polecat` 在当前 bead 达到“可审查结果”时触发，用于把问题尽早暴露在正式交付前。

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- 当前 bead 达到“可审查结果”时触发
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Choose review baseline mode:**

**Mode A — Commit range review**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**Mode B — Workspace review（工作区审查，for uncommitted or untracked work）**

```bash
git status --short
find <paths-to-review> -type f | sort
```

Use this mode when the work lives in new or uncommitted files and there is no reliable commit range.
工作区审查模式下，review 输入以路径范围和工作区状态为准，而不是 commit range。

**2. Dispatch code-reviewer subagent:**

Use the host's reviewer dispatch mechanism with the project-local template at `code-reviewer.md`.

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` / `{HEAD_SHA}` - Starting and ending commit when using commit range review
- `{WORKSPACE_PATHS}` - Paths to review when using workspace review
- `{WORKSPACE_STATUS}` - `git status --short` output or equivalent file summary
- `{DESCRIPTION}` - Brief summary

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

git status --short
find joinai-expert-agent/software-prototyper -type f | sort

[Dispatch reviewer using project-local template]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from docs/superpowers/plans/deployment-plan.md
  WORKSPACE_PATHS: joinai-expert-agent/software-prototyper
  WORKSPACE_STATUS: ?? joinai-expert-agent/software-prototyper/...
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: `code-reviewer.md`
