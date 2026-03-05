---
name: epstein
description: >
  Search 44,886+ DOJ-released Jeffrey Epstein documents (Jan 2026 release).
  Free, no payment required. Search by name, topic, location, or keyword across
  the full DugganUSA index of declassified Epstein files. Returns document previews,
  people mentioned, locations, aircraft, evidence types, and source references.
metadata:
  author: project-einstein
  version: "1.1.0"
  clawdbot:
    emoji: "📂"
    homepage: "https://emc2ai.io"
    requires:
      bins: ["node", "curl"]
---

# Epstein Files Search — Free DOJ Document Search

Search **44,886+ declassified Jeffrey Epstein documents** released by the U.S. Department of Justice on January 30, 2026. Powered by the [DugganUSA](https://analytics.dugganusa.com) public index.

**100% free. No API keys. No accounts. No payment.**

## Quick Start

```bash
# Search by name
node scripts/epstein.mjs search --query "Ghislaine Maxwell" --limit 10

# Search by topic
node scripts/epstein.mjs search --query "flight logs" --limit 20

# Search by location
node scripts/epstein.mjs search --query "Little St James"

# Get index statistics
node scripts/epstein.mjs stats
```

## Commands

### `search` — Search Epstein Documents

Search across all 44,886+ indexed documents by keyword, name, topic, or location.

```bash
node scripts/epstein.mjs search --query "SEARCH TERMS" [--limit N]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--query <terms>` | Search query (required) | — |
| `--limit <N>` | Number of results (1-500) | `10` |

**Examples:**

```bash
# Search for a specific person
node scripts/epstein.mjs search --query "Prince Andrew"

# Search for a topic
node scripts/epstein.mjs search --query "financial transactions"

# Search for locations
node scripts/epstein.mjs search --query "New York mansion"

# Get more results
node scripts/epstein.mjs search --query "flight logs" --limit 50

# Search for evidence types
node scripts/epstein.mjs search --query "phone records"
```

### `stats` — Index Statistics

Get the current state of the document index — total documents, database size, and last update time.

```bash
node scripts/epstein.mjs stats
```

## Output Format

Search results are returned as JSON to stdout (for easy piping and parsing). Status messages and **Quick Links** (direct PDF URLs) go to stderr for easy viewing.

### Search Result Shape

```json
{
  "query": "flight logs",
  "totalHits": 1523,
  "hits": [
    {
      "id": "doc-abc123",
      "efta_id": "EFTA-00001234",
      "content_preview": "Excerpt from the document...",
      "doc_type": "legal_document",
      "dataset": "epstein_files",
      "pages": 3,
      "people": ["Person A", "Person B"],
      "locations": ["New York", "Palm Beach"],
      "aircraft": ["N908JE"],
      "evidence_types": ["financial_record"],
      "source": "DOJ Release Jan 2026",
      "indexed_at": "2026-01-31T...",
      "doj_url": "https://www.justice.gov/epstein/files/DataSet%209/EFTA-00001234.pdf",
      "doj_listing_url": "https://www.justice.gov/epstein/doj-disclosures/data-set-9-files"
    }
  ]
}
```

**New in v1.1.0:** Each result now includes `doj_url` (direct PDF link) and `doj_listing_url` (dataset page). The CLI also displays Quick Links in stderr output:

```
--- Quick Links ---
1. EFTA-00001234: https://www.justice.gov/epstein/files/DataSet%209/EFTA-00001234.pdf
2. EFTA-00001235: https://www.justice.gov/epstein/files/DataSet%209/EFTA-00001235.pdf
```

### Stats Shape

```json
{
  "totalDocuments": 44886,
  "databaseSize": "2.1 GB",
  "lastUpdate": "2026-01-31T...",
  "isIndexing": false
}
```

## Data Source

All documents come from the **U.S. Department of Justice** release of Jeffrey Epstein-related records on January 30, 2026. The documents are indexed and searchable via the [DugganUSA](https://analytics.dugganusa.com) public API.

- **Source**: [DOJ Epstein Records](https://www.justice.gov/epstein)
- **Index**: [DugganUSA Analytics](https://analytics.dugganusa.com)
- **Coverage**: 44,886+ document files (3+ million pages)
- **Content**: Court filings, depositions, flight logs, financial records, communications, evidence inventories, and more

## Piping & Integration

Results go to stdout as JSON, making it easy to pipe into other tools:

```bash
# Pipe to jq for filtering
node scripts/epstein.mjs search --query "Maxwell" --limit 100 | jq '.hits[] | .people'

# Save results to file
node scripts/epstein.mjs search --query "flight logs" --limit 500 > flight-logs.json

# Count total hits
node scripts/epstein.mjs search --query "Palm Beach" | jq '.totalHits'

# Extract all mentioned people
node scripts/epstein.mjs search --query "2005" --limit 100 | jq '[.hits[].people[]?] | unique'
```

## Troubleshooting

**"Cannot reach API"**
Check your internet connection. The DugganUSA API may have temporary downtime.

**"No results found"**
Try broader search terms. The search is keyword-based — use names, locations, or document types rather than full sentences.

**Slow responses**
The API typically responds in 100-900ms. Larger result sets (limit > 100) may take slightly longer.

## References

- [DOJ Epstein Records](https://www.justice.gov/epstein) — Official DOJ release page
- [DugganUSA API](https://analytics.dugganusa.com) — Search index provider
- [Project Einstein](https://emc2ai.io) — AI agent with built-in Epstein files search
