# Pipeline Examples

This directory contains example pipeline configurations demonstrating the staged processing pattern.

## Available Examples

### content-pipeline.json
A 5-stage pipeline for content creation workflows:

```
Input → Extract → Analyze → Write → Review → Finalize → Output
```

**Stages:**
1. **Extract** - Pull key facts and information from source material
2. **Analyze** - Identify patterns, insights, and implications
3. **Write** - Create structured content based on analysis
4. **Review** - Quality check with improvement recommendations
5. **Finalize** - Format and polish for publication

**Usage:**
```bash
claw agent-orchestrator pipeline \
  --config skills/agent-orchestrator/examples/content-pipeline.json \
  --input "Your topic or source material here"
```

Or load with explicit input:
```bash
claw agent-orchestrator pipeline \
  --config skills/agent-orchestrator/examples/content-pipeline.json \
  --task "Research Bitcoin Lightning adoption trends in 2026"
```

## Creating Custom Pipelines

Pipeline configs are JSON files with this structure:

```json
{
  "name": "my-pipeline",
  "description": "What this pipeline does",
  "input_data": "Default input (optional)",
  "context_passing": "full|summary|minimal",
  "verbose": true,
  "stages": [
    {
      "name": "stage-name",
      "type": "extract|transform|validate|enrich|analyze|write|review|format|custom",
      "prompt": "Specific instructions for this stage",
      "timeout": 300,
      "on_failure": "stop|continue|skip",
      "gate_check": "Validation criteria (for validate stages)",
      "output_format": "Expected output format description"
    }
  ]
}
```

## Stage Types

- **extract** - Pull information from input
- **transform** - Modify/summarize/expand data
- **validate** - Check quality, gate progression
- **enrich** - Add context or detail
- **analyze** - Deep analysis and insights
- **write** - Content creation
- **review** - Critical review and feedback
- **format** - Convert to final output format
- **custom** - User-defined behavior

## Context Passing

Control how much data flows between stages:

- **full** (default) - Pass entire previous output
- **summary** - Pass condensed version (first 2000 chars)
- **minimal** - Pass only essential metadata

## Failure Handling

Each stage can specify what happens on failure:

- **stop** (default) - Halt pipeline immediately
- **continue** - Continue with warning logged
- **skip** - Skip the failed stage, use previous output

Useful for validation gates that must pass vs. optional enrichment stages.
