# Vector Memory Skill

Smart memory search with **zero configuration**. Automatically uses semantic vector embeddings when available, falls back to built-in search otherwise.

## 🎯 How It Works

```
┌─────────────────┐
│  User searches  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Vector  │ ←── Semantic understanding
    │ ready?  │     (synonyms, concepts)
    └────┬────┘
    Yes  │  No
    ┌────┘  └────┐
    ▼            ▼
┌────────┐  ┌──────────┐
│ Vector │  │ Built-in │ ←── Keyword matching
│ Search │  │ Search   │     (fallback)
└────────┘  └──────────┘
    │            │
    └──────┬─────┘
           ▼
    ┌──────────────┐
    │ Return results│
    └──────────────┘
```

**No setup required.** Install the skill and `memory_search` immediately works—just better when you sync.

## 🚀 Installation

### From ClawHub
```bash
npx clawhub install vector-memory
```

### From GitHub
```bash
curl -sL https://raw.githubusercontent.com/YOUR_USERNAME/vector-memory-openclaw/main/install.sh | bash
```

### Manual
```bash
git clone https://github.com/YOUR_USERNAME/vector-memory-openclaw.git
cd vector-memory-openclaw/vector-memory && npm install
```

## ✨ What You Get

### Immediate (No Sync Required)
- `memory_search` works with built-in keyword search
- `memory_get` retrieves full content
- All standard memory operations functional

### After First Sync (Recommended)
```bash
node vector-memory/smart_memory.js --sync
```

- **Semantic search** - "principles" finds "values"
- **Concept matching** - "values" finds "principles"
- **Better relevance** - Neural embeddings understand meaning

## 🛠️ Tools

### memory_search
**Automatically selects best method**

```javascript
// Works immediately (uses built-in)
memory_search("James values")

// Works better after sync (uses vector)
memory_search("James values")  // Same call, better results!
```

**Parameters:**
- `query` (string): What to search for
- `max_results` (number): Max results (default: 5)

**Returns:** Array of matches with path, lines, score, snippet

### memory_get
Get full content from a file.

```javascript
memory_get("MEMORY.md", 1, 20)  // Get lines 1-20
```

### memory_sync
Index memory files for vector search.

```bash
node vector-memory/smart_memory.js --sync
```

Run this after editing memory files.

### memory_status
Check which method is active.

```bash
node vector-memory/smart_memory.js --status
```

## 📊 Comparison

| Query | Before (Built-in) | After (Vector) |
|-------|------------------|----------------|
| "James principles" | ⚠️ Weak matches | ✅ "What He Values" section |
| "Nyx origin" | ⚠️ Literal match | ✅ "The Transfer" section |
| "values beliefs" | ⚠️ Weak match | ✅ Strong semantic match |

**Same function call. Better results after sync.**

## 🔧 How to Use

### In OpenClaw
Just use `memory_search` normally:

```javascript
// This automatically uses best available method
const results = await memory_search("what did we discuss about projects");
```

### CLI
```bash
# Search (auto-selects method)
node vector-memory/smart_memory.js --search "your query"

# Force check status
node vector-memory/smart_memory.js --status

# Sync for better results
node vector-memory/smart_memory.js --sync
```

## 🔄 Auto-Sync (Optional)

Add to `HEARTBEAT.md`:
```bash
# Sync memory if files changed
if [ -n "$(find memory MEMORY.md -newer vector-memory/.last_sync 2>/dev/null)" ]; then
    node vector-memory/smart_memory.js --sync
    touch vector-memory/.last_sync
fi
```

## 📁 File Structure

```
vector-memory/
├── smart_memory.js           ← Main entry (auto-selects method)
├── vector_memory_local.js    ← Vector implementation
├── memory.js                 ← OpenClaw wrapper
└── package.json
```

**You only need to call `smart_memory.js`** - it handles everything.

## 🎯 Zero-Config Philosophy

1. **Install** → Works immediately (built-in fallback)
2. **Sync** → Gets better (vector embeddings)
3. **Use** → Always best available method

No configuration files. No environment variables. No manual switching.

## 🐛 Troubleshooting

**"Vector not ready" in status**
- Normal on first install. Run `--sync` to index.

**Search returns few results**
- May be using built-in fallback. Run `--sync` for vector search.

**First sync is slow**
- Downloads ~80MB model. Subsequent syncs are fast.

**Want to force built-in search?**
- Just don't sync. Built-in is always available as fallback.

## 📈 Performance

| Method | Quality | Speed | Requirements |
|--------|---------|-------|--------------|
| Vector | ⭐⭐⭐⭐⭐ | ~100ms | Synced index |
| Built-in | ⭐⭐⭐ | ~10ms | None (fallback) |

Vector is used automatically when available. Built-in is instant fallback.

## 📝 Version History

- **v2.1.0** - Smart wrapper with automatic fallback
- **v2.0.0** - 100% local embeddings
- **v1.0.0** - Initial release

## 🤝 Contributing

PRs welcome! Particularly:
- Better fallback algorithms
- Additional storage backends
- Framework integrations

## 📜 License

MIT