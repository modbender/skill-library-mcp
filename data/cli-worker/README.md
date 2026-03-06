# CLI Worker Skill (Kimi CLI)

> Delegates coding tasks to Kimi CLI agents in isolated git worktrees

## Provenance

- **Repository**: https://github.com/quratus/openclaw_cli_agent_skill
- **NPM Package**: @sqncr/openclaw-cli-agent-skill
- **License**: MIT
- **Version**: 0.1.0

## Security

This skill is open source. You can audit the code at:
https://github.com/quratus/openclaw_cli_agent_skill

The skill delegates to Kimi CLI (`kimi-cli`), which is an official product from Kimi (Moonshot AI).

## Installation

For the CLI tool (required):
```bash
# Install from npm:
npm install -g @sqncr/openclaw-cli-agent-skill

# Or build from source:
git clone https://github.com/quratus/openclaw_cli_agent_skill.git
cd openclaw_cli_agent_skill
npm install && npm run build && npm link
```

For the OpenClaw skill:
```bash
# Install from ClawHub:
clawhub install cli-worker
```
