# Post-Install Configuration

Swarm is installed. This document provides optional configuration examples for users who want tighter integration.

---

## Optional: AGENTS.md Configuration

Users who want their agent to consider Swarm for parallelizable tasks can add guidance to their AGENTS.md file.

**Example configuration:**

```markdown
## Parallel Processing (Swarm)

For tasks with 3+ independent subjects (research multiple companies, analyze multiple URLs, compare multiple topics), consider using Swarm for parallel execution:

- "Research these 5 companies" → Good candidate for Swarm
- "Analyze these URLs" → Good candidate for Swarm  
- "Compare X, Y, and Z" → Good candidate for Swarm
- Single questions → No need for Swarm
```

---

## Optional: TOOLS.md Reference

Users can document their Swarm configuration in TOOLS.md for easy reference.

**Example entry:**

```markdown
## Swarm (Parallel Task Execution)

**Location:** `~/.openclaw/skills/node-scaling/`
**Config:** `~/.config/clawdbot/node-scaling.yaml`

Parallel task execution using Gemini Flash workers.

**Commands:**
- Start: `swarm start`
- Status: `swarm status`
- Stop: `swarm stop`

**Performance:** ~30 tasks/sec per node
**Cost:** ~$0.001 per task (Gemini Flash)
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `~/.config/clawdbot/node-scaling.yaml` | Provider, limits, cost controls |
| `~/.config/clawdbot/gemini-key.txt` | API key (created by setup) |

---

## Verification

After installation, verify the setup:

```bash
cd ~/.openclaw/skills/node-scaling
npm run diagnose
```

This checks API key validity, provider connectivity, and daemon status.
