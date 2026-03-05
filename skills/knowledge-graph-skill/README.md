# 🧠 Knowledge Graph Skill

Embedded knowledge graph for AI agents. Store structured knowledge as entities + relations, search with typo tolerance, extract knowledge from articles automatically, visualize interactively — all in pure JS with zero external dependencies.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Hybrid Search** | Exact + trigram fuzzy + BM25 — typo-tolerant, multilingual |
| **KGML Summary** | Smart index with auto-categories, ~76% smaller than JSON |
| **Script-Driven Extraction** | Feed an article → get structured KG nodes automatically |
| **Interactive Visualization** | Force-directed graph, zoom, pinch, clickable navigation |
| **Encrypted Vault** | AES-256-GCM secret storage |
| **Multi-Platform** | OpenClaw, Claude Code, Gemini CLI |
| **20 Entity Types** | human, org, event, concept, knowledge, device, place... |
| **18 Relation Types** | owns, uses, created, depends_on, knows, likes... |
| **Retrieval Benchmark** | 10-category automated test suite |
| **Zero Dependencies** | Pure JS, Node 18+, no npm install needed |

## 🚀 Quick Install

```bash
# Copy to your agent workspace
cp -r knowledge-graph /path/to/workspace/skills/knowledge-graph

# Run install (auto-detects platform)
cd /path/to/workspace
node skills/knowledge-graph/scripts/install.mjs
```

The installer will:
- Create `data/` directory with empty graph
- Detect your platform (OpenClaw / Claude Code / Gemini CLI)
- Patch your agent instructions file with KG usage block

## 📖 How It Works

After install, your agent **autonomously**:
1. Reads `kg-summary.md` each session (smart index of the graph)
2. Adds entities when users mention people, projects, orgs, decisions
3. Searches the graph before answering factual questions
4. Extracts knowledge from articles using script-driven workflow
5. Stores secrets in the encrypted vault

No special prompting needed — the injected instructions handle everything.

## 📚 Extracting Knowledge from Articles

The script-driven extraction workflow works with **any LLM** (tested with Claude Sonnet ~90%, Gemini 3 Pro ~75-87%):

```bash
# 1. Save article text
curl -s https://example.com/article | node -e "..." > /tmp/article.txt

# 2. Get complexity score + bash template
node scripts/depth-check.mjs --file /tmp/article.txt

# 3. Agent writes bash script following the template (5 phases)
# 4. Script self-validates using validate-kg.mjs
# 5. If FAIL → agent writes fix script → repeats until PASS
```

**Key insight:** Instead of asking the LLM to follow multi-pass instructions (which weaker models skip), the validation is embedded in the bash script itself. The script self-checks → LLM sees FAIL → forced to iterate.

## 🔧 Manual Usage

```bash
# Add entities
node scripts/add.mjs entity --id "john" --type "human" --label "John Doe" --attrs '{"role":"engineer"}'
node scripts/add.mjs rel --from "john" --to "acme" --rel "member_of"
node scripts/add.mjs quick "Acme Corp:org" --category company

# Search (typo-tolerant)
node scripts/query.mjs find "jonh doe"      # finds "John Doe" via trigram
node scripts/query.mjs find "engineer"       # finds via attr value

# Navigate
node scripts/query.mjs traverse john --depth 3
node scripts/query.mjs children john
node scripts/query.mjs rels john

# Other queries
node scripts/query.mjs type org              # all orgs
node scripts/query.mjs stats                 # graph overview
node scripts/query.mjs recent --days 7       # recently added
node scripts/query.mjs timeline              # chronological view

# Article extraction
node scripts/depth-check.mjs --file article.txt
node scripts/validate-kg.mjs --file article.txt --root article_id --fix

# Maintenance
node scripts/summarize.mjs                   # regenerate summary
node scripts/consolidate.mjs                 # auto-optimize graph
node scripts/visualize.mjs                   # generate HTML viz

# Secrets
node scripts/vault.mjs set API_KEY sk-xxx --note "OpenAI key"
node scripts/vault.mjs get API_KEY

# Test
node scripts/test-retrieval.mjs --verbose    # run retrieval benchmark
```

## 📊 KGML Summary Format

The agent reads `kg-summary.md` as a smart index. Example:

```
#KGML v2 | 144e 86r | depth:3 | 2026-03-02

[👤 People]
John Doe(JD):human — role:engineer, location:NYC

[📚 Articles & Knowledge]
AI Revolution 2026(AR):knowledge — date:2026-01-15
  Market Impact(MI):concept
    Company A(CA):org — revenue:$5B
    ↳ 3 children (2 org, 1 event)

%rel-summary
related_to(12) created(3) manages(2)
%key-relations
  [John Doe]
    John Doe >manages> Company A
  [AI Revolution 2026]
    Company A >related_to> Company B
%types org:15 concept:12 event:5 human:3
```

## 🏗️ Architecture

```
skills/knowledge-graph/
├── DESIGN.md              # Full design rationale & benchmarks
├── SKILL.md               # Agent reference docs
├── data/
│   ├── kg-store.json      # Graph data (JSON)
│   ├── kg-summary.md      # Auto-generated KGML index
│   ├── kg-viz.html        # Interactive visualization
│   └── vault.enc.json     # Encrypted secrets
├── lib/
│   ├── graph.mjs          # Core CRUD + access tracking
│   ├── query.mjs          # Hybrid search + traverse
│   ├── serialize.mjs      # JSON → KGML summary
│   └── vault.mjs          # AES-256-GCM encryption
└── scripts/
    ├── install.mjs        # Multi-platform setup
    ├── add.mjs            # Add entity/relation
    ├── query.mjs          # Search & navigate
    ├── depth-check.mjs    # Article complexity scorer
    ├── validate-kg.mjs    # Extraction validator
    ├── visualize.mjs      # HTML graph generator
    ├── test-retrieval.mjs # Quality benchmark
    └── ...                # consolidate, merge, vault, etc.
```

## 📈 Benchmarks

**Retrieval (test-retrieval.mjs):**
- 144-entity KG: 51/51 tests PASS (exact, fuzzy, partial, attrs, traverse, cross-branch)
- 26-entity KG: 36/36 tests PASS

**Article Extraction:**

| Article | Model | Entities | Relations | Score |
|---------|-------|----------|-----------|-------|
| 6000w economic analysis | Claude Sonnet | 54 | 28 | ~90% |
| 6000w economic analysis | Gemini 3 Pro | 95 | 49 | ~75% |
| 2000w tech article | Gemini 3 Pro | 35 | 26 | ~87% |

**Token efficiency:**
- KGML summary: ~76% smaller than JSON
- Summary budget: 5000 tokens (lazy-loaded)
- Agent instructions: ~800 tokens (static)

## 📋 Requirements

- **Node.js** ≥ 18.0.0
- No npm install needed — zero external dependencies
- Works on: Linux, macOS, Windows, Raspberry Pi

## 📄 License

MIT — Annie & xnohat
