---
name: domainkits
description: Turn AI into your domain investment expert. Search newly registered, expired, deleted domains. Check availability with pricing. WHOIS/DNS lookup. Track market trends.
homepage: https://domainkits.com/mcp
metadata: {"openclaw":{"emoji":"🌐","primaryEnv":"DOMAINKITS_API_KEY"}}

---

# DomainKits

Turn AI into your domain investment expert. Search, analyze, and discover domains with real-time market data.

## Why DomainKits?

DomainKits doesn't just give AI tools — it gives AI **domain intelligence**.

Your AI can now:
- **Think like a domainer** — Understand what makes a domain valuable, spot trends before they peak
- **Act on real-time data** — See what's registering now, what's expiring tomorrow, what just dropped
- **Make informed decisions** — Analyze backlinks, keyword value, brand risk, and safety in seconds
- **Execute instantly** — From idea to available domain with pricing and register links


## Setup

### Option 1: Direct call (no config needed)
```bash
# List all DomainKits tools
npx mcporter list --http-url https://api.domainkits.com/v1/mcp

# Call a tool directly
npx mcporter call https://api.domainkits.com/v1/mcp.available domain=example.com
```

### Option 2: Add to mcporter config (recommended)

Add to `config/mcporter.json` or `~/.mcporter/mcporter.json`:
```json
{
  "mcpServers": {
    "domainkits": {
      "description": "Domain intelligence tools for AI agents",
      "baseUrl": "https://api.domainkits.com/v1/mcp"
    }
  }
}
```

With API key (for higher limits):
```json
{
  "mcpServers": {
    "domainkits": {
      "description": "Domain intelligence tools for AI agents",
      "baseUrl": "https://api.domainkits.com/v1/mcp",
      "headers": {
        "X-API-Key": "$env:DOMAINKITS_API_KEY"
      }
    }
  }
}
```

Then call tools by name:
```bash
npx mcporter call domainkits.available domain=example.com
npx mcporter call domainkits.nrds keyword=ai limit=10
```

Get your API key at https://domainkits.com

## Instructions

Call DomainKits tools via mcporter:
```bash
# List available tools
mcporter list domainkits

# Check domain availability
mcporter call domainkits.available domain=example.com

# Search newly registered domains
mcporter call domainkits.nrds keyword=ai limit=10

# Full domain analysis
mcporter call domainkits.analyze domain=stripe.com
```

## Tools

Search
- `nrds` — Newly registered domains
- `aged` — Domains with 5-20+ years history
- `expired` — Domains entering deletion cycle
- `deleted` — Just-dropped domains, available now
- `active` — Live sites and for-sale listings
- `ns_reverse` — Domains on a specific nameserver
- `unregistered_ai` — Unregistered short .ai domains (3-letter, CVCV patterns)

Query
- `available` — Availability check with pricing
- `bulk_available` — Check multiple domains (max 10)
- `whois` — Registration details
- `dns` — DNS records
- `safety` — Google Safe Browsing check
- `tld_check` — Keyword availability across TLDs

Analysis (requires account)
- `backlink_summary` — SEO backlink profile
- `keyword_data` — Google Ads keyword data

Trends
- `keywords_trends` — Hot keywords in registrations
- `tld_trends` — TLD growth patterns
- `tld_rank` — Top TLDs by volume
- `price` — Registration costs by TLD

Bulk
- `bulk_tld` — Check keyword popularity across TLDs
- `bulk_available` — Batch availability check with pricing

Workflows
- `analyze` — Comprehensive domain audit
- `brand_match` — Brand conflict detection with trademark links
- `plan_b` — Find alternatives when domain is taken
- `domain_generator` — Generate creative domains with validation
- `expired_analysis` — Due diligence for expired domains
- `trend_hunter` — Spot trends and find related opportunities

Preferences
- `get_preferences` — Check memory status and retrieve preferences
- `set_preferences` — Save preferences (TLDs, budget, style)
- `delete_preferences` — Delete all data (GDPR Article 17)

Monitor (requires memory)
- `set_monitor` — Create domain monitoring task
- `get_monitors` — Retrieve pending monitor checks
- `update_monitor` — Save monitor results
- `delete_monitor` — Remove monitoring task

Strategy (requires memory)
- `set_strategy` — Create automated opportunity discovery
- `get_strategies` — Retrieve pending strategies
- `update_strategy` — Save strategy results
- `delete_strategy` — Remove strategy


## Instructions

When user wants domain suggestions:
1. Brainstorm names based on keywords
2. Call `bulk_available` to validate
3. Show available options with prices and `register_url`

When user wants to analyze a domain:
1. Call `whois`, `dns`, `safety`
2. Give a clear verdict

Output rules:
- Always show `register_url` for available domains
- Disclose affiliate links
- Default to `no_hyphen=true` and `no_number=true`

## Access Tiers

- **Guest** — Most tools, limited daily usage
- **Member** (free) — All tools, higher limits, memory features
- **Premium** — 500 requests/day, full result depth
- **Platinum** — Unlimited

Get API key at https://domainkits.com

## Privacy

- Works without API key
- Memory OFF by default
- GDPR compliant
- Delete data anytime via `delete_preferences`

## Links

- Website: https://domainkits.com/mcp
- GitHub: https://github.com/ABTdomain/domainkits-mcp
- Contact: info@domainkits.com