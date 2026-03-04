---
name: ahrefs-mcp
description: >
  Access Ahrefs SEO data through Model Context Protocol (MCP) for comprehensive SEO analysis, keyword research, backlink analysis, site audits, and competitive intelligence. Use when users mention: (1) SEO-related queries about websites, domains, or URLs, (2) Keyword research, rankings, or search volume data, (3) Backlink analysis or link profiles, (4) Domain metrics (DR, UR, traffic), (5) Competitor analysis or site comparison, (6) Rank tracking or SERP analysis, (7) Content gap analysis, (8) Site Explorer data requests. When uncertain if a query is SEO-related, ask if Ahrefs should be used.
---

# Ahrefs MCP

Access real-time Ahrefs SEO data directly through Model Context Protocol to analyze websites, research keywords, track rankings, and make data-driven SEO decisions.

## First-Time Setup

If this is your first time using Ahrefs MCP, read [references/setup.md](references/setup.md) for complete connection instructions. You'll need:
- An Ahrefs account (Lite plan or higher)
- To connect via the remote MCP server URL: `https://api.ahrefs.com/mcp/mcp`

After setup, return here for usage guidance.

## Core Capabilities

Ahrefs MCP provides access to:

1. **Site Explorer** - Domain metrics, backlinks, organic traffic, referring domains
2. **Keywords Explorer** - Search volume, keyword difficulty, SERP analysis, related keywords
3. **Rank Tracker** - Position tracking, visibility metrics, competitor rankings
4. **Site Audit** - Technical SEO issues, crawl data, site health
5. **Content Explorer** - Top performing content, content gaps

For detailed capability reference, see [references/capabilities.md](references/capabilities.md).

## Usage Workflow

### 1. Understand the Request

Identify what SEO data is needed:
- **Domain/URL analysis** → Site Explorer
- **Keyword data** → Keywords Explorer
- **Position tracking** → Rank Tracker
- **Technical SEO** → Site Audit
- **Content ideas** → Content Explorer

### 2. Query Ahrefs

Use natural language to request data. Examples:

```
"Get backlink profile for example.com"
"What's the search volume for 'best running shoes'?"
"Show me keyword difficulty scores for this list: [keywords]"
"Analyze competitor domains for example.com"
"Get current rankings from rank tracker project 'My Website'"
```

### 3. Analyze and Present

- Present data in clear, actionable formats
- Highlight key insights and opportunities
- Suggest next steps based on findings
- Cross-reference multiple data points when relevant

## Common Workflows

### Keyword Research + Cross-Reference

1. User provides keyword list
2. Query Ahrefs for each keyword's metrics (volume, difficulty, CPC)
3. Present consolidated analysis
4. Help prioritize based on criteria (difficulty vs. volume, intent, etc.)

See [references/workflows.md](references/workflows.md) for detailed workflow patterns.

### Competitive Analysis

1. Identify target domain and competitors
2. Compare domain metrics (DR, organic traffic, referring domains)
3. Analyze top organic keywords
4. Identify content gaps
5. Recommend opportunities

### Site Audit Review

1. Access site audit data for domain
2. Identify critical issues by severity
3. Prioritize fixes by impact
4. Provide technical recommendations

## When Ahrefs Connection is Missing

If the MCP connection is not configured:
1. Provide setup instructions from [references/setup.md](references/setup.md)
2. Share the connection URL: `https://api.ahrefs.com/mcp/mcp`
3. Guide through the authorization process
4. Test connection before proceeding

## API Limits Awareness

- Each plan has row limits per request and monthly API unit caps
- Track usage in Account settings → Limits and usage
- Enterprise users can purchase additional units
- Design efficient queries to conserve units

## Best Practices

- **Be specific**: Include target domain, date ranges, or specific metrics needed
- **Batch requests**: When analyzing multiple keywords/domains, request data efficiently
- **Context matters**: Cross-reference data points for deeper insights
- **Actionable output**: Always provide recommendations, not just raw data
- **Verify before expensive queries**: Confirm the scope before running large dataset requests
