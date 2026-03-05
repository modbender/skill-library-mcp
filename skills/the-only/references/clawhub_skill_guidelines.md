# Clawhub Skill Creation Guidelines (Self-Reminder)

## Core Structure

A publishable Clawhub skill *must* follow this structure:

```
the_ONLY/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description ONLY)
│   └── Markdown text instructions
├── scripts/ (optional, for executable code like Python/Bash)
├── references/ (optional, for lookup docs)
└── assets/ (optional, for templates/images)
```

## Restrictions

- **NO EXTRA DOCS**: Do not include `README.md`, `INSTALLATION_GUIDE.md`, or `package.json` in the root.
- **NO NODE.JS PLUGINS**: Standard Clawhub skills are prompt-driven Agent instructions (`SKILL.md`) augmented by `scripts/` (e.g., Python/Bash). They are not full TypeScript OpenClaw plugins with `index.ts` unless specifically supported by the packager. We should rely on standard OpenClaw tools (Cron CLI, etc.) via Agent prompts.
- **FRONTMATTER**: Only `name` and `description` are allowed in the YAML frontmatter. Do not put arbitrary JSON metadata here unless strictly permitted.
- **PACKAGING**: The skill must be able to pass `/Users/Clock/openclaw_only_project/new_only/skills/skill-creator/scripts/package_skill.py`.

## Action Plan for `the_ONLY`

1. Move any local JS/TS logic into `scripts/` (or rewrite as an Agent-driven prompt/Python script).
2. Ensure `SKILL.md` frontmatter only contains `name` and `description`.
3. Use OpenClaw tools (`openclaw cron`) via Agent actions rather than trying to write a native plugin.
4. Distribute by running `package_skill.py` to get `the_ONLY.skill`.
