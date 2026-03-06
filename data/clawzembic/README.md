# 💊 Clawzempic

**Weight Loss for Your OpenClaw Instance**

A Lighthouse-style audit for OpenClaw efficiency. Run it, get a grade (A+ to F), and shed the bloat.

## What It Does

Clawzempic scans your OpenClaw installation and scores it across six critical efficiency categories. Think of it as a health checkup for your AI assistant — identifying wasted tokens, bloated sessions, misconfigured crons, oversized context injection, and opportunities to right-size your models.

You get:
- **One letter grade** (A+ to F) summarizing overall health
- **Category-by-category breakdown** with weighted scoring
- **Actionable findings** — exactly what's bloated and why
- **Optional fix mode** — automated remediation suggestions

## Audit Categories

| Category | Weight | What Gets Flagged |
|----------|--------|-------------------|
| **Context Injection** | 25% | Oversized MEMORY.md, bloated workspace files eating tokens on every session init |
| **Cron Health** | 25% | Wrong models (Opus for routine tasks), high thinking on simple jobs, main-session pollution |
| **Session Bloat** | 20% | Stale sessions hogging context, waste ratio, sessions running at 40%+ capacity |
| **Config Health** | 15% | Heartbeat too frequent, subagent defaults, missing compaction/pruning |
| **Skill Bloat** | 10% | Too many skills injected into system prompt, unused skills |
| **Transcript Size** | 5% | Disk hogs, oversized transcripts (>10MB files) |

## Grade Scale

- **A+/A** (90-100): Lean machine 💪
- **B+/B** (75-89): Good shape, minor tweaks
- **C+/C** (60-74): Needs a diet 🍕
- **D+/D** (45-59): Significant bloat 🫠
- **F** (<45): Emergency Clawzembic needed 💊

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

## Requirements

**Zero external dependencies.** Python 3.8+ stdlib only. Works anywhere OpenClaw runs.

## Installation

**Via ClawHub:**
```bash
clawhub install clawzempic
```

**Manual:**
```bash
cd ~/.openclaw/workspace/skills
git clone https://clawhub.io/skills/clawzempic.git
```

> **Note:** The skill directory is named `clawzembic` (typo during development), but the official ClawHub slug is **`clawzempic`** (correct spelling, like Ozempic). Install via ClawHub to get the correct slug.

## Agent Usage

When Jeffrey asks for an audit or optimization report:

1. Run `bash skills/clawzembic/lean-audit.sh` (or `--remote user@claudette` for the VM)
2. Review the report and present key findings
3. Offer `--fix` mode for automated remediation if score < 75

For remote instances, ensure SSH key-based auth is configured.

## What It Won't Do

Clawzempic is **read-only** by default. It:
- ❌ Won't modify files, sessions, or config (unless you use `--fix` with confirmation)
- ❌ Won't delete transcripts or prune sessions automatically
- ❌ Won't change cron jobs or gateway config

It shows you the problem. You decide the fix.

## Example Output

```
  💊 Clawzembic Audit Report
  ──────────────────────────────────────────────────

  Overall Score: 72/100  Grade: C

  🟠 Context Injection (25% weight) — 65/100 C+
     ⚠ Workspace files total 21,450 bytes (20KB) — could be leaner
     ⚠  MEMORY.md: 12,300 bytes — could be trimmed
     ✓  AGENTS.md: 4,200 bytes

  🟡 Cron Health (25% weight) — 78/100 B
     ℹ Cron jobs: 12 enabled, 3 disabled
     ⚠  [daily-cleanup] uses default model (likely Opus) — consider Sonnet
     ✓  [security-patrol] model=opus thinking=high ✓

  🟠 Session Bloat (20% weight) — 62/100 C
     ℹ Sessions: 8 total, 3 stale/bloated, waste ratio: 35%
     ✗  agent:main:data-sync: 42% (84,000 tokens) — bloated

  ✅ Config Health (15% weight) — 92/100 A
     ✓ Heartbeat every 120m ✓
     ✓ Compaction: safeguard mode ✓

  🟡 Skill Bloat (10% weight) — 77/100 B
     ℹ Skills: 14 custom + 8 built-in = 22 total
     ℹ Estimated system prompt cost: ~3,300 tokens per session

  ✅ Transcript Size (5% weight) — 88/100 B+
     ℹ Transcripts: 47 files, 67.2MB total
     ✓ Transcript storage: 67.2MB — reasonable ✓

  ──────────────────────────────────────────────────
  Needs a diet. Run with --fix for recommendations. 💊
```

## License

MIT License — Copyright 2026 Jeffrey Deming

## ClawHub

Published at [clawhub.io/skills/clawzempic](https://clawhub.io/skills/clawzempic)

---

*Keep your instance lean. Run Clawzempic monthly.*
