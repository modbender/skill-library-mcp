# GTM System Setup Report

**Date:** 2026-02-06
**Status:** ✅ Operational

## Executive Summary

I evaluated `chapter-gtm/chapter` and determined it's **NOT suitable** for your needs. Instead, I built a lightweight, custom GTM tracking system that integrates natively with OpenClaw and your existing Telegram bot.

## Chapter-GTM Evaluation

### Why I Rejected It

1. **Development is PAUSED indefinitely** - The maintainers have moved on
2. **Heavy external API dependencies requiring paid subscriptions:**
   - PeopleDataLabs (~$99-500/mo) - contact enrichment
   - PitchBook (enterprise pricing) - funding data  
   - ScraperAPI ($49+/mo) - web scraping
   - OpenAI API costs on top
3. **Complex infrastructure** - Requires PostgreSQL, Redis, Next.js frontend
4. **Overkill** - Designed for sales teams, not founder-led GTM
5. **Risk** - Using abandoned software for business-critical functions

## What I Built Instead

A lightweight, self-contained GTM system that:

### Features
- ✅ **Daily action lists** - "What should I do today?"
- ✅ **Contact/company tracking** with pipeline stages
- ✅ **Follow-up reminders** with due date tracking
- ✅ **Opportunity crawlers** - HN, Reddit, GitHub (expandable)
- ✅ **Keyword-based relevance scoring** - Pre-configured for Bacalhau/Expanso
- ✅ **Telegram integration** via OpenClaw cron jobs
- ✅ **Zero external API costs** - Uses only free APIs

### Architecture
```
┌─────────────────────────────────────────────────────┐
│                  OpenClaw Agent                     │
│  • Natural language queries                         │
│  • Cron-based daily digests                         │
│  • Telegram notifications                           │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│               gtm-system/                           │
│  scripts/gtm.py  - CLI tool (Python, no deps)      │
│  data/gtm.db     - SQLite database                 │
│  SKILL.md        - Agent skill reference           │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Data Sources                       │
│  • Hacker News API (free)                          │
│  • Reddit JSON API (free)                          │
│  • GitHub Search API (free tier)                   │
└─────────────────────────────────────────────────────┘
```

## What's Set Up

### Cron Jobs (Pacific Time)
| Job | Schedule | Purpose |
|-----|----------|---------|
| `gtm-morning-crawl` | 6:00 AM | Crawl HN/Reddit/GitHub for opportunities |
| `gtm-daily-digest` | 8:30 AM | Send daily action digest via Telegram |

### Pre-configured Keywords
The system tracks mentions of:
- **Product:** bacalhau (2.0x weight)
- **Domain:** distributed computing, data orchestration, edge computing, data mesh
- **Tech:** wasm, webassembly, ipfs, filecoin, kubernetes
- **Adjacent:** airflow, dagster, prefect, dbt (competitor awareness)

### Initial Crawl Results
First crawl found **58 signals** including:
- Your own Bacalhau repo (sanity check ✅)
- Ray Project (⭐41k) - competitor/adjacent
- WebAssembly sandboxing projects - relevant tech
- Various data engineering discussions

## How to Use

### Via Telegram (Natural Language)
Just ask your OpenClaw agent:
- *"What's in my pipeline?"*
- *"Any follow-ups due today?"*
- *"Add a contact: John Doe from Acme Corp"*
- *"Check for new opportunities"*

### Via CLI
```bash
cd /home/daaronch/.openclaw/workspace/gtm-system

# Daily workflow
python3 scripts/gtm.py actions          # What to do today
python3 scripts/gtm.py pipeline         # View pipeline
python3 scripts/gtm.py signals          # New opportunities

# Add data
python3 scripts/gtm.py add-contact "Name" "email" --company "Co"
python3 scripts/gtm.py add-opp "Company" --contact 1 --priority 3
python3 scripts/gtm.py remind "Follow up" --opp 1 --date 2026-02-15

# Run crawlers manually
python3 scripts/gtm.py crawl
```

## Resource Usage

- **Disk:** ~200KB (SQLite DB + cache)
- **Memory:** Minimal (Python script, runs and exits)
- **CPU:** Light (crawls take <60s)
- **Network:** Public APIs only, no paid services

Fits easily on your 2vCPU/4GB droplet.

## Future Enhancements (Not Implemented)

These could be added if needed:
1. **Twitter/X crawler** - Monitor mentions and keywords
2. **LinkedIn Sales Nav integration** - If you have a subscription
3. **Email integration** - Auto-log email interactions
4. **Web UI** - Flask dashboard (I can add this if wanted)
5. **AI enrichment** - Use Claude to analyze signals and prioritize

## Files Created

```
/home/daaronch/.openclaw/workspace/gtm-system/
├── README.md           # Documentation
├── SKILL.md            # OpenClaw skill reference
├── SETUP_REPORT.md     # This file
├── scripts/
│   └── gtm.py          # Main CLI tool (750 lines, no dependencies)
└── data/
    └── gtm.db          # SQLite database
```

## Recommendation

**Use this system.** It's:
- Working now (tested, operational)
- Zero ongoing costs
- Integrated with your existing tools
- Easy to extend or modify
- Under your control (no vendor lock-in)

If you need more sophisticated lead enrichment later, consider adding:
- Hunter.io ($49/mo) for email finding
- Clearbit (~$99/mo) for company data
- Or just use manual LinkedIn research

But start with this lean system - it covers the core workflow.
