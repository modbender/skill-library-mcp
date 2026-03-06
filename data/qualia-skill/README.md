# Qualia Agent Skill 🤖🦾

Make **robotics training** a skill for your AI agent. This skill lets any agent fine-tune robotic foundation models on [Qualia](https://qualiastudios.dev) — launch training jobs, monitor progress, iterate on parameters, and build full pipelines from conversation.

## What can your agent do with this?

- Fine-tune robotic foundation models (ACT, SmolVLA, π0, π0.5, GR00T N1.5, and more)
- Monitor training progress in real-time
- Iterate on hyperparameters and reward functions
- Build full training pipelines from conversation
- Use Reward-Aware Behavior Cloning (RA-BC) with SARM reward models

## Supported Models

| Type | Description |
|------|-------------|
| `act` | Action Chunking Transformer — fast, lightweight |
| `smolvla` | SmolVLA — efficient open-source model |
| `pi0` | π0 — Physical Intelligence foundation model |
| `pi05` | π0.5 — dexterous manipulation variant |
| `gr00t_n1_5` | GR00T N1.5 — NVIDIA humanoid foundation model |
| `sarm` | SARM — reward model for RA-BC |

More models coming soon.

## Setup

1. Get a Qualia API key from the [Qualia app](https://app.qualiastudios.dev/)
2. Set the environment variable:
   ```bash
   export QUALIA_API_KEY="your-api-key"
   ```

### OpenClaw

Copy this skill to your workspace:
```bash
cp -r qualia-agent-skill ~/.openclaw/workspace/skills/qualia
```

Or install via ClawHub (coming soon):
```bash
clawhub install qualia
```

Then add `"qualia"` to your agent's skills list in `openclaw.json`.

### Claude Code / Other Agents

The `SKILL.md` file is a self-contained instruction set. Drop it into any agent's context that supports tool use and shell access.

## How it works

The skill provides a bash script (`scripts/qualia.sh`) that wraps the Qualia API. Your agent reads `SKILL.md` to understand the available commands and uses them to manage training jobs.

Example flow:
1. Agent checks available models → `qualia.sh models`
2. Inspects dataset image keys → `qualia.sh dataset-keys org/dataset`
3. Creates a project → `qualia.sh project-create "My Robot"`
4. Launches training → `qualia.sh finetune ...`
5. Monitors progress → `qualia.sh status <job_id>`
6. Adjusts and retrains as needed

## Requirements

- `curl` and `jq` (standard on most systems)
- A Qualia API key with credits

## Links

- [Qualia](https://qualiastudios.dev)
- [OpenClaw](https://github.com/openclaw/openclaw)
- [ClawHub](https://clawhub.ai)

## License

MIT
