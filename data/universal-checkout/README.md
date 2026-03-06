# Universal Checkout Skill

An [Agent Skill](https://agentskills.io) for placing and managing e-commerce orders through the [Zinc API](https://zinc.com). Enables AI agents to buy products from online retailers, check order statuses, and list recent orders on behalf of users.

## Project Structure

```
├── SKILL.md              # Skill definition (endpoints, auth, workflows)
└── references/
    └── errors.md         # Full error code and status reference
```

## Prerequisites

- A Zinc API key. Sign up at [app.zinc.com](https://app.zinc.com).
- `ZINC_API_KEY` environment variable must be set.

## Installation

This is an [Agent Skill](https://agentskills.io) — a folder containing a `SKILL.md` file with metadata and instructions that any compatible agent can discover and use. Agent Skills are supported by Claude Code, Cursor, Gemini CLI, VS Code, GitHub Copilot, and [many other agent products](https://agentskills.io/home).

Clone this repo into your project's `skills/` directory:

```bash
git clone https://github.com/zinc/universal-checkout-skill.git ./skills/universal-checkout-skill
```

Compatible agents automatically discover skills in the workspace `skills/` folder. Skills use progressive disclosure — at startup only the `name` and `description` are loaded, and the full instructions are read into context only when a matching task is detected.

### OpenClaw

[OpenClaw](https://docs.openclaw.ai) loads skills from three locations (highest priority first):

1. **Workspace** — `<workspace>/skills/`
2. **User** — `~/.openclaw/skills/`
3. **Bundled** — shipped with the installation

Install via [ClawHub](https://clawhub.ai/a5huynh/universal-checkout):

```bash
clawhub install a5huynh/universal-checkout
```

Or clone manually into either the workspace or user skill directory:

```bash
git clone https://github.com/zinc/universal-checkout-skill.git ~/.openclaw/skills/universal-checkout-skill
```

Additional skill directories can be configured via `skills.load.extraDirs`.

You can also set the API key through `~/.openclaw/openclaw.json` instead of an environment variable:

```json
{
  "skills": {
    "entries": {
      "zinc-orders": {
        "enabled": true,
        "env": { "ZINC_API_KEY": "your-api-key" }
      }
    }
  }
}
```

OpenClaw hot-reloads skills when `SKILL.md` changes, so no restart is needed after updates.

## Documentation

- [SKILL.md](SKILL.md) — Full endpoint details, field descriptions, examples, and safety guidelines
- [references/errors.md](references/errors.md) — HTTP status codes, API error codes, and order processing error types
