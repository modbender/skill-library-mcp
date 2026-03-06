# tokenmeter - Quick Reference

## Installation

```bash
cd ~/clawd/skills/tokenmeter
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Daily Commands

```bash
# Activate environment (always do this first!)
cd ~/clawd/tokenmeter && source .venv/bin/activate

# Discover session sources
tokenmeter scan

# Import all sessions
tokenmeter import --auto

# Preview import (no writes)
tokenmeter import --auto --dry-run

# Quick dashboard
tokenmeter dashboard

# Today's usage
tokenmeter summary

# This week
tokenmeter summary --period week

# This month (for billing comparison)
tokenmeter costs --period month
```

## Logging Usage Manually

```bash
tokenmeter log \
  -p anthropic \
  -m claude-sonnet-4 \
  -i 1500 \
  -o 500 \
  -a openclaw
```

## Model Pricing (Feb 2026)

| Model | Input/1M | Output/1M |
|-------|----------|-----------|
| claude-sonnet-4 | $3 | $15 |
| claude-opus-4 | $15 | $75 |
| claude-3.5-haiku | $0.80 | $4 |

## Max Plan Comparison

```bash
# Show monthly costs
tokenmeter costs --period month

# Compare "Total" to your $100 Max plan
# If Total > $100: You're saving money ✅
# If Total < $100: Consider downgrading (or enjoy peace of mind!)
```

## Import from OpenClaw & Claude Code

```bash
# Discover all session sources
tokenmeter scan

# Import everything
tokenmeter import --auto

# Or import specific directory
tokenmeter import --path ~/.clawdbot/agents/main/sessions/
```

## Database Location

```bash
~/.tokenmeter/usage.db
```

View directly:
```bash
sqlite3 ~/.tokenmeter/usage.db "SELECT * FROM usage ORDER BY timestamp DESC LIMIT 10;"
```

## Troubleshooting

**Command not found?**
```bash
cd ~/clawd/skills/tokenmeter && source .venv/bin/activate
```

**Empty dashboard?**
- Check if session files exist: `ls ~/.clawdbot/agents/*/sessions/*.jsonl`
- Run import: `tokenmeter import --auto`
- Or log manually: `tokenmeter log ...`

---

For detailed usage, see [SKILL.md](./SKILL.md)
