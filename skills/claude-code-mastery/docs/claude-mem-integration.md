# claude-mem Integration Guide

## What is claude-mem?

claude-mem is a persistent memory compression system for Claude Code that:
- Preserves context across sessions automatically
- Generates semantic summaries of tool usage
- Provides progressive disclosure of historical context
- Enables ~10x token savings vs re-reading everything

## Architecture

### Core Components

1. **5 Lifecycle Hooks**
   - SessionStart: Injects relevant context at session begin
   - UserPromptSubmit: Captures user prompts
   - PostToolUse: Records tool outputs as observations
   - Stop: Handles session interruptions
   - SessionEnd: Finalizes and summarizes session

2. **Worker Service**
   - HTTP API on port 37777
   - Web viewer UI
   - 10 search endpoints
   - Managed by Bun runtime

3. **SQLite Database**
   - Location: `~/.claude-mem/claude-mem.db`
   - Stores: sessions, observations, summaries
   - Full-text search with FTS5

4. **Chroma Vector Database**
   - Location: `~/.claude-mem/vector-db/`
   - Hybrid semantic + keyword search
   - Intelligent context retrieval

## Installation & Setup

claude-mem is already installed at:
`~/.claude/plugins/marketplaces/thedotmack/`

### Verify Installation
```bash
cd ~/.claude/plugins/marketplaces/thedotmack
ls -la
```

### Check Worker Status
```bash
cd ~/.claude/plugins/marketplaces/thedotmack
bun plugin/scripts/worker-service.cjs status
```

Expected output:
```
Worker is running
  PID: 52047
  Port: 37777
  Started: 2026-02-02T01:38:27.208Z
```

### Start Worker
```bash
cd ~/.claude/plugins/marketplaces/thedotmack
bun plugin/scripts/worker-service.cjs start
```

### Stop Worker
```bash
cd ~/.claude/plugins/marketplaces/thedotmack
bun plugin/scripts/worker-service.cjs stop
```

## Web UI

Access at: **http://localhost:37777**

Features:
- Real-time memory stream
- Session browser
- Observation viewer
- Search interface
- Settings configuration
- Version switching (stable/beta)

## MCP Search Tools

claude-mem provides 4 MCP tools following a **3-layer workflow**:

### The 3-Layer Pattern

1. **`search`** - Get compact index (~50-100 tokens/result)
2. **`timeline`** - Get chronological context around results
3. **`get_observations`** - Fetch full details ONLY for filtered IDs (~500-1000 tokens/result)

### Token Savings

This pattern provides ~10x token savings by filtering before fetching details.

### Example Usage

```typescript
// Step 1: Search for index
search(query="authentication bug", type="bugfix", limit=10)

// Step 2: Review index, identify relevant IDs (e.g., #123, #456)

// Step 3: Fetch full details for only the relevant ones
get_observations(ids=[123, 456])
```

### Available Tools

| Tool | Description |
|------|-------------|
| `search` | Search memory index with full-text queries, filters |
| `timeline` | Get chronological context around observation |
| `get_observations` | Fetch full details by IDs (batch multiple) |
| `__IMPORTANT` | Workflow documentation (always visible to Claude) |

## Configuration

Settings stored at: `~/.claude-mem/settings.json`

Key settings:
- AI model for summarization
- Worker port
- Data directory
- Log level
- Context injection settings

## Privacy Control

Use `<private>` tags to exclude sensitive content from storage:

```
<private>
API_KEY=secret123
</private>
```

Content within these tags won't be stored in the database.

## Troubleshooting

### Worker Not Running
```bash
# Check status
cd ~/.claude/plugins/marketplaces/thedotmack
bun plugin/scripts/worker-service.cjs status

# If not running, start it
bun plugin/scripts/worker-service.cjs start

# Check logs
cat ~/.claude-mem/logs/worker.log
```

### Port 37777 In Use
```bash
# Find what's using the port
lsof -i :37777

# Kill the process if needed
kill -9 <PID>

# Restart worker
bun plugin/scripts/worker-service.cjs start
```

### Database Issues
```bash
# Check database exists
ls -la ~/.claude-mem/claude-mem.db

# Check database integrity
sqlite3 ~/.claude-mem/claude-mem.db "PRAGMA integrity_check;"
```

### Generate Bug Report
```bash
cd ~/.claude/plugins/marketplaces/thedotmack
npm run bug-report
```

## Beta Features

Enable via Web UI (Settings) or version switching:

**Endless Mode**: Biomimetic memory architecture for extended sessions
- Automatic context management
- Adaptive recall based on relevance
- Experimental: may have rough edges

## Best Practices with claude-mem

### 1. Always Start Worker Before Coding
Make it part of your pre-flight checklist.

### 2. Use Search Before Re-Explaining
```
Search my memory for how we handled the auth migration last week
```

### 3. Check Web UI for Context
Before starting a related task, browse recent observations at http://localhost:37777

### 4. Let It Build History
The more you use Claude Code with claude-mem, the richer your searchable memory becomes.

### 5. Reference by Citation
Observations have IDs you can reference:
- API: `http://localhost:37777/api/observation/{id}`
- Web: `http://localhost:37777` (browse all)

## Integration with Clawdbot

When Clawdbot spawns Claude Code for coding tasks:

1. **Pre-task**: Verify worker is running
2. **During task**: claude-mem captures all tool usage
3. **Post-task**: Observations are searchable for future sessions

This creates persistent memory that survives across:
- Session restarts
- Different projects
- Extended time gaps

## Current Status

Installed version: **9.0.12**
Database observations: **7** (as of last check)
Worker status: **Running**
