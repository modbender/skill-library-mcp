# Vector Memory for OpenClaw

**Zero-configuration smart memory search**. Automatically uses neural embeddings when available, falls back to built-in search otherwise.

```bash
# Install and it just works
npx clawhub install vector-memory

# Optional: sync for better quality
node vector-memory/smart_memory.js --sync
```

## ✨ The Magic

**Same function call. Automatic best method.**

```javascript
// This automatically does the right thing
memory_search("User principles values")

// If vector synced: finds "autonomy, competence, creation" (semantic!)
// If not synced: uses keyword search (fallback)
```

No configuration. No manual switching. No broken workflows.

## 🚀 Quick Start

### From ClawHub (Recommended)
```bash
npx clawhub install vector-memory
```
Done. `memory_search` now has smart fallback.

### From GitHub
```bash
curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/vector-memory-openclaw/main/install.sh | bash
```

### Manual
```bash
git clone https://github.com/YOUR_USERNAME/vector-memory-openclaw.git
cd vector-memory-openclaw/vector-memory && npm install
```

## 🎯 How It Works

```
User searches
      │
      ▼
┌─────────────┐
│ Vector ready?│
└──────┬──────┘
   Yes │    │ No
      ▼     ▼
┌────────┐ ┌──────────┐
│ Neural │ │ Keyword  │
│ Search │ │ Search   │
│ (best) │ │ (fast)   │
└────┬───┘ └────┬─────┘
     │          │
     └────┬─────┘
          ▼
    ┌────────────┐
    │  Results   │
    └────────────┘
```

**Zero config philosophy:**
1. Install → Works immediately (built-in fallback)
2. Sync → Gets better (vector embeddings)
3. Use → Always best available

## 📊 Before & After

| Query | Without Skill | With Skill (Default) | With Skill (Synced) |
|-------|--------------|---------------------|---------------------|
| "User collaboration style" | ⚠️ Weak | ✅ Better | ✅ "work with me, not just for me" |
| "Agent origin" | ⚠️ Weak | ✅ Better | ✅ "Agent to Agent transfer" |
| "values beliefs" | ⚠️ Literal | ✅ Improved | ✅ Semantic match |

## 🛠️ Usage

### In OpenClaw
Just use `memory_search`:
```javascript
const results = await memory_search("what we discussed", 5);
// Automatically uses best available method
```

### CLI
```bash
# Search (auto-selects method)
node vector-memory/smart_memory.js --search "your query"

# Check what's active
node vector-memory/smart_memory.js --status

# Sync for better quality
node vector-memory/smart_memory.js --sync
```

## 📁 What's Included

```
vector-memory/
├── smart_memory.js           ← Main entry (auto-selects)
├── vector_memory_local.js    ← Neural embeddings
├── memory.js                 ← OpenClaw wrapper
├── package.json              ← Dependencies
└── references/
    ├── integration.md        ← Setup guide
    └── pgvector.md          ← Scale guide

skills/
└── vector-memory/
    ├── skill.json            ← OpenClaw manifest
    └── README.md             ← Skill docs
```

## 🔧 Requirements

- Node.js 18+
- ~80MB disk space (for model, cached after download)
- OpenClaw (or any Node.js agent)

## 🎛️ Tools

| Tool | Purpose |
|------|---------|
| `memory_search` | Smart search with auto-fallback |
| `memory_get` | Retrieve full content |
| `memory_sync` | Index for vector search |
| `memory_status` | Check which method is active |

## 🔄 Auto-Sync (Optional)

Add to `HEARTBEAT.md`:
```bash
if [ -n "$(find memory MEMORY.md -newer vector-memory/.last_sync 2>/dev/null)" ]; then
    node vector-memory/smart_memory.js --sync && touch vector-memory/.last_sync
fi
```

## 📈 Performance

| Method | Quality | Speed | When Used |
|--------|---------|-------|-----------|
| Vector | ⭐⭐⭐⭐⭐ | ~100ms | After sync |
| Built-in | ⭐⭐⭐ | ~10ms | Fallback / Before sync |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Vector not ready"** | Run: `node smart_memory.js --sync` |
| **No results found** | Check that MEMORY.md exists; try broader query |
| **First sync slow** | Normal - downloading ~80MB model; subsequent syncs fast |
| **Low quality results** | Sync again after editing memory files |
| **Want pure built-in?** | Don't sync - built-in always available as fallback |

## 🧪 Verify Installation

```bash
node vector-memory/smart_memory.js --test
```

Checks: dependencies, vector index, search functionality, memory files.

## 📋 For Agent Developers

Add to your `AGENTS.md`:
```markdown
## Memory Recall
Before answering about prior work, decisions, preferences:
1. Run memory_search with relevant query
2. Use memory_get for full context
3. If low confidence, say you checked
```

See full template in `AGENTS.md`.

## 🗂️ Suggested Memory Structure

```
workspace/
├── MEMORY.md              # Curated long-term memory
└── memory/
    ├── logs/              # Daily activity (YYYY-MM-DD.md)
    ├── projects/          # Project-specific notes
    ├── decisions/         # Important choices
    └── lessons/           # Mistakes learned
```

See `MEMORY_STRUCTURE.md` for templates.

## 🤝 Contributing

PRs welcome! See `CONTRIBUTING.md` (create one if needed).

## 📜 License

MIT

## 🙏 Acknowledgments

- Embeddings: [Xenova Transformers](https://github.com/xenova/transformers.js)
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Inspired by OpenClaw's memory system