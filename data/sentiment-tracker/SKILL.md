---
name: Sentiment Tracker
slug: sentiment-tracker
version: 1.0.0
homepage: https://clawic.com/skills/sentiment-tracker
description: Monitor brand sentiment, crypto opinions, and product perception across social media with automated tracking, alerts, and multi-entity dashboards.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

# Sentiment Analysis

Track what people say about anything — brands, crypto, products, competitors — across Twitter/X, Reddit, YouTube, Hacker News, and news sites.

**One-shot analysis** for quick checks. **Scheduled monitoring** for ongoing tracking. **Multi-entity dashboards** to compare multiple things at once.

## Setup

On first use, read `setup.md` and follow its guidelines. Data is stored locally in `~/sentiment-analysis/`.

## When to Use

User wants to know public opinion about something. Could be:
- "What are people saying about [brand]?"
- "How's sentiment on [crypto] right now?"
- "Monitor [product] mentions and alert me on negative spikes"
- "Compare sentiment: [brand A] vs [brand B]"

## Architecture

Data lives in `~/sentiment-analysis/`. See `memory-template.md` for setup.

```
~/sentiment-analysis/
├── memory.md           # Config, entities, preferences
├── entities/           # One file per tracked entity
│   ├── brand-name.md
│   └── crypto-xyz.md
├── reports/            # Generated analysis reports
│   └── YYYY-MM-DD-entity.md
└── alerts.md           # Alert history
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Source Diversity Matters
Never rely on a single platform. Each source has bias:
- **Twitter/X**: Real-time, emotional, viral content
- **Reddit**: Longer discussions, honest opinions, niche communities
- **YouTube**: Comments show product experiences
- **Hacker News**: Tech-focused, skeptical, early adopter views
- **News sites**: Official narratives, PR-filtered

Use at least 2-3 sources per analysis. Note source distribution in reports.

### 2. Time Windows Change Everything
Sentiment shifts fast. Always specify and report time window:
- **Last 24h**: Breaking news, viral events
- **Last 7d**: Weekly trends, sustained campaigns
- **Last 30d**: Product launches, seasonal patterns

Default: Last 7 days unless user specifies otherwise.

### 3. Quantify, Don't Guess
Every report includes concrete metrics:
```
📊 Entity: [Name]
🕐 Period: [Date range]
📈 Volume: [X mentions found]
😊 Positive: XX% | 😠 Negative: XX% | 😐 Neutral: XX%

Top Themes:
1. [Theme] — XX mentions, XX% negative
2. [Theme] — XX mentions, XX% positive

Notable Posts:
- [Quote] — [Platform, engagement]
```

### 4. Alerts Are Specific
Don't alert on every change. Track baselines and alert on:
- Negative spike >20% above baseline
- Viral negative post (>10x normal engagement)
- New negative theme appearing
- Competitor positive spike

### 5. Multi-Entity Comparison
When tracking multiple entities, always show relative performance:
```
📊 Sentiment Comparison (Last 7d)

| Entity | Volume | Positive | Negative | Trend |
|--------|--------|----------|----------|-------|
| Brand A | 1,240 | 62% | 18% | ↗️ +5% |
| Brand B | 890 | 45% | 32% | ↘️ -8% |
```

### 6. Scheduled Monitoring
For ongoing tracking, use cron. Default schedules:
- **Critical entities**: Daily at 09:00
- **Regular entities**: Every 3 days
- **Background entities**: Weekly

Store schedule in memory.md. Deliver reports to user's preferred channel.

### 7. Save Everything
After each analysis:
1. Update entity file with new data
2. Compare to previous analysis
3. Note trend changes
4. Archive raw findings

## Common Traps

- **Single-source analysis** → Completely skewed view. Reddit hates everything, Twitter loves drama. Always cross-reference.
- **No time window** → "Sentiment is positive" means nothing without dates. A product can be loved one week, hated the next.
- **Vanity metrics** → High volume ≠ positive sentiment. 1000 mentions with 80% negative is worse than 100 mentions with 60% positive.
- **Ignoring context** → A spike in "crypto X is dead" might be sarcasm or memes. Read actual posts, not just keyword counts.
- **Alert fatigue** → Alerting on every fluctuation makes users ignore alerts. Only signal meaningful changes.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| Search engines (via web_search) | Query text | Find mentions |
| Social platforms (via web_fetch) | URL requests | Read content |

No API keys required. No data stored externally. All analysis happens locally.

## Security & Privacy

**Data that leaves your machine:**
- Search queries sent to web search (query text only)
- URL requests to public posts (reading only)

**Data that stays local:**
- All entity tracking in ~/sentiment-analysis/
- Historical sentiment data
- Alert configurations

**This skill does NOT:**
- Require accounts on any platform
- Store data on external servers
- Send personal information anywhere
- Access private/protected content

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `analytics` — web traffic and conversion data
- `branding` — brand strategy and guidelines
- `monitor` — system and service monitoring

## Feedback

- If useful: `clawhub star sentiment-tracker`
- Stay updated: `clawhub sync`
