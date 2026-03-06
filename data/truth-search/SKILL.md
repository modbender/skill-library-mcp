---
name: search_skill_toc
description: 
  Search the web using Cloudsways TruthSearch API. Returns highly relevant results with dynamic summaries, snippets, and optional full-text content. Use when you need up-to-date information, news, or deep research data.
homepage: https://truth.cloudsway.net
metadata: 
  {
    "openclaw":
      {
        "emoji":"🔍",
        "requires":{"env":["CLOUDSWAYS_AK"]},"bins":["curl","jq"],
      },
  }
---

# Cloudsways TruthSearch Skill

Search the web and extract intelligent fragments or full-text content directly into the LLM context.

## Quick Setup

1. **Get your Access Key**: Sign up at [Cloudsways](https://truth.cloudsway.net/)
2. **Set environment variable**:

```bash
export CLOUDSWAYS_AK="your-access-key"
````

That's it! The skill is ready to use.

---

# Quick Start

## Method 1: Using the Script

```bash
cd ~/scripts/search
./scripts/search.sh '{"q": "your search query"}'
```

**Examples:**

```bash
# Basic search
./scripts/search.sh '{"q": "latest AI developments"}'

# Search with time filter and pagination
./scripts/search.sh '{"q": "OpenAI news", "freshness": "Week", "count": 20}'

# Deep research (extracts full content and dynamic key fragments)
./scripts/search.sh '{"q": "Agentic AI architecture", "enableContent": true, "mainText": true}'
```

## Method 2: Direct API Call (Recommended for Windows)

If the script has issues, use curl directly:

```bash
curl -s -G \
  --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your search query" \
  --data-urlencode "count=20" \
  --data-urlencode "freshness=Week"
```

**Real-world example:**

```bash
curl -s -G \
  --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=latest AI news February 2026" \
  --data-urlencode "count=20" \
  --data-urlencode "freshness=Week" \
  --data-urlencode "enableContent=true" \
  --data-urlencode "mainText=true"
```

---

## API Reference

### Endpoint

```
GET https://truthapi.cloudsway.net/api/search/smart
```

### Headers

| Header          | Type   | Value        | Description             |
| --------------- | ------ | ------------ | ----------------------- |
| `Authorization` | String | ` {YOUR_AK}` | Your assigned AccessKey |

### Request Parameters

| Parameter        | Required | Type    | Default | Description                                                       |
| ---------------- | -------- | ------- | ------- | ----------------------------------------------------------------- |
| `q`              | **Yes**  | String  | -       | Search query term (cannot be empty)                               |
| `count`          | No       | Integer | 10      | Number of results. **MUST be one of: 10, 20, 30, 40, or 50**      |
| `freshness`      | No       | String  | null    | Time filter: `Day` (24hrs), `Week`, or `Month`                    |
| `offset`         | No       | Integer | 0       | Pagination offset (skip N results)                                |
| `enableContent`  | No       | Boolean | false   | Extract full text content                                         |
| `contentType`    | No       | String  | TEXT    | Format: `HTML`, `MARKDOWN`, or `TEXT`                             |
| `contentTimeout` | No       | Float   | 3.0     | Timeout in seconds (max: 10.0, min: 0.1)                          |
| `mainText`       | No       | Boolean | false   | Return dynamic summary fragments (requires `enableContent: true`) |

**⚠️ Important Notes:**

* `count` must be exactly 10, 20, 30, 40, or 50 - other values will cause errors
* `mainText` only works when `enableContent` is set to `true`
* For real-time news/stock data, results are cached for 10 minutes by default

### Response Format

The API returns JSON with the following structure:

```json
{
  "queryContext": {
    "originalQuery": "your search query"
  },
  "webPages": {
    "value": [
      {
        "name": "Article Title",
        "url": "https://example.com/article",
        "datePublished": "2026-02-27T15:46:11.0000000",
        "snippet": "Short summary of the webpage...",
        "mainText": "Dynamic summary fragments relevant to your query...",
        "content": "Full webpage text content...",
        "score": 0.85
      }
    ]
  }
}
```

**Field Descriptions:**

* `name`: Page title
* `url`: Full URL to the source
* `datePublished`: Publication timestamp
* `snippet`: Always included - short content summary
* `mainText`: Only if `enableContent=true` + `mainText=true` - smart query-relevant excerpts
* `content`: Only if `enableContent=true` - full page text
* `score`: Relevance score (0-1)

---

## Content Strategy

Choose the right field based on your needs:

| Field      | Latency    | Token Cost  | Use Case                           |
| ---------- | ---------- | ----------- | ---------------------------------- |
| `snippet`  | ⚡ Fastest  | 💰 Low      | Quick overviews, browsing results  |
| `mainText` | ⚡⚡ Medium  | 💰💰 Medium | Precise answers, focused research  |
| `content`  | ⚡⚡⚡ Slower | 💰💰💰 High | Deep analysis, full context needed |

### Recommended Settings by Use Case

**Quick Research** (default)

```json
{"q": "topic", "count": 10}
```

Returns snippet only - fast and efficient.

**Focused Research** (recommended)

```json
{"q": "topic", "count": 20, "freshness": "Week", "enableContent": true, "mainText": true}
```

Returns snippet + smart excerpts - best balance of speed, cost, and relevance.

**Deep Research** (comprehensive)

```json
{"q": "topic", "count": 20, "enableContent": true, "contentType": "MARKDOWN"}
```

Returns full content - most comprehensive but highest token usage.

---

## Troubleshooting

### Script JSON Parsing Errors

If you get "Invalid JSON input" errors on Windows, use the direct curl method instead:

```bash
curl -s -G \
  --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your query here"
```

### SSL/Connection Issues

Do not use the `-k` flag in curl. Ensure that SSL verification is enabled for security.

### Count Parameter Error

If you see error about count parameter, ensure it's exactly 10, 20, 30, 40, or 50:

```bash
# ❌ Wrong: count=15
# ✅ Correct: count=20
```

### Environment Variable Not Set

Check if your AK is configured:

```bash
echo $CLOUDSWAYS_AK
```

If empty, set it:

```bash
export CLOUDSWAYS_AK="your-access-key"
```

---

## Quick Reference

### Common Commands

```bash
# Basic search
curl -s -G --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your query"

# Recent news (past week)
curl -s -G --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your query" \
  --data-urlencode "freshness=Week" \
  --data-urlencode "count=20"

# Deep research with excerpts
curl -s -G --url "https://truthapi.cloudsway.net/api/search/smart" \
  --header "Authorization:  ${CLOUDSWAYS_AK}" \
  --data-urlencode "q=your query" \
  --data-urlencode "enableContent=true" \
  --data-urlencode "mainText=true" \
  --data-urlencode "count=20"
```

### Parameter Cheat Sheet

* `count`: 10, 20, 30, 40, or 50 only
* `freshness`: Day, Week, or Month
* `contentType`: TEXT, HTML, or MARKDOWN
* `contentTimeout`: 0.1 to 10.0 seconds

### Support

* Documentation: [Cloudsways Docs](https://truth.cloudsway.net/docs)
* Sign up: [Cloudsways Sign Up](https://truth.cloudsway.net)
* Issues: Report in [Claude Code skill repository](https://github.com/0voice/Awesome-QuantDev-Learn)

---

**Last Updated:** 2026-02-28

---