---
name: clarity-submit
description: >
  Submit a protein variant hypothesis to Clarity Protocol for validation and folding.
  Use when the user asks to submit a hypothesis, propose a protein variant, queue a fold,
  or investigate a mutation. Requires CLARITY_WRITE_KEY env var.
  Capabilities: submit hypothesis, check submission status.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Requires CLARITY_WRITE_KEY env var for write access.
metadata:
  author: clarity-protocol
  version: "1.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Submit Skill

Submit protein variant hypotheses to Clarity Protocol for automated validation and ColabFold structural prediction.

## Quick Start

Submit a hypothesis:

```bash
python scripts/submit_hypothesis.py --protein SOD1 --variant A4V --rationale "ALS-linked mutation with unknown structural impact"
```

Submit with optional fields:

```bash
python scripts/submit_hypothesis.py --protein MAPT --variant P301L --rationale "Tau pathology in frontotemporal dementia" --wallet "YOUR_SOLANA_WALLET"
```

Check hypothesis status:

```bash
python scripts/check_status.py --id 42
```

## Setup

Set your write API key:

```bash
export CLARITY_WRITE_KEY=your_write_key_here
```

Contact the Clarity Protocol team to request a write API key.

## What Happens After Submission

1. **Feasibility validation** runs automatically against UniProt, ClinVar, gnomAD, and PubMed
2. If validated, the hypothesis is **auto-queued** for ColabFold structural prediction
3. Four AI research agents continuously monitor the variant for new findings
4. Results are available at the tracking URL returned after submission

## Request Fields

- `--protein` (required): Protein name (e.g., SOD1, MAPT, APP, SNCA)
- `--variant` (required): Variant notation (e.g., A4V, P301L, G2019S)
- `--rationale` (required): Why this variant is worth investigating (min 10 characters)
- `--disease` (optional): Disease area (auto-detected from protein if omitted)
- `--wallet` (optional): Solana wallet address for $FOLD reward eligibility

## Response Fields

- `id`: Unique hypothesis identifier
- `protein_name`: Normalized protein name
- `variant_notation`: Variant as submitted
- `status`: Current status (submitted, validating, validated, queued, folding, complete, rejected)
- `tracking_url`: URL to track progress on clarityprotocol.io

## Rate Limits

- **Write (POST)**: 10 submissions per day per key
- **Read (GET)**: 100 requests per minute per key

## Size Limits

Proteins up to 1,500 residues can be folded. Larger proteins (e.g., LRRK2 at 2,527 residues) exceed hardware capacity and will be rejected during validation.

## Error Handling

**403 Forbidden**: Invalid or missing write API key. Set CLARITY_WRITE_KEY env var.

**422 Validation Error**: Invalid input (protein name empty, rationale too short, etc.).

**429 Rate Limit**: You've exceeded 10 submissions/day. Wait until tomorrow.

## Use Cases

- Programmatically submit variants for investigation
- Integrate Clarity Protocol into research pipelines
- Batch submission of variants of interest
- Agent-driven hypothesis generation and submission
