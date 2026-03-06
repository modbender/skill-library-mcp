---
name: knowledge-graph
description: "Embedded knowledge graph for persistent structured knowledge. ALWAYS use proactively — do NOT wait for user to ask. Auto-triggers on: (1) any mention of people, projects, devices, services, organizations, or infrastructure — search KG first, add if new, (2) decisions or architectural choices worth remembering, (3) credentials or API keys (store in vault), (4) relationships between entities (who owns what, what runs where, what depends on what), (5) recurring concepts, principles, or lessons learned, (6) preferences and opinions (likes, dislikes, reviews), (7) places and locations (where someone lives, travels, frequents), (8) life events and milestones (birthdays, trips, meetings), (9) habits and routines (daily patterns, recurring behaviors), (10) knowledge artifacts — research papers, articles, insights, ideas, interesting facts shared by the user, (11) know-how and procedures — how to do something, debugging approaches, workflows, mental models, problem-solving frameworks. Also use when recalling facts, answering questions about known entities, or needing structured context. Run install script on first use. NOT for: ephemeral daily notes (use memory/), transient conversation, or rapidly changing data."
---

# Knowledge Graph Skill

Personal KG stored as JSON, queried via CLI scripts. Produces a compact KGML summary for session context.
Core instructions are in AGENTS.md (auto-injected by install). This file covers setup, advanced usage, and reference only.

## First-Time Setup

```bash
node scripts/install.mjs [--workspace /path/to/workspace] [--platform openclaw|claude|gemini]
```
Auto-detects platform and patches the agent instructions file (`AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`) with KG instructions + graph summary. Idempotent.

## KGML Format Reference

```
#KGML v2 | <count>e <count>r | depth:<N> | <date>
[category]
Label(Alias):type — attr1,attr2
  ChildLabel(CA):type — attrs    ← indent = parent>child
%rels
A>verb>B C>verb>D                ← cross-branch relations (aliases)
%vault key1,key2                 ← vault key names (no values)
```

## Advanced Query Commands

Beyond the basics in AGENTS.md (`find`, `traverse`, `rels`):
```bash
node scripts/query.mjs children <id>      # Direct children
node scripts/query.mjs type <type>         # All entities of a type
node scripts/query.mjs cat <category>      # All in category
node scripts/query.mjs orphans             # Unlinked entities
node scripts/query.mjs stats               # Graph statistics
node scripts/query.mjs recent [--days 7]   # Created/updated recently
node scripts/query.mjs timeline [--from YYYY-MM-DD] [--to YYYY-MM-DD]
node scripts/query.mjs changed             # Modified after creation
node scripts/query.mjs uncertain           # Confidence < 0.5
```

## Merge

```bash
node scripts/merge.mjs --target <id> --source <id> --mode absorb|nest
```

## Vault (secrets)

```bash
node scripts/vault.mjs set <key> <value> --note "description"
node scripts/vault.mjs get <key>          # Raw value (for piping)
node scripts/vault.mjs list               # Keys only
node scripts/vault.mjs del <key>
```

## Depth Heuristic — How Many Layers to Extract

Before adding a rich knowledge item (article, paper, report, system description), assess complexity first:

```bash
# Score text content and get recommended depth + checklist:
node scripts/depth-check.mjs "paste text or summary here"
echo "article text" | node scripts/depth-check.mjs
node scripts/depth-check.mjs --file /path/to/article.txt
node scripts/depth-check.mjs --json    # machine-readable

# Score interpretation:
# 0-1 → 1 layer (root only)
# 2-3 → 2 layers (root + concepts)
# 4-5 → 3 layers (root → domains → mechanisms)
# 6-7 → 4+ layers (full extraction with orgs/events/policies + cross-relations)
```

**Key rule:** Never stop at 2 layers for complex content. If score ≥ 4, extract all named orgs, events, policies, and cross-relations — not just the top-level themes.

## Visualization

```bash
node scripts/visualize.mjs                # → data/kg-viz.html
node scripts/visualize.mjs --output /tmp/graph.html
```
ALWAYS use this script. Do NOT write custom HTML. Output is self-contained, offline, no CDN.

Parent edges render as **blue dashed arrows** (60% opacity). Regular edges are red solid arrows.

## Configuration

All settings have sensible defaults. Override only what you need — config stores only your changes.

```bash
node scripts/config.mjs                       # list all settings with current values
node scripts/config.mjs get <key>              # get a value (e.g. summary.tokenBudget)
node scripts/config.mjs set <key> <value>      # set a value
node scripts/config.mjs reset <key>            # reset single key to default
node scripts/config.mjs reset --all            # reset everything
node scripts/config.mjs --json                 # full config as JSON
```

### Available Settings

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| **summary** | `tokenBudget` | 5000 | Max tokens for kg-summary.md |
| | `maxChildDepth` | auto | Tree depth (null=auto: 3/<100, 2/100-400, 1/>400) |
| | `maxAttrLen` | 40 | Max characters for attribute values |
| | `maxPerRoot` | 4 | Max relations shown per root subtree |
| | `compactThreshold` | 400 | Entity count for compact mode |
| | `mediumThreshold` | 200 | Entity count for medium depth |
| **validation** | `minEntities` | 30 | Min entities for extraction PASS |
| | `minRelationRatio` | 0.5 | Relations per entity ratio |
| | `minDepth` | 3 | Min hierarchy depth for PASS |
| | `minEvents` | 3 | Min event nodes for PASS |
| **depthCheck** | `entityCapForEstimate` | 50 | Cap NER count for target estimation |
| | `minEntitiesMultiplier` | 1.0 | Named entities → min target multiplier |
| | `extraEntities` | 30 | Added to min for max entity range |
| **consolidation** | `autoNest` | true | Auto-nest single-relation orphans |
| | `mergeSuggestions` | true | Suggest merges for similar labels |
| | `pruneEmptyAttrs` | true | Remove empty/null attrs |
| | `levenshteinThreshold` | 2 | Max edit distance for merge suggestions |
| **visualization** | `repulsion` | 5000 | Physics repulsion force |
| | `edgeRestLength` | 160 | Default edge rest length |
| | `overlapPenalty` | 3 | Overlap repulsion multiplier |
| | `simulationSteps` | 500 | Physics simulation iterations |
| | `initialSpread` | 1.5 | Initial node spread multiplier |
| | `zoomAnimationMs` | 400 | Zoom-to-node animation duration |

Config file: `data/kg-config.json` (per-agent, gitignored).

## Cross-Agent Access (read-only)

```javascript
import { createReader } from '<path-to-skill>/lib/reader.mjs';
const kg = createReader();
kg.search("query"); kg.traverse("id", { depth: 2 }); kg.stats();
```
Or CLI: `node scripts/export.mjs --format json --target /path/to/output.json`

## Memory Import

```bash
node scripts/import-memory.mjs            # dry-run
node scripts/import-memory.mjs --apply    # add with confidence 0.5
```
Then: `node scripts/query.mjs uncertain` to review auto-imported entities.

## Knowledge Entity Guide

The `knowledge` type covers both declarative and procedural knowledge. Use attrs and tags to differentiate:

| Kind | Tags | Key attrs | Example |
|------|------|-----------|---------|
| Fact/finding | `#fact`, `#til` | `source`, `field`, `summary` | "LLMs use ~4 chars per token" |
| Research/paper | `#paper`, `#research` | `source`, `field`, `summary`, `author` | AI alignment paper findings |
| Idea | `#idea` | `summary`, `status` | "Build a CLI for KG queries" |
| How-to/procedure | `#howto`, `#procedure` | `steps`, `context`, `summary` | "How to deploy on Pi" |
| Mental model | `#mental-model`, `#framework` | `steps`, `context`, `summary` | "Debug network: ping→DNS→firewall" |
| Workflow | `#workflow` | `steps`, `context`, `summary` | "Code review: tests first, then impl" |

**Attrs for procedural knowledge:**
- `steps`: ordered procedure as string (use `→` or numbered: `"1. Check logs → 2. Reproduce → 3. Fix → 4. Test"`)
- `context`: when/where to apply this knowledge (e.g. `"when network is down"`, `"during code review"`)
- `summary`: short description of what this knowledge is about

## Consolidation

Run `node scripts/consolidate.mjs` weekly or when entity count > 80. Then `summarize.mjs`.

## Security

- NEVER print vault values in chat or log to memory/ files
- vault.enc.json and .vault-key must never be in context
- Other agents: read-only via reader.mjs, NO write access
