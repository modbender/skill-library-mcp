# x402.direct -- Service Directory Skill

A Claude skill for discovering and searching x402-enabled services via the [x402.direct](https://x402.direct) directory API.

## What is x402.direct?

x402.direct is the first public directory of x402-enabled services -- APIs that accept crypto payments via the HTTP 402 protocol. It crawls known x402 facilitators, indexes every service it finds, and assigns each a trust score (ScoutScore) based on automated analysis.

## What This Skill Does

This skill teaches Claude agents how to:

- **Browse services** by category, network, trust score, and sort order (free)
- **Search services** with natural language queries via full-text search (paid, $0.001 via x402)
- **Get service details** including payment addresses, facilitator info, and raw metadata (free)
- **Check ecosystem stats** for total services, providers, networks, and average trust scores (free)
- **Understand trust scores** to evaluate service quality before calling them
- **Handle x402 payments** for the search endpoint using the standard x402 flow

## Installation

Copy the `x402-direct-skill/` folder into your Claude skills directory:

```
your-project/
  skills/
    x402-direct-skill/
      SKILL.md
      metadata.json
      README.md
```

Or reference it from your project's `CLAUDE.md`:

```markdown
## Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| x402-direct | `skills/x402-direct-skill/` | x402 service discovery and search |
```

## Example Use Cases

### "Find me an AI image generation service that accepts x402 payments"

The agent will call `GET https://x402.direct/api/services?category=image&sort=score&minScore=60` and return the top-rated image services with their pricing, trust scores, and endpoint URLs.

### "Search x402 services for text-to-speech"

The agent will call `GET https://x402.direct/api/search?q=text+to+speech&minScore=70` (paying $0.001 via x402) and return semantically matched results ranked by relevance and trust.

### "How many x402 services are there on Base mainnet?"

The agent will call `GET https://x402.direct/api/stats` and report the network breakdown.

### "Get the payment details for service 42"

The agent will call `GET https://x402.direct/api/services/42` and return the `payTo` address, `asset`, `network`, `price`, and `facilitator` info needed to construct an x402 payment.

## API Quick Reference

| Endpoint | Method | Cost | Description |
|----------|--------|------|-------------|
| `/api/services` | GET | Free | Paginated browse with filters |
| `/api/services/:id` | GET | Free | Full service details |
| `/api/stats` | GET | Free | Ecosystem statistics |
| `/api/search?q=...` | GET | $0.001 | Full-text search (x402) |

## Trust Score Ranges

| Score | Verdict | Meaning |
|-------|---------|---------|
| 70-100 | safe | Production-ready, well-documented |
| 40-69 | caution | Some trust signals missing |
| 0-39 | avoid | Missing critical trust signals |

## License

MIT
