---
name: clarity-literature
description: >
  Search research papers and get publication details from Clarity Protocol.
  Use when the user asks to search research papers, find publications,
  PubMed references, literature about protein, or citation details.
  Capabilities: search papers, get paper details by PMID.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Optional CLARITY_API_KEY env var for 100 req/min (vs 10 req/min).
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Literature Skill

Search and retrieve research papers from Clarity Protocol's curated literature database, sourced from PubMed and enriched with citation metrics from Semantic Scholar.

## Quick Start

List all papers in the database:

```bash
python scripts/search_papers.py
```

Get details for a specific paper by PMID:

```bash
python scripts/get_paper.py --pmid 12345678
```

Get paper details in readable format:

```bash
python scripts/get_paper.py --pmid 12345678 --format summary
```

## Paper Fields

Each paper includes:

- `pmid`: PubMed identifier
- `doi`: Digital Object Identifier
- `title`: Paper title
- `first_author`: First author name
- `publication_year`: Year published
- `journal`: Journal name
- `abstract`: Paper abstract (when available)
- `citation_count`: Number of citations (from Semantic Scholar)
- `influential_citations`: Number of highly influential citations
- `has_fulltext`: Whether full text is available in PubMed Central

## Rate Limits

- **Anonymous (no API key)**: 10 requests/minute
- **With API key**: 100 requests/minute

To use an API key, set the `CLARITY_API_KEY` environment variable:

```bash
export CLARITY_API_KEY=your_key_here
python scripts/search_papers.py
```

Get your API key at https://clarityprotocol.io

## Error Handling

**404 Not Found**: The paper with the specified PMID does not exist in the database.

**429 Rate Limit**: You've exceeded the rate limit. The script will display how long to wait.

**500 Server Error**: The API server encountered an error. Try again later.

**Timeout**: The request took longer than 30 seconds.

## Pagination

Paper lists are paginated. The API returns a `next_cursor` field if more results are available.

## Use Cases

- Find research papers related to protein variants
- Get citation metrics for a specific paper
- Check if a paper has full text available
- Extract abstracts for literature reviews
- Build bibliographies for protein research
