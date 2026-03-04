# Lead & Contact Data Enrichment Agent

Enrich your existing leads, contacts, and company lists with verified B2B data using the AgentSource API. Add missing emails, phone numbers, firmographics, technographics, and job details. Supports single records and bulk CSV enrichment.

Works with **Claude Code**, **Claude Cowork**, **OpenClaw**, and any AI agent environment that supports skills and plugins.

## How It Works

1. Provide your data — a single contact, a list, or a CSV file
2. Tell the agent what data you need (emails, phones, company info, etc.)
3. The agent matches your records, enriches them, and shows a preview
4. You confirm — then it exports the enriched data to CSV

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

### 3. Start enriching
```
Find the email for Jane Smith at Stripe
```
```
Enrich Salesforce, HubSpot, and Notion with firmographics and tech stack
```
```
Enrich my CSV at ~/Downloads/contacts.csv with emails and phone numbers
```
```
Add company data to my lead list at ~/Downloads/leads.csv
```
```
Get contact info for John Doe at Apple and Sarah Chen at Google
```

## Key Features

- **Single Contact Enrichment** — Look up any person by name + company
- **Bulk CSV Enrichment** — Import, match, enrich, and re-export CSVs
- **Inline List Support** — Paste a list of companies or contacts directly
- **Email Discovery** — Verified professional and personal emails
- **Phone Discovery** — Direct dial and mobile numbers
- **Firmographic Append** — Company size, revenue, industry, location
- **Tech Stack Append** — Full technology stack data
- **Funding Data** — Rounds, investors, total raised
- **Profile Completion** — Work history, education, LinkedIn URLs
- **Match & Deduplicate** — Match rates show data quality

## Data & Privacy

All API calls go to `https://api.explorium.ai/v1/`. See SKILL.md for full data handling details.
