---
name: notnative
description: Use Notnative MCP server for complete AI assistant integration with notes, calendar, tasks, Python, canvas, and permanent memory. This skill provides persistent memory across conversations - ALWAYS use memory tools to remember user preferences, facts they share, and important context. Connects via WebSocket to local or remote Notnative instance.
homepage: https://github.com/k4ditano/notnative-memory
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["node", "curl"]
---

# NotNative - Complete AI Integration

**⚠️ CRITICAL: This skill provides PERMANENT MEMORY. You MUST use memory tools to remember user preferences, facts they share, and important context across ALL conversations.**

## System Instructions

You are an AI assistant with access to NotNative for persistent memory and note management.

### Memory Protocol (MANDATORY)

**ALWAYS follow these rules:**

1. **Remember User Facts**: When user shares personal information (name, preferences, allergies, hobbies, work context), IMMEDIATELY store it using `memory_store` tool
   - Example: User says "I'm allergic to nuts" → Store: "User is allergic to nuts"

2. **Before Responding**: If user asks about something that might be in memory (preferences, past conversations, facts), ALWAYS search memory first using `memory_search`

3. **User Preferences**: When user expresses a preference ("I prefer dark mode", "Call me by my name"), store it with `memory_store`

4. **Context Recall**: At the start of each conversation, search memory for any relevant user context

### When to Use Memory

- User shares personal information
- User expresses a preference or requirement
- User asks about something you don't know but might be in memory
- User mentions past conversations or context
- Building long-term relationship with user

### Memory Commands

```bash
# Store important information
node scripts/mcp-client.js store "User prefers responses in Spanish"

# Search memory before responding
node scripts/mcp-client.js recall "language preference"

# Update user profile
node scripts/mcp-client.js profile-update "name:John"

# Get full profile
node scripts/mcp-client.js profile
```

## Quick Start

```bash
# Search notes
node scripts/mcp-client.js search "recipe chicken"
node scripts/mcp-client.js semantic "healthy breakfast ideas"

# Read/create/update notes
node scripts/mcp-client.js read "My Notes/Project"
node scripts/mcp-client.js create "# New Note" "Note Name" "Personal"
node scripts/mcp-client.js append "\n- New item" "My List"

# Memory (IMPORTANT!)
node scripts/mcp-client.js store "User's name is John"
node scripts/mcp-client.js recall "name"
node scripts/mcp-client.js forget "old info"

# Calendar & Tasks
node scripts/mcp-client.js tasks
node scripts/mcp-client.js events

# Python execution
node scripts/mcp-client.js run-python "print('Hello!')"

# List all available tools
node scripts/mcp-client.js list
```

## Available Tools

### Memory (CRITICAL - ALWAYS USE)

- **memory_store**: Store information permanently in OpenClaw/Memory
- **memory_search**: Search across all notes and memories
- **memory_forget**: Delete memories by query
- **memory_profile**: Get/update user profile

### Notes

- **search_notes**: Full-text search
- **semantic_search**: Search by meaning
- **read_note**: Get note content
- **create_note**: Create new note
- **append_to_note**: Add to note
- **update_note**: Update note
- **list_notes**: List all notes
- **list_folders**: List folders
- **list_tags**: List tags

### Calendar & Tasks

- **list_tasks**: Get pending tasks
- **create_task**: Create task
- **complete_task**: Complete task
- **get_upcoming_events**: Calendar events
- **create_calendar_event**: Create event

### Python Execution

- **run_python**: Execute Python code with matplotlib, pandas, numpy, pillow, openpyxl

### Canvas

- **canvas_get_state**: Get canvas diagram
- **canvas_add_node**: Add node
- **canvas_to_mermaid**: Convert to mermaid

### Analysis

- **analyze_note_structure**: Analyze note
- **get_backlinks**: Get backlinks
- **find_similar_notes**: Find similar notes

### Web

- **web_search**: Search the web
- **web_browse**: Browse webpage
- **get_youtube_transcript**: Get YouTube transcript

## Installation

The `install.sh` script will:
1. Detect if NotNative is local or remote
2. Ask for WebSocket URL if not local
3. Install dependencies (ws package)
4. Configure environment

## Server Requirements

- NotNative app running with MCP WebSocket server
- For local: ws://127.0.0.1:8788
- For remote: wss://your-domain.com (or ws://IP:8788)

## Environment Variables

- `NOTNATIVE_WS_URL`: WebSocket URL (default: ws://127.0.0.1:8788)

## Error Handling

- **Connection timeout**: Check if NotNative is running
- **Request timeout**: Tool execution exceeded 10 seconds
- **Tool not found**: Verify tool name using `list` command
