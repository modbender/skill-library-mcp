---
name: Memory Pro Skill
description: A highly efficient semantic search engine for your OpenClaw
  workspace memory, powered by FAISS and Sentence-Transformers.
---

# Memory Pro Skill

A highly efficient semantic search engine for your OpenClaw workspace memory, powered by FAISS and Sentence-Transformers.

This skill indexes Markdown files and key agent files (e.g. `MEMORY.md`, `SOUL.md`) to provide meaning-based context retrieval instead of exact keyword matching.

## 🚀 Installation

This skill can be installed on any OpenClaw host.

```bash
# Clone or copy the folder
cd memory-pro-export
chmod +x install.sh
./install.sh
```

The installation script will:
1. Copy the skill to `~/.openclaw/skills/memory-pro`
2. Set up a Python virtual environment using `uv`
3. Configure and start a `systemd` user service (`memory-pro.service`)

## ⚙️ Architecture

- **Engine**: FAISS + `sentence-transformers` (`all-MiniLM-L6-v2`)
- **API**: FastAPI running on port 8001
- **Data Source**: Configurable via environment variables (Defaults to `~/.openclaw/workspace/memory/` and `MEMORY.md`, `SOUL.md`, etc.)
- **Service**: Runs safely in the background, rebuilding the index on startup to ensure consistency.

## 💻 Usage (For Agents)

Use the client script to query the running service.

### 1. Semantic Search (Recommended)
```bash
# Basic search
python ~/.openclaw/skills/memory-pro/scripts/search.py "What did I do yesterday?"

# JSON output (for better tool parsing)
python ~/.openclaw/skills/memory-pro/scripts/search.py "project updates" --json
```

### 2. Manual Index Rebuild
The index is automatically rebuilt when the background service restarts. If you need to force an immediate update:

```bash
systemctl --user restart memory-pro.service
```
*(Note: Service restart takes ~15-20 seconds to rebuild index and load models. The client script has auto-retry logic.)*

## 🔧 Environment Configuration

The service behavior can be customized by editing `~/.config/systemd/user/memory-pro.service`:

- `MEMORY_PRO_WORKSPACE_DIR`: The root of your workspace (e.g., `~/.openclaw/workspace/`)
- `MEMORY_PRO_DATA_DIR`: Directory containing `.md` files to index.
- `MEMORY_PRO_CORE_FILES`: Comma-separated list of core files to always index.
- `MEMORY_PRO_PORT`: The port for the API (default `8001`).

## 🩺 Troubleshooting

### "Connection failed"
- The service might be stopped or restarting.
- Check status: `systemctl --user status memory-pro.service`
- If restarting, wait 15 seconds. The client script retries automatically for up to 20s.

### "Address already in use"
- Port 8001 is taken by a zombie process.
- **Fix**: `kill $(lsof -t -i:8001)` then restart service.
