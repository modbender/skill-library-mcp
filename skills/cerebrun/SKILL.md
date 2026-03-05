---
name: cerebrun
description: "MCP client for Cerebrun - comprehensive personal context and memory management system. Retrieve user context layers (language, projects, identity, vault), perform semantic search, manage knowledge base, and interact with LLM Gateway. Use when: (1) Retrieving user preferences or context, (2) Searching user's knowledge base, (3) Managing projects and goals, (4) Storing or querying personal information, (5) Accessing conversation history via LLM Gateway"
---

# Cerebrun MCP Client

Cerebrun (cereb.run) is a Model Context Protocol (MCP) server that provides persistent personal context management across sessions.

## Quick Start

All requests require:
- `api_key`: Cerebrun API key (Bearer token)
- `base_url`: https://cereb.run/mcp

## Context Layers

**Layer 0** - Language, timezone, comms prefs
**Layer 1** - Projects, goals, pinned memories
**Layer 2** - Personal identity info, API and other keys
**Layer 3** - Encrypted vault (requires consent)

## Usage

### Get Context
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_context","arguments":{"layer":0}}}' \
  https://cereb.run/mcp

### Search Context
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_context","arguments":{"query":"Rust authentication","limit":5}}}' \
  https://cereb.run/mcp

### Push Knowledge
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"push_knowledge","arguments":{"content":"Important insight","category":"learning","tags":["rust","performance"]}}}' \
  https://cereb.run/mcp

### Chat via Gateway
curl -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"chat_with_llm","arguments":{"message":"Hello","provider":"openai","model":"gpt-4"}}}' \
  https://cereb.run/mcp

## Tools Reference

See [REFERENCES.md](references/REFERENCES.md) for complete API documentation.

## Script Usage

```python
scripts/cerebrun.py get_context --layer 0 --api-key YOUR_KEY
scripts/cerebrun.py search_context --query "project" --api-key YOUR_KEY
scripts/cerebrun.py push_knowledge --content "New idea" --category "todo" --api-key YOUR_KEY
```

## Configuration

Store API key in environment: `CEREBRUN_API_KEY` or pass via `--api-key`