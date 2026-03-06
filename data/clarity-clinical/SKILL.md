---
name: clarity-clinical
description: >
  Query clinical variant data from ClinVar and gnomAD via Clarity Protocol.
  Use when the user asks about ClinVar classification, clinical significance,
  pathogenicity, gnomAD frequency, population genetics, or clinical data for gene.
  Capabilities: search clinical variants by gene, get detailed variant annotations.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Optional CLARITY_API_KEY env var for 100 req/min (vs 10 req/min).
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Clinical Skill

Access clinical variant annotations from ClinVar and population frequency data from gnomAD through Clarity Protocol's integrated database.

## Quick Start

List all clinical variants:

```bash
python scripts/query_clinical.py
```

Filter by gene symbol:

```bash
python scripts/query_clinical.py --gene-symbol MAPT
```

Get details for a specific variant:

```bash
python scripts/query_clinical.py --gene MAPT --variant NM_005910.6:c.926C>T
```

Get variant details in readable format:

```bash
python scripts/query_clinical.py --gene MAPT --variant NM_005910.6:c.926C>T --format summary
```

## Clinical Variant Fields

Each clinical variant includes:

- `gene_symbol`: HGNC gene symbol
- `variant_notation`: Full HGVS notation (transcript-based)
- `clinvar_significance`: Clinical significance classification (e.g., "Pathogenic", "Benign")
- `clinvar_review_status`: Review status stars (e.g., "criteria provided, multiple submitters")
- `clinvar_last_evaluated`: Date of last ClinVar evaluation
- `gnomad_af`: Allele frequency in gnomAD (population prevalence)
- `gnomad_ac`: Allele count in gnomAD
- `gnomad_an`: Total allele number in gnomAD
- `fetched_at`: When this data was retrieved from ClinVar/gnomAD

## ClinVar Significance Values

- **Pathogenic**: Strong evidence for disease causation
- **Likely pathogenic**: Moderate evidence for disease causation
- **Benign**: Strong evidence of no disease causation
- **Likely benign**: Moderate evidence of no disease causation
- **Uncertain significance**: Insufficient evidence
- **Conflicting interpretations**: Disagreement among submitters

## gnomAD Frequency Interpretation

- **af < 0.0001**: Very rare (< 0.01%)
- **af < 0.001**: Rare (< 0.1%)
- **af < 0.01**: Uncommon (< 1%)
- **af >= 0.01**: Common (>= 1%)

## Rate Limits

- **Anonymous (no API key)**: 10 requests/minute
- **With API key**: 100 requests/minute

To use an API key, set the `CLARITY_API_KEY` environment variable:

```bash
export CLARITY_API_KEY=your_key_here
python scripts/query_clinical.py --gene-symbol MAPT
```

Get your API key at https://clarityprotocol.io

## Error Handling

**404 Not Found**: The specified gene/variant combination does not exist in the clinical database.

**429 Rate Limit**: You've exceeded the rate limit. The script will display how long to wait.

**500 Server Error**: The API server encountered an error. Try again later.

**Timeout**: The request took longer than 30 seconds.

## Pagination

Clinical variant lists are paginated. The API returns a `next_cursor` field if more results are available.

## Use Cases

- Check if a variant is pathogenic in ClinVar
- Get population frequency data for a mutation
- Compare clinical significance across variants in a gene
- Assess variant review status quality
- Filter common vs. rare variants using gnomAD
