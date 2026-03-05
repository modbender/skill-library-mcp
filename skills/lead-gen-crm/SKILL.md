---
name: lead-gen-crm
description: "End-to-end lead generation and CRM pipeline automation for OpenClaw agents. Discover leads from web searches and directories, enrich with contact data, score and qualify leads, push to CRM (HubSpot, Pipedrive, Zoho), and run automated email outreach sequences with follow-ups. Use when: (1) finding new leads or prospects, (2) enriching lead data with emails and company info, (3) pushing leads to a CRM, (4) setting up email outreach campaigns, (5) scoring or qualifying leads, (6) managing a sales pipeline, or (7) automating follow-up sequences."
---

# Lead Gen + CRM Pipeline

Full lead generation pipeline — from discovery to CRM to outreach. Find prospects, enrich their data, qualify them, push to your CRM, and automate follow-up sequences.

## Setup

### Dependencies

```bash
pip3 install requests
```

### API Keys (configure in `config.json`)

- **Brave Search API** — lead discovery (already configured if web_search works)
- **Hunter.io** — email finding/verification (`HUNTER_API_KEY`, free 25 searches/mo)
- **HubSpot** — CRM integration (`HUBSPOT_API_KEY`)
- **Pipedrive** — CRM integration (`PIPEDRIVE_API_KEY` + `PIPEDRIVE_DOMAIN`)
- **Zoho** — CRM integration (`ZOHO_ACCESS_TOKEN`)
- **SendGrid or SMTP** — outreach emails (`SENDGRID_API_KEY` or SMTP config)

Not all are required — use what fits your stack.

### Workspace

```
lead-gen/
├── config.json           # API keys, CRM selection, scoring rules
├── leads/                # Lead database (JSON files)
│   ├── raw/              # Newly discovered leads
│   ├── enriched/         # Leads with contact data
│   ├── qualified/        # Scored and qualified
│   └── archived/         # Closed/rejected
├── campaigns/            # Outreach campaign configs
├── templates/            # Email templates
└── reports/              # Pipeline reports
```

Run `scripts/init-workspace.sh` to create this structure.

## Core Workflows

### 1. Lead Discovery

Find leads matching your ideal customer profile:

```bash
scripts/discover-leads.sh --query "ai agency owner" --count 20
scripts/discover-leads.sh --query "shopify store owner" --industry ecommerce --location "United States"
scripts/discover-leads.sh --directory yelp --category "marketing agencies" --location "Los Angeles"
```

Discovery sources:
- **Brave Search** — find companies/people matching criteria
- **Web scraping** — extract contact info from search results
- **Directory parsing** — structured business directories

Output: raw lead JSON files in `leads/raw/`.

### 2. Lead Enrichment

Add contact data and company info to raw leads:

```bash
scripts/enrich-lead.sh <lead-id>
scripts/enrich-leads.sh --batch raw    # Enrich all raw leads
```

Enrichment adds:
- **Email addresses** — via Hunter.io or pattern matching
- **Company info** — website, size, industry, tech stack
- **Social profiles** — LinkedIn, Twitter handles
- **Domain authority** — basic SEO metrics

### 3. Lead Scoring

Score leads based on configurable criteria:

```bash
scripts/score-leads.sh                  # Score all enriched leads
scripts/score-leads.sh --threshold 70   # Only qualify leads scoring 70+
```

Default scoring rubric (customizable in `config.json`):
- **Company size fit** (0-25) — matches your target
- **Industry match** (0-25) — in your target verticals
- **Email available** (0-20) — can reach them
- **Web presence** (0-15) — active website, social profiles
- **Tech signals** (0-15) — uses relevant technology

Leads scoring above threshold move to `leads/qualified/`.

### 4. CRM Integration

Push qualified leads to your CRM:

```bash
scripts/push-to-crm.sh <lead-id>
scripts/push-to-crm.sh --batch qualified   # Push all qualified leads
scripts/push-to-crm.sh --crm hubspot       # Override default CRM
```

Supported CRMs:
- **HubSpot** — creates contact + deal, sets pipeline stage
- **Pipedrive** — creates person + deal
- **Zoho** — creates lead record
- **CSV export** — fallback for any CRM via import

See `references/crm-setup.md` for per-CRM configuration.

### 5. Email Outreach

Run automated outreach campaigns with follow-ups:

```bash
scripts/create-campaign.sh --name "q1-outreach" --template cold-intro --leads qualified
scripts/send-campaign.sh --campaign "q1-outreach" --dry-run    # Preview first
scripts/send-campaign.sh --campaign "q1-outreach"              # Send for real
```

Campaign features:
- **Templates with variables** — personalized per lead
- **Multi-step sequences** — initial + 2-3 follow-ups
- **Delay between steps** — configurable (default 3 days)
- **Tracking** — opens, replies, bounces (via SendGrid)
- **Auto-pause** — stops sequence when lead replies
- **Human approval** — requires explicit approval before sending

**Critical: Never send without user approval.** `--dry-run` always first.

### 6. Pipeline Reports

```bash
scripts/pipeline-report.sh                 # Current pipeline summary
scripts/pipeline-report.sh --weekly        # Weekly activity report
scripts/pipeline-report.sh --conversion    # Conversion funnel metrics
```

## Email Templates

Store in `templates/` as JSON:

```json
{
  "name": "cold-intro",
  "subject": "Quick question about {company_name}",
  "body": "Hi {first_name},\n\nI noticed {company_name} is {personalization_hook}.\n\nWe help companies like yours {value_prop}.\n\nWould you be open to a quick chat this week?\n\nBest,\n{sender_name}",
  "follow_ups": [
    {
      "delay_days": 3,
      "subject": "Re: Quick question about {company_name}",
      "body": "Hi {first_name},\n\nJust following up on my previous note. {follow_up_hook}\n\nHappy to share more details if helpful.\n\nBest,\n{sender_name}"
    },
    {
      "delay_days": 7,
      "subject": "Last note from me",
      "body": "Hi {first_name},\n\nDon't want to be a pest — just one last check. If {value_prop_short} isn't a priority right now, no worries at all.\n\nIf timing changes, I'm here.\n\nBest,\n{sender_name}"
    }
  ]
}
```

## Safety & Compliance

- **CAN-SPAM / GDPR** — always include unsubscribe option
- **Rate limiting** — max 50 emails/day by default (configurable)
- **Bounce handling** — auto-remove bounced addresses
- **Never scrape emails from personal pages** — only business contacts
- **Always dry-run first** — no outreach without human review

## Cron Integration

- **Daily discovery** — run lead searches on schedule
- **Batch enrichment** — enrich new raw leads nightly
- **Follow-up sends** — check and send due follow-ups
- **Weekly pipeline report** — summarize funnel health

## References

- `references/crm-setup.md` — Setup guides for HubSpot, Pipedrive, Zoho
- `references/email-best-practices.md` — Deliverability, compliance, templates
- `references/scoring-customization.md` — How to tune the scoring model
