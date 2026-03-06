---
name: Auto-Research Skill
description: An autonomous research agent for OpenClaw that searches,
  synthesizes, and stores findings with full source tracking.
---

# Auto-Research Skill

An autonomous research agent for OpenClaw that searches, synthesizes, and stores findings with full source tracking.

## Overview

This skill enables OpenClaw to conduct autonomous research on any topic, compiling structured briefings with executive summaries, key findings, and actionable recommendations. Research outputs are stored in your Obsidian vault and vectorized in Qdrant for semantic retrieval.

## Usage

### Natural Language Triggers

- `"Research [topic]"` - Standard depth research
- `"Quick research on [topic]"` - Fast scan (5 sources)
- `"Deep dive into [topic]"` - Comprehensive analysis (10+ sources)

### Command Line Usage

```bash
# Quick scan - 5 sources, 1-page summary
./clawhub-skills/auto-research/research.sh "AI agents 2026" quick

# Standard research - 7 sources, full briefing
./clawhub-skills/auto-research/research.sh "construction CRM software" standard

# Deep dive - 10+ sources, comprehensive analysis
./clawhub-skills/auto-research/research.sh "quantum computing breakthroughs" deep
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BRAVE_API_KEY` | Brave Search API token | Uses built-in key |
| `OBSIDIAN_VAULT` | Path to Obsidian vault | `~/Documents/Obsidian/YoderVault` |
| `QDRANT_URL` | Qdrant server URL | `http://10.0.0.120:6333` |
| `REDIS_URL` | Redis cache server | `10.0.0.120:6379` |
| `RESEARCH_DEPTH` | Default depth level | `standard` |

### Depth Levels

| Level | Sources | Detail Level | Use Case |
|-------|---------|--------------|----------|
| `quick` | 5 | Brief summary | Fast fact-checking, initial exploration |
| `standard` | 7 | Full briefing | General research, decision support |
| `deep` | 10+ | Comprehensive | Strategic analysis, deep domain dives |

## Outputs

### 1. Obsidian Vault Briefing

**Location:** `Inbox/Research - {Topic} - {YYYY-MM-DD}.md`

**Structure:**
- **Executive Summary** - 3-5 sentence overview
- **Key Findings** - Bullet-point highlights
- **Detailed Analysis** - Organized by theme/subtopic
- **Sources** - Full citations with URLs and access dates
- **Action Items** - Recommendations and next steps
- **Confidence Rating** - High/Medium/Low based on source quality

### 2. Vectorized Knowledge (Qdrant)

**Collection:** `web_research`

Each research document is chunked into semantic segments and stored with:
- Source URL and title
- Research topic tags
- Publication/access date
- Confidence metadata

## Features

### Source Quality Assessment

Research automatically evaluates source credibility:

**High Confidence:**
- Academic institutions (.edu)
- Government sources (.gov)
- Major news organizations
- Industry-leading publications

**Medium Confidence:**
- Established tech blogs
- Company press releases
- Trade publications

**Low Confidence:**
- Anonymous forums
- Unverified blogs
- Outdated sources (>3 years)

### Smart Caching

Search results are cached for 24 hours to avoid redundant API calls:

- **Primary:** Redis (if available)
- **Fallback:** Local file cache in `/tmp/research-cache/`

Cache key format: `research:{topic_hash}:{depth}`

### Vector Search Integration

Once stored in Qdrant, research becomes discoverable via:

```bash
# Search your research corpus
./tools/yoder-kb.sh search "your query" 5 --collection web_research
```

## File Structure

```
clawhub-skills/auto-research/
├── SKILL.md                    # This documentation
├── research.sh                 # Main research orchestrator
├── vectorize.sh               # Qdrant vectorization
├── briefing-template.md       # Output format template
└── search-cache.sh           # Result caching utility
```

## Dependencies

### Required (Pre-installed)
- `curl` - API requests
- `jq` - JSON processing
- `python3` - Vectorization script

### Optional
- `redis-cli` - For distributed caching
- `obsidian-cli` - Vault integration

## Example Output

```markdown
# Research: Construction CRM Software 2026

**Date:** 2026-02-07  
**Depth:** Standard  
**Sources:** 7  
**Confidence:** High

## Executive Summary

The construction CRM market in 2026 is dominated by integrated platforms 
combining project management, client relationship tracking, and field 
mobility. Key players include Procore, Buildertrend, and emerging AI-
powered solutions like Attentive.ai. Mobile-first design and AI 
automation are the primary differentiators.

## Key Findings

- **Market Leaders:** Procore maintains ~35% market share with enterprise focus
- **AI Integration:** 60% of new platforms incorporate predictive analytics
- **Mobile Priority:** Field-accessible CRMs show 3x higher adoption rates
- **Pricing Trends:** Average $99-299/seat/month for full-featured platforms

[... detailed analysis continues ...]
```

## Integration with OpenClaw

### As a Skill

When placed in `clawhub-skills/auto-research/`, OpenClaw automatically:

1. Parses natural language research requests
2. Calls `research.sh` with appropriate parameters
3. Displays progress and final output path
4. Confirms vectorization success

### Standalone Usage

Scripts can run independently for automation:

```bash
# Daily research digest via cron
0 9 * * 1 /path/to/research.sh "weekly tech trends" quick
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No results returned | Check Brave API key; verify internet connection |
| Cache not working | Verify Redis is running at configured URL |
| Vault save fails | Check Obsidian vault path permissions |
| Vectorization fails | Verify Qdrant is accessible and collection exists |

## Version

**v1.0.0** - Initial release with Brave Search, Qdrant integration, and Obsidian output.

---

*Part of the ClawHub skill ecosystem for OpenClaw.*
