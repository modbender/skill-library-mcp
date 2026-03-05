---
name: openviking-mcp
description: Set up and run the OpenViking MCP server for RAG capabilities. Use when users need semantic search and document Q&A exposed through Model Context Protocol for Claude Desktop/CLI or other MCP clients. Triggers on requests about OpenViking MCP, RAG servers, or semantic search MCP setup.
---

# OpenViking MCP Server

HTTP MCP server that exposes OpenViking RAG capabilities as tools for Claude and other MCP clients.

## What It Provides

| Tool | Purpose |
|------|---------|
| `query` | Full RAG pipeline — semantic search + LLM answer generation |
| `search` | Semantic search only, returns matching documents with scores |
| `add_resource` | Ingest files, directories, or URLs into the database |

## Prerequisites

- Python 3.13+
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- OpenAI API key (for LLM and embeddings)

## Setup Steps

### Step 1: Get the Code

Clone the OpenViking repository:

```bash
git clone https://github.com/ZaynJarvis/openviking.git
# Or your fork/organization's repo
cd openviking/examples/mcp-query
```

### Step 2: Install Dependencies

```bash
uv sync
```

### Step 3: Configure API Keys (Human Input Required)

Copy the example config:

```bash
cp ov.conf.example ov.conf
```

**You must edit `ov.conf` and add your API tokens.** The critical fields:

| Field | Purpose | Example |
|-------|---------|---------|
| `vlm.token` | LLM for generating answers | `sk-...` (OpenAI) |
| `embedding.token` | Embeddings for semantic search | `sk-...` (OpenAI) |

**Wait for user to confirm:** Ask the user to paste their `ov.conf` (with tokens redacted if sharing logs) or confirm they've set it up before proceeding.

Example minimal config:

```json
{
  "vlm": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "token": "YOUR_OPENAI_API_KEY"
  },
  "embedding": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "token": "YOUR_OPENAI_API_KEY"
  }
}
```

### Step 4: Start the Server

```bash
uv run server.py
```

Server runs at `http://127.0.0.1:8000/mcp` by default.

### Step 5: Connect to Claude

**Claude CLI:**
```bash
claude mcp add --transport http openviking http://localhost:8000/mcp
```

**Claude Desktop:** Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "openviking": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Server Options

```
uv run server.py [OPTIONS]

  --config PATH       Config file path (default: ./ov.conf)
  --data PATH         Data directory path (default: ./data)
  --host HOST         Bind address (default: 127.0.0.1)
  --port PORT         Listen port (default: 8000)
  --transport TYPE    streamable-http | stdio (default: streamable-http)
```

Environment variables: `OV_CONFIG`, `OV_DATA`, `OV_PORT`, `OV_DEBUG`

## Usage Examples

Once connected, Claude can use these tools:

**Query with RAG:**
```
"Search my documents for information about Q3 revenue and summarize the findings"
```

**Semantic search only:**
```
"Find documents related to machine learning architecture"
```

**Add documents:**
```
"Index the PDF at ~/documents/report.pdf"
"Add https://example.com/article to my knowledge base"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | Change with `--port 9000` |
| Config not found | Ensure `ov.conf` exists or set `OV_CONFIG` path |
| Dependencies missing | Run `uv sync` in the mcp-query directory |
| Authentication errors | Check your API tokens in `ov.conf` |

## Resources

- OpenViking repo: `code/openviking/` or https://github.com/ZaynJarvis/openviking
