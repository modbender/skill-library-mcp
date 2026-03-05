# GA4 Deep Dive 🏴‍☠️

Comprehensive Google Analytics 4 property analysis — extracts EVERYTHING the API offers.

Built by Claudius for Solvr.

## Features

### Scripts

| Script | Purpose |
|--------|---------|
| `deep_dive_v3.py` | Executive summary with health scores |
| `deep_dive_v4.py` | THE FULL MONTY — everything GA4 can tell you |
| `send_report_email.py` | Email reports via AgentMail |
| `weekly_report.py` | Weekly comparison reports |

### V3 — Executive Summary
- Period comparison (this vs last)
- Health scores (7 dimensions)
- Traffic source analysis
- Content performance
- User segments
- Time patterns

### V4 — The Full Monty
- Scroll depth analysis
- Outbound link tracking
- Site search analysis
- Demographics (with Google Signals)
- Search Console integration
- Cohort retention
- Custom audience performance
- Event deep dive
- Mobile device breakdown

## Setup

```bash
cd ~/development/ga-deep-dive
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Auth (first time)

1. Create OAuth credentials in Google Cloud Console
2. Place `credentials.json` at `~/.config/ga-deep-dive/credentials.json`
3. Run any script — it will prompt for auth

## Usage

```bash
# Quick executive summary
python3 scripts/deep_dive_v3.py solvr

# Full analysis
python3 scripts/deep_dive_v4.py solvr --days 30

# Email report
python3 scripts/send_report_email.py
```

## Cron Setup

Bi-weekly reports (Mon & Thu at 9am São Paulo):
```bash
0 12 * * 1,4 cd ~/development/ga-deep-dive && .venv/bin/python3 scripts/send_report_email.py >> data/cron.log 2>&1
```

## Properties

| Name | Property ID |
|------|-------------|
| solvr | 523300499 |
| abecmed | 291040306 |
| sonus | 517562144 |

---
*Built for owners who want to UNDERSTAND their product, not just see numbers.* 🏴‍☠️
