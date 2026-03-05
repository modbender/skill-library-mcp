# Research Library Search Guide

This guide explains how the search and ranking system works in the Research Library.

## Overview

The Research Library uses SQLite FTS5 (Full-Text Search version 5) to provide fast, relevant search across research entries and their attachments. The system combines:

1. **FTS5 Relevance** - SQLite's BM25 text matching score
2. **Material Type Weighting** - Reference materials rank higher than research
3. **Confidence Scoring** - Higher confidence documents rank higher
4. **Recency Scoring** - Newer documents get a small boost

## Ranking Formula

```
final_score = (fts5_normalized × material_weight × 0.5) 
            + (confidence × 0.3) 
            + (recency_score × 0.2)
```

### Component Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Relevance | 0.5 | FTS5 score × material weight |
| Confidence | 0.3 | Document reliability (0.0-1.0) |
| Recency | 0.2 | How recently updated (0.1-1.0) |

### Material Type Weights

| Type | Weight | Description |
|------|--------|-------------|
| `reference` | 1.0 | Verified specs, datasheets, official docs |
| `research` | 0.5 | Blog posts, tutorials, experiments |

## Material Type System

### Reference Materials (weight 1.0)

Reference materials are authoritative, verified documents:
- Datasheets and specifications
- Official documentation
- Proven, deployed code
- Manufacturer specs

**Requirement:** Reference materials MUST have confidence ≥ 0.8

### Research Materials (weight 0.5)

Research materials are exploratory, potentially unverified:
- Blog posts and tutorials
- Forum discussions
- Experimental notes
- External libraries

**No minimum confidence required**

## Examples

### Example 1: Reference Beats Research at Same Relevance

Given two documents matching "servo tuning":

| Document | Material Type | Confidence | Age (days) | FTS5 Score |
|----------|--------------|------------|------------|------------|
| Servo Datasheet | reference | 0.95 | 30 | -25 |
| Blog Tutorial | research | 0.95 | 30 | -25 |

**Calculation:**

Servo Datasheet (Reference):
```
fts5_normalized = 0.70 (from -25)
material_weight = 1.0
relevance = 0.70 × 1.0 × 0.5 = 0.35
confidence = 0.95 × 0.3 = 0.285
recency = 0.96 × 0.2 = 0.192
TOTAL = 0.827
```

Blog Tutorial (Research):
```
fts5_normalized = 0.70 (same)
material_weight = 0.5
relevance = 0.70 × 0.5 × 0.5 = 0.175
confidence = 0.95 × 0.3 = 0.285
recency = 0.96 × 0.2 = 0.192
TOTAL = 0.652
```

**Result:** Reference ranks first (0.827 > 0.652)

### Example 2: High-Confidence Research Can Beat Low-Confidence Reference

| Document | Material Type | Confidence | Age | FTS5 |
|----------|--------------|------------|-----|------|
| Old Spec | reference | 0.80 | 500 | -10 |
| Lab Notes | research | 0.95 | 7 | -30 |

Old Spec:
```
relevance = 0.50 × 1.0 × 0.5 = 0.25
confidence = 0.80 × 0.3 = 0.24
recency = 0.45 × 0.2 = 0.09
TOTAL = 0.58
```

Lab Notes:
```
relevance = 0.74 × 0.5 × 0.5 = 0.185
confidence = 0.95 × 0.3 = 0.285
recency = 0.99 × 0.2 = 0.198
TOTAL = 0.668
```

**Result:** Recent, high-confidence research (0.668) beats old, low-confidence reference (0.58)

## Project Scoping

### Single Project Search

Search within a specific project:

```python
results = searcher.search_project("rc-quadcopter", "servo motor")
```

Uses index `idx_research_project_type` for fast filtering.

### Cross-Project Search

Search across all projects:

```python
results = searcher.search_all_projects("PID tuning")
```

Results include `project_id` for grouping:
```
rc-quadcopter: Servo PID Tuning Notes
robotic-arm: Joint PID Configuration
arduino-projects: PWM Control Tutorial
```

### Project Filter in General Search

```python
results = searcher.search(
    "motor",
    project_id="rc-quadcopter",
    material_type="reference",
    confidence_min=0.8
)
```

## Confidence Scoring

### Validation Rules

Reference materials must meet quality threshold:

```python
validate_material_type("reference", 0.9)  # True
validate_material_type("reference", 0.5)  # False - too low!
validate_material_type("research", 0.1)   # True - no minimum
```

### Automatic Confidence Scoring

When confidence isn't explicitly set:

```python
score = searcher.score_confidence(
    source_type="reference",  # or "research"
    recency_days=30
)
```

Heuristic:
- Reference starts at 0.9 base
- Research starts at 0.6 base
- Recent (<30 days): +0.05
- Old (>1 year): -0.1
- Very old (>2 years): -0.2

## Cross-Project Linking

The `research_links` table tracks relationships between research entries.

### Link Types

| Type | Description | Example |
|------|-------------|---------|
| `applies_to` | Code/spec applies to component | "Servo library applies to quadcopter" |
| `contradicts` | Information conflicts | "Blog A contradicts Blog B" |
| `supersedes` | Newer version replaces older | "Spec v2 supersedes v1" |
| `related` | Generally related (weak) | "Both about motor control" |
| `references` | Explicitly cited | "Paper A references Paper B" |

### Getting Linked Research

```python
# Get all links for a research entry
links = searcher.get_linked_research(research_id=42)

for link in links:
    print(f"{link.link_type}: {link.research_title}")
# Output:
# applies_to: RC Quadcopter Motor Assembly
# related: Servo Tuning Best Practices

# Filter by link type
superseding = searcher.get_linked_research(42, link_types=["supersedes"])

# Find contradicting info
contradictions = searcher.get_contradicting_research(42)
```

### Cross-Project Discovery

Find research in other projects that relates to your current work:

```python
# Research entry 5 is in project "rc-quadcopter"
# Find related entries in OTHER projects
links = searcher.get_linked_research(5, include_both_directions=True)

for link in links:
    if link.research_project_id != "rc-quadcopter":
        print(f"Related in {link.research_project_id}: {link.research_title}")
# Output:
# Related in robotic-arm: PID Tuning Methodology
```

## Query Syntax

### Basic Search

```python
results = searcher.search("servo tuning")
```

### Phrase Search

```python
results = searcher.search('"servo motor"')  # Exact phrase
```

### Boolean Operators

```python
results = searcher.search("servo AND tuning")
results = searcher.search("motor OR servo")
results = searcher.search("servo NOT dc")
```

### Filters

```python
results = searcher.search(
    "motor",
    project_id="rc-quadcopter",      # Single project
    material_type="reference",        # Only references
    confidence_min=0.8,               # High confidence
    catalog="real_world",             # External sources only
    include_attachments=True,         # Search PDFs too
    limit=20,                         # Pagination
    offset=0
)
```

## Performance

### Query Latencies (20 documents)

| Operation | Latency | Target |
|-----------|---------|--------|
| Basic FTS5 search | <1ms | <100ms |
| Project-scoped search | <1ms | <100ms |
| Link traversal | <1ms | <100ms |

### Indexes Used

- `idx_research_project_type` - Project + material filtering
- `idx_research_project_created` - Temporal queries
- `idx_research_links_source_type` - Link traversal
- `idx_research_links_relevance` - Strong links filter
- FTS5 internal indexes - Full-text search

## API Reference

### ResearchSearch Class

```python
from reslib import ResearchSearch

searcher = ResearchSearch(db_path="~/.openclaw/research/library.db")

# Basic search
results = searcher.search("query")

# Project search
results = searcher.search_project("project-id", "query")

# Cross-project
results = searcher.search_all_projects("query")

# Linked research
links = searcher.get_linked_research(research_id)

# File usage
usage = searcher.get_file_usage(attachment_id)

# Validation
is_valid = searcher.validate_material_type("reference", 0.9)

# Auto-score confidence
confidence = searcher.score_confidence("research", recency_days=30)

# Debug
explanation = searcher.explain_search("servo", limit=5)
```

### SearchResult Object

```python
result.research_id       # int: Database ID
result.title             # str: Entry title
result.content           # str: Full content
result.summary           # str: Summary
result.project_id        # str: Project identifier
result.material_type     # str: "reference" or "research"
result.confidence        # float: 0.0-1.0
result.catalog           # str: "real_world" or "openclaw"
result.created_at        # str: ISO timestamp
result.updated_at        # str: ISO timestamp
result.fts5_score        # float: Raw FTS5 score
result.rank_score        # float: Final ranking score
result.source_type       # str: "research" or "attachment"
result.attachment_id     # int: If from attachment
result.attachment_filename  # str: If from attachment
result.snippet           # str: Context snippet
```

### LinkedResult Object

```python
link.link_id              # int: Link database ID
link.source_research_id   # int: Source entry
link.target_research_id   # int: Target entry
link.link_type            # str: applies_to, contradicts, etc.
link.relevance_score      # float: 0.0-1.0
link.reason               # str: Why linked
link.research_title       # str: Title of linked entry
link.research_project_id  # str: Project of linked entry
link.research_material_type  # str: Material type
link.research_confidence  # float: Confidence
```

## Best Practices

1. **Tag material types accurately** - Reference vs Research matters for ranking
2. **Set confidence levels** - Higher confidence = better visibility
3. **Use project scoping** - Faster searches, relevant results
4. **Create meaningful links** - Cross-project discovery depends on links
5. **Update timestamps** - Recency affects ranking
6. **Extract attachment text** - PDFs/code become searchable

## Troubleshooting

### No Results?

1. Check query syntax - use quotes for special characters
2. Verify project_id exists
3. Check confidence_min isn't too restrictive
4. Ensure attachments have extracted_text

### Unexpected Ranking?

Use `explain_search()` to debug:

```python
print(searcher.explain_search("servo", limit=3))
```

Output shows component breakdown:
```
#1: Servo Motor Datasheet
    Type: REFERENCE (weight: 1.0)
    Confidence: 0.95
    FTS5 Score: -25.0
    Rank Score: 0.8274
    Components:
      - Relevance: 0.3500
      - Confidence: 0.2850
      - Recency: 0.1924
```

### Slow Queries?

1. Ensure indexes exist (check with `PRAGMA index_list(research)`)
2. Use project_id filter when possible
3. Add confidence_min to reduce result set
4. Use limit/offset for pagination
