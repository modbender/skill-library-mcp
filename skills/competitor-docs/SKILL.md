---
name: competitor-docs
description: Search and analyze competitor documentation archives using full-text search (FTS). Use when you need to find information in structured documentation folders containing articles with source URLs (marked with "*Source:" pattern). Provides fast BM25-ranked search across thousands of articles with automatic source URL extraction for citations. Ideal for competitive intelligence research, feature comparisons, and documentation lookups. Requires indexing documentation first with `docs.py index`.
---

# Competitor Documentation Search

Fast, indexed full-text search across competitor documentation using SQLite FTS5 with BM25 relevance ranking.

## When to Use

- Searching competitor documentation for specific features, capabilities, or limitations
- Finding official source URLs to cite in research reports
- Comparing documentation across multiple competitors
- Looking up technical specifications or configuration details

## Document Format Expected

Articles separated by `---` delimiter with `*Source:` URL:

```markdown
# Article Title

*Source: https://documentation.vendor.com/path/to/article.html*

Article content here...

---

# Next Article Title

*Source: https://documentation.vendor.com/another/article.html*

More content...
```

## Quick Start

```bash
# 1. Index the documentation (one-time or when docs change)
scripts/docs.py index ./docs

# 2. Search
scripts/docs.py search "kubernetes backup" --max 5

# 3. Check index status
scripts/docs.py status
```

## Primary Tool: docs.py

The unified CLI handles all operations:

### Indexing

```bash
# Index documentation directory
scripts/docs.py index ./docs

# Force full rebuild
scripts/docs.py index ./docs --rebuild

# Custom database location
scripts/docs.py index ./docs --db /path/to/custom.db
```

### Searching

```bash
# Basic search
scripts/docs.py search "kubernetes backup"

# Boolean operators
scripts/docs.py search "AWS AND S3 AND snapshot"

# Phrase search
scripts/docs.py search '"exact phrase match"'

# Prefix search
scripts/docs.py search "kube*"

# Exclude terms
scripts/docs.py search "backup NOT restore"

# Title-only search
scripts/docs.py search "kubernetes" --title-only

# Output formats
scripts/docs.py search "kubernetes" --format json
scripts/docs.py search "kubernetes" --format markdown

# More context around matches
scripts/docs.py search "kubernetes" --context 400

# Include full content in JSON
scripts/docs.py search "kubernetes" --format json --full-content
```

### FTS5 Query Syntax

| Syntax | Meaning |
|--------|---------|
| `term1 term2` | Documents with term1 OR term2 (ranked) |
| `term1 AND term2` | Documents with both terms |
| `term1 OR term2` | Documents with either term |
| `"exact phrase"` | Exact phrase match |
| `prefix*` | Words starting with prefix |
| `term1 NOT term2` | term1 without term2 |
| `title:term` | Search only titles |

### Getting Specific Articles

```bash
# Get article by partial URL or title
scripts/docs.py get "system_requirements_for_kubernetes" --full

# Find all matching articles
scripts/docs.py get "backup" --all
```

### Status

```bash
# Check index statistics
scripts/docs.py status
```

## Workflow for Research Tasks

### Discovery Phase

```bash
# Check what's indexed
scripts/docs.py status

# Explore topics with broad searches
scripts/docs.py search "<feature>" --max 20
```

### Research Phase

```bash
# Narrow down with boolean operators
scripts/docs.py search "<feature> AND <platform>"

# Find limitations
scripts/docs.py search "limitation OR restriction OR 'not supported'"

# Version-specific info
scripts/docs.py search '"11.42" OR "12.0"'
```

### Citation Phase

Every search result includes the `Source:` URL — use this in your reports:

```markdown
According to Commvault documentation, Kubernetes backup requires...

Source: https://documentation.commvault.com/11.42/software/kubernetes.html
```

## Multi-Competitor Setup

Each agent can have their own documentation and index:

```
~/OpenClaw/CI/frodo/docs/CommvaultDocumentation/
    ├── commvault_cloud_docs_part_01.md
    ├── competitor_docs.db      # Index lives with docs
    └── ...

~/OpenClaw/CI/sam/docs/DattoDocumentation/
    ├── datto_docs.md
    ├── competitor_docs.db
    └── ...
```

The `docs.py` script auto-detects the database location.

## Advanced Scripts

For specialized needs:

- `scripts/fts_search.py` — Direct FTS5 search with more options
- `scripts/index_docs.py` — Standalone indexing
- `scripts/list_sources.py` — List all source URLs
- `scripts/get_article.py` — Direct article retrieval
- `scripts/search_docs.py` — Regex-based search (no index needed)

## CI Research Patterns

For common competitive intelligence search patterns, see [references/ci-patterns.md](references/ci-patterns.md).

## Example Research Session

```bash
# What's available?
scripts/docs.py status
# Output: Files indexed: 37, Articles indexed: 32065

# Find Kubernetes backup info
scripts/docs.py search "kubernetes backup" --max 5

# Narrow to specific platform
scripts/docs.py search "kubernetes AND AWS" --max 5

# Find limitations
scripts/docs.py search "kubernetes AND (limitation OR 'not supported')"

# Get full article for citation
scripts/docs.py get "system_requirements_for_kubernetes" --full
```

## Best Practices

1. **Index once, search many times** — FTS5 is fast because it's indexed
2. **Use boolean operators** — `AND`, `OR`, `NOT` for precision
3. **Phrase search for exact terms** — `"exact match"` with quotes
4. **Always cite sources** — Include `Source:` URLs in reports
5. **Rebuild periodically** — Re-index when documentation updates
6. **Use JSON for analysis** — Pipe to `jq` or other tools for processing