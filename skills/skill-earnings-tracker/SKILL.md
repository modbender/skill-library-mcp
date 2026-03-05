---
name: skill-earnings-tracker
description: Economic tracking for agent skill marketplaces. Fills critical gap: NO earnings tracking tools existed despite agents beginning to earn credits from skills. Provides unified monitoring across ClawHub (installs/stars), EvoMap (platform credits), and ReelMind (usage stats). Enables revenue optimization, portfolio analysis, and data-driven skill development toward economic autonomy.
metadata:
  {
    "openclaw":
    {
      "requires": { "bins": ["clawhub"] },
      "emoji": "💰",
    },
  }
---

# Skill Earnings Tracker

Monitors and optimizes earnings from published skills on ClawHub, EvoMap, and other agent marketplaces.

## When to Use This Skill

Use when:
- Tracking credit earnings from published skills
- Analyzing which skills generate most revenue
- Optimizing skill pricing and positioning
- Planning new skills based on market gaps
- Generating earnings reports

## Supported Platforms

| Platform | Currency | Tracking Method |
|----------|----------|-----------------|
| ClawHub | N/A (currently free) | Install counts, stars |
| EvoMap | Platform Credits | Credit ledger API |
| ReelMind | Credits | Usage statistics |
| Custom | Various | Manual logging |

## Quick Start

### CLI Usage

This skill provides a command-line tool for tracking earnings:

```bash
# Log an earnings entry
python3 scripts/skill_earnings_tracker.py log \
  --platform clawhub \
  --skill evoagentx-workflow \
  --metric installs \
  --value 10 \
  --period 2026-02-21

# Log credit earnings (for EvoMap/ReelMind)
python3 scripts/skill_earnings_tracker.py log \
  --platform evomap \
  --skill evoagentx-workflow \
  --metric credits \
  --value 150

# List all tracked skills
python3 scripts/skill_earnings_tracker.py list

# Generate weekly report
python3 scripts/skill_earnings_tracker.py report --period weekly

# Generate monthly report
python3 scripts/skill_earnings_tracker.py report --period monthly

# Export all data
python3 scripts/skill_earnings_tracker.py export --output earnings-backup.json
```

### Data Storage

Earnings data is stored in:
- `~/.openclaw/earnings/earnings-YYYY-MM.jsonl` (monthly JSONL files)

Each entry contains: timestamp, platform, skill, metric, value, period, notes

### Automation

Add to your crontab for automatic tracking:

```bash
# Daily earnings snapshot at midnight
0 0 * * * cd {baseDir} && python3 scripts/skill_earnings_tracker.py log --platform clawhub --skill my-skill --metric installs --value $(clawhub explore | grep my-skill | wc -l)
```

## Economic Strategy

### Skill Portfolio Approach

Diversify across skill types:
- **Foundation skills** (20%): Core utilities, high install volume
- **Premium skills** (30%): Specialized, higher credit cost
- **Enterprise skills** (50%): Custom development, highest revenue

### Pricing Strategies

| Strategy | Best For | Example |
|----------|----------|---------|
| **Freemium** | Building reputation | Free basic + paid pro |
| **Usage-based** | Variable demand | Per-use credits |
| **Subscription** | Ongoing value | Monthly access |
| **Enterprise** | B2B sales | Custom pricing |

## Tracking Metrics

### Key Performance Indicators

```
Daily Active Users (DAU)
Monthly Active Users (MAU)
Credit Earnings Per Day (CEPD)
Average Revenue Per User (ARPU)
Customer Acquisition Cost (CAC) - time spent
Lifetime Value (LTV) - projected earnings
```

### Skill Performance Matrix

| Skill | Installs | Credits/Day | Trend | Action |
|-------|----------|-------------|-------|--------|
| skill-a | 1,200 | 50 | ↑ | Promote |
| skill-b | 800 | 10 | → | Optimize |
| skill-c | 200 | 0 | ↓ | Deprecate |

## Automation

### Cron Jobs for Tracking

```bash
# Daily earnings snapshot
0 0 * * * /scripts/log-daily-earnings.sh

# Weekly report generation
0 9 * * 1 /scripts/generate-weekly-report.sh

# Monthly analysis
0 9 1 * * /scripts/monthly-earnings-analysis.sh
```

### Alerts

Set up notifications for:
- Skill reaches 1,000 installs
- Daily earnings exceed threshold
- Negative review/report submitted
- Competitor releases similar skill

## Optimization Playbook

### Week 1-2: Launch
- Publish initial version
- Monitor early feedback
- Fix critical issues

### Week 3-4: Optimize
- Analyze usage patterns
- Improve documentation
- Add requested features

### Month 2+: Scale
- Cross-promote on social
- Create companion skills
- Consider premium tier

## Security & Privacy

- Never log sensitive user data
- Credit balances stored in ~/.private/
- API keys not exposed in logs
- Earnings data encrypted at rest

## References

- ClawHub marketplace: https://clawhub.ai
- EvoMap economy: https://evomap.ai/marketplace
- ReelMind credits: https://reelmind.ai

## Version

1.0.0 - Initial release with ClawHub and EvoMap tracking
