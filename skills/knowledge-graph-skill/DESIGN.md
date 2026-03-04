# Knowledge Graph Skill — Design Document

> Created: 2026-02-28
> Last updated: 2026-03-02 (major: script-driven extraction, smart summary index, visualization v3)
> This document captures the full design rationale so future maintainers know why things are the way they are.

---

## 1. Motivation

### Problem
Using `memory/` (flat markdown files) for daily notes works initially, but over time:
- **No relationships** between entities (people, projects, devices, decisions)
- **Hard to query precisely** — search relies only on semantic similarity or keywords
- **Must read many files** to piece together the full picture
- **Secrets** (API keys, passwords) have no safe storage

### Solution
Embedded Knowledge Graph (KG) running locally, using JS + JSON file storage, as an agent skill. Hybrid with memory/ — KG for structured knowledge, memory/ for daily notes.

### Key Design Insight
> "A good KG grows deeper, not wider"

Entity nesting keeps top-level compact while detail lives deeper. Over time, the graph grows deeper but summary size stays nearly constant.

---

## 2. Design Decisions

### 2.1 Why JSON file instead of a database?

**Chose JSON because:**
- Zero external dependency — only needs Node.js
- Portable — copy folder and go
- Human-readable — debug by eye
- Sufficient performance for personal KG (<1000 entities)
- No concurrent access needed (single agent writes)

**Accepted trade-off:** No indexing, full scan per query. With <1000 entities this is negligible.

### 2.2 Why KGML summary format?

KGML is a custom Markdown-compatible notation designed for KG summaries. Not a standard — just a practical convention.

**Benchmarked token cost (real data: 26 entities, 30 relations):**

| Format | Tokens | vs KGML | Notes |
|--------|--------|---------|-------|
| Minified JSON | ~3620 | +734% | Huge overhead from `{}[]"":,` |
| Compact JSON | ~1786 | +312% | Still heavy |
| Markdown prose | ~469 | +8% | Nearly identical |
| CSV (entities+rels) | ~397 | -9% | Slightly smaller but flat |
| **KGML** | **~434** | **baseline** | Structured + readable |

**Key insight:** KGML's advantage is NOT raw token savings over plain text formats — it's roughly equal to Markdown prose and slightly larger than CSV. The real win is **~76% savings vs JSON** and **structure**: hierarchy, categories, typed relations, and aliases all in a format every LLM reads natively (it's valid Markdown).

**Why every LLM reads it natively (no format explanation needed):**

Each element borrows from patterns LLMs have seen millions of times in training data:
- `Label(Alias):type` — looks like type annotations in code
- `— attr1,attr2` — looks like Markdown description lists
- Indent = hierarchy — every LLM understands indentation as nesting
- `A>verb>B` — looks like graph triple notation (subject>predicate>object)
- `[category]` — looks like INI file section headers
- `%rels` `%vault` — looks like pragma/directive keywords

No single element is novel. The format just combines familiar patterns into something purpose-built for KG summaries. This is why GPT, Claude, Gemini, Llama, etc. all parse it correctly without any format specification in the prompt.

**KGML features:**
- **Aliases 1-3 chars** — `F>owns>R` instead of `FullName>owns>FullName`, compact relations
- **Indent = containment** — parent-child relationship implied, no separate edge needed
- **Auto-categories** — grouped by entity type with emoji labels (`[👤 People]`, `[📚 Articles & Knowledge]`, `[🏢 Organizations]`, etc.)
- **Inline attrs** — `Label(Alias):type — attr1,attr2`
- **Collapsed children with type breakdown** — `↳ 10 children (8 org, 2 event)` instead of opaque `+10 children`
- **Relations grouped by subtree** — `%key-relations` shows top 4 per root subtree so no single node dominates
- **`%rel-summary`** — relation types with counts: `related_to(58) created(7) manages(6)`
- **`%types` footer** — quick entity type overview: `org:57 concept:54 event:20`
- **File extension: `.md`** — it IS Markdown, renders nicely everywhere

### 2.3 Why entity nesting (hierarchy)?

**Problem:** KG grows horizontally over time. 200 flat entities = 2000+ tokens in summary.

**Solution:** Entities have a `parent` field → tree structure.

**Rules:**
- `parent-child` relationship **needs no separate edge** (implied by indent)
- Only store **cross-branch** relations as explicit edges
- Auto-consolidation finds entities that can be nested

**Growth model:**
```
Month 1:  50 entities, depth 1-2, full summary     (~500 tokens)
Month 6:  200 entities, depth 2-3, consolidated     (~900 tokens)
Year 2:   500 entities, depth 3-4, top 100 + recent (~1200 tokens)
```

Summary size is effectively **capped at ~1500 tokens** thanks to consolidation + budget control.

### 2.4 Why hybrid search (Exact + Trigram + BM25)?

**Problem:** Simple `substring.includes()` fails in obvious ways:
- "raspi" can't find "RaspberryPi"
- "knowlege graph" (typo) returns nothing
- "piano harmonica" (multi-word) returns nothing
- No term weighting — "Tailscale network" treats both words equally

**Solution: 3-layer hybrid scoring:**

| Layer | Algorithm | What it catches | Score range |
|-------|-----------|----------------|-------------|
| L1: Exact | Exact + substring match on id/alias/label/tags | Known names, aliases | 30-100 |
| L2: Trigram | Sørensen–Dice coefficient over character trigrams | Typos, partial names, fuzzy matches | 0-60 |
| L3: BM25 | TF-IDF with length normalization (k1=1.2, b=0.75) | Multi-word queries, term importance | 0-40+ |

**Why trigram matching?**
- Character trigrams ("ras", "asp", "spi") overlap even with typos/abbreviations
- Sørensen–Dice coefficient: `2 * |A∩B| / (|A| + |B|)` — symmetric, 0..1
- Works across languages without language-specific stemming
- Short-query penalty (<4 chars → 0.5x score) to reduce false positives (e.g. "pho" matching "phone")
- Per-token matching: each query token finds its best match in candidate tokens

**Why BM25 on top?**
- Trigram is great for single-term fuzzy, but doesn't weight term importance
- BM25 provides corpus-aware IDF: rare terms (like "tailscale") score higher than common ones (like "the")
- Document length normalization prevents long tag lists from dominating
- Multi-word queries get proper per-term scoring

**Benchmarked on FukAI KG (26 entities) — before vs after:**

| Query | Old (substring) | New (hybrid) |
|-------|----------------|--------------|
| `raspi` | ❌ no results | ✅ RaspberryPi (118) |
| `knowlege graf` (typo) | ❌ no results | ✅ KnowledgeGraph (61) |
| `piano harmonica` | ❌ no results | ✅ Harmonica (409), Piano (406) |
| `đại học delaware` (cross-lang) | ❌ no results | ✅ University of Delaware (481) |
| `hobby sở thích` (mixed) | ❌ no results | ✅ Harmonica (450), Piano (441) |
| `bose quiet` (partial) | 40 | ✅ 390 |

Zero external dependencies — pure JS, instant on Raspberry Pi.

**Tags remain key:** Trigram + BM25 make tags even more powerful — synonyms, localized names, and abbreviations now fuzzy-match too. No embeddings/vectors needed at personal KG scale.

### 2.5 Why vault key lives inside the skill folder?

**Chose portability over key separation** — move the entire skill folder to another machine and start immediately.

**Security measures:**
- `.vault-key` file chmod 600 (owner-only read)
- `.gitignore` covers both vault.enc.json and .vault-key
- Encryption: AES-256-GCM + PBKDF2 (100k iterations)
- Agent must never print vault values in chat or log to memory/

### 2.6 Agent Context & Cache-Friendly Design

**Core concern:** LLMs wake up fresh each session, don't know what the graph contains.

**Solution — two-layer design:**

1. **Agent instructions file** (`AGENTS.md` / `CLAUDE.md` / `GEMINI.md`):
   - Contains KG instructions: when to add, how to add, script commands, entity/relation types
   - **Static** — does NOT contain graph data
   - **Never changes when KG changes** → LLM provider context cache stays valid
   - Includes instruction: `Read kg-summary.md to see what entities exist`

2. **`data/kg-summary.md`** — separate file with KGML graph summary:
   - Agent reads this on-demand (first use in session)
   - Updated by `summarize.mjs` without touching the instructions file
   - Budget-capped at ~1500 tokens
   - Frequency-ranked: entities queried more often appear first in compact mode

**Why not embed graph in AGENTS.md?**
Every time an entity is added → `summarize.mjs` runs → AGENTS.md changes → LLM provider invalidates cached system prompt → full re-encode cost. With 5 entities added per session, that's 5 cache invalidations. By keeping graph data separate, AGENTS.md stays stable indefinitely.

**Multi-platform support:**
Install script auto-detects which platform the workspace belongs to:
- OpenClaw: `AGENTS.md` (detected by AGENTS.md or SOUL.md)
- Claude Code: `CLAUDE.md`
- Gemini CLI: `GEMINI.md`
- Force with `--platform openclaw|claude|gemini`

### 2.7 Access Frequency Tracking

**Problem:** When KG grows >100 entities, summary must prioritize. Time-based "recent 20" is naive — a 6-month-old entity queried daily is more relevant than yesterday's one-off.

**Solution:** `data/kg-access.json` tracks access counts per entity:
- Every `search()` or `traverse()` call bumps counters for matched entities
- `serialize.mjs` uses access frequency as primary ranking signal in compact mode:
  ```
  score = access_count * 10 + recency_bonus (last 7 days) + creation_recency
  ```
- Top N entities by score appear in summary; rest are omitted with `%omitted N entities`

### 2.8 Knowledge Entity Design

The `knowledge` type covers both **declarative** (facts, papers) and **procedural** (how-to, workflows, mental models) knowledge.

**Differentiation via tags + attrs:**
- Declarative: `#fact`, `#paper`, `#til` — attrs: `source`, `field`, `summary`, `author`
- Procedural: `#howto`, `#procedure`, `#mental-model`, `#workflow` — attrs: `steps`, `context`, `summary`

**Why one type instead of separate types?** Fewer types = less cognitive load for agent when choosing. Tags provide sub-classification without type explosion.

### 2.9 KG Depth Heuristic

**Problem:** Agents default to shallow KG extraction (1-2 layers) even for information-rich content (long-form articles, research papers, system documentation). This means named organizations, events, policies, and causal chains get lost — only the top-level "topic" is recorded.

**Root cause:** Without explicit guidance, agents optimize for minimum viable effort. There is no signal telling them that a complex article with 15 named organizations, a timeline, multiple causal chains, and policy proposals requires fundamentally more extraction than a simple product preference.

**Solution: Complexity Scoring + Depth Mandate**

A 7-signal heuristic that agents apply before extracting any knowledge item:

| Signal | Heuristic |
|--------|-----------|
| ≥5 named entities | Count capitalized proper nouns |
| Timeline/events | Look for years, quarters, before/after sequences |
| Causal chains | Look for "because", "leads to", "as a result", etc. |
| ≥3 distinct domains | Tech + finance + social + policy etc. |
| Policy/proposals | Any "Act", "Bill", "Initiative", "Framework" |
| Quantitative data | Percentages, dollar amounts, large numbers |
| Multiple actors | Different orgs/people with distinct roles |

**Score → required extraction depth:**

```
0–1 → 1 layer (root only)
2–3 → 2 layers (root + key concepts)
4–5 → 3 layers (root → domains → mechanisms)
6–7 → 4+ layers (root → domains → mechanisms → concrete entities + cross-relations)
```

**Layer template for complex content (score ≥ 4):**
1. Root node — the article/topic (knowledge or concept type)
2. Domain nodes — major themes ("Economic Impact", "Technical Mechanisms")
3. Mechanism/concept nodes — specific named phenomena, frameworks, effects
4. Concrete entity nodes — orgs, people, events, policies (with attrs: numbers, dates, quotes)
5. Cross-relations — link entities across branches

**Why mandatory self-checklist?** Even with the score table, agents may finish prematurely. The checklist forces explicit verification before closing extraction:
- "Did I capture all named orgs/companies/people?"
- "Did I capture key events with dates?"
- "Did I capture policy responses or proposals?"
- "Are there causal chains I should link with relations?"
- "Would someone searching for a sub-topic find it, or only the root?"

**`depth-check.mjs` — automated scorer + template generator (model-agnostic):**

CLI tool that scores text content and outputs recommended depth + quality targets. For complex content (score ≥ 4), outputs a **bash script template** with built-in validation. Uses regex-based heuristics (no LLM, deterministic, instant).

Detection signals:
- Named entity detection: Title Case pattern matching with stop-word filtering
- Timeline detection: year patterns, quarter notation, sequence words
- Causal chain detection: causal connective density
- Domain detection: keyword density per domain (tech/finance/social/policy/science/geopolitics/health)
- Stats detection: percentage/dollar/large number density

Outputs human-readable report with targets or `--json` for machine-readable scoring. Also accepts `--file` or stdin pipe for long-form content.

**`validate-kg.mjs` — post-extraction validator:**

CLI tool that compares article text against current KG to find extraction gaps. Designed to be called **inside** the extraction bash script as a mandatory checkpoint.

Detection (regex NER, no LLM):
- **Orgs:** ticker patterns, corp suffixes, known financial names, possessives, financial verb context. Multi-signal scoring (candidates need ≥2 confidence to be flagged). Extensive stop word list (~100 words) prevents false positives like "CapEx", "White", "Permanent".
- **People:** Name patterns near role indicator words (CEO, author, etc.)
- **Events:** Bloomberg-style headlines, quarter+year references, month+year references
- **Stats:** Percentages, dollar amounts

Quality gates: entities ≥30, relations ≥50% of entities, depth ≥3, events ≥3, no empty orgs. Exit code 0 (PASS) or 1 (FAIL). `--fix` flag outputs suggested add.mjs commands.

**Anti-pattern: "Attr stuffing"**
Agents naturally optimize for fewer tool calls. Without explicit instruction, they create a concept node like "Private Credit Contagion" and stuff 10 organization names into its attrs JSON. This means searching for "Zendesk" or "Apollo" won't find a node — only a substring inside an attr value. The extraction workflow explicitly forbids this: every named org, person, event, and policy MUST be its own entity node.

### Script-Driven Extraction (the breakthrough)

**Problem:** Multi-pass text instructions (Enumerate → Build → Cross-link → Verify) worked well for Claude Sonnet (~90% extraction) but failed for Gemini 3 Pro (~35%). Gemini optimizes for "1-shot completion" — it skips enumerate and verify steps, writes one bash script and stops.

**Key insight:** Instead of asking the LLM to follow multi-pass in its thinking (which weaker models skip), **embed the validation into the bash script itself**. The script self-checks → LLM sees FAIL output → forced to iterate.

**Workflow (5 steps):**
1. Save article text to `/tmp/article.txt`
2. Run `depth-check.mjs` — get score + bash template
3. Write bash script following template (5 phases):
   - Phase 1: Root + domain nodes
   - Phase 2: Mechanisms/sub-concepts under domains
   - Phase 3: Orgs, people, events under mechanisms (depth ≥3)
   - Phase 4: Relations (≥1 per 2 entities)
   - Phase 5: `summarize.mjs` + `validate-kg.mjs` (MANDATORY)
4. Run script — check validation output
5. If FAIL → write fix script → run → validate again → repeat until PASS

**Why this works for all models:**
- Gemini's 1-shot behavior now helps — it writes 1 big bash script with all 5 phases
- Validation is deterministic (regex NER), not dependent on model reasoning
- FAIL output tells the LLM exactly what's missing → forces iteration
- Template is model-agnostic — any model can follow the structure
- The multi-pass isn't in thinking, it's in script → validate → fix → validate loop

**Real-world validation results:**

| Article | Model | Approach | Entities | Relations | Depth | Weighted Score |
|---|---|---|---|---|---|---|
| 2028 GIC (6000w, 30+ orgs) | Sonnet | text instructions | 54 | 28 | 4 | ~90% |
| 2028 GIC | Gemini 3 Pro | text instructions | 29 | 9 | 2 | ~35% |
| 2028 GIC | Gemini 3 Pro | **script-driven** | **95** | **49** | **3** | **~75%** |
| SaaS-Pocalypse (Forbes, 2000w) | Gemini 3 Pro | **script-driven** | **35** | **26** | **3** | **~87%** |

Gemini improved from ~35% → ~75-87% just by changing instructions. The script-driven approach closes most of the gap between models.

---

## 3. Architecture

```
~/.openclaw/skills/knowledge-graph/
├── SKILL.md              # Agent instructions (advanced reference)
├── DESIGN.md             # This file — design rationale
├── data/
│   ├── kg-store.json     # Source of truth (JSON graph)
│   ├── kg-summary.md     # Auto-generated KGML summary (agent reads on-demand)
│   ├── kg-access.json    # Access frequency counters per entity
│   ├── kg-viz.html       # Generated interactive graph visualization
│   ├── vault.enc.json    # 🔐 Encrypted secrets
│   ├── .vault-key        # 🔐 Encryption key (chmod 600)
│   └── .gitignore        # Excludes vault files from git
├── lib/
│   ├── graph.mjs         # Core: CRUD nodes + edges + merge + access tracking
│   ├── query.mjs         # Multi-layer search + traverse (bumps access counters)
│   ├── reader.mjs        # Read-only API for cross-agent access
│   ├── serialize.mjs     # JSON → KGML v2 (budget-capped, frequency-ranked)
│   └── vault.mjs         # AES-256-GCM encrypt/decrypt
└── scripts/
    ├── install.mjs       # First-time setup (multi-platform: OpenClaw/Claude/Gemini)
    ├── add.mjs           # Add entity/relation
    ├── remove.mjs        # Remove entity/relation
    ├── query.mjs         # Query (search, traverse, stats, temporal)
    ├── merge.mjs         # Merge entities (absorb or nest)
    ├── consolidate.mjs   # Auto-optimize (nest, orphans, merge suggest)
    ├── summarize.mjs     # Regenerate kg-summary.md
    ├── vault.mjs         # Secret management CLI
    ├── visualize.mjs     # Generate interactive HTML graph (self-contained, no CDN)
    ├── depth-check.mjs   # Complexity scorer → outputs bash template + quality targets
    ├── validate-kg.mjs   # Post-extraction validator (regex NER compares article vs KG → PASS/FAIL)
    ├── test-retrieval.mjs # Retrieval quality benchmark (auto-discovers test data from KG)
    ├── import-memory.mjs # Extract entities from memory/ files
    └── export.mjs        # Export KG for other agents
```

---

## 4. Data Model

### Node (Entity)
```json
{
  "id": "string — lowercase kebab-case, unique",
  "alias": "string — 1-3 chars, used in KGML summary",
  "type": "string — see types below",
  "label": "string — human-readable name",
  "parent": "string|null — id of parent node (creates hierarchy)",
  "tags": ["array — synonyms, localized names, abbreviations for search"],
  "attrs": {"object — free-form key-value metadata"},
  "confidence": "number|undefined — 0.0-1.0",
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD"
}
```

**Entity types:**
- Tech & infra: `human` `ai` `device` `platform` `project` `decision` `concept` `skill` `network` `credential` `org` `service`
- Life & world: `place` `event` `media` `product` `account` `routine` `knowledge`

### Edge (Relation)
```json
{
  "from": "string — source node id",
  "to": "string — target node id",
  "rel": "string — see relations below",
  "attrs": {"object — optional metadata"},
  "created": "YYYY-MM-DD"
}
```

**Relation types:**
- Tech: `owns` `uses` `runs_on` `runs` `created` `related_to` `part_of` `instance_of` `decided` `depends_on` `connected` `manages`
- Life & social: `likes` `dislikes` `located_in` `knows` `member_of` `has`

**Key rule:** Parent-child relationships are implied by `parent` field — NO explicit edge needed.

---

## 5. Token Budget & Serialization

### Context allocation:
- **KG instructions** (in agent file): ~800 tokens — **static, never changes**
- **KG summary** (kg-summary.md, lazy-loaded on-demand): ≤5000 tokens — changes when KG changes

Since kg-summary.md is **lazy-loaded** (agent reads it explicitly when needed, NOT embedded in every context), the token budget can be generous — 5000 tokens is cheaper than a single tool call round-trip and provides much better discoverability.

### Serialization strategies (in `serialize.mjs`):

| Level | Entities | Child depth | Attr length | Notes |
|-------|----------|-------------|-------------|-------|
| Small (<200) | Full tree | 3 | 40 chars | All entities visible |
| Medium (200-400) | Full tree | 2 | 30 chars | Deeper children collapsed with type breakdown |
| Large (>400) | Full tree | 1 | 25 chars | Only top-level + direct children |

### Auto-categorization:
Top-level entities are automatically grouped by type — no manual category assignment needed:
- `[👤 People]` for `human` type
- `[📚 Articles & Knowledge]` for `knowledge` type
- `[🏢 Organizations]` for `org` type
- `[📅 Events]` for `event` type
- etc.

### Collapsed children format:
When tree depth exceeds limit, children are summarized with type breakdown:
```
↳ 10 children (8 org, 2 event)
```
This tells the agent exactly what types of entities are hidden, helping it decide whether to query deeper.

### Relations section:
- **`%rel-summary`**: relation types with counts — quick overview
- **`%key-relations`**: top 4 relations per root subtree — distributed evenly so no single node dominates. Cross-branch relations prioritized over intra-branch.

---

## 6. Consolidation Rules

Runs periodically (weekly or when entity count > 80).

| Rule | Trigger | Action |
|------|---------|--------|
| Auto-nest | Entity has only 1 edge, rel implies containment | Become child, remove edge |
| Absorb | 2 entities same type + similar label (Levenshtein ≤ 2) | Merge attrs+tags, keep 1 |
| Prune | Attr value empty/null | Remove attr |
| Promote | Child has >3 cross-branch relations | Promote to top-level |
| Archive | Entity not referenced >90 days | Flag for review |

---

## 7. Workflow

### Install (once per workspace):
```bash
node scripts/install.mjs [--workspace /path] [--platform openclaw|claude|gemini]
```
→ Patches agent instructions file + creates data/ + generates kg-summary.md

### Every session:
1. Agent reads `data/kg-summary.md` → knows what's in the graph
2. Conversation proceeds, agent auto-adds/queries as needed
3. After changes → runs `summarize.mjs` (updates kg-summary.md only, NOT agent file)

### Periodic maintenance:
- `consolidate.mjs` weekly
- `import-memory.mjs` to bootstrap from memory files
- `query.mjs uncertain` to review low-confidence entities

---

## 8. Multi-Platform Support

### Supported platforms:

| Platform | Agent file | Detection |
|----------|-----------|-----------|
| OpenClaw | `AGENTS.md` | Finds `AGENTS.md` or `SOUL.md` |
| Claude Code | `CLAUDE.md` | Finds `CLAUDE.md` |
| Gemini CLI | `GEMINI.md` | Finds `GEMINI.md` |

### How it works:
- `install.mjs` auto-detects platform → patches correct file with KG block (HTML comment markers)
- `summarize.mjs` does NOT touch agent files (cache-friendly)
- Same KG block content works across all platforms (standard Markdown)
- If no agent file exists, `install.mjs` creates it

---

## 9. Security

| Rule | Reason |
|------|--------|
| Never print vault values in chat | Could leak to logs/history |
| Never log secrets to memory/ files | Plain-text, backed up to git |
| vault.enc.json + .vault-key excluded from git | .gitignore auto-created |
| Other agents: read-only via reader.mjs | Only owning agent modifies KG |
| AES-256-GCM + PBKDF2 100k iterations | Industry standard encryption |

---

## 10. Visualization (`visualize.mjs`)

Self-contained HTML graph visualization. No external dependencies, no CDN — works offline.

**Features:**
- **Force-directed layout** with overlap prevention (size-aware repulsion, 3x penalty for overlapping nodes)
- **Zoom:** scroll wheel (zooms toward cursor), pinch-to-zoom (2 fingers on mobile), ＋/－ buttons
- **Pan:** click-drag canvas (no node dragging — nodes are fixed after layout)
- **Click node** → sidebar with full detail (label, type, attrs, tags, confidence, dates)
- **Clickable links** in sidebar: relations, parent, children all link to target node
- **Navigate to node:** animated pan + zoom (easeInOut 400ms) centers target node at 1.5x zoom
- **Search:** real-time filter by label/id/type/tags (unmatched nodes fade)
- **Toggle buttons:** Hierarchy (parent-child dashed lines), Labels (on/off)
- **Tooltip on hover:** node name, type, confidence, connection count
- **Color-coded** by entity type (20 types, same palette as KGML categories)
- **Node size** scales with connection count (8-32px radius)
- **All buttons have descriptive tooltips** on hover

**Physics tuning (anti-overlap):**
- Base repulsion: 5000, with 3x penalty when nodes overlap (distance < sum of radii + 20px)
- Edge rest length: 140-180px (scales with node sizes)
- 500 simulation steps for stable layout
- Initial positions: wide circle with random jitter to break symmetry

---

## 11. Retrieval Quality Benchmark (`test-retrieval.mjs`)

Automated test suite that validates KG query quality. Tests **auto-discover** data from the current KG — no hardcoded entity names, works on any KG.

**10 test categories:**

| # | Category | What it tests | Key assertions |
|---|----------|---------------|----------------|
| 1 | **Exact Match** | Search by full label, ID | Target in top 3 |
| 2 | **Partial Match** | Substring of label | Still finds entity |
| 3 | **Fuzzy Match** | Typos (char swaps) | Trigram similarity recovers |
| 4 | **Tag & Alias** | Search by tags, short alias | Entity found |
| 5 | **Attribute Search** | Search by attr values (dates, roles) | Parent entity found |
| 6 | **Traverse** | Hierarchy (children, grandchildren) + edge relations | Complete traversal |
| 7 | **Token Efficiency** | Default limit ≤20, depth-1 bounded | Output not excessive |
| 8 | **Summary Index** | All top-level in summary, categories, rels, types | Summary = useful index |
| 9 | **Cross-branch** | Find entities from different subtrees | No subtree isolation |
| 10 | **Ranking** | Exact label ranks #1, findByType correct | Relevance order |

**Usage:**
```bash
node scripts/test-retrieval.mjs              # Run all
node scripts/test-retrieval.mjs --verbose     # Show each pass
node scripts/test-retrieval.mjs --category exact  # One category only
```

**Benchmark results (2026-03-02):**
- FukAI KG (144 entities, 86 relations): **51/51 PASS (100%)**
- Annie KG (26 entities, 1 relation): **36/36 PASS (100%)**

**Why this matters:** As the KG grows, retrieval quality could degrade (false positives, missing results, slow queries). Running this benchmark after changes to `query.mjs`, `serialize.mjs`, or the data model catches regressions early.

---

## 12. What We Deliberately Don't Do

| Decision | Rationale |
|----------|-----------|
| No external DB | Zero deps, portable |
| No vector embeddings | Hybrid trigram+BM25 search + tags sufficient at personal scale; tested local ONNX embeddings (bge-m3-m2v-512) — cross-language quality too low, 659MB RAM on Pi |
| No replacing memory/ | Hybrid: KG for structure, memory/ for daily notes |
| No external CDN/libs | Everything offline, self-contained |
| No LLM-based extraction | Regex is deterministic, free, no hallucination — depth-check.mjs uses regex heuristics, not an LLM |
| No write access for other agents | Only owning agent modifies |
| No embedding graph in agent file | Cache-friendly: agent file stays stable |
| No complex temporal logic | Simple date fields sufficient |

---

*Update this document when significant design changes are made.*
