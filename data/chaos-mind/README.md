# CHAOS Memory - ClawdHub Skill

**Hybrid search for team memories with auto-capture.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://clawdhub.com/skills/chaos-memory)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/hargabyte/chaos-memory/blob/main/LICENSE)

---

## Features

🔍 **Hybrid Search** - Combines 4 signals for optimal relevance:
- BM25 keyword matching (0.4 weight)
- Vector semantic search (0.4 weight)
- Graph relationships (0.1 weight)
- Heat/access patterns (0.1 weight)

🤖 **Auto-Capture (The Killer Feature - Opt-In)** - Automatically builds your memory from sessions:
- **43x faster** than manual entry - captures context while you work
- Extracts decisions, insights, facts automatically with Qwen3-1.7B
- 100% local processing (no cloud/external APIs)
- **Disabled by default** for privacy - you control what it reads
- See "Auto-Capture" section below for setup (takes ~5 minutes)

📊 **Progressive Disclosure** - Choose detail level:
- Index mode: ~75 tokens/result (90% savings)
- Summary mode: ~250 tokens/result (67% savings)
- Full mode: ~750 tokens/result (complete context)

⚡ **43x Faster** - Optimized extraction:
- 2.6s per message
- ~42s per 16-message session
- Qwen3-1.7B with thinking disabled

🔗 **Enhanced with Cortex + Beads** (optional):
- **Cortex** - Anchor memories to code locations (semantic linking)
- **Beads** - Link memories to tasks/issues (project tracking)
- Together: Search shows memories → code → tasks in one view

---

## Installation

### Via ClawdHub (Recommended)

```bash
clawdhub install chaos-memory
```

### Via Bot

Send to your AI assistant:
```
Install the chaos-memory skill from ClawdHub
```

### Manual

```bash
curl -fsSL https://raw.githubusercontent.com/hargabyte/Chaos-mind/main/install.sh | bash
```

---

## Quick Start

**Search memories:**
```bash
chaos-cli search "pricing decisions" --mode summary --limit 5
```

**Store a memory:**
```bash
chaos-cli store "Important decision: ..." --category decision --priority 0.9
```

**List recent:**
```bash
chaos-cli list 10
```

---

## Usage

### Search

```bash
# Fast scan (index mode)
chaos-cli search "architecture" --mode index --limit 10

# Balanced (summary mode)
chaos-cli search "pricing" --mode summary --limit 5

# Deep dive (full mode)
chaos-cli search "model selection" --mode full --limit 3

# Enable hybrid search
chaos-cli search "query" --hybrid
```

### Store

```bash
# Decision
chaos-cli store "Enterprise tier at $99/mo" --category decision --priority 0.9

# Core fact
chaos-cli store "CHAOS uses port 3307" --category core --priority 0.7

# Research finding
chaos-cli store "43x performance improvement" --category research --priority 0.8
```

### Categories

| Category | Use For |
|----------|---------|
| `decision` | Team decisions, commitments |
| `core` | Fundamental facts, configurations |
| `semantic` | Domain knowledge, concepts |
| `research` | Findings, experiments |

### Priority Levels

| Level | Meaning |
|-------|---------|
| 0.9-1.0 | Critical (major decisions) |
| 0.7-0.8 | High (important context) |
| 0.5-0.6 | Medium (useful reference) |
| 0.3-0.4 | Low (general notes) |

---

## 🚀 Auto-Capture - The Most Powerful Feature

**What it does:** Automatically extracts memories from your AI sessions in the background - no manual input needed!

**Why it matters:**
- **43x faster** than manual memory creation
- Captures context you'd otherwise lose
- Extracts decisions, insights, and key facts automatically
- Builds your knowledge base while you work

**The catch:** Disabled by default for privacy (you control when/what it reads)

### How to Enable Auto-Capture

**1. Review what it does:**
- Reads session transcript files (only paths you configure)
- Extracts meaningful content using local Qwen3-1.7B
- Stores in your local database (no cloud/external APIs)
- Processes 100% on your machine

**2. Configure paths:**
```bash
nano ~/.chaos/config/consolidator.yaml
```

Edit these sections:
```yaml
auto_capture:
  enabled: true  # Change from false
  sources:  # Add your session paths
    - ~/.openclaw-*/agents/*/sessions/*.jsonl
    - ~/your-project/memory/*.md
```

**3. Install dependencies:**
```bash
# Install Ollama (if not already)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen3:1.7b
```

**4. Test it:**
```bash
# Dry-run (shows what would be processed)
chaos-consolidator --auto-capture --once --dry-run

# Process once
chaos-consolidator --auto-capture --once

# Run continuously in background
nohup chaos-consolidator --auto-capture > ~/.chaos/consolidator.log 2>&1 &
```

**5. Check it's working:**
```bash
tail -f ~/.chaos/consolidator.log
chaos-cli list  # Should see extracted memories
```

### What Gets Captured

**✅ Captures:**
- Decisions and reasoning
- Important facts and data
- Key insights and discoveries
- Technical details and specifications
- Problem-solving approaches

**❌ Skips:**
- Greetings and pleasantries
- Filler words and acknowledgments
- Repetitive confirmations
- Low-value back-and-forth

### Performance

- **Speed:** 2.6s per message (~42s per 16-message session)
- **Accuracy:** 0.7+ confidence threshold (high-quality extraction)
- **Efficiency:** Processes in background, doesn't slow your work

### Privacy & Control

- **Disabled by default** - you must explicitly enable
- **You choose paths** - only processes files you configure
- **100% local** - no external API calls or cloud services
- **Auditable** - check logs anytime: `tail -f ~/.chaos/consolidator.log`
- **Reversible** - disable anytime by setting `enabled: false`

**Bottom line:** Auto-capture is optional but highly recommended once you're comfortable with the privacy model.

---

## Configuration

**Location:** `~/.chaos/chaos.conf`

```bash
CHAOS_HOME=~/.chaos/chaos-memory
CHAOS_DB_DIR=~/.chaos/data
CHAOS_DB_PORT=3307
CHAOS_MODEL=qwen3:1.7b
```

**Override:**
```bash
export CHAOS_DB_PORT=3308
chaos-cli search "query"
```

---

## 🔗 Integrations (Optional Enhancements)

CHAOS Memory becomes dramatically more powerful when paired with complementary tools:

### Cortex (cx) - Semantic Code Anchoring

**What:** Links memories to specific code locations and files  
**Why:** Provides concrete code context for abstract decisions  
**Install:** https://github.com/hargabyte/cortex

**Example:**
```bash
# Search returns memory + code location
chaos-cli search "auth implementation"
→ "Changed to JWT-based auth"
→ 📍 src/auth/middleware.ts:45-89
→ 📍 config/security.yml:12
```

**How it works:**
- CHAOS auto-detects `cx` binary on startup
- Creates semantic links when storing memories near code changes
- Search results include relevant code snippets automatically

**Status:** Check logs for `[OPT] Cortex Engine: FOUND`

### Beads - Task & Issue Tracking

**What:** Connects memories to tasks, PRs, and project milestones  
**Why:** Track decision → implementation pipeline  
**Install:** https://github.com/hargabyte/beads

**Example:**
```bash
# Store with task reference
chaos-cli store "Refactor auth module" --task AUTH-42

# Search shows task status
chaos-cli search "auth refactor"
→ "Refactor auth module"
→ 📋 AUTH-42: In Progress
→ 🔗 PR #156, commit abc123
```

**How it works:**
- CHAOS auto-detects `beads` or `beads-rust` binary
- Links memories to Beads issues bidirectionally
- Search can filter by task status, assignee, or milestone

**Status:** Check logs for `[OPT] Beads Task Manager: FOUND`

### Combined Power: The Trinity

When **CHAOS + Cortex + Beads** work together, you get:

```bash
chaos-cli search "caching"
→ Memory: "Added Redis for session storage"
→ 📍 Code: cache/redis.ts:34-156, config/redis.yml
→ 📋 Task: PERF-089 (Completed 2024-02-01)
→ 🔗 Related: 4 memories, 7 files, 2 PRs
→ 🔥 Heat: 0.87 (accessed 12 times)
```

**Benefits:**
- **Context-complete:** Never wonder "where is this code?" or "which task?"
- **Faster onboarding:** New team members see decisions → implementations → code
- **Better search:** Multi-signal ranking (text + code + tasks + heat)
- **Historical insight:** Track how decisions evolved into working code

**Installation:**
```bash
# 1. Install CHAOS (this skill)
clawdhub install chaos-memory

# 2. Install Cortex (optional)
clawdhub install cortex

# 3. Install Beads (optional)
clawdhub install beads-rust

# All three auto-discover each other!
```

**Recommended for:**
- Teams with multiple projects
- Long-running codebases (6+ months)
- Frequent context-switching
- Remote/distributed teams

---

## Performance

| Metric | Value |
|--------|-------|
| Extraction speed | 2.6s per message |
| Session speed | ~42s for 16 messages |
| Improvement | 43x faster |
| Token savings (index) | 90% |
| Token savings (summary) | 67% |

---

## Requirements

- **RAM:** 16 GB minimum
- **Disk:** 5 GB (for model + database)
- **CPU:** 6+ cores recommended
- **OS:** Linux, macOS, Windows (WSL)

**Dependencies** (auto-installed):
- Dolt 0.50.0+
- Ollama 0.1.0+
- Go 1.21+ (for building)

---

## Troubleshooting

**Command not found:**
```bash
which chaos-cli
# If not found: cd ~/.chaos/chaos-memory && ./install.sh
```

**No results:**
```bash
# Check database
cd ~/.chaos/data && dolt sql -q "SELECT COUNT(*) FROM memories;"

# Run extraction
chaos-consolidator --auto-capture --once
```

**Database error:**
```bash
# Restart Dolt
ps aux | grep dolt
cd ~/.chaos/data && dolt sql-server &
```

---

## Security & Privacy

**🔒 Local-Only Storage:**
- All memories stored locally: `~/.chaos/db`
- No cloud sync, no external transmission
- Your data never leaves your machine
- Database is version-controlled (Dolt) for full auditability

**⚙️ Auto-Capture (Opt-In Only):**
- **Disabled by default** - requires explicit configuration
- You control which session files to process
- Manual configuration required in `~/.chaos/config.yaml`
- Only processes paths you explicitly specify in `auto_capture.sources`
- All processing runs locally via your own Ollama instance
- No external API calls or cloud services

**🔍 Permissions:**
- **Read:** Session transcript files (only paths you configure)
- **Write:** Local database (`~/.chaos/db`)
- **Network:** None (100% offline operation)

**✅ Transparency:**
- Install script included in repo (`install.sh`) - auditable before running
- Binaries built via GitHub Actions (reproducible builds)
- Database is plain Dolt SQL - inspect anytime with `dolt sql`
- Open source: Review all code at https://github.com/hargabyte/Chaos-mind

**🛡️ Control:**
```bash
# Preview what auto-capture would process (dry-run)
chaos-consolidator --auto-capture --once --dry-run

# Disable auto-capture completely
# Edit ~/.chaos/config.yaml and set:
auto_capture:
  enabled: false

# Or simply don't configure any session paths
```

**📋 What Data is Accessed:**
- Manual mode: Only what you explicitly store via `chaos-cli store`
- Auto-capture mode: Only session files in paths you configure
- Never: Passwords, API keys, or system files (unless you explicitly configure them)

---

## Links

- **GitHub:** https://github.com/hargabyte/Chaos-mind
- **Documentation:** https://github.com/hargabyte/Chaos-mind#readme
- **Security Policy:** https://github.com/hargabyte/Chaos-mind/blob/main/SECURITY.md
- **Issues:** https://github.com/hargabyte/Chaos-mind/issues
- **ClawdHub:** https://clawdhub.com/skills/chaos-memory

---

## License

MIT License - see [LICENSE](https://github.com/hargabyte/chaos-memory/blob/main/LICENSE)

---

## Support

- **Issues:** https://github.com/hargabyte/chaos-memory/issues
- **Discussions:** https://github.com/hargabyte/chaos-memory/discussions
- **Email:** support@hargabyte.com

---

**Version:** 1.0.0  
**Author:** Hargabyte Software  
**Model:** Qwen3-1.7B (locked default)  
**Performance:** 43x faster extraction
