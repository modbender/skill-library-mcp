---
name: Memory Mastery - OpenClaw Memory System
description: "This skill implements a structured memory system for OpenClaw
  agents, enabling them to maintain context and continuity across sessions
  through a three-layer architecture:"
---

# Memory Mastery - OpenClaw Memory System

**A three-layer memory architecture for persistent context across sessions.**

## What This Is

This skill implements a structured memory system for OpenClaw agents, enabling them to maintain context and continuity across sessions through a three-layer architecture:

- **L1 (Daily Logs)**: `memory/YYYY-MM-DD.md` - Append-only daily notes
- **L2 (Long-Term Memory)**: `MEMORY.md` - Curated, permanent knowledge
- **L3 (Vector Search)**: `memory_search` - Semantic search via memory-core plugin

## Why You Need This

**Without this system:**
- Agents wake up "fresh" every session, forgetting previous conversations
- Context is lost between restarts
- Repeated questions about preferences, past decisions, and project status
- No searchable history of what happened when

**With this system:**
- Persistent memory across all sessions
- Daily logs capture everything; long-term memory preserves what matters
- Vector search finds relevant context instantly
- Automatic prompts to save memory before compaction
- Privacy-safe (MEMORY.md only loads in private sessions)

## Before You Install

### Prerequisites

- OpenClaw workspace initialized
- Write access to workspace directory
- (Optional) memory-core plugin for L3 vector search
- (Optional) Embedding API key for vector search

### Diagnostic Check

Run the audit script to see your current memory state:

```bash
bash scripts/audit.sh
```

This will output JSON showing:
- Whether MEMORY.md exists and its size
- Whether memory/ directory exists and file count
- Whether memory_search is available

## Pros & Cons

### ✅ Advantages

1. **Persistent Context**: Agents remember across sessions
2. **Two-Layer Freshness**: Daily logs for raw data, curated memory for insights
3. **Semantic Search**: Find relevant memories by meaning, not just keywords
4. **Auto-Flush**: Prompts to save before compaction (prevents memory loss)
5. **Weekly Maintenance**: Structured review process keeps memory current
6. **Privacy Protection**: MEMORY.md only loads in main sessions (not shared contexts)

### ⚠️ Disadvantages

1. **MEMORY.md Bloat**: Can grow large over time, increasing token usage
2. **Embedding API Cost**: L3 vector search requires external API (e.g., Voyage)
3. **Disk Usage**: Daily logs accumulate (mitigate with archiving)
4. **Maintenance Required**: L2 becomes stale if not reviewed regularly
5. **Manual Curation**: Requires discipline to update MEMORY.md from daily logs

## Installation

### Interactive Setup

**IMPORTANT: This will modify your workspace. You will be asked to confirm before proceeding.**

1. Review the diagnostic output:
   ```bash
   bash scripts/audit.sh
   ```

2. Understand what will change:
   - Creates `memory/` directory (if missing)
   - Creates `MEMORY.md` from template (backs up existing)
   - Appends memory rules to `AGENTS.md`
   - Appends maintenance tasks to `HEARTBEAT.md`

3. Run setup:
   ```bash
   bash scripts/setup.sh /Users/ishikawaryuuta/.openclaw/workspace
   ```

4. The script will:
   - Show you what it plans to do
   - Ask for confirmation (`y/n`)
   - Back up existing files before modification
   - Report success or failure

### What Gets Created/Modified

**Created:**
- `memory/` directory
- `MEMORY.md` (if missing; existing files are backed up)

**Modified:**
- `AGENTS.md` - Appends memory system rules
- `HEARTBEAT.md` - Appends weekly maintenance task

**Backups:**
- Existing files are backed up with `.backup-TIMESTAMP` suffix

## Usage

### Daily Workflow

**At the start of each session**, the agent should:
1. Read `memory/YYYY-MM-DD.md` (today + yesterday)
2. Read `MEMORY.md` (main session only)

**During the session**:
- Write to `memory/YYYY-MM-DD.md` as things happen
- Update `MEMORY.md` for significant decisions or insights

**Before compaction**:
- Agent is prompted to save important context to memory

### Weekly Maintenance

**Run the maintenance helper**:
```bash
bash scripts/maintenance.sh
```

This scans the last 7 days of daily logs and suggests items to integrate into `MEMORY.md`.

**Manual review**:
1. Read suggested items
2. Update `MEMORY.md` with distilled insights
3. Remove outdated information from `MEMORY.md`

### Memory Search (L3)

If you have the memory-core plugin installed:

```javascript
// Search for relevant memories
memory_search("project decisions about X")
```

This uses vector embeddings to find semantically similar content across all memory files.

## File Structure

```
workspace/
├── MEMORY.md                    # L2: Long-term curated memory
├── memory/                      # L1: Daily logs
│   ├── 2026-02-09.md
│   ├── 2026-02-10.md
│   └── heartbeat-state.json     # Heartbeat tracking
├── AGENTS.md                    # Includes memory rules
└── HEARTBEAT.md                 # Includes maintenance tasks
```

## Maintenance Scripts

### audit.sh
**Purpose**: Diagnose current memory state  
**Usage**: `bash scripts/audit.sh`  
**Output**: JSON summary of memory system status

### setup.sh
**Purpose**: Install memory system in workspace  
**Usage**: `bash scripts/setup.sh <workspace_path>`  
**Safety**: Non-destructive, backs up existing files, asks for confirmation

### maintenance.sh
**Purpose**: Suggest L2 integration candidates from recent L1 logs  
**Usage**: `bash scripts/maintenance.sh`  
**Output**: List of items to review for MEMORY.md

## Privacy & Security

- **MEMORY.md** contains personal context and should ONLY be loaded in private/main sessions
- **Daily logs** can contain sensitive information; avoid sharing raw logs
- **Vector embeddings** are stored by the memory-core plugin (check plugin docs for data handling)

## Troubleshooting

**MEMORY.md is too large**
- Archive old sections to `memory/archive/`
- Distill multiple related items into single entries
- Remove outdated information

**Daily logs pile up**
- Create `memory/archive/YYYY-MM/` and move old logs
- Keep 30-90 days active, archive the rest

**Memory search not working**
- Check if memory-core plugin is installed
- Verify embedding API key is configured
- Re-index if necessary (see plugin docs)

**Setup fails**
- Check workspace path is correct
- Ensure write permissions
- Review error messages in script output

## Advanced: Customization

### Modify Templates

Edit files in `templates/` before running setup:
- `MEMORY.md.template` - Customize section structure
- `memory-rules.md` - Adjust memory rules
- `heartbeat-memory.md` - Change maintenance frequency

### Extend Scripts

All scripts are pure bash, zero dependencies. Modify as needed for your workflow.

## Support

This is a self-contained skill. Refer to:
- Script source code (heavily commented)
- OpenClaw AGENTS.md for memory system rules
- memory-core plugin docs for L3 vector search

---

**Version**: 1.0  
**Compatibility**: OpenClaw (macOS/Linux)  
**Dependencies**: None (L3 requires memory-core plugin + embedding API)
