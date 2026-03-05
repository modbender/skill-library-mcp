---
name: pubmed2blog
description: Transform PubMed papers into SEO-optimized healthcare blog articles
bins:
  - pubmed2blog
install: npm install -g pubmed2blog
requires: []
---

# pubmed2blog Skill

This skill provides access to the `pubmed2blog` CLI tool for converting PubMed papers into blog articles.

## Commands

### discover
Search PubMed for relevant studies ranked by blog suitability.
```
pubmed2blog discover "cardiovascular prevention"
pubmed2blog discover "sleep quality" --days 30 --tier tier1,tier2
```

### extract
Fetch full paper details from PubMed.
```
pubmed2blog extract 39847521
pubmed2blog extract 39847521 --json
```

### generate
Generate a blog article from a PubMed paper.
```
pubmed2blog generate 39847521 --type research-explainer
pubmed2blog generate 39847521 --type patient-facing --lang en,de --save
```

### pipeline
Full pipeline: discover + extract + generate.
```
pubmed2blog pipeline "sleep quality" --top 3 --save
```

### init
Interactive setup for API keys and preferences.
```
pubmed2blog init
```

## Article Types

- **research-explainer**: Study findings for lay audience
- **patient-facing**: Accessible, no jargon
- **differentiation**: "Why we don't offer X"
- **service-connection**: Connect findings to services

## Agent Usage

When using this skill as an agent:

1. Run `pubmed2blog discover <keyword>` to find relevant papers
2. Use `pubmed2blog extract <pmid>` to get full details
3. Generate with `pubmed2blog generate <pmid> --type <type> --save`
4. Deliver results to user in chat
5. Schedule via cron for regular content generation

## Setup

```bash
npm install -g pubmed2blog
pubmed2blog init
```

Supports Anthropic, OpenAI, and Z.AI providers.
