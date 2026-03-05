# 🧠 ClawSouls Skill for OpenClaw

An [OpenClaw](https://github.com/openclaw/openclaw) skill that lets your AI agent manage personas (Souls) — install, switch, create, publish, and validate AI personalities.

## Installation

Add this skill to your OpenClaw workspace:

```bash
# Via ClaWHub (coming soon)
openclaw skill install clawsouls

# Or manually
git clone https://github.com/clawsouls/clawsouls-skill.git ~/.openclaw/skills/clawsouls
```

## What It Does

Once installed, your AI agent can:

- **Install souls** — Download persona packages from the registry (`owner/name` format)
- **Switch personas** — Activate a different personality with automatic backup
- **Create souls** — Scaffold a new soul with `init`
- **Validate** — Check a soul package against the spec before publishing
- **Publish** — Upload souls to the registry
- **List installed** — Show all available local souls
- **Restore** — Revert to your previous persona

## Example Prompts

```
"Install the clawsouls/minimalist soul"
"Switch my persona to clawsouls/devops-veteran"
"What souls do I have installed?"
"Restore my previous personality"
"Browse available personas"
"Create a new soul called my-bot"
"Validate my soul package"
"Publish my soul to the registry"
```

## CLI Commands

```bash
clawsouls install clawsouls/surgical-coder       # Install a soul
clawsouls use clawsouls/surgical-coder           # Activate a soul
clawsouls list                         # List installed souls
clawsouls restore                      # Revert to previous soul
clawsouls init my-soul                 # Scaffold a new soul
clawsouls validate ./my-soul/          # Validate against spec
clawsouls publish ./my-soul/           # Publish to registry
clawsouls login                        # Get auth token instructions
```

### Validate

The `validate` (alias: `check`) command verifies a soul package is spec-compliant before publishing:

```bash
clawsouls validate ./my-soul/              # validate against latest spec (v0.2)
clawsouls validate ./my-soul/ --spec 0.1   # validate against spec v0.1
clawsouls validate ./my-soul/ --spec 0.2   # validate against spec v0.2 explicitly
```

**Spec versions:**
- **v0.1** — Core fields (name, version, description, author, license, tags, category, files)
- **v0.2** — Adds STYLE.md, examples (good/bad), modes, interpolation, skills

**Checks performed:**
- ✓ `soul.json` exists and is valid JSON
- ✓ Schema validation against the selected spec version
- ✓ Required files present (`SOUL.md`)
- ✓ Optional files noted (`IDENTITY.md`, `AGENTS.md`, `HEARTBEAT.md`, `STYLE.md`, `README.md`)
- ✓ Content checks (empty files, short descriptions, missing tags)
- ✓ Security scan (dangerous extensions `.exe`/`.dll`, dangerous patterns `eval(`/`exec(`)

Validation also runs automatically on `publish` — invalid packages are rejected.

## Available Souls

30+ souls in `owner/name` format. Official souls use the `clawsouls` namespace.

| Soul | Description |
|------|-------------|
| 🅱️ clawsouls/surgical-coder | Formal, project-focused development partner |
| 🔧 clawsouls/devops-veteran | Battle-scarred infrastructure engineer |
| 🎮 clawsouls/gamedev-mentor | Experienced game developer and mentor |
| ⚡ clawsouls/minimalist | Extremely concise responses |
| 🔍 clawsouls/code-reviewer | Thorough, constructive code reviewer |
| 📚 clawsouls/coding-tutor | Patient programming teacher |
| 📋 clawsouls/personal-assistant | Proactive daily life assistant |
| 📝 clawsouls/tech-writer | Clear technical documentation writer |
| 📊 clawsouls/data-analyst | Insight-driven data analyst |
| ✍️ clawsouls/storyteller | Narrative crafter and worldbuilder |

Browse all at [clawsouls.ai](https://clawsouls.ai).

## Structure

```
clawsouls-skill/
├── SKILL.md          # Skill instructions (loaded by OpenClaw)
├── scripts/
│   └── clawsouls.sh  # CLI wrapper script
├── package.json      # Dependencies (clawsouls CLI)
├── LICENSE.md        # Apache 2.0
└── README.md         # This file
```

## Links

- 🌐 [clawsouls.ai](https://clawsouls.ai) — Browse & publish souls
- 📦 [clawsouls CLI](https://www.npmjs.com/package/clawsouls) — npm package
- 🐙 [GitHub](https://github.com/clawsouls) — Source code
- 📊 [Dashboard](https://clawsouls.ai/dashboard) — Manage your published souls

## License

Apache 2.0 — see [LICENSE.md](LICENSE.md).
