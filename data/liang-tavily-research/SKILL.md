---
name: tavily-research
description: Comprehensive research grounded in web data with explicit citations. Use when you need multi-source synthesis—comparisons, current events, market analysis, detailed reports.
homepage: https://tavily.com
metadata: {"openclaw":{"emoji":"📊","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Tavily Research

Conduct comprehensive research on any topic with automatic source gathering, analysis, and response generation with citations.

## Authentication

Get your API key at https://tavily.com and add to your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "tavily-research": {
        "enabled": true,
        "apiKey": "tvly-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Or set the environment variable:
```bash
export TAVILY_API_KEY="tvly-YOUR_API_KEY_HERE"
```

## Quick Start

### Using the Script

```bash
node {baseDir}/scripts/research.mjs "query"
node {baseDir}/scripts/research.mjs "query" --pro
node {baseDir}/scripts/research.mjs "query" --output report.md
```

### Examples

```bash
# Quick overview
node {baseDir}/scripts/research.mjs "What is retrieval augmented generation?"

# Comprehensive analysis
node {baseDir}/scripts/research.mjs "LangGraph vs CrewAI for multi-agent systems" --pro

# Market research with output file
node {baseDir}/scripts/research.mjs "Fintech startup landscape 2025" --pro --output fintech-report.md

# Technical comparison
node {baseDir}/scripts/research.mjs "React vs Vue vs Svelte" --pro
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model <model>` | Model: `mini`, `pro`, `auto` | `mini` |
| `--output <file>` | Save report to file | - |
| `--json` | Output raw JSON | false |

## Model Selection

**Rule of thumb**: "what does X do?" → mini. "X vs Y vs Z" or "best way to..." → pro.

| Model | Use Case | Speed |
|-------|----------|-------|
| `mini` | Single topic, targeted research | ~30s |
| `pro` | Comprehensive multi-angle analysis | ~60-120s |
| `auto` | API chooses based on complexity | Varies |

## Output Format

The research includes:
- **AI-generated answer**: Comprehensive synthesis
- **Sources**: Citations with titles, URLs, and relevance scores
- **Metadata**: Query, response time, and statistics

## Tips

- Research can take 30-120 seconds depending on complexity
- Use `--pro` for comparisons, market analysis, or detailed reports
- Use `--output` to save reports for later reference
- The `auto` model lets Tavily choose based on query complexity