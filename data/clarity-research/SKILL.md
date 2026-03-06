---
name: clarity-research
description: >
  Search protein folding research data from Clarity Protocol.
  Use when the user asks to search variants, query protein research,
  find fold results, or explore disease-specific protein data.
  Capabilities: list variants by disease or protein name, get API info.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Optional CLARITY_API_KEY env var for 100 req/min (vs 10 req/min).
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Research Skill

Search protein folding research data from Clarity Protocol, a community-driven platform for protein mutation analysis using AlphaFold2 via ColabFold.

## Quick Start

List all available variants:

```bash
python scripts/query_variants.py
```

Filter by disease:

```bash
python scripts/query_variants.py --disease Alzheimer
```

Filter by protein name:

```bash
python scripts/query_variants.py --protein-name MAPT
```

## Output Fields

Each variant result includes:

- `id`: Unique fold identifier
- `protein_name`: Protein name (e.g., "tau", "APP")
- `variant`: Mutation notation (e.g., "P301L", "A246E")
- `disease`: Associated disease
- `uniprot_id`: UniProt database identifier
- `average_confidence`: AlphaFold confidence score (0-100)
- `created_at`: When the fold was created

## Rate Limits

- **Anonymous (no API key)**: 10 requests/minute
- **With API key**: 100 requests/minute

To use an API key, set the `CLARITY_API_KEY` environment variable:

```bash
export CLARITY_API_KEY=your_key_here
python scripts/query_variants.py
```

Get your API key at https://clarityprotocol.io

## Error Handling

**404 Not Found**: The endpoint or resource does not exist.

**429 Rate Limit**: You've exceeded the rate limit. The script will display how long to wait before retrying.

**500 Server Error**: The API server encountered an error. Try again later.

**Timeout**: The request took longer than 30 seconds. The server may be under heavy load.

## Pagination

Results are paginated. The API returns a `next_cursor` field if more results are available. The script automatically handles pagination for typical queries.

## Use Cases

- Explore available protein variants for a specific disease
- Find all folded mutations for a particular protein
- Get an overview of research data available in Clarity Protocol
- Identify fold IDs for detailed analysis with other skills
