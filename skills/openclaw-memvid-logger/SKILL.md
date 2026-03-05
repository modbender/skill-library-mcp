# Unified Conversation Logger v1.2.5

**Version:** 1.2.5 (Critical Fixes Edition)  
**Author:** stackBlock  
**License:** MIT  
**OpenClaw:** >= 2026.2.12

A dual-output conversation logger for OpenClaw that captures **everything** - user messages, assistant responses, sub-agent conversations, tool calls, and system events - to both JSONL (backup) and Memvid (semantic search) formats.

> **Memvid**: A single-file memory layer for AI agents with instant retrieval and long-term memory. Persistent, versioned, and portable memory, without databases.
>
> *"Replace complex RAG pipelines with a single portable file you own, and give your agent instant retrieval and long-term memory."*

---

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

## What's New in v1.2.5

### Critical Fixes
- **Memvid Tag Format Fixed:** Updated to `KEY=VALUE` format for Memvid 2.0+ compatibility
  - Old (broken): `--tag "user,telegram"`
  - New (fixed): `--tag "role=user" --tag "source=telegram"`
- **Environment Variable Documentation:** Added `/etc/environment` instructions (`.bashrc` doesn't work for background services)
- **Hook Handler Format:** Documented JavaScript (`.js`) requirement for OpenClaw 2026.2.12+
- **Comprehensive Troubleshooting:** Added detailed troubleshooting section for common setup issues

### Compatibility
- Verified with OpenClaw 2026.2.12
- Verified with Memvid CLI 2.0+

## Previous Versions

### v1.2.4
- **Neural Search Default:** Updated search guidance to use `--mode neural` as default for maximum accuracy
- **Performance Documentation:** Clarified latency trade-offs (~200ms for neural vs ~8ms for lexical)
- **Search Mode Policy:** Recommends neural for semantic understanding, lexical only when speed is critical

### v1.2.3
- **Version Cohesion:** All files synchronized to v1.2.3
- **Documentation Consistency:** README and SKILL.md now have matching content
- **Security Improvements:** Generic paths (no hardcoded user directories), install script asks permission
- **Registry Compliance:** Complete metadata (env vars, credentials, warnings) for ClawHub transparency
- **Privacy Documentation:** Comprehensive Security & Privacy Notice explaining data capture scope
- **Role Tagging:** Distinguishes user, assistant, agent:*, system, and tool messages
- **Full Context:** Captures sub-agent chatter, tool results, background processes
- **Three Storage Modes:** API mode (single file), Free mode (50MB), Sharding mode (monthly rotation)
- **Semantic Search:** Ask "What did the researcher agent find?" or "What did I say about X?"

## Quick Install (Choose Your Mode)

### Option 1: API Mode (Recommended) - Near Limitless Memory
**Best for:** Heavy users, unified search across everything  
**Cost:** $59-299/month via [memvid.com](https://memvid.com)

```bash
# 1. Get API key from memvid.com ($59/month for 1GB, $299 for 25GB)
export MEMVID_API_KEY="your_api_key_here"
export MEMVID_MODE="single"

# 2. Install
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/

# 3. Create unified memory file
memvid create ~/memory.mv2

# 4. Start OpenClaw - everything logs to one searchable file
```

**Search everything at once:**
```bash
memvid ask memory.mv2 "What did we discuss about BadjAI?"
memvid ask memory.mv2 "What did the researcher agent find about Tesla?"
memvid ask memory.mv2 "Show me all the Python scripts I asked for"
```

---

### Option 2: Free Mode (50MB Limit) - Complete Memory in One Place
**Best for:** Testing, light usage, single searchable file  
**Cost:** FREE

```bash
# 1. Install (no API key needed)
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="single"

# 2. Create memory file
memvid create ~/memory.mv2

# 3. Start OpenClaw
```

**⚠️ Limit:** 50MB (~5,000 conversation turns). When you hit it:
- Archive and start fresh, OR
- Upgrade to API mode ($59-299/month), OR  
- Switch to Sharding mode

---

### Option 3: Sharding Mode - More Than 50MB, Free Forever
**Best for:** Long-term use, staying under free tier  
**Cost:** FREE  
**Trade-off:** Multi-file search

```bash
# 1. Install (no API key needed)
npm install -g memvid
git clone https://github.com/stackBlock/openclaw-memvid-logger.git
cp -r openclaw-memvid-logger ~/.openclaw/workspace/skills/
export MEMVID_MODE="monthly"  # This is the default

# 2. Start OpenClaw - auto-creates monthly files
```

**How it works:**
- `memory_2026-02.mv2` (February)
- `memory_2026-03.mv2` (March - auto-created)
- Each file stays under 50MB

**⚠️ Sharding Search Differences:**

Single-file search (API/Free modes):
```bash
# One search gets everything
memvid ask memory.mv2 "What car did I decide to buy?"
# Returns: Results from ALL conversations across ALL time
```

Sharding search (requires multiple queries):
```bash
# Must search each month separately
memvid ask memory_2026-02.mv2 "car decision"  # Recent
memvid ask memory_2026-01.mv2 "car decision"  # January

# Or use a wrapper script to search all files
for file in memory_*.mv2; do
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

## What Gets Logged

### Role Tags (Automatic)

| Role | Tag | Example Search |
|------|-----|----------------|
| **User** | `[user]` | "What did **I** say about Mercedes?" |
| **Assistant** | `[assistant]` | "What did **you** recommend?" |
| **Sub-agents** | `[agent:researcher]`, `[agent:coder]` | "What did the **researcher** find?" |
| **System** | `[system]` | "When did the **cron job** run?" |
| **Tools** | `[tool:exec]`, `[tool:browser]` | "What **commands** were run?" |

### Everything Captured

- ✅ User messages (what you type)
- ✅ Assistant responses (what I say back)
- ✅ Sub-agent conversations (researcher, coder, vision, math, etc.)
- ✅ Tool executions (bash commands, browser actions, file edits)
- ✅ Background processes (cron jobs, heartbeats, scheduled tasks)
- ✅ System events (config changes, restarts, errors)

## Architecture

```
┌─────────────────────────────────────────┐
│           OpenClaw Ecosystem            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  User   │  │Assistant│  │  Agents │ │
│  │ Messages│  │Responses│  │Research │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       └─────────────┴─────────────┘     │
│                     │                   │
│              ┌──────▼──────┐            │
│              │  log.py     │            │
│              │  (this skill)│           │
│              └──────┬──────┘            │
└─────────────────────┼───────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
┌───────┐      ┌─────────────┐    ┌──────────┐
│ JSONL │      │   Memvid    │    │  Search  │
│ File  │      │   Files     │    │  Query   │
└───────┘      └─────────────┘    └──────────┘
    │                 │
    ↓                 ↓
 grep/jq       memvid ask/find
```

## Usage Examples

### Natural Language Search

```bash
# What did you say about...?
memvid ask memory_2026-02.mv2 "What was your recommendation about the Mercedes vs Tesla?"

# What did I ask for...?
memvid ask memory_2026-02.mv2 "What Python scripts did I request last week?"

# What did agents do...?
memvid ask memory_2026-02.mv2 "What did the researcher agent find about options trading?"

# System events...?
memvid ask memory_2026-02.mv2 "When did the PowerSchool grades cron job run?"
```

### Keyword Search

```bash
# Find specific terms
memvid find memory_2026-02.mv2 --query "Mercedes"

# With filters
memvid find memory_2026-02.mv2 --query "script" --tag agent:coder
```

### Temporal Queries

```bash
memvid when memory_2026-02.mv2 "yesterday"
memvid when memory_2026-02.mv2 "last Tuesday"
memvid when memory_2026-02.mv2 "3 days ago"
```

## ⚡ Search Performance Guide

Memvid has three search modes. **This skill uses `--mode neural` by default for maximum accuracy:**

### Default: Neural Search (Recommended)
```bash
# Always use neural for semantic understanding and context
memvid ask memory.mv2 "What supplements did Dr. Sinclair recommend?" --mode neural
memvid ask memory.mv2 "What did we discuss about BadjAI?" --mode neural
memvid ask memory.mv2 "Show me the Python scripts I requested" --mode neural
```
**Speed:** ~200ms | **Best for:** Semantic understanding, context, synonyms, conceptual relationships

### Alternative Modes (Use When Explicitly Requested)

**Mode 1: Lexical Search (Fastest)**
```bash
# Use only for exact keyword matching when speed is critical
memvid find memory.mv2 --mode lex --query "metformin"
```
**Speed:** ~8ms | **Use when:** Exact word matching needed, latency is critical

**Mode 2: Hybrid Search (Balanced)**
```bash
# Combines lexical + neural
memvid find memory.mv2 --mode hybrid --query "diabetes medications"
```
**Speed:** ~300-500ms | **Use when:** You want both exact matches and semantic similarity

### Why Neural as Default?

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| `neural` | ~200ms | **Highest** | **Default - semantic understanding** |
| `lex` | ~8ms | Keyword only | Speed-critical exact matches |
| `hybrid` | ~300-500ms | High | Balanced approach |

**The ~200ms trade-off is worth it:** Neural mode understands context, handles paraphrases, and finds conceptually related information that lexical search misses entirely.

### JSONL Backup

```bash
# Quick grep
grep "Mercedes" conversation_log.jsonl

# Complex queries with jq
jq 'select(.role_tag == "user" and .content | contains("Python"))' conversation_log.jsonl

# Time range
jq 'select(.timestamp >= "2026-02-01" and .timestamp < "2026-03-01")' conversation_log.jsonl
```

## Configuration

### Environment Variables

| Variable | Default | Mode | Description |
|----------|---------|------|-------------|
| `MEMVID_API_KEY` | (none) | API | Your memvid.com API key |
| `MEMVID_MODE` | `monthly` | All | `single` or `monthly` |
| `JSONL_LOG_PATH` | `~/workspace/conversation_log.jsonl` | All | Backup log file |
| `MEMVID_PATH` | `~/workspace/memory.mv2` | All | Base path for memory files |
| `MEMVID_BIN` | `~/.npm-global/bin/memvid` | All | Path to memvid CLI |

### OpenClaw Hooks (Advanced)

Add to `openclaw.json`:

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "conversation-logger": {
          "enabled": true,
          "command": "python3 ~/.openclaw/workspace/skills/unified-logger/tools/log.py"
        }
      }
    }
  }
}
```

## Memory File Formats

### Mode 1: Single File (API or Free Mode)
```
memory.mv2
├── [user] messages
├── [assistant] responses  
├── [agent:researcher] findings
├── [agent:coder] code
├── [tool:exec] commands
└── [system] events
```

### Mode 2: Sharding (Monthly Rotation)
```
memory_2026-01.mv2  (January conversations)
memory_2026-02.mv2  (February conversations) ← Current
memory_2026-03.mv2  (March, auto-created on March 1)
```

## Troubleshooting

### "Free tier limit exceeded" (Free Mode)
```bash
# Option 1: Archive and start fresh
mv memory.mv2 memory_archive.mv2
memvid create memory.mv2

# Option 2: Switch to monthly sharding
export MEMVID_MODE="monthly"

# Option 3: Get API key
export MEMVID_API_KEY="your_key"  # $59-299/month at memvid.com
```

### "Cannot find memory file" (Sharding Mode)
Current month's file auto-creates. If missing:
```bash
memvid create memory_$(date +%Y-%m).mv2
```

### Missing agent conversations
Agents log to their own sessions. Ensure skill is installed in main agent workspace and sub-agents inherit it.

### Search returns wrong speaker
Memvid uses semantic search. Be specific:
- ❌ "Mercedes" → Returns all mentions
- ✅ "What did I say about Mercedes" → Targets [user] frames
- ✅ "Your recommendation about Mercedes" → Targets [assistant] frames

## Comparing the Three Modes

| Feature | API Mode | Free Mode | Sharding Mode |
|---------|----------|-----------|---------------|
| **Cost** | $59-299/mo | FREE | FREE |
| **Capacity** | 1-25GB+ | 50MB | Unlimited (files) |
| **Files** | 1 | 1 | Multiple (monthly) |
| **Unified Search** | ✅ Yes | ✅ Yes | ❌ Per-file only |
| **Cross-Context Search** | ✅ Full history | ✅ Full history | ❌ Month isolated |
| **Best For** | Power users | Testing | Long-term free use |
| **Complexity** | Simple | Simple | Must track files |

## 💸 The Pricing Gap (AKA Why Sharding Exists)

**The situation:** Memvid's pricing goes from $0 (50MB) straight to $59/month (25GB).  
**The problem:** That's like buying a Ferrari when you just need a Honda Civic for your commute.

**What we're doing about it:**  
I reached out. While they consider it, Sharding Mode exists so you don't have to pay Ferrari prices for Honda Civic usage.

**You can help:**  
If you also think $0 → $59 is a bit much, reach out to Memvid at [memvid.com](https://memvid.com) and tell them stackBlock sent you. The more voices, the faster we get that $10-20 middle tier for the rest of us.

*Until then: Sharding Mode. Because startups shouldn't have to choose between ramen and memory.* 🍜

## Future Enhancements

- [ ] Auto-archive old months to cold storage
- [ ] Web UI for browsing conversations
- [ ] Cross-file search wrapper script
- [ ] Export to other formats (Markdown, PDF)
- [ ] Conversation threading visualization

## Support

- **GitHub Issues:** [github.com/stackBlock/openclaw-memvid-logger](https://github.com/stackBlock/openclaw-memvid-logger)
- **OpenClaw Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Memvid Support:** [memvid.com/docs](https://memvid.com/docs)

## License

MIT - See [LICENSE](LICENSE)

---

**About Memvid:**
> Memvid is a single-file memory layer for AI agents with instant retrieval and long-term memory. 
> Persistent, versioned, and portable memory, without databases.
> 
> Replace complex RAG pipelines with a single portable file you own, and give your agent 
> instant retrieval and long-term memory.
