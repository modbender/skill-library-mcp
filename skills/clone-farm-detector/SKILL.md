---
name: clone-farm-detector
description: >
  Helps detect clone farming and reputation gaming in AI agent marketplaces.
  Identifies near-duplicate skills that wash IDs, batch-publish patterns,
  and artificial reputation inflation through coordinated uploads.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🧬"
---

# 40% of Marketplace Skills Are Clones — Detect Gene Farming Before It Erodes Trust

> Helps identify coordinated clone campaigns that flood agent marketplaces with near-duplicate skills to game reputation systems.

## Problem

Agent marketplaces rank skills by popularity, downloads, and publisher reputation. This creates an incentive to game the system: publish dozens of near-identical skills under different names, each citing the others, to artificially inflate metrics. The result? Genuine skills get buried under clones, search results become useless, and users can't distinguish real innovation from reputation farming. This is the AI equivalent of SEO spam — and most marketplaces have no defense against it.

## What This Checks

This detector examines a set of marketplace skills for clone farming indicators:

1. **Content similarity** — Compares Capsule source code and Gene summaries across skills. Near-identical content with trivially changed variable names, comments, or formatting suggests cloning
2. **Batch publish patterns** — Multiple skills published by the same node within a short time window, especially with sequential or templated naming
3. **ID washing** — Skills with different SHA-256 hashes but functionally identical code, achieved by injecting whitespace, comments, or no-op statements to bypass deduplication
4. **Cross-citation rings** — Skills that reference each other in dependency chains without functional necessity, creating artificial trust graphs
5. **Metadata templating** — Identical description structures, same emoji sets, copy-paste summaries with only the noun changed

## How to Use

**Input**: Provide one of:
- A list of Capsule/Gene JSON objects to compare
- A publisher node ID to scan their published catalog
- A marketplace search term to check top results for cloning

**Output**: A structured report containing:
- Cluster groups of similar/identical skills
- Similarity scores between flagged pairs
- Publishing timeline analysis
- Risk rating: CLEAN / SUSPECT / FARMING
- Evidence summary for each cluster

## Example

**Input**: Scan top 10 results for "code formatter" on marketplace

```
🧬 FARMING DETECTED — 2 clone clusters found

Cluster A (4 skills, 92% avg similarity):
  - "python-formatter-pro"     published 2024-12-01 08:01
  - "py-code-beautifier"       published 2024-12-01 08:03
  - "format-python-fast"       published 2024-12-01 08:07
  - "python-style-fixer"       published 2024-12-01 08:12
  Publisher: same node (node_a8f3...)
  Technique: variable rename + comment injection
  ID washing: 4 unique hashes, 1 functional implementation

Cluster B (2 skills, 87% similarity):
  - "js-lint-helper"           published 2024-12-02
  - "javascript-lint-tool"     published 2024-12-02
  Publisher: same node (node_a8f3...)
  Cross-cites Cluster A skills as "dependencies"

Total: 6/10 top results are clones from one publisher.
Recommendation: Flag publisher for review. Genuine skills in results: 4/10.
```

## Limitations

Similarity detection helps surface likely clones but cannot prove intent. Legitimate forks, templates, and educational variations may trigger false positives. High similarity alone is an indicator, not a verdict — human review is recommended for final determination.
