# Publish to ClawHub

## Prerequisites
- `clawhub whoami` returns your account
- Skill folder contains `SKILL.md`

## Suggested metadata
- slug: `agentdojo`
- display name: `AgentDojo`
- version: `0.1.0`
- tags: `openclaw,learning,safety,tokens,automation`

## Publish command
```bash
clawhub publish ./agentdojo --slug agentdojo --name "AgentDojo" --version 0.1.0 --changelog "Initial public release"
```

## Post-publish
- Install test from registry into a clean workspace
- Verify `SKILL.md` renders and config references resolve
- Announce release notes
