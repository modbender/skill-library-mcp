---
name: create-agent
displayName: Create Agent | Overclaw Skill
description: Creates new Overstory agents for Overclaw by updating all seven integration points (config, manifest, agent-def, gateway prompt, task_router, generate_agent_context, and regeneration). Supports manual creation and optional analysis from logs, TROUBLESHOOTING.md, mulch, and project tree.
version: 1.0.0
---

# Create Agent

Creates and registers new Overstory agents so Overclaw can recognize and use them. Automates the steps documented in [.overstory/CREATING_AGENTS.md](../../.overstory/CREATING_AGENTS.md).

## When to use

- You want to add a new agent type (e.g. troubleshooter, docs-writer) to Overclaw.
- You want to ensure all seven integration points are updated consistently.
- You want to suggest new agents from Overclaw logs, TROUBLESHOOTING.md, mulch, or project structure.

## Scripts

### create_agent.py

Main CLI for creating or validating agents.

**Manual creation:**
```bash
python3 scripts/create_agent.py \
  --name "troubleshooter" \
  --description "Analyzes logs and troubleshoots issues" \
  --capabilities "troubleshoot,debug,analyze" \
  --model "sonnet" \
  --tools "Read,Glob,Grep,Bash" \
  --can-spawn false \
  --constraints "read-only"
```

**Options:** `--dry-run` (preview only), `--no-regenerate` (skip gateway context regeneration), `--rollback-on-fail` (revert changes if validation fails).

**Analysis mode (suggestions only):**
```bash
python3 scripts/create_agent.py \
  --analyze-from-logs \
  --analyze-from-troubleshooting \
  --suggest-only
```

### analyze_agent_needs.py

Helper for analysis mode: parses logs, TROUBLESHOOTING.md, mulch, and project tree to suggest new agent definitions. Can be run standalone or via create_agent.py `--analyze-*`.

## Integration points updated

1. `.overstory/config.yaml` — capability entry
2. `.overstory/agent-manifest.json` — agent + capabilityIndex
3. `.overstory/agent-defs/<name>.md` — agent definition
4. `scripts/overclaw_gateway.py` — orchestrator system prompt
5. `skills/nanobot-overstory-bridge/scripts/task_router.py` — CAPABILITY_PATTERNS
6. `skills/nanobot-overstory-bridge/scripts/generate_agent_context.py` — CAPABILITY_PRIVILEGES
7. Regeneration of gateway-context.md and skills-manifest.json

## References

- [CREATING_AGENTS.md](../../.overstory/CREATING_AGENTS.md) — Step-by-step explainer
- [.overstory/agent-defs/blogger.md](../../.overstory/agent-defs/blogger.md) — Example agent def
- [.overstory/agent-defs/supervisor.md](../../.overstory/agent-defs/supervisor.md) — Example coordinator-style agent
