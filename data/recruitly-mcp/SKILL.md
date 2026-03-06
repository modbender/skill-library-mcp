---
name: recruitly-mcp
description: "Search candidates, manage jobs, view pipelines, track billing and team performance in Recruitly CRM via MCP."
homepage: https://recruitly.io
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      bins:
        - mcporter
      env:
        - RECRUITLY_TOKEN
---

# Recruitly CRM

Access your Recruitly recruitment CRM via MCP — search candidates, manage jobs, view pipelines, and track team performance from any messaging app.

## Setup

### 1. Get your token

Sign in at [mcp.recruitly.dev](https://mcp.recruitly.dev) using your Recruitly account (Google, Microsoft, or email). Your OAuth token is issued automatically.

### 2. Configure mcporter

Add to `config/mcporter.json`:

```json
{
  "mcpServers": {
    "recruitly": {
      "baseUrl": "https://mcp.recruitly.dev/mcp",
      "description": "Recruitly CRM",
      "headers": {
        "Authorization": "Bearer ${RECRUITLY_TOKEN}"
      }
    }
  }
}
```

### 3. Set your token

```bash
export RECRUITLY_TOKEN="your_oauth_token_here"
```

## Available Tools

### Discovery

| Tool | Description |
|------|-------------|
| **list_options** | Returns all field options (job statuses, candidate statuses, activity types) for your account. Call this first before filtering by status or type. |

### Search & List

| Tool | Description |
|------|-------------|
| **search_candidates** | Search candidates by keyword, location, skills, or job title |
| **search_contacts** | Search contacts (clients, hiring managers) by name, company, or email |
| **search_companies** | Search companies by name, industry, or location |
| **list_jobs** | List jobs with optional status and keyword filters |
| **list_pipelines** | List hiring pipelines (deal flows) |

### Detail

| Tool | Description |
|------|-------------|
| **get_record** | Get a specific candidate, contact, company, or job by ID |

## Usage Examples

**Find candidates:**
> "Find React developers in London"

Calls `search_candidates` with query "React" and location "London".

**Check open jobs:**
> "Show me all open jobs"

Calls `list_options` to get the exact status label for open jobs, then `list_jobs` with that status.

**Pipeline overview:**
> "What's in my pipeline?"

Calls `list_pipelines` and summarises stage counts.

**Company lookup:**
> "Find me details on Acme Corp"

Calls `search_companies` with query "Acme Corp", then `get_record` for the full company profile.

**Weekly report:**
> "Give me a summary of new candidates this week"

Calls `search_candidates` with recent date filters and summarises by skills and location.

## Notes

- All data respects your Recruitly account permissions and team visibility rules
- Status and type values are tenant-configured (may be in any language) — always call `list_options` first
- Search results are capped at 50 per request; use pagination for larger result sets
- Works on Recruitly's free plan — no upgrade needed

## Links

- [Recruitly](https://recruitly.io)
- [MCP Server](https://recruitly.io/mcp)
