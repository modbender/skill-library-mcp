---
name: pmc-harvest
description: Fetch articles from PubMed Central using NCBI APIs. Search journals, retrieve full text via OAI-PMH, batch harvest for RAG pipelines. No API key required.
version: 1.0.0
author: Ania
metadata:
  clawdbot:
    emoji: "📚"
    requires:
      bins: ["node"]
---

# PMC Harvest

Fetch full-text articles from PubMed Central using official NCBI APIs.

## Features

- **E-utilities search** — Find articles by journal, year, query
- **OAI-PMH full text** — Retrieve complete article XML (open access only)
- **Batch harvesting** — Process multiple journals at once
- **Abstract fetch** — Lightweight retrieval for review queues
- **No API key required** — Uses public NCBI APIs (rate-limited)

## Usage

```bash
# Search a journal
node {baseDir}/scripts/pmc-harvest.js --search "J Stroke[journal]" --year 2025

# Fetch full text for a specific article
node {baseDir}/scripts/pmc-harvest.js --fetch PMC12345678

# Batch harvest from multiple journals
node {baseDir}/scripts/pmc-harvest.js --harvest journals.json --year 2025

# Test with known journals
node {baseDir}/scripts/pmc-harvest.js --test
```

## Options

| Flag | Description |
|------|-------------|
| `--search <query>` | PMC search query (use journal[name] format) |
| `--year <year>` | Filter by publication year |
| `--max <n>` | Max results (default: 100) |
| `--fetch <pmcid>` | Fetch full text for specific PMCID |
| `--harvest <file>` | Batch harvest from JSON journal list |
| `--test` | Run test with sample journals |

## Programmatic API

```javascript
const pmc = require('{baseDir}/lib/api.js');

// Search
const { count, pmcids } = await pmc.searchJournal('"J Stroke"[journal]', { year: 2025 });

// Get summaries
const summaries = await pmc.getSummaries(pmcids);

// Fetch full text
const { available, xml, reason } = await pmc.fetchFullText('PMC12345678');

// Parse JATS XML
const { title, abstract, body } = pmc.parseJATS(xml);

// Fetch abstract only (lightweight)
const { title, abstract } = await pmc.fetchAbstract('PMC12345678');
```

## Journal Query Examples

```javascript
const queries = {
  'Stroke': '"Stroke"[journal]',
  'Journal of Stroke': '"J Stroke"[journal]',
  'Stroke & Vascular Neurology': '"Stroke Vasc Neurol"[journal]',
  'European Stroke Journal': '"Eur Stroke J"[journal]',
  'BMC Neurology': '"BMC Neurol"[journal]'
};
```

## Limitations

- **OAI-PMH only returns open-access articles** — restricted content unavailable
- **Rate limits** — ~3 requests/second without API key
- **Peak hours** — NCBI recommends avoiding 5AM-9PM ET for large batches

## API Reference

This skill wraps NCBI's official APIs:

- **E-utilities**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
  - `esearch.fcgi` — Search PMC
  - `esummary.fcgi` — Get article metadata
- **OAI-PMH**: `https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh`
  - `GetRecord` — Fetch full text XML

Full docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/
