# ClawHub Skill Publisher

Reliable publish automation for ClawHub skills.

## Value for agents and bot builders

- Ship faster: publish skills with one command.
- Ship safer: run secret and content policy checks before upload.
- Ship consistently: use deterministic CLI flow in local runs and CI.

## Trust and safety design

- Token is read from runtime env or a local env file.
- Token value is never printed to terminal output.
- Publish is blocked when common credential patterns are detected.
- Publish is blocked when CJK characters are detected (unless explicitly allowed).

## Quick start

Single skill publish:

```bash
bash scripts/publish_skill.sh \
  --path "$HOME/.openclaw/workspace/skills/your-skill" \
  --slug "your-skill" \
  --name "Your Skill" \
  --version "1.0.0" \
  --changelog "Initial publish" \
  --tags "latest"
```

Batch sync:

```bash
bash scripts/sync_skills.sh \
  --root "$HOME/.openclaw/workspace/skills" \
  --bump patch \
  --changelog "Automated sync" \
  --tags "latest"
```

## Ideal use cases

- OpenClaw operators who maintain many local skills.
- Agent teams that need repeatable, auditable release steps.
- Builders who want strict preflight policy checks before public upload.
