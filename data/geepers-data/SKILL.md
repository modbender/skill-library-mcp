---
name: geepers-data
description: Fetch structured data from 17 authoritative APIs — arXiv, Census Bureau, GitHub, NASA, Wikipedia, PubMed, news, weather, finance, FEC, and more — through a single endpoint. Use when you need real data from authoritative sources for research, visualizations, or analysis.
---

# Dreamer Data

Access 17 structured data sources through `https://api.dr.eamer.dev`.

## Authentication

```bash
export DREAMER_API_KEY=your_key_here
```

## Endpoints

### List Available Sources
```
GET https://api.dr.eamer.dev/v1/data
```

### Search Across Sources
```
POST https://api.dr.eamer.dev/v1/data/search
Body:
{
  "source": "arxiv",
  "query": "machine learning interpretability",
  "limit": 10
}
```

### Available Sources
| Source | ID | What it provides |
|--------|-----|-----------------|
| arXiv | `arxiv` | Academic papers |
| Census Bureau | `census` | US demographic data |
| GitHub | `github` | Code repositories, issues, users |
| NASA | `nasa` | Space data, images, astronomy |
| Wikipedia | `wikipedia` | Encyclopedia articles |
| PubMed | `pubmed` | Biomedical literature |
| News | `news` | Current events from 80+ outlets |
| Weather | `weather` | Current and forecast weather |
| Finance | `finance` | Stock prices and market data |
| FEC | `fec` | Federal campaign finance |
| OpenLibrary | `openlibrary` | Books and library records |
| Semantic Scholar | `semantic_scholar` | Academic citation graphs |
| YouTube | `youtube` | Video metadata |
| Wolfram Alpha | `wolfram` | Computational knowledge |
| Wayback Machine | `archive` | Web archive snapshots |
| Judiciary | `judiciary` | US court records |
| MAL | `mal` | Anime and manga data |

## When to Use
- Research that needs verified, citable data
- Building data pipelines from authoritative sources
- Enriching existing datasets with external context

## Don't Use When
- The source you need isn't in the list (check `/v1/data` first)
- You have direct API access to the source with higher rate limits
