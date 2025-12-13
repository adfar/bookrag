# Repository Guidelines

## Project Structure & Module Organization
- `docs/`: Planning and design documents.
- `docs/plans/`: Date-prefixed, kebab-case plans (e.g., `2025-12-11-web-book-interface-design.md`).
- `CLAUDE.md`: Agent collaboration rules and working agreements—review before automating changes.
- `.worktrees/` and `.claude/`: Internal tooling directories; do not edit.
- Future code: place libraries/app code in `src/` and tests in `tests/`. Keep modules small, cohesive, and documented with a short header explaining purpose and inputs/outputs.

## Build, Test, and Development Commands
- This repository is documentation-first; no build system is configured.
- Preview Markdown using your editor’s preview or GitHub’s renderer.
- Fast search across files: `rg "keyword"` (use `rg -n` to show line numbers).
- If you introduce code, add minimal scripts (e.g., `make lint`, `make test`) or a `README` section describing how to run/lint/test. Propose tooling in your PR.

## Coding Style & Naming Conventions
- Markdown: sentence-case headings, concise bullets over long paragraphs, relative links, and clear callouts for decisions/trade-offs.
- Filenames: kebab-case for docs (`YYYY-MM-DD-topic.md`), snake_case for code files, PascalCase for classes, lower_snake_case for functions/variables.
- Indentation: 2 spaces for YAML/JSON; 4 spaces for code unless language style dictates otherwise.
- Wrap lines at ~100 characters; keep paragraphs short and scannable.

## Testing Guidelines
- When code is added, mirror package structure under `tests/`.
- Prefer fast, deterministic tests; target ≥80% coverage where practical.
- Naming: `test_<module>.py` (Python) or `<module>.test.<ext>` per ecosystem norms.
- Document how to run tests in the PR and update `README` if adding tooling.

## Commit & Pull Request Guidelines
- Commits: imperative, concise subjects. Example: `Add web book interface design document`.
- Keep subject ≤72 chars; add a body if context or rationale aids reviewers.
- PRs: include a clear description, linked issues, rationale/trade-offs, and screenshots (UI) or sample output (CLI).
- Keep changes focused; update docs when behavior or decisions change.

## Agent-Specific Notes
- Follow `CLAUDE.md` for automation etiquette; prefer small, reviewable patches.
- Do not rewrite history on the default branch; use feature branches and PRs.
