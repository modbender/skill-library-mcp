---
name: Ultimate Unified Memory System (Overkill Memory System)
description: A comprehensive 6-tier memory architecture with neuroscience
  integration, WAL protocol, and full automation for OpenClaw agents.
---

# Ultimate Unified Memory System (Overkill Memory System)
## VERSION 1.9.3 (SPEED-FIRST)

A comprehensive 6-tier memory architecture with neuroscience integration, WAL protocol, and full automation for OpenClaw agents.

## Overview

The Ultimate Unified Memory System implements a **biologically-inspired, speed-first** memory hierarchy. It provides persistent, contextual memory across agent sessions with automatic importance weighting, emotional tagging, and value-based retention.

### What It Does

- **Brain-Full Architecture**: 6 brain regions (Hippocampus, Amygdala, VTA, Basal Ganglia, Insula, ACC)
- **Speed-First Architecture**: Optimized for ~5ms average query time
- **Fast File Search**: Uses `fd` + `rg` for 10x faster file tier searching
- **Knowledge Graph**: Structured atomic facts with versioning
- **Self-Improving**: Continuous learning from errors and corrections
- **Self-Reflection**: Periodic self-assessment and performance review
- **Multi-Agent Support**: Shared + private ChromaDB areas per agent
- **6-Tier Memory Architecture**: From instant recall (HOT) to archival (COLD/GIT-NOTES)
- **Hybrid Neuroscience**: Filter + Ranker approach for precision + speed
- **WAL (Write-Ahead Log) Protocol**: Ensures no memory is ever lost
- **Neuroscience Integration**: Hippocampus (importance), Amygdala (emotions), VTA (rewards/motivation)
- **Error Learning**: Tracks and learns from user corrections
- **Spaced Repetition**: FSRS-6 via Vestige for natural memory decay
- **Semantic Search**: ChromaDB-powered vector storage for contextual retrieval
- **Cloud Backup**: Supermemory integration for cross-device backup (NOT in query path)
- **Full Automation**: Cron jobs for cross-session messages, platform posts, diary entries, and proactive memory maintenance

### Speed Targets

| Scenario | Time |
|----------|------|
| Compiled query match | ~0ms |
| Ultra-hot hit | ~0.1ms |
| Hot cache hit | ~1ms |
| Mem0 hit | ~22ms |
| Full search | ~55ms |
| **Average** | **~5ms** |

> **Note**: Supermemory is NOT in the query path - it's a **background sync** only (daily backup). This keeps queries fast (~5ms). Cloud access is only for backup/restore, not real-time queries.

---
## Speed-First Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    ULTRA-HOT (Dict)           │
          │    Last 10 queries ~0.1ms    │
          │    (RETURN if hit!)           │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    HOT CACHE (Redis)          │
          │    Recent queries ~1ms        │
          │    (RETURN if hit!)           │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    COMPILED QUERIES           │
          │    Pre-parsed common queries │
          │    ~0ms (dict lookup)        │
          │    (USE if match!)            │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    EMOTIONAL DETECTOR         │
          │    preference/error/important │
          │    ~0.5ms                    │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    BLOOM FILTER               │
          │    "Does it exist?" ~0ms     │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    MEM0 (FIRST!)              │
          │    Fast cache ~20ms           │
          │    80% token savings          │
          │    (RETURN if hit!)           │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    EARLY WEIGHTING            │
          │    Adjust tier weights        │
          │    ~1ms                      │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    RUN TIERS PARALLEL          │
          │    acc-err, vestige, chromadb, │
          │    gitnotes, file             │
          │    ~30ms                      │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    MERGE + RANKING            │
          │    Neuroscience scoring       │
          │    PASS 1: Quick filter      │
          │    PASS 2: Full rank          │
          │    ~10ms                      │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    CONFIDENCE EARLY EXIT     │
          │    confidence > 0.95? return 1│
          │    gap > 0.5? return 1        │
          └───────────────┬───────────────┘
                          │
          ┌───────────────▼───────────────┐
          │    BACKGROUND SYNC           │
          │    Supermemory (daily backup) │
          │    NOT in query path!       │
          └───────────────┬───────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   RESULTS     │
                  │  (~5-15ms)    │
                  └───────────────┘
```
---

## Features

### 1. Speed Optimizations (NEW in v1.3.0)

| Optimization | Time Saved |
|-------------|-----------|
| **Ultra-Hot Tier** | In-memory dict for last 10 queries (~0.1ms) |
| **Compiled Queries** | Pre-parsed common queries (~0ms) |
| **Lazy Loading** | Import heavy libs only when needed |
| **Confidence Early Exit** | Skip ranking if confident enough |
| **Mem0 First** | 80% queries hit here (~22ms) |
| **Parallel Tiers** | All tiers queried simultaneously |

### 2. Six-Tier Memory Architecture

| Tier | Name | Storage | Retention | Use Case |
|------|------|---------|-----------|----------|
| 1 | HOT | Session state | Current session | Active context, WAL buffer |
| 2 | WARM | Daily notes | 24-48 hours | Recent conversations, working memory |
| 3 | TEMP | Cache | Minutes-hours | Temporary processing, scratchpad |
| 4 | COLD | Core memory | Weeks-months | Important facts, decisions, preferences |
| 5 | ARCHIVE | Diary | Months-years | Long-term journal, milestone memories |
| 6 | COLD-STORAGE | Git-Notes | Indefinite | Permanent knowledge base |

### 2. Neuroscience Components

#### Hippocampus (Importance Scoring)
- Analyzes content for importance signals
- Maintains index.json with memory importance scores
- Auto-weights memories based on repetition and context

#### Amygdala (Emotional Tagging)
- Detects 8 emotions: joy, sadness, anger, fear, curiosity, connection, accomplishment, fatigue
- Tracks emotional dimensions: valence, arousal, connection, curiosity, energy
- Stores state in emotional-state.json

#### VTA (Value/Reward System)
- Computes motivation scores based on reward types
- Reward categories: accomplishment, social, curiosity, connection, creative, competence
- Drives attention toward high-value memories

### 3. Hybrid Search (NEW in v1.3.0)

#### Emotional Detector
- Detects query intent: preference, error, important, recent, project, general
- Adjusts tier weights based on detected intent
- Runs AFTER cache checks (only when needed)

#### Early Weighting
| Query Type | Keywords | Weight Adjustments |
|------------|----------|-------------------|
| Error/Fix | "bug", "fix", "error" | acc-error: 2x |
| Preference | "prefer", "like", "always" | vestige: 2x |
| Important | "remember", "critical" | all: 1.5x |
| Recent | "yesterday", "last week" | hot: 2x |
| Project | "project", "architecture" | gitnotes: 1.5x |

### 4. Hybrid Neuroscience (NEW in v1.3.0)

Two-pass approach for precision + speed:

| Pass | What | When |
|------|------|------|
| Pass 1 | Quick filter (skip 0 importance) | High-importance queries |
| Pass 2 | Full ranking (all components) | Always |

#### Scoring Formula
```
Final Score = 
    (Base Relevance × 0.25) +
    (Importance × 0.30) +      ← Hippocampus
    (Value × 0.25) +          ← VTA
    (Emotion Match × 0.20)    ← Amygdala
```

### 5. Error Learning (NEW in v1.3.0)

- **acc-error-memory** integration
- Tracks error patterns over time
- Records user corrections
- Learns from mistakes
- High priority in search results

### 6. Spaced Repetition (NEW in v1.3.0)

- **vestige** integration (FSRS-6)
- Memories fade naturally like human memory
- Preferences strengthen with use
- Solutions decay if unused

### 7. Write-Ahead Log (WAL) Protocol
- Session state maintained in SESSION-STATE.md
- WAL buffer ensures atomic commits
- Crash recovery from uncommitted state

### 4. Automation Features

- **Cron Inbox**: Cross-session messages via cron-inbox.md
- **Platform Posts**: Tracks Discord/Telegram posts in platform-posts.md
- **Diary Entry**: Daily journal entries in diary/ directory
- **Daily Notes**: Session logs in daily/ directory
- **Heartbeat State**: Tracks periodic check timestamps

---

## Installation & Setup

### Prerequisites

```bash
# Ensure Python 3.8+ is available
python3 --version

# Optional: ChromaDB for semantic search
pip install chromadb

# Optional: Ollama for embeddings
# Install from https://github.com/ollama/ollama
```

### Step 1: Install the Skill

```bash
# The skill should be placed in your skills directory
# ~/.openclaw/workspace/skills/overkill-memory-system/
```

### Step 2: Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your preferences
```

### Step 3: Initialize Memory System

```bash
python3 cli.py init
```

This creates all required memory files:
- `~/.openclaw/memory/SESSION-STATE.md`
- `~/.openclaw/memory/MEMORY.md`
- `~/.openclaw/memory/cron-inbox.md`
- `~/.openclaw/memory/platform-posts.md`
- `~/.openclaw/memory/strategy-notes.md`
- `~/.openclaw/memory/heartbeat-state.json`
- `~/.openclaw/memory/diary/`
- `~/.openclaw/memory/daily/`
- `~/.openclaw/memory/chroma/`
- `~/.openclaw/memory/git-notes/`

---

## CLI Commands

### Initialization

```bash
# Initialize memory system files
python3 cli.py init

# Initialize with custom memory base path
python3 cli.py init --path /custom/path
```

### Memory Operations

```bash
# Add a memory with auto-detected importance & emotions
python3 cli.py add "Finished the project, feeling accomplished!"

# Add memory with explicit importance (0.0-1.0)
python3 cli.py add "Important decision made" --importance 0.9

# Add with explicit emotions
python3 cli.py add "Excited about the new feature" --emotions joy,curiosity

# Add with reward/value tracking
python3 cli.py add "Shipped v2.0" --reward accomplishment --intensity 0.8
```

### Retrieval

```bash
# Search memories (hybrid - default, uses all optimizations)
python3 cli.py search "project updates"

# Fast mode (cache + ultra-hot only)
python3 cli.py search "query" --fast

# Full search (all tiers)
python3 cli.py search "query" --full

# Get recent memories
python3 cli.py recent --limit 10

# Get memories by importance threshold
python3 cli.py important --threshold 0.7
```

### Error Tracking (NEW)

```bash
# Track an error
python3 cli.py error track "Forgot to add import"

# Show error patterns
python3 cli.py error patterns

# Show corrections made
python3 cli.py error corrections

# Error statistics
python3 cli.py error stats
```

### Vestige Integration (NEW)

```bash
# Search vestige memories
python3 cli.py vestige search "user preferences"

# Ingest with tags
python3 cli.py vestige ingest "User prefers dark mode" --tags preference

# Promote memory (strengthen)
python3 cli.py vestige promote <memory_id>

# Demote memory (weaken)
python3 cli.py vestige demote <memory_id>

# Check vestige stats
python3 cli.py vestige stats
```

### File Search (NEW)

```bash
# Search by file name (uses fd)
python3 cli.py file search "*.md"

# Search by content (uses rg)
python3 cli.py file content "TODO"

# Fast combined search
python3 cli.py file fast "pattern"
```

### Knowledge Graph (NEW)

```bash
# Add atomic fact
python3 cli.py kg add --entity "people/kasper" --category "preference" --fact "Prefers TypeScript"

# Supersede old fact
python3 cli.py kg supersede --entity "people/kasper" --old kasper-001 --fact "New fact"

# Generate entity summary
python3 cli.py kg summarize --entity "people/kasper"

# Search knowledge graph
python3 cli.py kg search "preference"

# List all entities
python3 cli.py kg list
```

### Self-Improving (NEW)

```bash
# Log an error
python3 cli.py improve error "Command failed" --context "details"

# Log user correction
python3 cli.py improve correct "No, that's wrong" --context "user corrected me"

# Log feature request
python3 cli.py improve request "Need markdown support"

# Log best practice
python3 cli.py improve better "Use async for I/O" --context "found during work"

# Get all learnings
python3 cli.py improve list
```

### Neuroscience (NEW)

```bash
# Show neuroscience statistics
python3 cli.py neuro stats

# Analyze text for neuroscience scores
python3 cli.py neuro analyze "I'm excited about this project!"
```

### Session Management

```bash
# Start new session (flushes WAL to daily)
python3 cli.py session new

# End session (commits WAL buffer)
python3 cli.py session end

# Show session state
python3 cli.py session status
```

### Neuroscience Queries

```bash
# Get current emotional state
python3 cli.py brain state

# Get motivation/drive level
python3 cli.py brain drive

# Update emotional dimensions
python3 cli.py brain update --valence 0.8 --arousal 0.6
```

### Daily & Diary

```bash
# Create daily note entry
python3 cli.py daily "What happened today"

# Create diary entry (prompts for date)
python3 cli.py diary "Reflecting on the week"

# List recent diary entries
python3 cli.py diary list --limit 5
```

### Automation

```bash
# Process cron inbox messages
python3 cli.py cron process

# Sync platform posts
python3 cli.py sync posts

# Run memory analysis
python3 cli.py analyze
```

### Utilities

```bash
# Show memory statistics
python3 cli.py stats

# Export memory backup
python3 cli.py export /path/to/backup/

# Import memory backup
python3 cli.py import /path/to/backup/
```

---

## Configuration (.env)

```bash
# Memory base directory
MEMORY_BASE=/home/user/.openclaw/memory

# ChromaDB settings (optional)
CHROMA_URL=http://localhost:8100
CHROMA_COLLECTION=memory-v2

# Ollama settings (optional)
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=bge-m3

# Capture settings
POLL_INTERVAL=300

# Processing settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval settings
CACHE_TTL=3600
MAX_RESULTS=10
```


---

## Storage Guidelines

### Tier 1: HOT (Session State)
- **Location**: `~/.openclaw/memory/SESSION-STATE.md`
- **Size**: Keep under 50KB
- **Content**: Active context, current task, recent messages

### Tier 2: WARM (Daily)
- **Location**: `~/.openclaw/memory/daily/YYYY-MM-DD.md`
- **Size**: Up to 100KB per day
- **Content**: Daily logs, conversation summaries

### Tier 3: TEMP (Cache)
- **Location**: `~/.cache/memory-v2/`
- **Size**: Auto-cleaned after 24h
- **Content**: Processing scratchpad, temporary embeddings

### Tier 4: COLD (Core)
- **Location**: `~/.openclaw/memory/MEMORY.md`
- **Size**: Keep under 500KB
- **Content**: Key facts, decisions, preferences, lessons learned

### Tier 5: ARCHIVE (Diary)
- **Location**: `~/.openclaw/memory/diary/`
- **Size**: Unlimited
- **Content**: Personal journal, milestone reflections

### Tier 6: COLD-STORAGE (Git-Notes)
- **Location**: `~/.openclaw/memory/git-notes/`
- **Size**: Unlimited
- **Content**: Knowledge base, permanent reference

---

## Cron Jobs

### Recommended Cron Setup

```bash
# Process cron inbox every 5 minutes
*/5 * * * * cd ~/.openclaw/workspace-cody/skills/overkill-memory-system && python3 cli.py cron process >> /var/log/memory-cron.log 2>&1

# Sync platform posts every 15 minutes
*/15 * * * * cd ~/.openclaw/workspace-cody/skills/overkill-memory-system && python3 cli.py sync posts >> /var/log/memory-sync.log 2>&1

# Daily diary entry at 9 PM
0 21 * * * cd ~/.openclaw/workspace-cody/skills/overkill-memory-system && python3 cli.py diary "Daily reflection" >> /var/log/memory-diary.log 2>&1

# Weekly memory analysis (Sunday 10 PM)
0 22 * * 0 cd ~/.openclaw/workspace-cody/skills/overkill-memory-system && python3 cli.py analyze >> /var/log/memory-analyze.log 2>&1
```

### Heartbeat Integration

Add to `HEARTBEAT.md`:

```markdown
## Memory System Checks

- [ ] Check cron-inbox for cross-session messages
- [ ] Check platform-posts for new activity
- [ ] Review recent daily notes for important context
- [ ] Update emotional state if significantly changed
```

---

## Troubleshooting

### Memory System Won't Initialize

```bash
# Check directory permissions
ls -la ~/.openclaw/memory/

# Manually create directory
mkdir -p ~/.openclaw/memory
```

### ChromaDB Connection Failed

```bash
# Check if ChromaDB is running
curl http://localhost:8100/api/v1/heartbeat

# Or use keyword search fallback
python3 cli.py search "query" --method keyword
```

### Ollama Embeddings Not Working

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Verify embedding model
ollama list
```

### Session State Not Persisting

```bash
# Manually flush WAL buffer
python3 cli.py session end

# Check session file
cat ~/.openclaw/memory/SESSION-STATE.md
```

### Memory Search Returns No Results

```bash
# Rebuild search index
python3 cli.py analyze

# Try keyword fallback
python3 cli.py search "term" --method keyword
```

### Git-Notes Sync Issues

```bash
# Check git-notes directory
ls -la ~/.openclaw/memory/git-notes/

# Initialize git repo if needed
cd ~/.openclaw/memory/git-notes && git init
```

---

## File Structure

```
overkill-memory-system/
├── SKILL.md                 # This file
├── README.md                # Quick start guide
├── .env.example             # Environment template
├── cli.py                   # Main CLI interface
├── config.py                # Configuration
├── scripts/
│   └── analyze_memories.py # Memory analysis tool
├── templates/               # Future: custom templates
└── ULTIMATE_UNIFIED_FRAMEWORK.md  # Full framework docs
```

---

## Credits & Sources
- **vestige** - FSRS-6 spaced repetition for natural memory decay and preferences
- **acc-error-memory** - Error pattern tracking and correction learning

Built with neuroscience-inspired architecture:
- **Hippocampus**: Importance-based memory consolidation
- **Amygdala**: Emotional tagging and valence processing
- **VTA**: Reward-driven attention and motivation

Based on the Ultimate Unified Memory Framework (ULTIMATE_UNIFIED_FRAMEWORK.md)

---

## Credits & Sources
- **vestige** - FSRS-6 spaced repetition for natural memory decay and preferences
- **acc-error-memory** - Error pattern tracking and correction learning

This skill was built by integrating ideas and features from the following ClawHub skills:

### Core Architecture
- **elite-longterm-memory** - WAL Protocol, Git-Notes knowledge graph, SESSION-STATE.md concept
- **jarvis-memory-architecture** - Cron inbox, diary, daily logs, platform post tracking, adaptive learning
- **memory-hygiene** - Auto-cleanup, storage guidelines

### Neuroscience Components
- **hippocampus-memory** - Importance-weighted recall and memory encoding
- **amygdala-memory** - Emotional tagging and processing
- **vta-memory** - Value scoring and motivation tracking

### Storage & Integration
- **chromadb-memory** - Vector storage integration (ChromaDB + Ollama bge-m3)
- **supermemory-free** - Optional cloud backup integration
- **mem0** - Auto-fact extraction (80% token reduction)
- **memory-system-v2** - Core unified memory framework

### Created By
- Initial implementation by Cody (AI coding specialist)
- Framework designed by Broedkrummen
- Built with OpenClaw agent-orchestrator

---

*Last Updated: 2026-02-25 | Version 1.3.0 (Speed-First)*

### Cloud Integration (Requires Setup)

The system supports optional cloud backup and sync:

- **Supermemory Integration**: Push memories to cloud for cross-device access
- **Mem0 Auto-Fact Extraction**: Automatic fact extraction from conversations (80% token reduction)

Configure via environment variables:
- `SUPERMEMORY_API_KEY` - For cloud backup
- `MEM0_API_KEY` - For auto-fact extraction

---

## Speed Optimizations (v1.0.5)

### Optimization Techniques Implemented

| Technique | Layer | Complexity | Benefit |
|-----------|-------|------------|---------|
| Bloom Filters | Pre-query | O(1) | Skip expensive queries |
| Redis Hot Cache | L0 | <1ms | Sub-millisecond access |
| Mem0 L1 Cache | L1 | <10ms | 80% token reduction |
| Parallel Queries | All | O(1) wall | Concurrent tier queries |
| Connection Pooling | ChromaDB | Reuse | No connection overhead |
| Binary Search | Git-Notes | O(log n) | Fast sorted lookups |
| Pre-computed Embeddings | Cache | Skip compute | Cache hits = instant |
| Lazy Loading | Files | On-demand | Reduced memory footprint |
| Pre-fetch Context | Predictive | Anticipate | Results ready before ask |
| Result Caching | TTL | 1-5min | Avoid redundant queries |

### L1 Cache (Mem0)
- **Purpose**: First-layer cache for 80% token reduction
- **How**: Mem0 extracts facts from conversations automatically
- **Benefit**: Reduces context window usage while preserving key information

### Parallel Tier Query
- **Purpose**: Query all memory tiers simultaneously
- **How**: Async queries to Mem0, ChromaDB, Git-Notes, and file search
- **Benefit**: O(1) wall-clock time instead of sequential O(n) tier traversal

### Redis Hot Cache (L0)
- **Purpose**: Ultra-fast L0 cache for frequently accessed memories
- **TTL**: 5-15 minutes for hot data
- **Benefit**: Sub-millisecond access for top results

### Result Caching with TTL
- **Purpose**: Cache search results to avoid redundant queries
- **TTL**: 1-5 minutes depending on tier
- **Benefit**: Dramatically reduces API calls and computation

### Binary Search (Git-Notes)
- **Purpose**: O(log n) lookup in sorted memory index
- **How**: Maintain sorted timestamp/index files
- **Benefit**: Fast retrieval from large Git-Notes collections

### Connection Pooling
- **Purpose**: Reuse ChromaDB and Ollama connections
- **How**: Persistent connection pools with health checks
- **Benefit**: Eliminates connection overhead on each query

### Bloom Filters
- **Purpose**: Quick existence checks before expensive queries
- **How**: Probabilistic filter for memory presence
- **Benefit**: Skip unnecessary tier searches when result is definitely not present

### Pre-fetch Context
- **Purpose**: Predictive memory loading based on context
- **How**: Anticipate likely queries based on current session
- **Benefit**: Results ready before user asks

### Lazy Loading
- **Purpose**: Load files only when needed
- **How**: On-demand loading of large files
- **Benefit**: Reduced memory footprint and faster initial response

### Pre-computed Embeddings
- **Purpose**: Cache embeddings for frequently queried content
- **How**: Store embeddings alongside source data
- **Benefit**: Skip embedding computation on cache hit
- **How**: Store embeddings alongside source data
- **Benefit**: Skip embedding computation on cache hit

---

## Cloud Architecture (v1.0.5)

### Priority Order
```
Mem0 (L1 Cache) → ChromaDB → Git-Notes → Supermemory (Backup)
```

| Tier | Service | Purpose | Latency | Cost |
|------|---------|---------|---------|------|
| L0 | Redis | Hot cache | <1ms | Low |
| L1 | Mem0 | Auto-extracted facts | <10ms | Medium |
| L2 | ChromaDB | Semantic vectors | <50ms | Low |
| L3 | Git-Notes | Knowledge graph | <20ms | Free |
| Backup | Supermemory | Offsite backup | Daily | Free |

### Cloud Services Integration

#### Mem0 (L1 Cache)
- **Purpose**: First-layer cache for 80% token reduction
- **How**: Auto-extracts facts from conversations
- **API**: `MEM0_API_KEY` environment variable
- **Benefit**: Reduces context window usage while preserving key information

#### ChromaDB (Vector Storage)
- **Purpose**: Semantic similarity search
- **Embeddings**: bge-m3 via Ollama
- **Connection**: Pooled connections for speed
- **Fallback**: Keyword search if unavailable

#### Git-Notes (Knowledge Graph)
- **Purpose**: Structured JSON storage
- **Lookup**: Binary search O(log n)
- **Sync**: Git-based versioning

#### Supermemory (Cloud Backup)
- **Purpose**: Daily backup only (not real-time sync)
- **Frequency**: Once per day
- **API**: `SUPERMEMORY_API_KEY` environment variable
- **Benefit**: Reduces API calls while maintaining offsite backup

### Environment Variables
```bash
# Required for cloud features
MEM0_API_KEY=your_mem0_key          # Auto-fact extraction
SUPERMEMORY_API_KEY=your_key       # Cloud backup

# Optional overrides
CHROMA_URL=http://localhost:8100   # ChromaDB server
OLLAMA_URL=http://localhost:11434   # Ollama server
EMBEDDING_MODEL=bge-m3              # Embedding model
```

---

## Search Priority Flow (v1.0.5)

```
Query Input
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. BLOOM FILTER CHECK (O(1))                                │
│    • Probabilistic existence check                          │
│    • Skip expensive queries if definitely not present        │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. REDIS HOT CACHE / L0 CACHE (Sub-millisecond)            │
│    • TTL: 5-15 minutes                                       │
│    • Frequently accessed memories                           │
│    • Return immediately if cached                           │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. MEM0 L1 CACHE (First Priority)                            │
│    • Auto-extracted facts (80% token reduction)             │
│    • Fast fact lookup                                        │
│    • No embedding computation needed                         │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. CHROMADB (Second Priority)                                │
│    • Semantic vector search (bge-m3 embeddings)             │
│    • Connection pooling for speed                            │
│    • Return top-k results with scores                        │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. GIT-NOTES (Third Priority)                                │
│    • Structured JSON knowledge graph                         │
│    • Binary search on sorted index                           │
│    • O(log n) lookup time                                     │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. FILE SEARCH (Fallback)                                    │
│    • Raw grep on daily/diary files                          │
│    • Last resort fallback                                    │
└──────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│ RESULTS MERGE & RANKING                                      │
│    • Combine results from all tiers                         │
│    • Apply importance weights (Hippocampus)                 │
│    • Apply emotional relevance (Amygdala)                   │
│    • Apply value scores (VTA)                               │
│    • Return unified ranked results                          │
└──────────────────────────────────────────────────────────────┘
```

### Cache Strategy Details
- **Cache Hit**: Return cached result immediately (sub-ms)
- **Cache Miss**: Query next tier, cache result with TTL
- **Negative Cache**: Optionally cache "not found" results (shorter TTL)
- **Cache Invalidation**: On session end, new memory add, or manual trigger


---

## ⚠️ Prerequisites & Setup

### Required Services (must be running)
- ChromaDB on http://localhost:8100
- Ollama on http://localhost:11434 with bge-m3 model

### Optional Services (require API keys)
- Mem0.ai account (for cloud fact extraction)
- Supermemory.ai account (for cloud backup)
- Redis (optional, falls back to in-memory)

### Environment Setup
1. Copy `.env.example` to `.env`
2. Fill in optional API keys if using cloud features
3. Run `python3 cli.py --help` to get started

### Manual Setup for Automation
The CLI provides commands but cron jobs are NOT auto-installed. To enable:
- Add cron jobs manually via `crontab -e`
- Example: `0 3 * * * python3 /path/to/cli.py cloud sync`

---

## ⚠️ Important Notes

### On-Import Side Effects
When Python imports cli.py, it may create memory directories under `~/.openclaw/memory/`. This is intentional - the system needs these directories to function. To avoid this, run commands via subprocess rather than import.

### No Auto-Installed Cron Jobs
The skill provides CLI commands for automation but does NOT auto-install cron jobs. You must manually add them if desired:
```bash
# Add to crontab -e
0 3 * * * python3 /path/to/cli.py cloud sync
```

### Cloud Features
Cloud features (Mem0, Supermemory) require API keys. Set in environment or .env file before use.

---

## 🔐 Security & Network Access

### When Network Access Occurs

| Variable | When Accessed | External Service |
|----------|--------------|-----------------|
| CHROMA_URL | If set | ChromaDB server |
| OLLAMA_URL | If set | Ollama server |
| MEM0_API_KEY | If set AND MEM0_USE_LOCAL=false | Mem0.ai API |
| SUPERMEMORY_API_KEY | If set | Supermemory.ai API |
| REDIS_URL | If set | Redis server |

### Default Behavior (No Network)
- Without API keys, system runs **fully offline**
- Uses local ChromaDB + local Ollama (if available)
- All data stored locally in ~/.openclaw/memory/

### Cloud Features
Only enabled when you:
1. Set MEM0_API_KEY and set MEM0_USE_LOCAL=false
2. Set SUPERMEMORY_API_KEY

These are opt-in only. Default = offline.
