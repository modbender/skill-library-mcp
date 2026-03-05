---
name: supermarket-deals
description: Search German supermarket flyers (Aldi, Lidl, REWE, EDEKA, Kaufland) for product deals via Marktguru. Results ranked by best price per litre (EUR/L). No API key needed.
---

# supermarket-deals

Search German supermarket flyers for product deals via the Marktguru API. Results are ranked by best price per litre.

## What this skill does
- Fetches Marktguru API keys automatically from the homepage (no registration needed, keys are cached 6h)
- Searches current Prospekte (flyers) by product query + ZIP code
- Supports multiple search terms in one call (merged + deduplicated)
- Filters by store, ranks by EUR/L
- Returns a direct Marktguru link for each deal
- The skill is intentionally "dumb" — it fetches and formats data. Your agent applies smart filtering and formatting for notifications.

## Setup

```bash
cd path/to/supermarket-deals
npm install
npm run build
```

Optionally set your defaults:
```bash
node dist/index.js config set zip 85540
node dist/index.js config set stores "Lidl,REWE,EDEKA,ALDI SÜD,Kaufland"
```

## Usage

```bash
# Single search term
node dist/index.js search "Cola Zero" --zip 85540

# Multiple terms (merged + deduped, useful for product aliases)
node dist/index.js search "Cola Zero" "Coke Zero" --zip 85540

# Broad search — let your agent do the filtering
node dist/index.js search "Cola" --zip 85540

# Filter by specific stores
node dist/index.js search "Monster Energy" --zip 80331 --stores "Lidl,ALDI SÜD"

# JSON output for agent/cron use
node dist/index.js search "Cola" --zip 85540 --json

# Show config
node dist/index.js config
```

## Agent pattern (recommended)

Use a broad search term and let your agent filter intelligently:

```
node dist/index.js search "Cola" --zip 85540 --json
```

Then instruct your agent to:
- Include deals where description says "versch. Sorten" (these bundle all variants incl. Zero)
- Include deals that explicitly mention Coca-Cola, Coke Zero, etc.
- Exclude deals that only mention Powerade, Fuze Tea, Sprite-only, etc.
- Rank by EUR/L and highlight the best deal

This approach catches deals that Marktguru lists as generic "Cola category" without naming every variant.

## Output columns
| Column | Description |
|--------|-------------|
| Description | Product description from flyer |
| Store | Retailer name |
| Size | Volume × quantity (e.g. `6×0.33l`, `1.5l`) |
| Price | Total price |
| EUR/L | Price per litre (calculated or from API reference price) |
| Valid | Deal validity dates |
| URL | Direct link to Marktguru offer page |

## Notes
- Prospekte refresh on Mondays and Thursdays
- Results are cached by Marktguru for ~15 minutes
- Some regional store branches may not submit flyers to Marktguru — broad queries catch more
- API keys rotate and are fetched fresh at runtime (cached 6h in `~/.supermarket-deals/keys.json`)
