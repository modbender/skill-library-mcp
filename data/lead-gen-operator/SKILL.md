---
name: Lead Gen Operator
description: Automated lead generation assistant - finds companies, scores them, writes personalized outreach emails, and tracks pipeline.
metadata:
  {
    "openclaw": { "version": "1.0.0" },
    "version": "1.0.0",
    "price": 19,
    "category": "sales",
    "tags": ["leads", "outreach", "sales", "automation"]
  }
---

# Lead Gen Operator

An automated lead generation assistant that finds companies, scores them based on funding/size/industry, writes personalized outreach emails, and tracks your entire sales pipeline.

## What It Does

- **Find leads** - Add companies with details (name, size, industry, funding)
- **Auto-score** - Scores leads 0-100 based on funding stage, team size, industry
- **Write outreach** - Generates personalized cold emails
- **Track pipeline** - Status flows: new → enriched → drafted → sent → replied → closed
- **Follow-ups** - Get recommendations on who to follow up with
- **Export** - Export leads to CSV

## Setup

1. Copy to your OpenClaw workspace:
```bash
cp -r lead-gen-operator/* ~/.openclaw/workspace/
```

2. The memory-manager tool is pre-configured at:
```
~/.openclaw/workspace/skills/memory-manager/
```

## Commands

```bash
# Add a lead
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js add-lead leads.json "CompanyName" "" "" "11-50" "SaaS" "Series A"

# Score a lead
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js score-lead leads.json "CompanyName"

# Write outreach
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js write-outreach leads.json "CompanyName"

# Get outreach
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js get-outreach leads.json "CompanyName"

# Update status
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js update-status leads.json "CompanyName" "sent"

# View all leads
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js list leads.json

# View stats
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js stats leads.json

# Export to CSV
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js export-csv leads.json

# Follow-ups
node ~/.openclaw/workspace/skills/memory-manager/memory-manager.js get-followups leads.json
```

## Lead Scoring

| Factor | Points |
|--------|--------|
| Series A | +20 |
| Series B | +30 |
| Series C | +40 |
| Unicorn/Billion | +50 |
| 1-10 employees | +10 |
| 11-50 employees | +20 |
| 51-100 employees | +30 |
| 100+ employees | +40 |
| AI/ML industry | +15 |
| Fintech industry | +15 |
| SaaS industry | +10 |

## Status Flow

```
new → enriched → drafted → sent → replied → closed
                      ↓
                    lost
```

## Included Files

- SOUL.md - Agent persona definition
- memory-manager/ - Lead management tool
- SETUP-GUIDE.md - Complete user guide
- README.md - Overview

## Requirements

- OpenClaw installed
- Node.js (for memory-manager)
- Optional: Gmail (for sending emails)

## Support

For issues or questions, reach out through OpenClaw Discord.
