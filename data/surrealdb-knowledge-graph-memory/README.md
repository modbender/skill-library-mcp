# SurrealDB Knowledge Graph Memory v2

> A comprehensive knowledge graph memory system for OpenClaw with semantic search, episodic memory, and automatic context injection.

## ✨ Features

- **🧠 Semantic Memory** — Vector-indexed facts with confidence scoring
- **📚 Episodic Memory** — Task histories with decisions, problems, solutions, learnings
- **💾 Working Memory** — YAML-based task state that survives crashes
- **🔄 Auto-Injection** — Relevant facts/episodes automatically injected into agent prompts
- **📈 Outcome Calibration** — Facts used in successful tasks gain confidence
- **🔗 Entity Extraction** — Automatic entity linking and relationship discovery
- **⏰ Confidence Decay** — Stale facts naturally decay over time

## 🖥️ Dashboard UI

Two-column layout in the Control dashboard:

| Left: Dashboard | Right: Operations |
|-----------------|-------------------|
| 📊 Live statistics (facts, entities, relations) | 📥 Extract Changes / Find Relations / Full Sync |
| 📈 Confidence bar with average score | 🔧 Apply Decay / Prune Stale / Full Sweep |
| 🏥 System health status | 💡 Tips & quick reference |
| 🔗 Link to DB Studio | Progress bars with real-time updates |

The Installation section only appears when setup is needed — keeping the UI clean when everything is working.

## 🚀 Quick Start

```bash
# 1. Install SurrealDB
./scripts/install.sh

# 2. Start the server
surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.openclaw/memory/knowledge.db

# 3. Initialize schema
./scripts/init-db.sh

# 4. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install surrealdb openai pyyaml
```

## 🔧 MCP Integration

Add to your `config/mcporter.json`:

```json
{
  "servers": {
    "surrealdb-memory": {
      "command": ["python3", "/path/to/surrealdb-memory/scripts/mcp-server-v2.py"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

## 🛠 Available Tools (11)

| Tool | Description |
|------|-------------|
| `knowledge_search` | Semantic search for facts |
| `knowledge_recall` | Get fact with full context |
| `knowledge_store` | Store a new fact |
| `knowledge_stats` | Database statistics |
| `knowledge_store_sync` | Store with importance routing |
| `episode_search` | Find similar past tasks |
| `episode_learnings` | Get learnings from history |
| `episode_store` | Record completed episode |
| `working_memory_status` | Current task state |
| `context_aware_search` | Task-boosted search |
| `memory_inject` | **Context injection for prompts** |

## 🎯 Auto-Injection

Enable automatic memory injection in the Mode UI:

1. Open Control dashboard → **Mode** tab
2. Scroll to **🧠 Memory & Knowledge Graph**
3. Toggle **Auto-Inject Context**
4. Configure limits as needed

When enabled, every user message triggers:
1. Semantic search against the knowledge graph
2. If confidence is below threshold, episodic memories are included
3. Formatted context is injected into the agent's system prompt

## 📊 Example Output

```markdown
## Semantic Memory (Relevant Facts)
📌 [60% relevant, 100% confidence] User prefers direct communication
📌 [55% relevant, 95% confidence] Previous project used React

## Related Entities
• User (person)
• React (technology)

## Episodic Memory (Past Experiences)
✅ Task: Deploy marketing site [58% similar]
   → Used Vercel for deployment
```

## 📥 Extraction with Progress

Run extraction from the UI with real-time progress tracking:

- **Progress bar** with percentage and gradient fill
- **Current step** indicator (e.g., "Extracting facts from MEMORY.md")
- **Counter** showing file progress (3/7)
- **Pulsing animation** while initializing

Operations automatically refresh statistics when complete.

## 📁 File Structure

```
surrealdb-memory/
├── SKILL.md                 # Detailed documentation
├── skill.json               # Clawhub manifest
├── README.md                # This file
├── scripts/
│   ├── mcp-server-v2.py     # MCP server (11 tools)
│   ├── episodes.py          # Episodic memory module
│   ├── working_memory.py    # Working memory module
│   ├── memory-cli.py        # CLI interface
│   ├── extract-knowledge.py # Bulk extraction
│   ├── schema-v2.sql        # Database schema
│   └── ...
├── openclaw-integration/
│   ├── gateway/memory.ts    # Gateway methods
│   └── ui/                  # Dashboard UI
└── .venv/                   # Python environment
```

## 📈 Stats

```bash
mcporter call surrealdb-memory.knowledge_stats
```

```json
{
  "facts": 379,
  "entities": 485,
  "relations": 106,
  "episodes": 3,
  "avg_confidence": 0.99
}
```

## 📖 Documentation

See [SKILL.md](./SKILL.md) for complete documentation including:
- Detailed setup instructions
- All CLI commands
- Database schema details
- Confidence scoring algorithm
- Maintenance procedures
- Troubleshooting guide

## 📜 License

MIT
