# Repository Guidelines

## Project Structure & Module Organization

This repository stores JAS expert-agent assets, not a single runnable app. Work is organized by domain:

- `construction-aduit/`, `software-prototyper/`, `video-generation/`: domain modules with their own `agents/`, `skills/`, `docs/`, `gt/`, and `output/` folders.
- `*/agents/*.md`: source-of-truth agent definitions.
- `*/skills/*/SKILL.md`: staged skill definitions; helper scripts usually live under `scripts/`, and tests under `tests/`.
- `README.md`: repository-level overview.

When you enter a module, read its local `AGENTS.md` first; module-specific runtime and output rules override root-level guidance.

## Build, Test, and Development Commands

There is no monolithic root build. Validate only the area you touch.

- `python -m pytest -q --import-mode=importlib`: run the repository’s Python test suites.
- `pytest construction-aduit/skills/<skill-name>/tests -q`: run one skill’s focused tests during iteration.
- `python3 -m json.tool construction-aduit/gt/settings/config.json`: validate edited Gas Town JSON config files.
- `rg --files construction-aduit video-generation software-prototyper`: quickly inspect asset locations before editing.

## Coding Style & Naming Conventions

- Use Markdown for agents and skills; keep headings short and steps explicit.
- Python helper scripts use 4-space indentation, `snake_case` for functions/files, and `test_*.py` for tests.
- Prefer immutable updates, explicit input validation, and user-facing error messages.
- Keep changes narrow: update only the affected module, and avoid editing generated outputs in `*/output/` unless the task is specifically about delivery evidence.

## Testing Guidelines

- Put tests next to the skill they protect, usually under `*/skills/<skill>/tests/`.
- Add or update tests whenever you change `scripts/`, parsing logic, or output contracts.
- Aim for at least 80% coverage on touched logic, and run the smallest relevant suite before broader validation.
- For config-only changes, pair a syntax check (`json.tool`) with a brief manual review of the affected bead/role mapping.

## Commit & Pull Request Guidelines

- Follow the repository’s commit style: `feat: ...`, `docs: ...`, `chore: ...` (for example, `feat: add software-prototyper expert agent`).
- Keep one logical change per commit and mention the affected module when helpful.
- PRs should include purpose, touched paths, validation commands/results, and any linked issue or task.
- If you change docs, prompts, or output artifacts, include representative paths or screenshots in the PR description so reviewers can inspect them quickly.

## Security & Configuration Tips

- Never commit secrets, `.env*`, generated runtime state, or `.opencode/` artifacts.
- Treat `gt/` and user-level OpenCode registrations as environment-sensitive; verify paths and role mappings before changing runtime docs.
