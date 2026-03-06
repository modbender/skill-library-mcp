---
name: cloudsways-search
description: "Search the web using Cloudsways SmartSearch API. Returns highly relevant results with dynamic summaries, snippets, and optional full-text content. Use when you need up-to-date information, news, or deep research data."
requires:
  env:
    - CLOUDSWAYS_BASE_PATH
    - CLOUDSWAYS_ENDPOINT
    - CLOUDSWAYS_AK
  bins:
    - curl
    - jq
---

# Cloudsways SmartSearch Skill

Search the web and extract intelligent fragments or full-text content directly into the LLM context.

## Authentication

[cite_start]Authentication is handled via the URL endpoint and an Access Key[cite: 3, 5]. You must set the following environment variables before using the script:

```bash
export CLOUDSWAYS_BASE_PATH="your-base-path"
export CLOUDSWAYS_ENDPOINT="your-endpoint"
export CLOUDSWAYS_AK="your-access-key"
```
---
# Quick Start

## Using the Script

If you have configured the script locally, you can call it by passing a JSON object:

```bash
./scripts/search.sh '<json>'
```

**Examples:**

```bash
# Basic search
./scripts/search.sh '{"q": "python async patterns"}'

# Search with time filter and pagination
./scripts/search.sh '{"q": "Apple earnings", "freshness": "Week", "count": 20}'

# Deep research (extracts full content and dynamic key fragments)
./scripts/search.sh '{"q": "Agentic AI architecture", "enableContent": true, "mainText": true}'
```

---

## Basic Search (cURL)

```bash
curl -i --location --request GET 'https://{BasePath}/search/{Endpoint}/smart?q=latest+developments+in+quantum+computing&count=5' \
  --header 'Authorization: Bearer {AK}' \
  --header 'pragma: no-cache'
```

## Advanced Search with Full Content (cURL)

```bash
curl -i --location --request GET 'https://{BasePath}/search/{Endpoint}/smart?q=machine+learning+best+practices&count=10&enableContent=true&mainText=true' \
  --header 'Authorization: Bearer {AK}' \
  --header 'pragma: no-cache'
```

---

## API Reference

### Endpoint

```
GET https://{BasePath}/search/{Endpoint}/smart
```

### Headers

| Header | Type | Value | Description |
|---|---|---|---|
| `Authorization` | String | `Bearer {AK}` | Input value uses your assigned AccessKey. |
| `pragma` | String | `no-cache` | Entering `no-cache` returns results without caching, making each request independent; omitting this caches results for the same query term for 10 minutes. |

### Request Parameters

| Parameter | Required | Type | Default | Description |
|---|---|---|---|---|
| `q` | Y | String | - | User search query term; cannot be empty. |
| `count` | N | Short | 10 | Number of search results included. Enum values: `10`, `20`, `30`, `40`, `50`. |
| `freshness` | N | String | null | Filter search results by time periods: `Day` (Past 24 hours), `Week`, `Month`. |
| `offset` | N | Short | 0 | Zero-based offset indicating the number of search results to skip. Use with `count` to paginate. |
| `enableContent` | N | bool | false | Controls whether full text (content) extraction is enabled: `true` or `false`. |
| `contentType` | N | String | TEXT | Full text return format. Optional values: `HTML`, `MARKDOWN`, `TEXT`. |
| `contentTimeout` | N | Float | 3.0 | Full text read timeout. Maximum supported is 10 seconds. For low latency, set to `0.1`. |
| `mainText` | N | bool | false | Used to return dynamic summary key fragments. Takes effect only when `enableContent` is true. |

### Response Format

```json
{
  "queryContext": {
    "originalQuery": "open ai recent news"
  },
  "webPages": {
    "value": [
      {
        "name": "OpenAI just launched ChatGPT-5.1 Pro...",
        "url": "https://www.example.com/page",
        "datePublished": "2025-07-14T01:15:00.0000000Z",
        "snippet": "ChatGPT is looking to compete with Gemini...",
        "mainText": "Now GPT-5.1 Pro takes a lot of these improvements and makes them smarter...",
        "content": "Full extracted body text goes here...",
        "score": 0.8521444
      }
    ]
  }
}
```

---

## Content  Strategy

Understanding which text field to request is critical for token optimization:

| Field | Latency | Relevance | Description |
|---|---|---|---|
| `snippet` | Lowest | Good | A short text summary describing the webpage content. Best for general queries and fast browsing. |
| `mainText` | Medium | Highest | Dynamic summary fragments most relevant to the query term extracted from the body text. Smarter than the snippet. |
| `content` | Higher | High | Webpage full text information. Best for deep research, but consumes significant context tokens. |

**Tips:**

- For standard answers, rely on the default `snippet`.
- When you need precise, detailed answers without reading the whole page, use `enableContent=true` and `mainText=true`.
- Always set `pragma: no-cache` if you are querying real-time news or stock updates.

---

## MCP Client Integration (Alternative)

For environments supporting the Model Context Protocol (MCP), configure your MCP Client using `streamable_http`:

```json
{
  "mcpServers": {
    "smartsearch": {
      "transport": "streamable_http",
      "url": "https://searchmcp.cloudsway.net/search/{YOUR_SMARTSEARCH_ENDPOINT}/smart",
      "headers": {
        "Authorization": "Bearer {YOUR_SMARTSEARCH_AK}"
      }
    }
  }
}
```