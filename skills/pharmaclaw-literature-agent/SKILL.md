---
name: pharmaclaw-literature-agent
description: Literature mining agent v2.0.0 for novel drug discovery: PubMed/Semantic Scholar + ClinicalTrials Phase II/III + bioRxiv preprints. Novelty scoring, phase/FDA query boosts. Best for latest breakthroughs. Searches PubMed (NCBI E-utilities) and Semantic Scholar for papers related to compounds, targets, diseases, mechanisms, reactions, and catalysts. Returns structured results with titles, authors, abstracts, DOIs, MeSH terms, citation counts, TLDR summaries, and open-access PDFs. Supports paper lookup by DOI/PMID, citation tracking, and related paper discovery. Chains from any PharmaClaw agent (compound name, target, disease) and recommends next agents based on findings. No API keys required. Triggers on literature, papers, publications, PubMed, search papers, citations, references, what's published, research on, studies about, review articles, recent papers, state of the art.
---

# Literature Agent v1.0.0

## Overview

Dual-source literature search combining PubMed (biomedical focus) and Semantic Scholar (broader CS/ML/AI coverage). Deduplicates across sources, enriches with citation metrics and TLDR summaries.

**Key capabilities:**
- PubMed search with MeSH terms, abstracts, publication types
- Semantic Scholar search with citation counts, influential citations, TLDR
- Paper lookup by DOI or PMID
- Citation tracking (who cited this paper?)
- Related paper discovery (what did this paper reference?)
- Automatic query construction from compound/target/disease inputs
- Cross-source deduplication and enrichment

## Quick Start

```bash
# Search by topic
python scripts/pubmed_search.py --query "KRAS G12C inhibitor" --max-results 5

# Search Semantic Scholar (includes ML/AI papers)
python scripts/semantic_scholar.py --query "graph neural network drug discovery"

# Full chain: compound + disease context
python scripts/chain_entry.py --input-json '{"compound": "sotorasib", "disease": "lung cancer"}'

# Look up a specific paper and find who cited it
python scripts/semantic_scholar.py --paper-id "DOI:10.1038/s41586-021-03819-2" --citations

# Recent papers only (last 3 years)
python scripts/pubmed_search.py --query "organometallic catalyst drug synthesis" --years 3
```

## Scripts

### `scripts/pubmed_search.py`
PubMed via NCBI E-utilities (public, no key required, rate limit: 3 req/sec).

```
--query <text>          Required. Search query
--max-results <N>       1-50 (default: 10)
--sort <type>           relevance | date (default: relevance)
--years <N>             Limit to last N years
```

Returns: PMID, title, authors, journal, year, DOI, abstract, MeSH terms, keywords, publication types.

### `scripts/semantic_scholar.py`
Semantic Scholar API (public, no key required, rate limit: 100 req/5 min).

```
--query <text>          Search query
--paper-id <id>         Paper ID (DOI:xxx, PMID:xxx, ArXiv:xxx)
--related               Get references of a paper (requires --paper-id)
--citations             Get papers citing a paper (requires --paper-id)
--max-results <N>       1-50 (default: 10)
--year-range <range>    e.g., "2020-2026" or "2023-"
```

Returns: title, authors, year, abstract, TLDR, citation count, influential citations, DOI, ArXiv ID, open-access PDF URL.

### `scripts/chain_entry.py`
Standard PharmaClaw chain interface. Searches both PubMed and Semantic Scholar, deduplicates, and sorts by citation impact.

Input keys: `query`, `compound`/`name`, `target`, `disease`, `mechanism`, `reaction`, `topic`, `doi`, `pmid`, `max_results`, `years`, `context`

Automatic query building: `{"compound": "aspirin", "disease": "colorectal cancer"}` → searches "aspirin colorectal cancer"

## Chaining

| From | Input | To |
|------|-------|----|
| Chemistry Query | Compound name/SMILES | **Literature** → find published studies |
| Catalyst Design | Reaction type | **Literature** → find catalyst optimization papers |
| **Literature** | Key findings | Pharmacology → validate claims |
| **Literature** | Synthesis references | Chemistry Query → retrosynthesis |
| **Literature** | Patent mentions | IP Expansion → FTO analysis |
