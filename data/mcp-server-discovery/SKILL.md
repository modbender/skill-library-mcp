---
name: mcp-server-discovery
description: Discover, search, and manage MCP (Model Context Protocol) servers. Use when the user needs to find MCP servers, get server information, generate MCP client configurations, or work with the MCP ecosystem. Triggers on queries about MCP servers, Model Context Protocol, server discovery, or MCP configuration.
---

# MCP Server Discovery

This skill helps you discover and manage MCP (Model Context Protocol) servers.

## What is MCP?

Model Context Protocol (MCP) is an open standard that enables AI systems to connect with external data sources and tools. It provides a standardized way for AI assistants to access files, databases, APIs, and other resources.

## Available Commands

Use the `scripts/mcp_discover.py` script for all MCP operations:

### List Available Servers

```bash
python3 scripts/mcp_discover.py list
```

Filter by category:
```bash
python3 scripts/mcp_discover.py list --category database
```

Categories: filesystem, dev, database, web, search, memory

### Search for Servers

```bash
python3 scripts/mcp_discover.py search --query "database"
```

### Get Server Details

```bash
python3 scripts/mcp_discover.py info --name postgres
```

### Generate MCP Client Configuration

```bash
python3 scripts/mcp_discover.py config --servers "filesystem,github,memory"
```

## Common Workflows

### Setting up a new MCP client

1. List available servers to see options
2. Select the servers you need
3. Generate configuration with those servers
4. Save the output to your MCP client's config file

### Finding the right server

1. Use `search` with keywords related to your need
2. Use `info` to get detailed information about a specific server
3. Check the install command and URL for setup instructions

## Server Categories

- **filesystem**: File system access and management
- **dev**: Development tools and integrations (GitHub, etc.)
- **database**: Database connections (PostgreSQL, SQLite)
- **web**: Web scraping and content fetching
- **search**: Search engine integrations
- **memory**: Persistent memory and knowledge graph

## JSON Output

All commands support `--json` flag for programmatic use:

```bash
python3 scripts/mcp_discover.py list --json
```
