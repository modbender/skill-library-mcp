---
name: biz-reporter
description: >
  Automated business intelligence reports pulling data from Google Analytics GA4, Google Search Console,
  Stripe revenue, social media metrics (Twitter/X, LinkedIn, Instagram), HubSpot CRM, and Airtable into
  formatted daily KPI snapshots, weekly marketing reports, and monthly business reviews with trend
  detection and anomaly alerts. Use this skill for: business reports, KPI dashboard, weekly metrics,
  marketing report, revenue summary, traffic report, analytics summary, performance report, "how are
  we doing", "show me our metrics", "what are our numbers", MRR tracking, conversion rate analysis,
  SEO performance report, social media analytics, sales pipeline report, automated reporting via cron,
  data visualization, business intelligence, growth metrics, churn analysis, or any request to combine
  data from multiple business tools into a single formatted report. Also works for ad-hoc questions
  like "how did our launch go" or "compare this month to last month". Delivers via Slack, email,
  Notion, or Markdown file.
metadata:
  openclaw:
    emoji: "📊"
---

# Biz Reporter

Business intelligence that writes itself. Pull data from multiple sources, spot trends, and generate beautiful reports — on demand or on schedule.

## Why This Exists

Data & Analytics has only 18 skills out of 3,286 on ClawHub — the most underserved category by far. Yet automated reporting is called "the most universally loved automation" in the OpenClaw community. Every business needs it, nobody has built it properly.

## How It Works

Biz Reporter connects to the user's business tools, pulls key metrics, applies trend analysis, and generates a formatted report. It works with whatever tools the user has — from a solo founder with just Google Analytics to a team with a full data stack.

## Supported Data Sources

### Web Analytics
- **Google Analytics (GA4)**: sessions, users, pageviews, bounce rate, top pages, traffic sources
- **Google Search Console**: impressions, clicks, CTR, average position, top queries
- Access via `gog` tool, browser automation, or API calls

### Revenue & Payments
- **Stripe**: MRR, revenue, new customers, churn, top products
- **PayPal**: transaction summaries
- Access via CLI tools or API calls with stored credentials

### Social Media
- **Twitter/X**: followers, engagement, top posts
- **LinkedIn**: page views, post engagement, follower growth
- **Instagram**: reach, engagement, follower count
- Access via APIs or browser automation

### CRM & Sales
- **HubSpot**: leads, pipeline value, deals closed, contact growth
- **Airtable**: custom database metrics
- Access via API with stored keys

### Custom Sources
- **Any API**: the user can specify custom API endpoints to pull data from
- **CSV files**: if the user dumps data as CSV, parse and include it
- **Spreadsheets**: Google Sheets via API

## Report Types

### Daily KPI Snapshot
Quick pulse check — 2-3 minutes to generate, meant for morning review.

```
📊 Daily KPI Snapshot — [Date]

🌐 Website: [sessions] sessions ([+/-]% vs yesterday)
   Top page: [page] ([views] views)
   
💰 Revenue: $[amount] ([+/-]% vs yesterday)
   New customers: [count]
   
📱 Social: [total engagement] across platforms
   Best post: [platform] — [description] ([engagement])

⚡ Quick take: [One sentence AI analysis of the day]
```

### Weekly Marketing Report
Comprehensive marketing performance overview.

```
📈 Weekly Marketing Report — [Date Range]

EXECUTIVE SUMMARY
[2-3 sentence overview: what went well, what needs attention, key number]

WEBSITE PERFORMANCE
• Sessions: [number] ([%] vs last week)
• Unique visitors: [number]
• Top traffic sources: [source 1] ([%]), [source 2] ([%]), [source 3] ([%])
• Top 5 pages by traffic:
  1. [page] — [views] views
  2. ...
• Bounce rate: [%] ([trend])

SEARCH PERFORMANCE
• Impressions: [number] ([%] change)
• Clicks: [number] ([%] change)
• Average CTR: [%]
• Average position: [number]
• Top gaining queries: [query] (+[positions])
• Top losing queries: [query] (-[positions])

SOCIAL MEDIA
• Total followers: [number] (net +[growth])
• Total engagement: [number]
• Best performing post: [description]
• Platform breakdown:
  - Twitter/X: [followers], [engagement]
  - LinkedIn: [followers], [engagement]

REVENUE (if available)
• Total revenue: $[amount] ([%] vs last week)
• New customers: [count]
• Churn: [count] ([%])
• MRR: $[amount]

TRENDS & INSIGHTS
• [AI-generated insight about notable trends]
• [Comparison to historical averages]
• [Actionable recommendation]

NEXT WEEK FOCUS
• [Suggested action based on data]
```

### Monthly Business Review
Deep analysis with historical comparisons and strategic recommendations.

Follow the weekly format but expand with:
- Month-over-month and year-over-year comparisons
- Cohort analysis for customer retention (if data available)
- Content performance breakdown (which articles drove traffic)
- Funnel analysis: visitors → signups → customers (if trackable)
- Strategic recommendations section with specific actions

### Custom Report
If the user asks for something specific, build it:
- "Show me our top 10 pages by revenue contribution"
- "Compare this month's social engagement to last month"
- "What keywords are we losing rankings for?"

## Trend Detection

Biz Reporter doesn't just show numbers — it spots patterns:

1. **Week-over-week anomalies**: flag metrics that changed more than 20% from the prior week
2. **Declining trends**: if a metric has dropped for 3+ consecutive periods, raise it prominently
3. **Correlation hints**: "Traffic from Twitter spiked 40% — this correlates with your viral post on [date]"
4. **Seasonal patterns**: if historical data shows patterns (e.g., weekend dips), note them instead of alerting
5. **Comparison framing**: always show the comparison baseline so numbers have context

## Natural Language Queries

Users can ask questions about their data conversationally:

| User says | Action |
|-----------|--------|
| "How's our traffic this week?" | Quick web analytics summary with week-over-week comparison |
| "What's our MRR?" | Pull Stripe data, show current MRR with trend |
| "Which blog posts are getting the most traffic?" | Top pages report from GA4 |
| "Are we ranking better or worse this month?" | Search Console comparison |
| "Generate my weekly report" | Full weekly marketing report |
| "How did our launch go?" | Pull metrics for a specific date range around the launch |
| "Show me revenue by month for the last 6 months" | Historical revenue chart description |

## Scheduling Reports

Help users set up recurring reports via cron:

```json
[
  {
    "name": "Daily KPI snapshot",
    "schedule": "0 8 * * 1-5",
    "prompt": "Generate daily KPI snapshot and send to Slack #metrics"
  },
  {
    "name": "Weekly marketing report",
    "schedule": "0 9 * * 1",
    "prompt": "Generate weekly marketing report for last week and send via email"
  },
  {
    "name": "Monthly business review",
    "schedule": "0 10 1 * *",
    "prompt": "Generate monthly business review for last month and post to Notion"
  }
]
```

## Setup & Configuration

On first use:

1. **Discover available tools**: check which data sources the user has access to (GA4, Stripe, etc.)
2. **Authenticate**: help configure API keys or tool access for each source. Store securely in environment variables, never in SKILL.md or memory.
3. **Baseline**: pull initial data to establish benchmarks for future comparisons
4. **Preferences**: ask about reporting frequency, delivery channel, and which metrics matter most
5. **Store config**: save all preferences in workspace memory

## Output Formats

Reports can be delivered as:
- **Chat message**: formatted directly in the conversation or messaging channel
- **Markdown file**: saved to workspace for archival
- **Notion page**: if Notion skill is available
- **Email**: via configured email skill
- **Slack/Discord message**: for team channels

## Edge Cases

- **Partial data**: if some sources are unavailable, generate the report with what's available and note what's missing
- **No historical data**: on first run, can only show current snapshot. Note that comparisons will be available next period.
- **API rate limits**: cache data within a session and batch requests
- **Zero traffic / new site**: don't show depressing "0 visitors" — instead focus on setup progress and first wins
- **Multiple properties**: if user has multiple websites/products, ask which one or generate combined report
- **Currency**: detect user locale and format currency appropriately
- **Privacy**: never include individual user data or PII in reports. Aggregate only.
