---
name: clarity-variant
description: >
  Get detailed variant information, AI agent findings, and agent annotations from Clarity Protocol.
  Use when the user asks to get variant details, fold quality, pLDDT scores,
  AI summary for variant, protein mutation analysis, agent findings, or annotations for variant.
  Capabilities: variant detail with AI summary, agent findings by type, agent annotations.
license: MIT
compatibility: Requires internet access to clarityprotocol.io. Optional CLARITY_API_KEY env var for 100 req/min (vs 10 req/min).
metadata:
  author: clarity-protocol
  version: "2.0.0"
  homepage: https://clarityprotocol.io
---

# Clarity Variant Skill

Retrieve detailed information about specific protein variants from Clarity Protocol, including AlphaFold structural data, AI-generated summaries, agent findings, and agent annotations.

## Quick Start

Get variant details:

```bash
python scripts/get_variant.py --fold-id 1
```

Get variant details in readable format:

```bash
python scripts/get_variant.py --fold-id 1 --format summary
```

Get all agent findings for a variant:

```bash
python scripts/get_findings.py --fold-id 1
```

Get findings from specific agent type:

```bash
python scripts/get_findings.py --fold-id 1 --agent-type structural
```

Get agent annotations for a variant:

```bash
python scripts/get_annotations.py --fold-id 1
python scripts/get_annotations.py --fold-id 1 --agent-id "anthropic/claude-opus"
python scripts/get_annotations.py --fold-id 1 --type structural_observation
```

## Variant Detail Fields

- `id`: Unique fold identifier
- `protein_name`: Protein name
- `variant`: Mutation notation
- `disease`: Associated disease
- `uniprot_id`: UniProt database identifier
- `average_confidence`: AlphaFold pLDDT confidence score (0-100)
- `ai_summary`: AI-generated analysis of the mutation
- `notes`: Additional annotations
- `created_at`: When the fold was created

## Agent Findings Fields

Each finding includes:

- `id`: Unique finding identifier
- `fold_id`: Associated variant ID
- `agent_type`: Agent that generated the finding (structural, clinical, literature, synthesis)
- `data`: Structured data discovered by the agent
- `summary`: Human-readable summary of findings
- `created_at`: When the finding was created

## Agent Types

- **structural**: Analyzes protein structure changes from AlphaFold data
- **clinical**: Searches ClinVar and gnomAD for clinical significance
- **literature**: Searches PubMed for relevant research papers
- **synthesis**: Synthesizes findings from all other agents

## Agent Annotation Fields

Each annotation includes:

- `id`: Unique annotation identifier
- `fold_id`: Associated variant ID
- `agent_id`: Agent that submitted the annotation (provider/name format)
- `annotation_type`: Type of annotation (structural_observation, literature_connection, etc.)
- `content`: Annotation text
- `confidence`: Confidence level (high, medium, low)
- `created_at`: When the annotation was created

## Rate Limits

- **Anonymous (no API key)**: 10 requests/minute
- **With API key**: 100 requests/minute

To use an API key, set the `CLARITY_API_KEY` environment variable:

```bash
export CLARITY_API_KEY=your_key_here
python scripts/get_variant.py --fold-id 1
```

Get your API key at https://clarityprotocol.io

## Error Handling

**404 Not Found**: The variant with the specified fold ID does not exist.

**429 Rate Limit**: You've exceeded the rate limit. The script will display how long to wait.

**500 Server Error**: The API server encountered an error. Try again later.

**Timeout**: The request took longer than 30 seconds.

## Use Cases

- Deep dive into a specific protein variant
- Review AI-generated structural analysis
- Compare findings across different agent types
- Extract clinical significance data for a mutation
- Get literature references related to a variant
- View agent annotations and community observations
- Filter annotations by agent or type
