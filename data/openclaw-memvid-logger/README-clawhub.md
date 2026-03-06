# MemSync - Dual Memory System

A dual-output conversation logger for OpenClaw that captures **everything** - user messages, assistant responses, sub-agent conversations, tool executions, and system events.

## What It Does

- **📝 Dual Storage** - Every message saved to JSONL (backup) + single-file memory (searchable)
- **🔍 Semantic Search** - Ask "What did the researcher agent find about Tesla?" not just keyword search
- **🤖 Full Context** - Captures user input, assistant output, agent chatter, tool results
- **💾 Three Modes** - API (unlimited), Free (50MB), Sharding (multi-file)
- **🚀 Always On** - Hooks into OpenClaw automatically

## Quick Start

### Installation

```bash
npm install -g @memvid/cli  # External dependency
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/
```

### Choose Your Mode

**Mode 1: API** - Near limitless, paid tier ($59-299/month)
```bash
export MEMVID_API_KEY="your_key"
export MEMVID_MODE="single"
memvid create ~/memory.mv2
```

**Mode 2: Free** - 50MB limit, single file
```bash
export MEMVID_MODE="single"
memvid create ~/memory.mv2
```

**Mode 3: Sharding** - Free forever, monthly files
```bash
export MEMVID_MODE="monthly"  # Default
# Auto-creates: memory_2026-02.mv2, memory_2026-03.mv2, etc.
```

## Search Your Conversations

**API/Free Mode:**
```bash
memvid ask memory.mv2 "What did we discuss?"
memvid ask memory.mv2 "What did the researcher agent find?"
```

**Sharding Mode:**
```bash
memvid ask memory_2026-02.mv2 "recent discussions"
memvid ask memory_2026-01.mv2 "January conversations"
```

## What Gets Logged

| Source | Tag | Description |
|--------|-----|-------------|
| **Your messages** | `[user]` | Everything you type |
| **My responses** | `[assistant]` | All AI responses |
| **Sub-agents** | `[agent:name]` | Researcher, coder, vision, math |
| **Tools** | `[tool:name]` | Bash, browser, file operations |
| **System** | `[system]` | Cron, heartbeats, events |

## Storage Modes Compared

| Feature | API | Free | Sharding |
|---------|-----|------|----------|
| **Cost** | $59-299/mo | FREE | FREE |
| **Capacity** | 1-25GB+ | 50MB | Unlimited |
| **Files** | 1 | 1 | Monthly |
| **Unified Search** | ✅ | ✅ | ❌ Per-file |
| **Best For** | Power users | Testing | Long-term free |

## Configuration

```bash
# Choose mode
export MEMVID_MODE="single"    # API or Free
export MEMVID_MODE="monthly"   # Sharding (default)

# Optional paths
export JSONL_LOG_PATH="~/conversation_log.jsonl"
export MEMVID_PATH="~/memory.mv2"

# For API mode only
export MEMVID_API_KEY="your_key"
```

## About the Technology

This skill uses **Memvid** - a single-file memory layer for AI agents with instant retrieval and long-term memory. It provides persistent, versioned, and portable memory without databases.

> "Replace complex RAG pipelines with a single portable file you own, and give your agent instant retrieval and long-term memory."

Learn more at [memvid.com](https://memvid.com)

## License

MIT - See [LICENSE](LICENSE)

**Made with 🤝 for the OpenClaw community**
