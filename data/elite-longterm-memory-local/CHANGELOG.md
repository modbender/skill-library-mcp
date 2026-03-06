# Changelog

## 1.0.0 (2026-03-01)

### Features
- 🧠 Local embedding with Ollama (nomic-embed-text)
- 💾 LanceDB vector storage
- 🔍 Semantic memory search
- 📝 Memory store/recall/forget tools
- 🚀 Auto-recall before agent starts
- 📁 File-based memory structure (SESSION-STATE.md, MEMORY.md, daily logs)
- 🔒 Privacy-first: no data leaves your machine
- 🌐 Works offline

### Architecture
- Hot RAM: SESSION-STATE.md (active context)
- Warm Store: LanceDB vectors (semantic search)
- Cold Store: Git-notes ready (structured decisions)
- Archive: MEMORY.md + daily/ (human-readable)

### Requirements
- Node.js 18+
- Ollama server
- nomic-embed-text model

### OpenClaw Integration
- Plugin: `elite-longterm-memory-local`
- Tools: `memory_recall`, `memory_store`, `memory_forget`
- CLI: `elite-memory` command
