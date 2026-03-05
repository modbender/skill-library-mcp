# PeonPing Skill (ClawdHub-ready)

This package provides an OpenClaw skill for installing and managing **peon-ping** with a hassle-free default setup (Orc Peon voice enabled immediately).

## Included files

- `SKILL.md` — complete skill spec with frontmatter, workflow, examples, and guardrails.
- `NOTES.md` — assumptions and source-validation notes.

## Scope

This skill is intentionally simple and practical:
- focuses on install, verify, configure, and troubleshoot
- uses real commands published by the peon-ping project
- avoids non-existent OpenClaw or peon-ping commands

## Suggested publish checks

Before uploading to ClawdHub:
1. Confirm links still resolve.
2. Run commands in a clean shell.
3. Ensure `peon status` and `peon preview` work on your target OS.
