---
name: mindgardener
description: Local-first long-term memory for autonomous agents. Extracts entities from daily logs into a wiki-style knowledge graph, scores events by surprise (prediction error), and assembles token-budget-aware context. Includes identity-level consolidation that tracks belief drift about the principal. No database required — just markdown files.
metadata:
  clawdbot:
    requires:
      bins: ["garden"]
    install:
      - id: mindgardener
        kind: pip
        package: mindgardener
        bins: ["garden"]
        label: "Install MindGardener CLI (pip)"
    env:
      - name: GEMINI_API_KEY
        description: "Google Gemini API key (free tier available). Required unless using Ollama."
        required: false
      - name: OPENAI_API_KEY
        description: "OpenAI API key. Alternative to Gemini."
        required: false
      - name: ANTHROPIC_API_KEY
        description: "Anthropic API key. Alternative to Gemini."
        required: false
---

# MindGardener 🌱

**Your agents forget everything. This fixes it.**

## What It Does

MindGardener gives your agent persistent memory by reading daily conversation logs and building:
- A **wiki** of people, projects, companies (one `.md` file per entity)
- A **knowledge graph** via `[[wikilinks]]` and JSONL triplets
- **Surprise-scored consolidation** — only unexpected events get promoted to long-term memory
- **Identity-level tracking** — models *who the agent thinks you are* and updates when beliefs shift
- **Token-budget context assembly** — loads exactly what fits in your context window

No database. No server. No Docker. Just files you can `grep`, `git diff`, and browse in Obsidian.

## Install

```bash
pip install mindgardener
garden init
```

For fully local (no API key needed):
```bash
garden init --provider ollama
```

## Setup

1. Set your LLM provider key:
   ```bash
   export GEMINI_API_KEY=your-key  # Free tier: 1500 req/day
   # OR: export OPENAI_API_KEY=your-key
   # OR: export ANTHROPIC_API_KEY=your-key
   # OR: use Ollama (free, local)
   ```

2. Initialize workspace:
   ```bash
   garden init
   ```

3. Bootstrap identity model from existing memory:
   ```bash
   garden beliefs --bootstrap
   ```

## Commands (15 total)

### Memory Building (3 use LLM, rest are free)
```bash
garden extract --input memory/2026-02-17.md  # Daily log → entity wiki + graph
garden surprise                                # Score events by prediction error
garden consolidate                             # Promote high-surprise → MEMORY.md
```

### Retrieval (no LLM needed)
```bash
garden recall "Kadoa"                          # Search entities + graph
garden context "job search" --budget 4000       # Token-budget-aware assembly
garden evaluate --text "agent output"           # Fact-check against knowledge graph
garden beliefs                                  # View identity model
garden beliefs --drift --apply                  # Detect + apply belief changes
```

### Maintenance
```bash
garden entities              # List all known entities
garden prune --days 30       # Archive inactive entities
garden merge "src" "target"  # Merge duplicates
garden fix type "X" "tool"   # Fix entity type
garden reindex               # Rebuild graph after manual edits
garden viz                   # Mermaid graph visualization
garden stats                 # Quick overview
```

## Nightly Sleep Cycle

Add to your agent's cron (recommended: 3 AM daily):

```bash
garden extract    # Read today's logs → entity wiki
garden surprise   # Score by prediction error
garden consolidate # Promote to MEMORY.md
garden beliefs --drift --apply  # Update identity model
garden prune --days 30          # Archive stale entities
```

## How It Works

### Entity Extraction
`garden extract` reads a daily log and creates one `.md` file per entity with `[[wikilinks]]`:

```markdown
# Kadoa
**Type:** company

## Facts
- AI web scraping startup (YC W24)

## Timeline
### [[2026-02-16]]
- [[Marcus]] received reply from [[Adrian Krebs]]
```

### Surprise Scoring
Uses **prediction error** — predicts what should have happened, compares with reality, scores the delta. High surprise = worth remembering. Low surprise = routine.

### Identity-Level Consolidation
Maintains `memory/self-model.yaml` — beliefs about the principal:
```yaml
beliefs:
  - claim: "Prefers local-first tools"
    confidence: 0.8
    category: preferences
    evidence_for: ["Built MindGardener", "Uses Ollama"]
```

`garden beliefs --drift` detects when today's events change these beliefs.

### Token-Budget Context Assembly
`garden context "query" --budget 4000` scores entities by relevance, follows wikilinks, and fills the budget with the most important context. Logs a manifest of what was loaded and what was skipped.

## Configuration

```yaml
# garden.yaml
workspace: /path/to/workspace
memory_dir: memory/
entities_dir: memory/entities/
graph_file: memory/graph.jsonl
long_term_memory: MEMORY.md

extraction:
  provider: google        # google, openai, anthropic, ollama, compatible
  model: gemini-2.0-flash

consolidation:
  surprise_threshold: 0.5
  decay_days: 30
```

## Supported LLM Providers

| Provider | Config | Cost |
|----------|--------|------|
| Google Gemini | `provider: google` | Free tier available |
| OpenAI | `provider: openai` | From $0.15/1M tokens |
| Anthropic | `provider: anthropic` | From $0.25/1M tokens |
| Ollama | `provider: ollama` | Free (local) |
| Any OpenAI-compatible | `provider: compatible` | Varies |

Daily cost: ~$0.004/day (Gemini Flash). $0 with Ollama.

## Privacy & Data Flow

**Which commands send data to an LLM:**
- `garden extract` — sends daily log text → receives structured entities (LLM call)
- `garden surprise` — sends MEMORY.md + daily log → receives surprise scores (2 LLM calls)
- `garden consolidate` — sends high-surprise events → receives MEMORY.md updates (LLM call)
- `garden beliefs --bootstrap` — sends MEMORY.md → receives belief model (LLM call)
- `garden beliefs --drift` — sends self-model + daily log → receives drift report (LLM call)

**Which commands are 100% local (no network):**
- `garden recall`, `garden context`, `garden evaluate`, `garden entities`, `garden prune`, `garden merge`, `garden fix`, `garden reindex`, `garden viz`, `garden stats`, `garden init`

**For fully offline operation:** Use `garden init --provider ollama` — all LLM calls stay on your machine.

All data stays in your workspace as markdown files. Nothing is sent to MindGardener servers (there are none).

## Links
- **GitHub:** https://github.com/widingmarcus-cyber/mindgardener
- **Tests:** 177 passing in <3s
- **Dependencies:** Python 3.10+ and PyYAML. That's it.
