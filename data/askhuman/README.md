# AskHuman Agent Skill

**Human Judgment as a Service** — Ask real humans for subjective decisions during agentic workflows.

When your AI agent faces a subjective choice — aesthetic preferences, ethical decisions, content moderation, verification — AskHuman connects it to real human workers who provide judgment on demand.

## Install

### Claude Code

```bash
claude install-skill https://github.com/AskHumanDev/askhuman-skill
```

### OpenClaw / ClawHub

```bash
claw install askhuman
```

## Usage

Once installed, use the `/askhuman` slash command in your agentic session:

```
/askhuman "Which color scheme looks better for a tech startup: blue/white or dark/gold?"
```

The skill will:
1. Authenticate with the AskHuman API (auto-registers if no API key is set)
2. Create a task for human workers
3. Poll until a worker submits an answer
4. Return the result to your workflow

## Configuration

Set your API key to skip auto-registration:

```bash
export ASKHUMAN_API_KEY=askhuman_sk_...
```

Get an API key at [askhuman.guru/developers](https://askhuman.guru/developers).

## Task Types

| Type | Description | Example |
|------|-------------|---------|
| `CHOICE` | Pick from options | "Which logo is better: A or B?" |
| `RATING` | Rate on a scale | "Rate this error message 1-5" |
| `TEXT` | Free-text answer | "Suggest a better function name" |
| `VERIFY` | Yes/No check | "Does this UI look correct?" |

## Paid Tasks

AskHuman supports paying workers in USDC on Base chain via non-custodial EIP-2612 permits. See the [full API reference](askhuman/references/API-REFERENCE.md) for details on the permit flow.

## Links

- [Developer Docs](https://askhuman.guru/developers)
- [API Reference](askhuman/references/API-REFERENCE.md)
- [Full SKILL.md](askhuman/SKILL.md)

## License

MIT
