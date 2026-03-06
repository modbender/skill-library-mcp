# GTM System Quick Start

## What's Ready Now

✅ **GTM tracking system** - Pipeline, contacts, signals, reminders
✅ **Daily cron jobs** - Morning crawl (6am PT) + digest (8:30am PT)  
✅ **58 signals detected** - Initial crawl of HN/Reddit/GitHub

## Immediate Actions (Do Today - 5 mins each)

### 1. Sign Up for F5Bot (FREE)
- Go to: https://f5bot.com/signup
- Add keywords: `bacalhau`, `expanso`, `compute over data`, `distributed computing`
- You'll get email alerts for Reddit, HN, and Lobsters mentions

### 2. Create Apollo.io Account (FREE)
- Go to: https://www.apollo.io/
- Free tier includes:
  - 10K email credits/month
  - Basic sequences
  - Contact lookup
- Use for contact enrichment when you find prospects

### 3. Test the System
```bash
cd /home/daaronch/.openclaw/workspace/gtm-system

# See today's actions
python3 scripts/gtm.py actions

# View pipeline
python3 scripts/gtm.py pipeline

# List signals from crawl
python3 scripts/gtm.py signals

# Manually trigger a crawl
python3 scripts/gtm.py crawl
```

## Using Via Telegram

Just message your bot naturally:
- "What's my pipeline look like?"
- "Any follow-ups due?"
- "Check for new opportunities"
- "Add contact John Doe from Acme Corp"

## Daily Workflow

**Morning (automatic via Telegram):**
1. Review digest notification (~8:30am PT)
2. Check highlighted signals
3. Prioritize follow-ups

**During the day:**
1. Add contacts as you meet them
2. Log interactions after calls
3. Update opportunity stages

**Commands for common tasks:**
```bash
# Add a contact
python3 scripts/gtm.py add-contact "Name" "email" --company "Co" --role "CTO"

# Create an opportunity
python3 scripts/gtm.py add-opp "Company" --priority 3 --description "Interested in X"

# Log interaction
python3 scripts/gtm.py log "Had demo call" --opp 1

# Move to next stage
python3 scripts/gtm.py move-stage 1 evaluation

# Set follow-up
python3 scripts/gtm.py remind "Send proposal" --opp 1 --date 2026-02-10
```

## Next Week

Consider adding:
- **Syften** ($29/mo) - Better community monitoring with Slack/webhook integration
- **Koala** (free tier) - Website visitor identification

## Files

| File | Purpose |
|------|---------|
| `README.md` | Full documentation |
| `SETUP_REPORT.md` | What was built and why |
| `RESEARCH_GTM_TOOLS.md` | Tool landscape research |
| `SKILL.md` | OpenClaw agent reference |
| `scripts/gtm.py` | Main CLI tool |
| `data/gtm.db` | SQLite database |

## Support

The system is entirely in your workspace. Modify freely:
- Add new keywords: `python3 scripts/gtm.py add-keyword "term" --weight 1.5`
- Extend crawlers: Edit `scripts/gtm.py` 
- Add integrations: It's all Python

Questions? Just ask your agent. I know this system inside and out.
