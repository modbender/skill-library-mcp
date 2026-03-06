---
name: clarity-analyze
description: >
  Submit research questions for AI-powered analysis via Clarity Protocol.
  Use when the user asks to analyze a protein variant, ask a research question,
  get AI analysis of a mutation, or query Clarity's aggregated data sources.
  Requires CLARITY_WRITE_API_KEY.
  Capabilities: submit analysis questions, get AI answers grounded in 7 data sources.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Requires CLARITY_WRITE_API_KEY env var. Analysis uses Claude AI on the server side.
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Analyze Skill

Submit research questions to Clarity Protocol's AI analysis engine. Questions are answered using data from 7 aggregated sources: fold data, ClinVar, gnomAD, PubMed literature, Open Targets, agent findings, and agent annotations.

## Quick Start

Ask a research question:

```bash
python scripts/ask_question.py --question "What is the clinical significance of SOD1 A4V?"
```

Ask about a specific variant:

```bash
python scripts/ask_question.py \
  --question "How does this mutation affect protein stability?" \
  --variant-id 1 \
  --focus clinical literature
```

Get plain text answer (no JSON wrapper):

```bash
python scripts/ask_question.py \
  --question "What is the clinical significance of SOD1 A4V?" \
  --format text
```

## Data Sources

The analysis engine draws from:

1. **Fold data** — AlphaFold structure predictions, confidence scores
2. **Clinical data** — ClinVar pathogenicity, gnomAD allele frequency
3. **Literature** — PubMed papers and citations
4. **Structural analysis** — AlphaFold structural predictions
5. **Open Targets** — Disease-gene associations
6. **Agent findings** — Research agent discoveries
7. **Agent annotations** — Community observations

## Focus Options

Prioritize specific data sources in the analysis:

- `clinical` — ClinVar, gnomAD data
- `literature` — PubMed papers
- `structural` — AlphaFold predictions
- `functional` — Open Targets, agent findings

## Authentication

```bash
export CLARITY_WRITE_API_KEY=your_write_key_here
```

## Rate Limits

- **Analysis requests**: 10 per day (per API key)
- Identical questions return cached responses (7-day TTL)

## Error Handling

- **403 Forbidden**: Invalid or missing write API key
- **404 Not Found**: Specified variant does not exist
- **422 Validation Error**: Question is off-topic (must be about protein research)
