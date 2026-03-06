# Company Research & Business Intelligence Agent

Deep-dive company research in seconds using the AgentSource API. Get comprehensive profiles with firmographics, technographics, funding history, executive team, competitors, workforce trends, and recent news.

Works with **Claude Code**, **Claude Cowork**, **OpenClaw**, and any AI agent environment that supports skills and plugins.

## How It Works

1. Name a company (or list of companies) you want to research
2. Choose your research depth (quick overview, full profile, specific focus areas)
3. The agent pulls comprehensive data from Explorium's database
4. Results are presented in structured, actionable format

## Requirements

- Python 3.8+ (standard library only)
- An Explorium AgentSource API key
- Any AI agent environment that supports skills/plugins

## Quick Start

### 1. Install
```bash
./setup.sh
```

### 2. Set your API key

**Do not share your API key in the AI chat.** Set it securely:

```bash
export EXPLORIUM_API_KEY=your_api_key_here
# Or: python3 ~/.agentsource/bin/agentsource.py config --api-key your_api_key_here
```

### 3. Start researching
```
Research Stripe — give me a full company profile
```
```
What tech stack does HubSpot use?
```
```
Compare Stripe, Square, and Adyen side by side
```
```
Who are the executives at Datadog?
```
```
Show me the funding history of Notion
```
```
What are the competitors of Snowflake?
```

## Key Features

- **Company Profiles** — Size, revenue, industry, location, description
- **Technology Analysis** — Full tech stack organized by category
- **Funding Intelligence** — Rounds, investors, valuations, acquisitions
- **Financial Metrics** — Revenue, margins, market cap (public companies)
- **Competitive Intel** — Competitors, market positioning from SEC filings
- **Workforce Trends** — Department breakdown, hiring velocity
- **Event Monitoring** — Funding, hiring, partnerships, M&A activity
- **Executive Discovery** — C-suite and senior leadership profiles
- **Multi-Company Compare** — Side-by-side comparison tables
- **Corporate Hierarchy** — Parent companies, subsidiaries

## Data & Privacy

All API calls go to `https://api.explorium.ai/v1/`. See SKILL.md for full data handling details.
