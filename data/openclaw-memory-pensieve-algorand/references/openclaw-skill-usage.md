# OpenClaw skill creation, loading, and sharing

This summary is based on OpenClaw local docs:
- `/usr/lib/node_modules/openclaw/docs/tools/creating-skills.md`
- `/usr/lib/node_modules/openclaw/docs/tools/skills.md`

## Creation

- A skill is a folder with `SKILL.md` (YAML frontmatter + markdown instructions).
- Optional resource folders: `scripts/`, `references/`, `assets/`.

## Loading locations and precedence

OpenClaw loads skills from:
1. `<workspace>/skills` (highest precedence)
2. `~/.openclaw/skills`
3. bundled install skills (lowest)

## Refresh

After adding/modifying a skill:
- Ask the agent to refresh skills, or
- Restart gateway.

## Sharing options

1. Folder sharing:
   - Share the whole skill directory.
   - Receiver copies it into `<workspace>/skills` or `~/.openclaw/skills`.

2. Package sharing (`.skill`):
   - Use packager script:
     `python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> <optional-output-dir>`
   - Share generated `.skill` archive with other users.

3. Registry sharing:
   - Publish/sync via ClawHub (`clawhub.com`) when desired.

## Security notes

- Treat third-party skills as untrusted code.
- Keep secrets out of prompts and git.
- Prefer local-first behavior; add external writes only when necessary.
