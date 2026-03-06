# 🧠 Memory Pro (OpenClaw Skill)

[![Version: 2.0.0](https://img.shields.io/badge/Version-2.0.0-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://github.com/openclaw/openclaw)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A highly efficient semantic search engine for your OpenClaw workspace memory, powered by **FAISS** and **Sentence-Transformers**.

This skill indexes Markdown files and key agent files (e.g. `MEMORY.md`, `SOUL.md`) to provide **meaning-based context retrieval** instead of rigid exact-keyword matching. 

---

## 🚀 Features

- **Semantic Understanding**: Uses `all-MiniLM-L6-v2` to understand the *meaning* of your query.
- **Fast Retrieval**: Powered by Facebook's FAISS (Facebook AI Similarity Search).
- **Agent Friendly**: Zero-dependency client script designed for AI agents to easily execute via CLI.
- **Robust**: Background `systemd` service with auto-rebuild consistency checks.
- **Zero Hardcoding**: Dynamically resolves your workspace paths via environment variables.

## 🛠️ Installation

This skill can be installed on any OpenClaw host running Linux.

```bash
# Clone the repository
git clone https://github.com/yourusername/memory-pro-skill.git
cd memory-pro-skill

# Run the automated installer
chmod +x install.sh
./install.sh
```

The installation script will:
1. Copy the skill to `~/.openclaw/skills/memory-pro`
2. Set up an isolated Python virtual environment using `uv`
3. Configure and start a `systemd` user service (`memory-pro.service`)

## 💻 Usage (For Agents)

Once installed, OpenClaw agents can use the client script to query the running service.

### 1. Semantic Search (Recommended)
```bash
# Basic search for human reading
python ~/.openclaw/skills/memory-pro/scripts/search.py "What did I do yesterday?"

# JSON output for agent tool parsing
python ~/.openclaw/skills/memory-pro/scripts/search.py "project updates" --json
```

### 2. Manual Index Rebuild
The index is automatically rebuilt when the background service restarts. If you need to force an immediate update:

```bash
systemctl --user restart memory-pro.service
```
*(Note: Service restart takes ~15-20 seconds to rebuild index and load models. The client script has auto-retry logic built-in.)*

## 🔧 Environment Configuration

The service behavior can be customized by editing `~/.config/systemd/user/memory-pro.service`:

- `MEMORY_PRO_WORKSPACE_DIR`: The root of your workspace (e.g., `~/.openclaw/workspace/`)
- `MEMORY_PRO_DATA_DIR`: Directory containing `.md` files to index.
- `MEMORY_PRO_CORE_FILES`: Comma-separated list of core files to always index.
- `MEMORY_PRO_PORT`: The port for the API (default `8001`).

## 🩺 Troubleshooting

- **"Connection failed"**: The service might be stopped or restarting. Wait 15 seconds. Check with `systemctl --user status memory-pro.service`.
- **"Address already in use"**: Port 8001 is taken. **Fix**: `kill $(lsof -t -i:8001)` then restart the service.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
