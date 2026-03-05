# MCP Registry Manager 🌐

Centralized discovery and quality scoring for the exploding MCP (Model Context Protocol) ecosystem.

## What It Does

The MCP ecosystem is growing fast — `awesome-mcp-servers`, `AllInOneMCP`, GitHub — but no unified discovery or quality checks.

**MCP Registry Manager** provides:
- **Unified discovery** — Aggregate servers from multiple sources
- **Quality scoring** — Test coverage, documentation, maintenance status
- **Semantic search** — "Find servers for file operations" (not just keyword search)
- **Install management** — Install/uninstall with dependency resolution
- **Categorization** — Organize by domain (files, databases, APIs, dev tools)

## Problem It Solves

MCP is becoming the "USB-C of agent tools" but:
- Discovery is fragmented (GitHub repos, lists, registries)
- No quality signals (which servers are production-ready?)
- No semantic search (can't find "what does this do?")
- No unified management

## Usage

```bash
# Discover all MCP servers
python3 scripts/mcp-registry.py --discover

# Search semantically
python3 scripts/mcp-registry.py --search "file system operations"

# Get quality report for a server
python3 scripts/mcp-registry.py --score @modelcontext/official-filesystem

# Install a server
python3 scripts/mcp-registry.py --install @modelcontext/official-filesystem

# List installed servers
python3 scripts/mcp-registry.py --list

# Update all installed servers
python3 scripts/mcp-registry.py --update
```

## Quality Score Formula

```
Quality = (0.4 * TestCoverage) + (0.3 * Documentation) + (0.2 * Maintenance) + (0.1 * Community)

Where:
- TestCoverage = % of code covered by tests
- Documentation = README completeness, API docs, examples
- Maintenance = Recent commits, responsive issues
- Community = Stars, forks, contributors
```

## Data Sources

| Source | Type | Coverage |
|---------|--------|-----------|
| awesome-mcp-servers | Curated list | Manual discovery |
| GitHub Search | Repos with `mcp-server` topic | Fresh discoveries |
| AllInOneMCP | API registry | Centralized metadata |
| Klavis AI | MCP integrations | Production services |

## Categories

- **Files** — Filesystem, storage, S3
- **Databases** — PostgreSQL, MongoDB, Redis, SQLite
- **APIs** — HTTP, GraphQL, REST
- **Dev Tools** — Git, Docker, CI/CD
- **Media** — Image processing, video, audio
- **Communication** — Email, Slack, Discord
- **Utilities** — Time, crypto, encryption

## Architecture

```
┌─────────────────┐
│  Discovery      │  ← awesome-mcp, GitHub, AllInOneMCP
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Registry DB    │  ← SQLite/PostgreSQL with metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quality Scorer │  ← Test coverage, docs, maintenance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Semantic Search│  ← Embeddings + vector search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CLI Interface  │  ← Install/uninstall/update
└─────────────────┘
```

## Requirements

- Python 3.9+
- requests (for GitHub API)
- sentence-transformers (for semantic search)
- numpy/pandas (for scoring)

## Installation

```bash
# Clone repo
git clone https://github.com/orosha-ai/mcp-registry-manager

# Install dependencies
pip install requests sentence-transformers numpy pandas

# Run discovery
python3 scripts/mcp-registry.py --discover
```

## Inspiration

- **MCP Server Stack guide** — Essential servers list
- **awesome-mcp-servers** — Community-curated directory
- **AllInOneMCP** — Remote MCP registry
- **Klavis AI** — MCP integration platform

## Local-Only Promise

- Registry metadata is cached locally
- Install operations run locally
- No telemetry or data sent to external services

## Version History

- **v0.1** — MVP: Discovery, quality scoring, semantic search
- Roadmap: GitHub integration, CI tests, auto-updates
