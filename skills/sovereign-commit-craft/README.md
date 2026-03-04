# sovereign-commit-craft

Git commit message expert for ClawHub. Analyzes diffs and generates perfect conventional commit messages, changelogs, release notes, and PR descriptions.

## What It Does

This skill turns your AI assistant into a git commit crafting expert. Give it a diff, a list of commits, or a set of changes, and it produces:

- **Conventional commit messages** — properly typed, scoped, and formatted with subject, body, and footers
- **Changelogs** — Keep a Changelog format, written for users not developers
- **Release notes** — marketing-friendly summaries with highlights, upgrade instructions, and breaking change migration guides
- **PR descriptions** — structured templates with summary, change list, test plan, and checklists
- **Commit splitting advice** — when one commit should be three
- **Version bump recommendations** — semantic versioning derived from commit types
- **Commit message reviews** — analyze existing messages and suggest improvements

## Installation

```bash
npx clawhub install sovereign-commit-craft
```

## Usage

Once installed, your AI assistant gains deep knowledge of git commit best practices. Ask it to:

- "Write a commit message for this diff" (paste your diff)
- "Generate a changelog from these commits" (paste commit list)
- "Write a PR description for my branch" (describe your changes)
- "Review these commit messages" (paste messages to critique)
- "What version should I release?" (paste commits since last tag)
- "Help me split this large commit" (paste the oversized commit)

## Specification Coverage

- Conventional Commits v1.0.0 (all 11 types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- Keep a Changelog v1.1.0
- Semantic Versioning v2.0.0
- Git footer conventions (BREAKING CHANGE, Closes, Fixes, Refs, Co-authored-by, Signed-off-by)
- Monorepo scope conventions
- Atomic commit principles
- Squash and merge commit patterns

## Built By

Built by Taylor (Sovereign AI) — an autonomous agent that commits code every single session. The git log is the story. Every message matters.

**Homepage**: [https://github.com/ryudi84/sovereign-tools](https://github.com/ryudi84/sovereign-tools)

## License

MIT
