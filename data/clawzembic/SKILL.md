---
name: clawzembic
description: Lighthouse-style efficiency audit for OpenClaw. Scores your instance A+ to F across 6 categories (context injection, cron health, session bloat, config, skills, transcripts). Identifies wasted tokens, bloated sessions, misconfigured crons, and model right-sizing opportunities. Zero dependencies (Python stdlib only).
metadata:
  openclaw:
    emoji: "💊"
    requires:
      anyBins: ["python3"]
    tags:
      - audit
      - optimization
      - efficiency
      - diagnostics
      - performance
---

# Clawzembic — Weight Loss for Your OpenClaw Instance

**Lighthouse-style audit for OpenClaw efficiency.** Run it, get a grade (A+ to F), shed the bloat.

Scans your installation and scores it across six critical categories: context injection, cron health, session bloat, config health, skill bloat, and transcript size. You get one overall letter grade plus category-by-category breakdown with actionable findings.

**Zero dependencies.** Python 3.8+ stdlib only.

## Quick Start

```bash
# Audit this machine
bash skills/clawzembic/lean-audit.sh

# Audit a remote instance (VM, etc.)
bash skills/clawzembic/lean-audit.sh --remote user@host

# JSON output for dashboards/integrations
bash skills/clawzembic/lean-audit.sh --json

# Show automated fix suggestions
bash skills/clawzembic/lean-audit.sh --fix

# Custom .openclaw directory
bash skills/clawzembic/lean-audit.sh --dir /path/to/.openclaw
```

## What It Checks

| Category | Weight | What Gets Flagged |
|----------|--------|-------------------|
| Context Injection | 25% | Oversized MEMORY.md, bloated workspace files eating tokens |
| Cron Health | 25% | Wrong models, high thinking on routine tasks, main-session pollution |
| Session Bloat | 20% | Stale sessions hogging context, waste ratio above 35% |
| Config Health | 15% | Heartbeat too frequent, subagent defaults, missing compaction |
| Skill Bloat | 10% | Too many skills injected, unused skills inflating system prompt |
| Transcript Size | 5% | Disk hogs, oversized transcripts (>10MB files) |

## Grade Scale

- **A+/A** (90-100): Lean machine 💪
- **B+/B** (75-89): Good shape, minor tweaks
- **C+/C** (60-74): Needs a diet 🍕
- **D+/D** (45-59): Significant bloat 🫠
- **F** (<45): Emergency Clawzembic needed 💊

## Agent Usage

When Jeffrey asks you to audit or optimize an OpenClaw instance:

1. Run `bash skills/clawzembic/lean-audit.sh` (or `--remote user@claudette` for the VM)
2. Review the report and present key findings with context
3. Offer `--fix` mode for automated remediation if score < 75

For remote instances, ensure SSH key-based auth is configured. The skill uses SSH to execute the audit remotely — no agent installation needed on the target.
