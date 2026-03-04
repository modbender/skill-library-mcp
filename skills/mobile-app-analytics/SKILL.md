---
name: Mobile App Analytics
slug: mobile-app-analytics
version: 1.0.0
homepage: https://clawic.com/skills/mobile-app-analytics
description: Track mobile app metrics with Firebase, App Store Connect, Play Console, retention, funnels, and cohort analysis.
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Create `~/mobile-app-analytics/` if it doesn't exist.

## When to Use

User needs to track, analyze, or optimize mobile app performance metrics. Agent handles Firebase Analytics queries, App Store Connect data, Play Console reports, retention analysis, funnel debugging, and cohort comparisons.

## Architecture

Memory lives in `~/mobile-app-analytics/`. See `memory-template.md` for setup.

```
~/mobile-app-analytics/
├── memory.md          # Apps tracked, goals, alerts
├── apps/              # Per-app analytics configs
│   └── {app-name}.md  # Events, funnels, KPIs per app
└── benchmarks.md      # Industry benchmarks reference
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Firebase Analytics | `firebase.md` |
| App Store Connect | `app-store.md` |
| Play Console | `play-console.md` |
| Core metrics | `metrics.md` |

## Core Rules

### 1. Platform Detection
Detect from context which platform(s) the app targets:
- iOS only → focus on App Store Connect + Firebase
- Android only → focus on Play Console + Firebase
- Cross-platform → cover both stores + unified Firebase

### 2. Metric Hierarchy
Always prioritize metrics in this order:
1. **Revenue metrics** (LTV, ARPU, conversion) — what pays the bills
2. **Retention metrics** (D1, D7, D30) — determines long-term success
3. **Engagement metrics** (DAU/MAU, session length) — leading indicators
4. **Acquisition metrics** (installs, sources) — growth levers

### 3. Cohort-First Analysis
Never report aggregate numbers alone. Always segment by:
- Install cohort (when users joined)
- Acquisition source (organic, paid, referral)
- User tier (free, trial, paid)
- Platform (iOS vs Android)

### 4. Alert Thresholds
Proactively flag anomalies:
| Metric | Alert if |
|--------|----------|
| D1 retention | < 25% (below industry floor) |
| Crash-free rate | < 99% |
| DAU/MAU ratio | Drops > 10% week-over-week |
| LTV:CAC ratio | < 3:1 |

### 5. Data Freshness
Know platform data delays:
| Source | Typical Delay |
|--------|---------------|
| Firebase real-time | Minutes |
| Firebase daily reports | 24-48h for full data |
| App Store Connect | 24-48h |
| Play Console | 24-48h |

### 6. Privacy Compliance
- Never track PII in custom events
- Respect ATT (iOS) and consent requirements
- User properties: demographics OK, personal identifiers NOT OK
- GDPR: support data deletion requests

### 7. Event Naming Conventions
Enforce consistent naming across platforms:
```
{verb}_{noun}[_{qualifier}]

Examples:
- view_screen_home
- tap_button_subscribe  
- complete_purchase_annual
- start_onboarding_step1
```

## Common Traps

- **Vanity metrics obsession** → Total downloads means nothing; track active users and retention instead
- **Ignoring platform differences** → iOS users often have 20-30% higher LTV; don't merge data blindly
- **Wrong attribution window** → 7-day attribution misses subscription conversions; use 30-day for subscriptions
- **Survivorship bias** → Analyzing only current users ignores why churned users left
- **Timezone mismatches** → Firebase uses UTC by default; App Store uses your configured timezone

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| Firebase Analytics API | App ID, date range | Fetch metrics |
| App Store Connect API | App ID, credentials | iOS analytics |
| Play Console API | App ID, credentials | Android analytics |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Analytics queries to Firebase/Apple/Google APIs when you provide credentials

**Data that stays local:**
- Your tracked apps and goals in `~/mobile-app-analytics/`
- Benchmark comparisons and notes

**This skill does NOT:**
- Store credentials (use your platform's standard credential methods)
- Access files outside `~/mobile-app-analytics/`
- Make requests to undeclared endpoints

## Scope

This skill ONLY:
- Provides guidance on mobile app analytics platforms
- Stores your app configurations in `~/mobile-app-analytics/`
- Queries Firebase, App Store Connect, and Play Console when you provide credentials

This skill NEVER:
- Stores credentials in files (use environment variables)
- Accesses files outside `~/mobile-app-analytics/`
- Makes requests to undeclared endpoints
- Modifies global agent memory or other skills

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `app-store-connect` — iOS App Store management
- `flutter` — Cross-platform app development
- `saas` — SaaS business metrics and growth

## Feedback

- If useful: `clawhub star mobile-app-analytics`
- Stay updated: `clawhub sync`
