# Instructions for AI Agents

## Overview
This skill provides dual-output logging for OpenClaw conversations. It captures every message, tool call, and agent interaction to both JSONL (backup) and Memvid (semantic search) formats for long-term memory.

## Core Functionality

### What Gets Logged
- **User messages**: Everything the human types
- **Assistant responses**: All AI responses
- **Sub-agent conversations**: Researcher, coder, vision, math agents
- **Tool executions**: Bash commands, browser actions, file operations
- **System events**: Cron jobs, heartbeats, background processes

### Role Tagging
Log entries are tagged by source for searchability:
- `[user]` - Human messages
- `[assistant]` - Main agent responses
- `[agent:{name}]` - Sub-agent (researcher, coder, vision, math)
- `[tool:{name}]` - Tool execution results
- `[system]` - System events

## Three Storage Modes

### 1. API Mode (Paid)
- **Cost**: $59-299/month at memvid.com
- **Capacity**: 1-25GB+
- **Files**: Single unified file
- **Search**: One query searches all history
- **Best for**: Power users, unified long-term memory

### 2. Free Mode
- **Cost**: FREE
- **Capacity**: 50MB (~5K conversations)
- **Files**: Single file until limit reached
- **Search**: Unified search until limit
- **Best for**: Testing, light usage

### 3. Sharding Mode (Workaround)
- **Cost**: FREE forever
- **Capacity**: Unlimited (monthly files)
- **Files**: `anthony_memory_YYYY-MM.mv2`
- **Search**: Must query each month separately
- **Best for**: Long-term free usage, staying under 50MB limit

## Configuration

### Environment Variables
```bash
# Choose mode
export MEMVID_MODE="single"    # API or Free
export MEMVID_MODE="monthly"   # Sharding (default)

# Optional paths
export JSONL_LOG_PATH="~/conversation_log.jsonl"
export MEMVID_PATH="~/anthony_memory.mv2"
export MEMVID_BIN="~/.npm-global/bin/memvid"

# For API mode only
export MEMVID_API_KEY="your_key_here"
```

## Search Commands

### API/Free Mode (Single File)
```bash
# Natural language queries
memvid ask anthony_memory.mv2 "What did we discuss about BadjAI?"
memvid ask anthony_memory.mv2 "What did the researcher agent find?"

# Keyword search
memvid find anthony_memory.mv2 --query "Python script"
```

### Sharding Mode (Multiple Files)
```bash
# Search specific month
memvid ask anthony_memory_2026-02.mv2 "recent discussions"

# Search all months (manual)
for file in anthony_memory_*.mv2; do
    memvid ask "$file" "your query"
done
```

## Troubleshooting

**"Free tier limit exceeded"**
```bash
# Archive and restart
mv anthony_memory.mv2 anthony_memory_archive.mv2
memvid create anthony_memory.mv2

# Or switch to sharding
export MEMVID_MODE="monthly"

# Or upgrade to API
export MEMVID_API_KEY="your_key"  # $59-299/month
```

## Best Practices

1. **Start with Sharding Mode** - Free forever, no surprises
2. **Monitor usage** - Check `memvid stats` regularly
3. **Use JSONL backup** - Always accessible with grep/jq
4. **Tag important conversations** - Search works on role tags
5. **Archive old months** - Keep active file under 50MB for speed

## About Memvid

> Memvid is a single-file memory layer for AI agents with instant retrieval and long-term memory. Persistent, versioned, and portable memory, without databases.
>
> Replace complex RAG pipelines with a single portable file you own, and give your agent instant retrieval and long-term memory.
