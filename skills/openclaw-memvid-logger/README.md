# OpenClaw Memvid Logger

[![OpenClaw](https://img.shields.io/badge/OpenClaw->=2026.2.12-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Memvid](https://img.shields.io/badge/Memvid-2.0+-green)](https://memvid.com)

> **Memvid**: A single-file memory layer for AI agents with instant retrieval and long-term memory. Persistent, versioned, and portable memory, without databases.
>
> *"Replace complex RAG pipelines with a single portable file you own, and give your agent instant retrieval and long-term memory."*

A dual-output conversation logger for [OpenClaw](https://openclaw.ai) that captures **everything** - user messages, assistant responses, sub-agent conversations, tool executions, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

## ⚠️ Security & Privacy Notice

**Before installing, please understand:**

This skill captures **everything** - by design. It logs all user messages, assistant responses, sub-agent conversations, tool outputs, and system events to local files. This enables powerful long-term memory but requires trust.

**What you should know:**
- **Broad capture scope:** This is intentional - the skill's purpose is complete conversation logging
- **Sensitive data risk:** Tool outputs (commands, API responses, file contents) are logged. Review what tools expose.
- **Continuous logging:** Once installed, it runs automatically on every assistant response until removed
- **Optional cloud mode:** API mode with `MEMVID_API_KEY` sends data to memvid.com (third-party service). Free/local modes keep data on your machine only.
- **Your responsibility:** Secure the JSONL/.mv2 files, rotate logs regularly, and audit what gets captured.

**Mitigations available:**
- Use **Free/Sharding mode** to keep data local (no API key needed)
- Change default paths to encrypted locations
- Review `tools/log.py` before installing to understand exactly what gets logged
- File permissions: restrict access to log files (`chmod 600`)

**This skill is for users who want complete conversation memory and accept the privacy trade-offs.**

---

## ✨ What Makes This Different

- **📝 Dual Storage** - Every message saved to JSONL + Memvid simultaneously
- **🔍 Semantic Search** - Ask "What did the researcher agent find about Tesla?" not just keyword search
- **🤖 Full Context** - Captures user input, assistant output, agent chatter, tool results
- **💾 Three Modes** - API (unlimited), Free (50MB), or Sharding (multi-file)
- **🚀 Always On** - Hooks into OpenClaw automatically

## 🚀 Quick Start (Pick Your Mode)

### Option 1: API Mode - Near Limitless Memory ⭐ Recommended
**Best for:** Heavy users, unified search across everything  
**Cost:** $59-299/month via [memvid.com](https://memvid.com)

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger

# Configure
export MEMVID_API_KEY="your_key_here"
export MEMVID_MODE="single"

# Create memory
memvid create ~/anthony_memory.mv2

# Start OpenClaw - everything logs to one searchable file
```

**Search everything (single query across all time):**
```bash
# Natural language questions
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?"
memvid ask anthony_memory.mv2 "What did the researcher agent find?"
memvid ask anthony_memory.mv2 "Show me all Python scripts I requested"

# Keyword search
memvid find anthony_memory.mv2 --query "Mercedes"

# Temporal queries
memvid when anthony_memory.mv2 "last Tuesday"
```

---

### Option 2: Free Mode - 50MB Limit
**Best for:** Testing, light usage, single file  
**Cost:** FREE

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="single"

# Create memory
memvid create ~/anthony_memory.mv2

# Start OpenClaw
```

**⚠️ Limit:** 50MB (~5,000 conversation turns). When you hit it:
- Archive and start fresh, OR
- Upgrade to API mode ($59-299/month), OR  
- Switch to Sharding mode

---

### Option 3: Sharding Mode - Free Forever (Workaround)
**Best for:** Long-term use, staying under free tier  
**Cost:** FREE  
**Trade-off:** Multi-file search required

```bash
# Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/unified-logger
export MEMVID_MODE="monthly"  # Default

# Start OpenClaw - auto-creates monthly files
```

**How it works:**
- `anthony_memory_2026-02.mv2` (February)
- `anthony_memory_2026-03.mv2` (March - auto-created)
- Each file stays under 50MB

**⚠️ Sharding Search Differences:**

Single-file search (API/Free modes):
```bash
# One search gets everything
memvid ask anthony_memory.mv2 "What car did I decide to buy?"
# Returns: Results from ALL conversations across ALL time
```

Sharding search (requires multiple queries):
```bash
# Must search each month separately
memvid ask anthony_memory_2026-02.mv2 "car decision"  # Recent
memvid ask anthony_memory_2026-01.mv2 "car decision"  # January

# Or use a wrapper script to search all files
for file in anthony_memory_*.mv2; do
    echo "=== $file ==="
    memvid ask "$file" "car decision" 2>/dev/null | head -5
done

# You must know which month the conversation happened
# No cross-month context - "compare this month to last month" won't work
```

**Why sharding is harder:**
- Can't ask "what did we discuss in the past 3 months?" in one query
- No unified timeline across months
- Must remember which month you talked about what
- No cross-file semantic comparison

---

## 📊 Three Modes Compared

| Feature | API Mode | Free Mode | Sharding Mode |
|---------|----------|-----------|---------------|
| **Cost** | $59-299/mo | FREE | FREE |
| **Capacity** | 1GB-25GB+ | 50MB | Unlimited (files) |
| **Files** | 1 | 1 | Multiple (monthly) |
| **Unified Search** | ✅ One query | ✅ One query | ❌ Per-file queries |
| **Cross-Context Search** | ✅ Full history | ✅ Full history | ❌ Month isolated |
| **Best For** | Power users | Testing | Workaround for free tier |
| **Complexity** | Simple | Simple | Must track files |

---

## 💸 The Pricing Gap (AKA Why Sharding Exists)

**The situation:** Memvid's pricing goes from $0 (50MB) straight to $59/month (25GB).  
**The problem:** That's like buying a Ferrari when you just need a Honda Civic for your commute.

**What we're doing about it:**  
I reached out. While they consider it, Sharding Mode exists so you don't have to pay Ferrari prices for Honda Civic usage.

**You can help:**  
If you also think $0 → $59 is a bit much, reach out to Memvid at [memvid.com](https://memvid.com) and tell them stackBlock sent you. The more voices, the faster we get that $10-20 middle tier for the rest of us.

*Until then: Sharding Mode. Because startups shouldn't have to choose between ramen and memory.* 🍜

---

## 🔍 Search Examples by Mode

### API Mode / Free Mode (Single File)

**One command searches everything:**

```bash
# What did you say about...?
memvid ask anthony_memory.mv2 "What was your recommendation about the Mercedes?"

# What did I ask for...?
memvid ask anthony_memory.mv2 "What Python scripts did I request?"

# What did agents do...?
memvid ask anthony_memory.mv2 "What did the researcher agent find about options?"

# Temporal - searches all history
memvid when anthony_memory.mv2 "last month"

# Cross-time context
memvid ask anthony_memory.mv2 "Compare our BadjAI discussions from January to March"
```

### Sharding Mode (Multiple Files)

**Must specify which file to search:**

```bash
# Recent conversations (current month)
memvid ask anthony_memory_2026-02.mv2 "recent discussions"

# Specific month
memvid ask anthony_memory_2026-01.mv2 "January conversations"

# Search all months (manual)
for file in anthony_memory_*.mv2; do
    echo "=== $file ==="
    memvid ask "$file" "your query"
done

# Can't do: cross-month comparison
# Can't do: "what did we discuss over the past 3 months"
# Can't do: unified timeline view
```

### JSONL Backup (All Modes)

```bash
# Quick grep
grep "Mercedes" conversation_log.jsonl

# Complex queries with jq
jq 'select(.role_tag == "user" and .content | contains("Python"))' conversation_log.jsonl

# Time range (works across all modes)
jq 'select(.timestamp >= "2026-02-01" and .timestamp < "2026-03-01")' conversation_log.jsonl
```

---

## 🔍 Search Usage

**Default search mode: `--mode neural`** for maximum accuracy and semantic understanding:

```bash
# Semantic search (default recommended mode)
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?" --mode neural
memvid ask anthony_memory.mv2 "What supplements did Dr. Sinclair recommend?" --mode neural
memvid ask anthony_memory.mv2 "Show me all Python scripts I requested" --mode neural

# Alternative modes (when explicitly needed)
memvid find anthony_memory.mv2 --mode lex --query "exact_keyword"     # Fastest: ~8ms
memvid find anthony_memory.mv2 --mode hybrid --query "diabetes meds"  # Balanced: ~300ms
```

**Speed vs Accuracy:**
- `neural`: ~200ms — **Default** — Understands context, synonyms, meaning
- `lex`: ~8ms — Exact keyword matching only
- `hybrid`: ~300-500ms — Combines both approaches

The ~200ms latency for neural mode is the recommended default for production use.

## 📁 What Gets Logged

| Source | Tag | Captured |
|--------|-----|----------|
| **Your messages** | `[user]` | ✅ Everything you type |
| **My responses** | `[assistant]` | ✅ Everything I say |
| **Sub-agents** | `[agent:researcher]`, `[agent:coder]` | ✅ Agent conversations |
| **Tool calls** | `[tool:exec]`, `[tool:browser]` | ✅ Commands & results |
| **System** | `[system]` | ✅ Cron, heartbeats, events |

---

## 🏗️ Architecture

```
User → OpenClaw → log.py → JSONL (backup)
                         → Memvid .mv2 (search)
```

**Zero data loss:** Every character preserved  
**Instant indexing:** Searchable immediately  
**Crash proof:** Append-only writes

---

## ⚙️ Configuration

**⚠️ CRITICAL: Environment variables must be set system-wide**

OpenClaw runs as a background service and does not inherit `.bashrc` or `.profile`. You **must** set environment variables in `/etc/environment`:

```bash
# Add to /etc/environment (requires sudo)
sudo tee -a /etc/environment << 'EOF'
MEMVID_MODE="monthly"
MEMVID_PATH="/home/YOUR_USERNAME/.openclaw/workspace/anthony_memory_2026-02.mv2"
JSONL_LOG_PATH="/home/YOUR_USERNAME/.openclaw/workspace/conversation_log.jsonl"
MEMVID_BIN="/home/YOUR_USERNAME/.npm-global/bin/memvid"
EOF

# Reboot to apply
sudo reboot
```

**Why `/etc/environment`?**
- `.bashrc` / `.profile`: Only work for interactive terminal sessions
- `/etc/environment`: System-wide, works for background services including OpenClaw

**After reboot, verify:**
```bash
echo $MEMVID_MODE  # Should show: monthly
```

### Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MEMVID_MODE` | Yes | `monthly` | `single` (one file) or `monthly` (rotation) |
| `MEMVID_PATH` | Yes | Auto-derived | Path to `.mv2` memory file |
| `JSONL_LOG_PATH` | Yes | Auto-derived | Path to JSONL backup |
| `MEMVID_BIN` | Yes | `memvid` | Path to memvid CLI |
| `MEMVID_API_KEY` | No | - | For API mode only (paid) |

### Quick Mode Reference

```bash
# API Mode (single file, cloud, paid)
export MEMVID_MODE="single"
export MEMVID_API_KEY="your_key_here"

# Free Mode (single file, local, 50MB limit)
export MEMVID_MODE="single"

# Sharding Mode (monthly files, local, unlimited) ⭐ Recommended
export MEMVID_MODE="monthly"
```

---

## 🆘 Troubleshooting

### "Environment variables not set" / Hook not logging

**Symptoms:**
- `openclaw hooks info unified-logger` shows environment requirements as ❌
- JSONL file not being written
- `echo $MEMVID_MODE` returns empty

**Cause:** Variables set in `.bashrc` or `.profile` don't persist for background services.

**Fix:**
```bash
# Check current setting
echo $MEMVID_MODE

# If empty, add to /etc/environment (NOT .bashrc)
sudo tee -a /etc/environment << 'EOF'
MEMVID_MODE="monthly"
MEMVID_PATH="/home/YOUR_USERNAME/.openclaw/workspace/memory_2026-02.mv2"
JSONL_LOG_PATH="/home/YOUR_USERNAME/.openclaw/workspace/conversation_log.jsonl"
MEMVID_BIN="/home/YOUR_USERNAME/.npm-global/bin/memvid"
EOF

# Reboot and verify
sudo reboot
# After reboot:
echo $MEMVID_MODE  # Should show: monthly
```

### "Hook registered but not logging messages"

**Symptoms:**
- `openclaw hooks list` shows ✅ ready
- `openclaw hooks info unified-logger` shows all requirements met
- But JSONL/Memvid not being updated

**Cause:** OpenClaw 2026.2.12+ requires JavaScript (`.js`) handlers, not TypeScript (`.ts`), for managed hooks.

**Fix:** Ensure handler is JavaScript:
```bash
ls ~/.openclaw/hooks/unified-logger/
# Should show: handler.js (NOT handler.ts)

# If you have handler.ts, rename/create handler.js instead
```

**Correct hook structure:**
```
~/.openclaw/hooks/unified-logger/
├── HOOK.md      # Metadata with "export": "default"
├── handler.js   # JavaScript handler (NOT .ts)
└── healthcheck.py  # Optional monitoring
```

### "Memvid index not updating" / "invalid value for --tag"

**Symptoms:**
- JSONL file updates correctly
- Memvid search returns no results
- Error: `expected KEY=VALUE, got 'user,telegram'`

**Cause:** Memvid 2.0+ changed tag format from comma-separated to `KEY=VALUE` pairs.

**Fix:** Update to unified-logger v1.2.5+ which uses correct format:
```python
# OLD (broken):
--tag "user,telegram,agent:researcher"

# NEW (correct):
--tag "role=user" --tag "source=telegram" --tag "agent=researcher"
```

### "Free tier limit exceeded" (Free Mode)

```bash
# Option 1: Archive and start fresh
mv anthony_memory.mv2 anthony_memory_archive.mv2
memvid create anthony_memory.mv2

# Option 2: Switch to monthly sharding (recommended)
# Edit /etc/environment:
MEMVID_MODE="monthly"
# Then reboot

# Option 3: Get API key for unlimited
export MEMVID_API_KEY="your_key"  # $59-299/month at memvid.com
```

### "memvid: command not found"

```bash
npm install -g memvid

# Verify:
which memvid  # Should show path
memvid --version  # Should show version
```

### Check Everything is Working

```bash
# 1. Environment variables
echo $MEMVID_MODE
echo $JSONL_LOG_PATH
echo $MEMVID_PATH
echo $MEMVID_BIN

# 2. Hook status
openclaw hooks list
openclaw hooks info unified-logger

# 3. Recent logs
tail -5 "$JSONL_LOG_PATH"

# 4. Memvid search
memvid find "$MEMVID_PATH" --query "test"

# 5. Health check log
cat ~/.openclaw/logs/logger-health.log
```

---

## 📚 Documentation

- [SKILL.md](SKILL.md) - Detailed OpenClaw skill documentation
- [Memvid Docs](https://memvid.com/docs) - Memvid CLI reference
- [OpenClaw Docs](https://docs.openclaw.ai) - OpenClaw framework

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT - See [LICENSE](LICENSE)

---

**Made with 🤝 for the OpenClaw community**

- GitHub: [github.com/stackBlock/openclaw-memvid-logger](https://github.com/stackBlock/openclaw-memvid-logger)
- Discord: [discord.com/invite/clawd](https://discord.com/invite/clawd)

**About Memvid:**
> Memvid is a single-file memory layer for AI agents with instant retrieval and long-term memory. 
> Persistent, versioned, and portable memory, without databases.
> 
> Replace complex RAG pipelines with a single portable file you own, and give your agent 
> instant retrieval and long-term memory.
