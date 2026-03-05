---
name: dify-kb-search
description: Search Dify Knowledge Base (Dataset) to get accurate context for RAG-enhanced answers.
metadata:
  openclaw:
    requires:
      env:
        - DIFY_API_KEY
        - DIFY_BASE_URL
    install:
      - id: python
        kind: node
        package: python3
        bins:
          - python3
      - id: requests
        kind: node
        package: requests
        bins: []
        label: Install Python requests library
commandDispatch: tool
commandTool: exec
commandArgMode: json
---

# Dify Knowledge Base Search Skill

🔍 **Search your Dify Knowledge Base to get accurate, contextual answers**

This skill enables AI agents to query Dify datasets for RAG (Retrieval-Augmented Generation) context retrieval. Perfect for knowledge base Q&A, documentation search, and contextual AI responses.

![Dify Knowledge Base](https://dify.ai/favicon.ico)

## ✨ Features

- **List Knowledge Bases** - Discover all available Dify datasets
- **Smart Search** - Query datasets with hybrid, semantic, or keyword search
- **Auto-Discovery** - Automatically find available datasets if ID not provided
- **Configurable Results** - Adjust top-k, search method, and reranking
- **Error Handling** - Graceful error messages for debugging
- **Zero Hardcoding** - All configuration via environment variables

## 🚀 Quick Start

### 1. Configure Environment Variables

Set up in `openclaw.json`:

```json
{
  "env": {
    "vars": {
      "DIFY_API_KEY": "${DIFY_API_KEY}",
      "DIFY_BASE_URL": "https://dify.example.com/v1"
    }
  }
}
```

**Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DIFY_API_KEY` | ✅ Yes | - | Your Dify API Key (from Settings → API) |
| `DIFY_BASE_URL` | ❌ No | `http://localhost/v1` | Your Dify instance base URL |

### 2. Install Dependencies

```bash
pip3 install requests
```

## 🛠️ Tools

### dify_list

Lists all available knowledge bases (datasets) in your Dify instance.

**Invocation:** `dify_list` tool

**Example Response:**
```json
{
  "status": "success",
  "count": 2,
  "datasets": [
    {
      "id": "dataset-abc123",
      "name": "Product Documentation",
      "doc_count": 42,
      "description": "All product guides and tutorials"
    },
    {
      "id": "dataset-xyz789",
      "name": "API Reference",
      "doc_count": 156,
      "description": "REST API documentation"
    }
  ]
}
```

**Usage:**
```json
{}
```

### dify_search

Searches a Dify Dataset for relevant context chunks.

**Invocation:** `dify_search` tool (mapped to `python3 scripts/search.py`)

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query or question |
| `dataset_id` | string | ❌ No | Auto-discover | Specific dataset ID to search |
| `top_k` | integer | ❌ No | 3 | Number of results to return |
| `search_method` | string | ❌ No | `hybrid_search` | Search strategy |
| `reranking_enable` | boolean | ❌ No | `false` | Enable reranking for better results |

**Search Methods:**

- `hybrid_search` - Combine semantic + keyword search (recommended)
- `semantic_search` - Meaning-based similarity search
- `keyword_search` - Exact keyword matching

**Example Usage:**

```json
{
  "query": "How do I configure OpenClaw?",
  "top_k": 5
}
```

```json
{
  "query": "API authentication methods",
  "dataset_id": "dataset-xyz789",
  "search_method": "semantic_search",
  "reranking_enable": true
}
```

**Example Response:**
```json
{
  "status": "success",
  "query": "How do I configure OpenClaw?",
  "dataset_id": "dataset-abc123",
  "count": 3,
  "results": [
    {
      "content": "To configure OpenClaw, edit the openclaw.json file...",
      "score": 0.8923,
      "title": "Installation Guide",
      "document_id": "doc-001"
    },
    {
      "content": "OpenClaw supports environment variables via...",
      "score": 0.8451,
      "title": "Configuration Options",
      "document_id": "doc-002"
    }
  ]
}
```

## 📋 Complete Workflow Example

```json
[
  {
    "tool": "dify_list",
    "parameters": {}
  },
  {
    "tool": "dify_search",
    "parameters": {
      "query": "What are the system requirements?",
      "top_k": 5,
      "search_method": "hybrid_search"
    }
  }
]
```

## 🔧 Troubleshooting

### Common Errors

| Error | Solution |
|-------|----------|
| `Missing DIFY_API_KEY` | Set `DIFY_API_KEY` in environment variables |
| `Connection refused` | Check `DIFY_BASE_URL` is correct and accessible |
| `No datasets found` | Verify dataset exists in your Dify workspace |
| `API request failed` | Check network connectivity and API key permissions |

### Debug Mode

Run manually to see detailed errors:

```bash
DIFY_API_KEY=your-key python3 scripts/search.py <<< '{"query":"test"}'
```

## 📚 Integration Tips

### RAG Pipeline Integration

```python
# Example: Use search results in AI response
results = dify_search(query, top_k=5)
context = "\n".join([r["content"] for r in results["results"]])
final_prompt = f"Answer based on context:\n\n{context}\n\nQuestion: {query}"
```

### Multiple Datasets

For searching across multiple datasets, loop through them:

```json
{
  "query": "Find information about authentication",
  "dataset_id": "dataset-api-docs"
}
```

Then query another dataset separately.

## 🔒 Security

- **Never commit API keys** - Use environment variables or `.env` files
- **Rotate keys regularly** - Generate new keys in Dify Settings
- **Restrict access** - Limit API key permissions where possible

## 📖 Implementation Details

This skill uses the Dify Dataset API:

- **List Datasets:** `GET /v1/datasets`
- **Search:** `POST /v1/datasets/{id}/retrieve`

For API documentation, see: https://docs.dify.ai/reference/api-reference

## 📝 Changelog

**v1.1.0** (2026-02-08):
- ✅ Added search method selection (hybrid/semantic/keyword)
- ✅ Added reranking support
- ✅ Auto-discovery of datasets
- ✅ Improved error handling
- ✅ Removed hardcoded URLs (fully configurable)
- ✅ Added detailed logging

**v1.0.0** (2026-02-06):
- Initial release
- Basic list and search functionality
