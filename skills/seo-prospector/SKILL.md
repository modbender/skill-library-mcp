---
name: seo-prospector
description: >-
  Automated SEO prospect research and outreach for web designers, agencies, and freelancers.
  Use when researching local business prospects, running scheduled prospect clusters,
  creating outreach packages, generating daily summaries, or managing a lead pipeline.
  Triggers on "research prospect", "find leads", "prospect report", "outreach for [business]",
  "run today's clusters", "daily prospect summary", "batch research", "generate outreach",
  "SEO audit prospect", "local business leads", "cold outreach", "lead pipeline".
license: Proprietary. See LICENSE.txt for complete terms.
---

# SEO Prospector

Automated local business lead generation for web designers and agencies.

Pipeline: discover → research → audit → report → outreach → track.

## How It Works

This skill turns you into a prospecting machine. Point it at a city or industry, and it:

1. Finds businesses with weak websites (via SEO audit + web research)
2. Generates detailed prospect reports with specific issues found
3. Creates personalized outreach (HTML emails, LinkedIn messages, DMs)
4. Tracks everything in a database with dedup + cluster rotation
5. Delivers daily summaries of your pipeline health

## Setup (First Run)

Before using, configure your agency details:

```bash
# Copy and edit the config file
cp references/config-template.json ~/.openclaw/workspace/leads/data/seo-prospector-config.json
```

Edit the config with your info:
```json
{
  "agency": {
    "name": "Your Agency Name",
    "owner": "Your Name",
    "phone": "(555) 123-4567",
    "email": "you@agency.com",
    "website": "youragency.com",
    "city": "Your City",
    "tagline": "Your one-liner value prop"
  },
  "outreach": {
    "default_tone": "casual",
    "signature_style": "friendly"
  }
}
```

## Quick Reference

### Research One Prospect
```bash
python3 scripts/research_prospect.py \
  --business "Business Name" --domain "example.com" --industry "Restaurant" \
  --priority HIGH --cluster "Restaurants"
```

### Batch Research (Today's Rotation)
```bash
python3 scripts/batch_research.py --run morning    # Today's run_1 cluster
python3 scripts/batch_research.py --run afternoon   # Today's run_2 cluster
python3 scripts/batch_research.py --cluster "Restaurants" --limit 5
```

### Generate Outreach
```bash
python3 scripts/create_outreach.py --report path/to/report.md --template casual
python3 scripts/create_outreach.py --business "Name" --template professional --format html
```

### Daily Summary
```bash
python3 scripts/daily_summary.py                     # Today, Discord format
python3 scripts/daily_summary.py --date 2026-02-09 --format markdown
```

### Pipeline Management
```bash
python3 scripts/prospect_tracker.py today-clusters
python3 scripts/prospect_tracker.py check --business "Name"
python3 scripts/prospect_tracker.py stats
python3 scripts/prospect_tracker.py outreach-ready
```

## Workflow

### 1. Check Schedule & Dedup
- Run `prospect_tracker.py today-clusters` to see scheduled clusters
- Run `prospect_tracker.py check --business "Name"` before researching (14-day dedup window)

### 2. Research Phase
Data sources in priority order:
1. **SEO Quick Audit** (`seo_quick_audit.py`) — on-page technical analysis
2. **Perplexity Search** (`perplexity_search.py`) — business intel, reviews, reputation
3. **Browser verification** (optional) — visual check for high-priority prospects

### 3. Report Generation
Reports follow `references/research-template.md`. Key sections:
- Executive Summary (specific findings, not generic)
- Business Overview (what they do, how long, reviews)
- Online Presence Analysis (SEO audit results with pass/fail)
- Why [Your Agency] (pitch angle customized to their gaps)
- Contact & Next Steps (confidence level + recommended action)

Output: `~/.openclaw/workspace/leads/prospects/YYYY-MM-DD-{cluster}/{business}.md`

### 4. Outreach Generation
`scripts/create_outreach.py` supports:
- **HTML emails** (professional, mobile-responsive, branded)
- **Plain text emails** (casual, no-frills)
- **LinkedIn messages** (see `references/outreach-templates.md`)
- **DMs** (Instagram, Facebook, SMS — see `assets/templates/dm-outreach.md`)

Each outreach package includes:
- Email draft (HTML or plain text)
- Review checklist for manual QA
- Tracking JSON for pipeline status

### 5. Pipeline Tracking
Every prospect gets tracked via `prospect_tracker.py add`. The database enables dedup, coverage stats, cluster tracking, and outreach status.

Status pipeline: `draft_ready → pending_review → approved → sent → followed_up → responded → closed`

## Priority Scoring (Strict)

Aim for ~30% HIGH, ~50% MEDIUM, ~20% LOW:
- **HIGH**: No website OR completely broken site, AND business confirmed active
- **MEDIUM**: Has website but major SEO gaps (no H1, no meta, no schema, bad mobile), AND confirmed active
- **LOW**: Decent website with minor issues, OR business activity unconfirmed

If unsure, default to MEDIUM.

## Verification (Mandatory)

Before recording any prospect, verify:
```bash
python3 scripts/verify_prospect.py <report_path>
```
Skip prospects with: dead URLs, parked domains, suspended hosting, permanently closed businesses.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/research_prospect.py` | Full pipeline for single prospect |
| `scripts/batch_research.py` | Research multiple prospects from cluster or input |
| `scripts/create_outreach.py` | Generate personalized outreach (HTML + plain text) |
| `scripts/generate_outreach_batch.py` | Batch outreach for all prospects from a date |
| `scripts/daily_summary.py` | Pipeline summary (Discord or markdown) |
| `scripts/prospect_tracker.py` | Database, dedup, cluster rotation, stats |
| `scripts/verify_prospect.py` | URL/domain/phone verification |
| `scripts/seo_quick_audit.py` | On-page SEO technical audit |

## References

| File | Use When |
|------|----------|
| `references/research-template.md` | Writing or reviewing prospect reports |
| `references/outreach-templates.md` | Drafting email/LinkedIn/DM outreach |
| `references/industry-insights.md` | Industry-specific talking points |
| `references/objection-handling.md` | Handling "we already have a site" etc. |
| `references/config-template.json` | First-time setup of agency details |
| `references/cluster-template.json` | Setting up industry cluster rotation |

## Assets

- `assets/templates/email-html.html` — Professional HTML email template with merge fields
- `assets/templates/email-plain.txt` — Plain text email template
- `assets/templates/linkedin-message.md` — LinkedIn outreach templates
- `assets/templates/dm-outreach.md` — DM templates (SMS, IG, FB)
- `assets/examples/example-report.md` — Completed prospect report
- `assets/examples/example-outreach.md` — Completed outreach package

## Cron Integration

Designed for automated daily prospecting:
```
8:30 AM  — SERP Gap Scanner (identify opportunities for 5 industries)
10:00 AM — batch_research.py --run morning (Tier A/B cluster)
11:30 AM — batch_research.py --run afternoon (Tier B/C cluster)
5:00 PM  — daily_summary.py (pipeline summary)
```

## Quality Rules

1. Always check for duplicates first (14-day window)
2. Minimum 2 data sources per prospect (SEO audit + web research)
3. Specific findings only — "missing H1 tag" not "SEO issues"
4. Authentic compliments — if their site is good, say so honestly
5. 5 prospects per cluster max — depth over breadth
6. Match outreach tone to industry — casual for restaurants, professional for law firms
7. Verify every prospect before recording — no dead URLs, no parked domains
8. Never exaggerate issues — stick to what the audit actually found

## Error Handling

- **Site unreachable**: Research via web search only, note limitation
- **Duplicate detected**: Skip with message, don't waste API calls
- **Search timeout**: Continue without, flag as lower confidence
- **Empty cluster**: Log and move on (cluster may be exhausted)
- **Minimum data**: Business name + (domain OR industry) required
