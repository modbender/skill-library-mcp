---
name: client-reporting
description: "Automated client reporting for agencies and freelancers using OpenClaw. Pull data from Google Analytics, Google Search Console, social media platforms, and custom sources to generate branded weekly/monthly reports. Auto-deliver via email or Slack. Use when: (1) generating client reports, (2) pulling analytics data for reporting, (3) automating recurring reports, (4) creating branded PDF or HTML reports, (5) scheduling report delivery, or (6) tracking client KPIs over time."
---

# Client Reporting Automation

Pull metrics from multiple sources, generate branded reports, and auto-deliver to clients. Built for agencies and freelancers who need consistent, professional reporting without manual work.

## Setup

### Dependencies

```bash
pip3 install requests jinja2
```

### API Keys (configure in `config.json`)

- **Google Analytics 4** — `GA4_PROPERTY_ID` + service account key
- **Google Search Console** — service account key (see seo-audit-suite references)
- **Social platforms** — same credentials as social-media-autopilot skill
- **SendGrid** — for email delivery (`SENDGRID_API_KEY`)

### Workspace

```
client-reports/
├── config.json           # Global settings, API keys
├── clients/              # Per-client configuration
│   └── client-name/
│       ├── config.json   # Client-specific settings (property IDs, branding)
│       ├── reports/      # Generated reports
│       └── data/         # Cached metrics data
├── templates/            # Report templates (Jinja2 HTML)
└── schedules.json        # Automated delivery schedule
```

Run `scripts/init-workspace.sh` to create this structure.

## Core Workflows

### 1. Add a Client

```bash
scripts/add-client.sh --name "acme-corp" --domain "acme.com" --email "ceo@acme.com"
```

Creates client directory with config template. Edit `clients/acme-corp/config.json` to add:
- GA4 property ID
- Search Console site URL
- Social media handles
- Branding (logo URL, brand colors)
- Report preferences (metrics to include, frequency)

### 2. Pull Metrics

Fetch fresh data for a client:

```bash
scripts/pull-metrics.sh --client "acme-corp"                    # All sources
scripts/pull-metrics.sh --client "acme-corp" --source ga4       # Google Analytics only
scripts/pull-metrics.sh --client "acme-corp" --source gsc       # Search Console only
scripts/pull-metrics.sh --client "acme-corp" --source social    # Social metrics
scripts/pull-metrics.sh --client "acme-corp" --period 30d       # Last 30 days
```

Data sources and metrics:

**Google Analytics 4:**
- Sessions, users, new users, bounce rate
- Top pages by views
- Traffic sources breakdown
- Conversion events
- Device/browser breakdown

**Google Search Console:**
- Total clicks, impressions, CTR, avg position
- Top queries by clicks
- Top pages by impressions
- Position changes vs previous period

**Social Media:**
- Followers/following changes
- Post engagement (likes, shares, comments)
- Top performing posts
- Reach/impressions

### 3. Generate Reports

```bash
scripts/generate-report.sh --client "acme-corp" --type monthly
scripts/generate-report.sh --client "acme-corp" --type weekly --format html
scripts/generate-report.sh --client "acme-corp" --type custom --metrics "traffic,rankings,social"
```

Report types:
- **weekly** — 7-day snapshot with week-over-week changes
- **monthly** — 30-day deep dive with month-over-month trends
- **quarterly** — 90-day strategic overview
- **custom** — pick specific metrics

Output formats:
- **Markdown** — default, good for Slack/email
- **HTML** — branded, professional, email-ready
- **PDF** — via HTML-to-PDF conversion (requires `wkhtmltopdf` or similar)

### 4. Auto-Deliver Reports

```bash
scripts/deliver-report.sh --client "acme-corp" --latest         # Send most recent
scripts/deliver-report.sh --client "acme-corp" --via email      # Email delivery
scripts/deliver-report.sh --client "acme-corp" --via slack      # Slack webhook
```

### 5. Schedule Recurring Reports

Configure in `schedules.json`:

```json
{
  "schedules": [
    {
      "client": "acme-corp",
      "type": "weekly",
      "day": "monday",
      "time": "09:00",
      "timezone": "America/Los_Angeles",
      "deliver_via": "email",
      "enabled": true
    },
    {
      "client": "acme-corp",
      "type": "monthly",
      "day_of_month": 1,
      "time": "09:00",
      "timezone": "America/Los_Angeles",
      "deliver_via": "email",
      "enabled": true
    }
  ]
}
```

Use with OpenClaw cron to automate: check schedules daily, generate and deliver due reports.

### 6. KPI Dashboard

Quick terminal dashboard for any client:

```bash
scripts/dashboard.sh --client "acme-corp"
```

Shows current period vs previous: traffic, rankings, social growth, conversions.

## Report Template System

Templates use Jinja2 and live in `templates/`:

```html
<!-- templates/monthly.html -->
<html>
<head><style>/* brand styles */</style></head>
<body>
  <h1>Monthly Report — {{ client.name }}</h1>
  <p>{{ period.start }} to {{ period.end }}</p>
  
  <h2>Traffic Overview</h2>
  <table>
    <tr><td>Sessions</td><td>{{ ga4.sessions }}</td><td>{{ ga4.sessions_change }}%</td></tr>
    <tr><td>Users</td><td>{{ ga4.users }}</td><td>{{ ga4.users_change }}%</td></tr>
  </table>
  
  <h2>Search Performance</h2>
  <!-- ... -->
</body>
</html>
```

Customize templates per client by placing overrides in `clients/<name>/templates/`.

## Cron Integration

- **Daily:** Pull fresh metrics for all active clients
- **Weekly:** Generate and deliver weekly reports (Monday AM)
- **Monthly:** Generate and deliver monthly reports (1st of month)
- **Quarterly:** Generate quarterly reviews

## References

- `references/ga4-setup.md` — Google Analytics 4 API setup and available metrics
- `references/report-customization.md` — How to customize templates and metrics
