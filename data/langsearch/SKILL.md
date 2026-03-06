---
name: langsearch
description: Free web search and semantic reranking API for AGI applications. Use when you need to perform web searches, retrieve current information from the internet, or improve search accuracy with semantic reranking. Includes integration examples for building RAG (Retrieval-Augmented Generation) pipelines and LLM applications that require real-world context. Requires LANGSEARCH_API_KEY credential.
metadata:
  version: 1.0.1
  homepage: "https://langsearch.com"
  source: "https://langsearch.com/api-keys"
  openclaw:
    requires:
      env:
        - LANGSEARCH_API_KEY
    primaryEnv: LANGSEARCH_API_KEY
  credentialsDescription: "API key for LangSearch service. Get a free key at https://langsearch.com/api-keys"
  networkAccess: "LangSearch API (https://api.langsearch.com)"
  supplyChainRisk: "Low - communicates only with official LangSearch API"
  apiEndpoint: "https://api.langsearch.com/v1"
---

# LangSearch

## ⚠️ Security & Credentials

**Required Credentials:**
- `LANGSEARCH_API_KEY` - Your free LangSearch API key (required)

**Security Best Practices:**
1. **Get a free API key** - Sign up at [langsearch.com/api-keys](https://langsearch.com/api-keys)
2. **Protect your API key** - Never commit `.env` files containing `LANGSEARCH_API_KEY` to version control
3. **Use environment variables** - Store the key in `.env` or set via `export LANGSEARCH_API_KEY="..."`
4. **Monitor usage** - Check your API usage on the LangSearch dashboard
5. **Code inspection** - This tool only uses the official LangSearch API. All communication is via HTTPS to `api.langsearch.com`

**Network Access:**
- Only connects to: `https://api.langsearch.com` (official LangSearch API)
- No external data collection or telemetry
- No tracking or logging sent elsewhere

## Overview

LangSearch provides free APIs for web search and semantic reranking. It combines keyword search precision with vector-based semantic matching, making it ideal for integrating current web information into LLM applications and building RAG systems.

## Quick Start

### Prerequisites

1. Get a free API key at https://langsearch.com/api-keys
2. Set your API key as an environment variable: `export LANGSEARCH_API_KEY="your-api-key"`

### Basic Web Search

The simplest way to search the web using LangSearch:

```python
import requests
import json
import os

api_key = os.getenv("LANGSEARCH_API_KEY")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

query = "latest AI developments 2025"
payload = {
    "query": query,
    "count": 5,
    "summary": True
}

response = requests.post(
    "https://api.langsearch.com/v1/web-search",
    headers=headers,
    json=payload
)

results = response.json()
print(json.dumps(results, indent=2))
```

Or using cURL:

```bash
curl -X POST https://api.langsearch.com/v1/web-search \
  -H "Authorization: Bearer $LANGSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest AI developments 2025",
    "count": 5,
    "summary": true
  }'
```

## Web Search API

The web search endpoint retrieves information from billions of web documents using hybrid search (keyword + vector matching) with optional summaries.

### Endpoint
`POST https://api.langsearch.com/v1/web-search`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query |
| `count` | integer | No | Number of results to return (default: 10, max: 100) |
| `summary` | boolean | No | Include markdown summaries in results (default: false) |
| `freshness` | string | No | Filter results by freshness (`day`, `week`, `month`, `year`) |

### Response Structure

The API returns an array of search results with:
- `title` - Result title
- `url` - Result URL
- `snippet` - Text excerpt from the page
- `summary` - Markdown formatted summary (if `summary: true` in request)
- `score` - Relevance score

### Example Use Cases

**Current Information Retrieval**
When your LLM needs up-to-date information:

```python
# Search for recent developments
response = requests.post(
    "https://api.langsearch.com/v1/web-search",
    headers=headers,
    json={
        "query": "Python 3.14 release notes",
        "count": 3,
        "summary": True,
        "freshness": "week"
    }
)
```

**Multi-Query Research**
Build context from multiple searches:

```python
queries = [
    "climate change mitigation strategies",
    "renewable energy trends 2025",
    "carbon capture technology"
]

all_results = []
for query in queries:
    response = requests.post(
        "https://api.langsearch.com/v1/web-search",
        headers=headers,
        json={"query": query, "count": 5, "summary": True}
    )
    all_results.extend(response.json())
```

## Semantic Reranking API

Improve search accuracy by reranking results based on semantic relevance to your query.

### Endpoint
`POST https://api.langsearch.com/v1/rerank`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query for context |
| `documents` | array | Yes | Array of documents to rerank (each with `title`, `text`, etc.) |
| `model` | string | No | Reranking model (default: `langsearch-rerank-1`) |
| `top_n` | integer | No | Number of top results to return (default: 10) |
| `return_documents` | boolean | No | Include full documents in response (default: false) |

### Example: Reranking Web Search Results

```python
# Get initial search results
search_response = requests.post(
    "https://api.langsearch.com/v1/web-search",
    headers=headers,
    json={"query": "machine learning deployment best practices", "count": 10}
)

search_results = search_response.json()

# Prepare documents for reranking
documents = [
    {"title": r.get("title", ""), "text": r.get("snippet", "")}
    for r in search_results
]

# Rerank for better relevance
rerank_response = requests.post(
    "https://api.langsearch.com/v1/rerank",
    headers=headers,
    json={
        "query": "best practices for deploying ML models in production",
        "documents": documents,
        "top_n": 5
    }
)

reranked = rerank_response.json()
```

## Building RAG Applications

Combine web search with LLM context for better information retrieval and generation:

```python
def rag_query(user_question):
    # Step 1: Search the web for relevant information
    search_response = requests.post(
        "https://api.langsearch.com/v1/web-search",
        headers=headers,
        json={
            "query": user_question,
            "count": 5,
            "summary": True
        }
    )

    search_results = search_response.json()

    # Step 2: Extract summaries and URLs for context
    context = "\n".join([
        f"- {r['title']}: {r.get('summary', r.get('snippet', ''))}"
        for r in search_results
    ])

    # Step 3: Use with your LLM
    # This is where you'd call your LLM with the context
    rag_context = f"""
Based on recent web search results:

{context}

Answer the user's question: {user_question}
"""

    return rag_context, search_results
```

## Error Handling

Common HTTP status codes:

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Results returned normally |
| 401 | Unauthorized | Check API key is valid and set correctly |
| 429 | Rate limited | Retry with exponential backoff |
| 500 | Server error | Retry the request later |

See `scripts/web_search_example.py` for a complete example with error handling.

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
