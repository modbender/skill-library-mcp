---
name: generect-api
description: Search B2B leads and companies, find/validate emails via Generect Live API. Use when the user needs to find people by job title/company/industry, search companies by ICP, generate business emails from name+domain, or validate email addresses. Covers lead generation, prospecting, enrichment, and email discovery workflows.
---

# Generect Live API

Real-time B2B data from LinkedIn, Crunchbase, and AI-powered email discovery.

**Base URL:** `https://api.generect.com`
**Auth:** `Authorization: Token <GENERECT_API_KEY>`

## Setup

Requires `GENERECT_API_KEY` environment variable. Get a key at https://beta.generect.com

## Endpoints

### Search Leads
`POST /api/v1/leads/by_icp/`

Find people by ICP filters. Returns enriched LinkedIn profiles with job history, education, skills.

```json
{
  "job_title": ["CEO", "CTO"],
  "location": ["United States"],
  "industry": ["Software Development"],
  "company_headcount_range": ["11-50", "51-200"],
  "page": 1,
  "per_page": 10
}
```

Key filters: `job_title`, `location`, `industry`, `company_headcount_range`, `company_name`, `seniority_level`, `job_function`. All accept arrays.

Response: `{ "amount": N, "leads": [...] }` — each lead has `full_name`, `headline`, `job_title`, `company_name`, `company_website`, `linkedin_url`, `jobs[]`, `educations[]`, `skills[]`.

### Search Companies
`POST /api/v1/companies/by_icp/`

Find companies by ICP. Returns company profiles with headcount, industry, location, funding.

```json
{
  "industry": ["Software Development"],
  "location": ["San Francisco"],
  "headcount_range": ["51-200"],
  "page": 1,
  "per_page": 10
}
```

Key filters: `industry`, `location`, `headcount_range`, `company_type`, `founded_year_min`, `founded_year_max`, `keyword`.

Response: `{ "amount": N, "companies": [...] }` — each has `name`, `domain`, `industry`, `headcount_range`, `headcount_exact`, `location`, `description`, `linkedin_link`, `website`, `founded_year`.

### Get Lead by LinkedIn URL
`POST /api/v1/leads/by_url/`

```json
{ "url": "https://www.linkedin.com/in/username/" }
```

Returns full enriched profile for a specific LinkedIn URL.

### Generate Email
`POST /api/v1/email_generator/`

AI-powered email discovery from name + domain.

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "domain": "example.com"
}
```

Response: `{ "email": "...", "result": "valid|risky|invalid", "catch_all": bool }`

### Validate Email
`POST /api/v1/email_validator/`

```json
{ "email": "john@example.com" }
```

Response: `{ "result": "valid|invalid|risky", "catch_all": bool, "mx_domain": "...", "exist": "yes|no" }`

## Usage via curl

```bash
curl -X POST https://api.generect.com/api/v1/leads/by_icp/ \
  -H "Authorization: Token $GENERECT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"job_title":["VP Sales"],"location":["United States"],"per_page":5}'
```

## MCP Server (Alternative)

Generect also provides an MCP server for AI tool integrations:
- Remote: `mcp-remote https://mcp.generect.com/mcp --header "Authorization: Bearer Token API_KEY"`
- Local: `npx -y generect-ultimate-mcp@latest` with env `GENERECT_API_KEY`

Tools: `search_leads`, `search_companies`, `generate_email`, `get_lead_by_url`, `health`

## Tips

- `amount: -1` in response means exact count unavailable; iterate pages until empty
- Leads endpoint is live — each request queries LinkedIn in real-time (may take 5-15s)
- Email generator uses AI permutations + validation; `valid` results are safe to send
- Combine lead search → email generation for full prospecting pipeline
- Rate limits apply per API key tier
