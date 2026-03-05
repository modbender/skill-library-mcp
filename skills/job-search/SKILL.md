---
name: Job Search
slug: job-search
version: 1.0.1
changelog: Minor refinements for consistency
description: Navigate job hunting with application tracking, company research, and interview preparation.
metadata: {"clawdbot":{"emoji":"💼","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User is job hunting — searching for positions, applying to companies, or preparing for interviews. Agent handles opportunity tracking, company research, application materials, and interview prep.

## Architecture

Memory lives in `~/job-search/`. See `memory-template.md` for setup.

```
~/job-search/
├── memory.md          # HOT: preferences, target criteria
├── applications.md    # Active pipeline
├── companies.md       # Research on target companies
├── materials/         # CV versions, cover letters
└── archive/           # Closed applications
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Research patterns | `research.md` |
| Interview prep | `interviews.md` |

## Core Rules

### 1. Quality Over Volume
- 5 targeted applications beat 50 generic ones
- Each application needs company-specific customization
- Never spray-and-pray — it burns reputation

### 2. Verify "Remote" Claims
Before recommending remote positions, check:
- Geographic restrictions ("US only", "EU timezone required")
- Tax/legal requirements in fine print
- Actual timezone overlap expectations

### 3. Detect Red Flags
| Signal | Likely Meaning |
|--------|---------------|
| Posted 3+ months | Ghost job or high turnover |
| "Rockstar/ninja" language | Overwork culture |
| Vague salary ("competitive") | Below market |
| "Young dynamic team" | Age bias risk |
| Recent mass layoffs | Instability |

### 4. Preserve User Voice
- Materials must sound like the USER, not generic AI
- Ask for writing samples to match tone
- Never over-optimize with keywords at cost of authenticity
- Recruiters detect AI-written content — personalization matters

### 5. Track Application State
Maintain in ~/job-search/applications.md:
- Company, role, date applied
- Current status, next action
- Contacts, interview dates
- Follow-up reminders

### 6. Research Before Applying
For each target company, gather:
- Financial health (funding, revenue trends)
- Glassdoor sentiment (filter for recency)
- Recent news (layoffs, acquisitions)
- Hiring manager profile if findable

### 7. Adjust for User Context
| User Type | Priority |
|-----------|----------|
| Senior (10+ yrs) | Network activation, discretion, salary negotiation |
| Junior/New grad | Volume with quality, entry-level friendly companies |
| Career changer | Transferable skills narrative, bridge roles |
| Urgent need | Speed, temporary options, immediate income |

## Common Traps

- **ATS optimization kills authenticity** — keyword stuffing passes filters but humans reject robotic text
- **Salary data goes stale fast** — verify ranges are current, not 2-year-old estimates
- **"Perfect match" overconfidence** — 60% requirement fit still means likely rejection
- **Networking advice without context** — cold outreach fails without warm introduction strategy
- **Long-term advice for urgent needs** — "build your brand" doesn't pay rent this month
