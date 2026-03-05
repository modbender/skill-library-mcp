# GTM Tracking System for Expanso/Prometheus

## Overview

A lightweight, self-hosted Go-To-Market tracking system designed for founder-driven BD.

## Why NOT Chapter-GTM?

After thorough evaluation of [chapter-gtm/chapter](https://github.com/chapter-gtm/chapter):

1. **Development is PAUSED indefinitely** - Last meaningful commit months ago, maintainers moved on
2. **Heavy external API dependencies** - Requires paid subscriptions to:
   - PeopleDataLabs ($$$) - contact enrichment
   - PitchBook ($$$) - funding data
   - ScraperAPI ($) - web scraping
   - OpenAI - AI features
3. **Complex infrastructure** - PostgreSQL, Redis, Next.js frontend, Python backend
4. **Focused on outbound lead gen** - Not daily task management or founder workflows
5. **Overkill for solo/small team** - Designed for sales teams, not founder-led growth

## Our Solution: OpenClaw-Native GTM

A lightweight system that:
- Uses SQLite (no external DB needed)
- Leverages OpenClaw's existing AI + cron capabilities
- Sends notifications via your existing Telegram bot
- Runs comfortably on this 2vCPU/4GB droplet

## Features

### 1. Daily Action Items
- AI-generated task list each morning
- "What should I do today to move the business forward?"
- Prioritized by opportunity stage and urgency

### 2. Contact/User Tracking
- Track companies and contacts
- Pipeline stages (Awareness → Interest → Evaluation → Closed)
- Interaction history
- Follow-up reminders

### 3. Opportunity Crawling
- Hacker News (Show HN, relevant keywords)
- Reddit (r/dataengineering, r/devops, etc.)
- Twitter/X mentions
- GitHub activity (stars, issues on related repos)
- News (data infrastructure, cloud, etc.)

### 4. Query Interface
- Ask questions via Telegram: "What's in my pipeline?", "Any follow-ups due?"
- Telegram command-based or natural language

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Agent                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  GTM Skills │  │ Cron Jobs    │  │ Telegram Channel  │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                 │                   │
          ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    gtm-system/                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ SQLite DB   │  │ Python CLI   │  │ Crawlers          │  │
│  │ - contacts  │  │ - gtm.py     │  │ - HN, Reddit      │  │
│  │ - opps      │  │ - query      │  │ - GitHub, News    │  │
│  │ - tasks     │  │ - report     │  │                   │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Setup

1. Initialize database: `python3 scripts/gtm.py init`
2. Configure cron jobs (via OpenClaw)
3. Start crawling: `python3 scripts/gtm.py crawl`

## Usage

### CLI Commands
```bash
# View today's action items
python3 gtm.py actions

# Add a contact
python3 gtm.py add-contact "John Doe" "john@company.com" --company "Acme Inc"

# Log an interaction
python3 gtm.py log-interaction <contact_id> "Had intro call, interested in Bacalhau"

# Move opportunity stage
python3 gtm.py move-stage <opp_id> evaluation

# Set follow-up reminder
python3 gtm.py remind <contact_id> "2024-02-15" "Send pricing proposal"

# Get pipeline summary
python3 gtm.py pipeline

# Run crawlers
python3 gtm.py crawl --sources hn,reddit,github
```

### Telegram (via OpenClaw)
Just ask your agent:
- "What's my pipeline looking like?"
- "Any follow-ups due today?"
- "Add a note that I talked to John at Acme"
- "Find opportunities in the data engineering space"

## Files

- `scripts/gtm.py` - Main CLI tool
- `data/gtm.db` - SQLite database
- `data/crawl_cache.json` - Crawler cache (dedup)
- `templates/daily_digest.md` - Daily email/notification template
