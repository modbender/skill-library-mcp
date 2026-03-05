---
name: skills-search-fts
description: Instantly find the best AI agent skills, tools, and capabilities from across the entire web.
version: 1.0.6
metadata:
  openclaw:
    requires:
      bins:
        - python3
    files: ["scripts/*"]
    emoji: "🚀"
---

# Global Skills Search

Stop building from scratch. This skill gives you instant access to a massive library of 240,000+ pre-built agent skills, specialized tool definitions, and expert system prompts indexed from across the internet.

## Why use this?

Discover existing high-quality capabilities for any task—fast. Whether you need a specialized web scraper, a financial analyzer, or a niche API integration, this search engine finds the most relevant, battle-tested agent tools available.

## Usage

Search by keywords to find exactly the capabilities you need.

```bash
python3 scripts/search.py "YOUR_QUERY"
```

## Example Queries

- **Basic**: `python3 scripts/search.py "browser automation"`
- **Multi-Skill**: `python3 scripts/search.py "reddit AND sentiment analysis"`
- **Specific**: `python3 scripts/search.py "stripe payment integration"`

## Response Format

The search tool returns a prioritized list of matching skills, including their names, origins, and descriptions.

## Privacy & Security Disclosure

> [!IMPORTANT]
> **Data Transit**: This skill forwards your search queries to an external API to perform the high-speed full-text search against the discovery index.
>
> **Best Practices**: 
> - **Sensitive Data**: Avoid including API keys, passwords, or PII (Personally Identifiable Information) in search queries.
> - **Provenance**: This service is managed by the skill publisher to provide a centralized hub for 240,000+ public agent capabilities.
