# Project Notes for Claude

## Reference Documentation

Before answering any question about ClawHub commands, SKILL.md format, or skill configuration — fetch and read the relevant documentation page first:

- https://docs.openclaw.ai/tools/clawhub — ClawHub CLI commands (install, update, list, publish, etc.)
- https://docs.openclaw.ai/tools/skills — SKILL.md structure and frontmatter spec
- https://docs.openclaw.ai/tools/skills-config — skill configuration and openclaw.json

### ClawHub CLI reference (from docs)

```
clawhub install <slug>
clawhub update <slug>
clawhub update --all
clawhub update --version <version>   # single slug only
clawhub update --force               # overwrite when local files don't match published version
clawhub list                         # reads .clawhub/lock.json
```

## Key conventions

- `SKILL.md` frontmatter `metadata` must be a **single-line JSON** with the `openclaw` namespace:
  ```
  metadata: {"openclaw": {"requires": {"bins": [...], "env": [...]}, "primaryEnv": "..."}}
  ```
- `name` in SKILL.md frontmatter is the registry package ID (e.g. `sergei-mikhailov-stt`), not a display name
- Display name is the `#` heading in the body of SKILL.md
