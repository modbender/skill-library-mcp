# HITL Protocol — Agent Skill

The root-level [SKILL.md](../SKILL.md) teaches autonomous agents the HITL Protocol so they can build HITL-compliant services or handle HITL responses.

## Structure

```
SKILL.md                          ← Protocol overview, quick starts, feature matrix
skills/
  README.md                       ← You are here
  references/
    service-integration.md        ← Detailed guide for service/website builders
    agent-integration.md          ← Detailed guide for agent developers
```

Progressive disclosure (per [Agent Skills Standard](https://agentskills.io/specification)):
- **Discovery:** Frontmatter `name` + `description` (~100 tokens)
- **Activation:** Full SKILL.md body loaded when task matches (~1600 words)
- **Execution:** Reference files loaded on demand

## Publishing

### ClawhHub.ai (for OpenClaw and autonomous agents)

```bash
clawhub publish ./SKILL.md \
  --slug hitl-protocol \
  --name "HITL Protocol" \
  --version 0.5.0 \
  --tags "protocol,hitl,human-in-the-loop,agent-ready,http-202"
```

Requires a [ClawhHub.ai](https://clawhub.ai) account (GitHub login).

### Claude Marketplace (for Claude and classical agents)

Submit the SKILL.md via the [Anthropic Skills submission process](https://platform.claude.com/docs/en/agents-and-tools/agent-skills).

### GitHub Discovery

The SKILL.md in the repository root is automatically discoverable by agents that scan GitHub repositories for agent skills (Codex, Copilot, etc.).

## For Services Using HITL

If your service integrates HITL Protocol, declare support in **your own** SKILL.md frontmatter using the `metadata.hitl` extension:

```yaml
---
name: your-service-name
description: "Your service description"
metadata:
  hitl:
    supported: true
    types: [selection, confirmation]
    review_base_url: "https://yourservice.com/review"
    timeout_default: "24h"
    info: "May ask user to select items or confirm actions."
---
```

See [spec Section 12](../spec/v0.5/hitl-protocol.md) for the full `metadata.hitl` field reference.
