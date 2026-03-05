---
name: valyu-search
description: "Use Valyu (valyu.ai) to search the web, extract content from web pages, answer with sources, and do deepresearch."
metadata: {"openclaw":{"emoji":"🔎","requires":{"bins":["node"],"env":["VALYU_API_KEY"]},"primaryEnv":"VALYU_API_KEY","homepage":"https://docs.valyu.ai"}}
---

# Valyu Search

Search across the world's knowledge.

## When to Use

Trigger this skill when the user asks for:
- "search the web", "web search", "look up", "find online", "find papers on..."
- "current news about...", "latest updates on..."
- "research [topic]", "what's happening with...", "deep research on..."
- "extract content from [URL]", "scrape this page", "get the text from..."
- "answer this with sources", "what does the research say about..."
- Fact-checking with citations needed
- Academic, medical, financial, or patent research
- Structured data extraction from web pages

## Prerequisites

- Get an API key at [valyu.ai](https://www.valyu.ai)
- Set `VALYU_API_KEY` in the Gateway environment (recommended) or in `~/.openclaw/.env`.
---

## Commands

Run a search across the web:

```bash
node {baseDir}/scripts/valyu.mjs search web "<query>"
```

Search across news, academic papers, financial data, patents and more

```bash
node {baseDir}/scripts/valyu.mjs search news "<query>"
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (required) |
| `searchType` | string | `"web"`, `"proprietary"`, `"news"`, or `"all"` (default: `"all"`) |
| `maxNumResults` | number | 1-20 (default: 10) |
| `includedSources` | string[] | Limit to specific sources (e.g., `["valyu/valyu-arxiv"]`) |
| `excludedSources` | string[] | Exclude specific sources |
| `startDate` | string | Filter from date (YYYY-MM-DD) |
| `endDate` | string | Filter to date (YYYY-MM-DD) |
| `countryCode` | string | ISO 3166-1 alpha-2 (e.g., `"US"`, `"GB"`) |
| `responseLength` | string | `"short"`, `"medium"`, `"large"`, `"max"` |
| `fastMode` | boolean | Reduced latency mode |
| `category` | string | Natural language category (e.g., `"academic research"`) |
| `relevanceThreshold` | number | 0.0-1.0 (default: 0.5) |

### Available Proprietary Sources

| Source | Description |
|--------|-------------|
| `valyu/valyu-arxiv` | Academic papers from arXiv |
| `valyu/valyu-pubmed` | Medical and life science literature |
| `valyu/valyu-stocks` | Global stock market data |

Additional sources: BioRxiv, MedRxiv, clinical trials, FDA drug labels, WHO health data, SEC filings, USPTO patents, Wikipedia, UK Parliament, UK National Rail, maritime vessel tracking, and more.

## 2. Contents API

Extract clean, structured content from any URL. Converts web pages to markdown or structured data.

### Usage

```bash
node {baseDir}/scripts/valyu.mjs contents "https://example.com" --summary
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `urls` | string[] | Array of URLs to extract (required) |
| `responseLength` | string | Output length: `"short"`, `"medium"`, `"large"`, `"max"` |
| `extractEffort` | string | `"auto"`, `"lightweight"`, `"moderate"`, `"heavy"` |
| `jsonSchema` | object | JSON Schema for structured extraction |


## 3. Answer API

Get AI-generated answers grounded in real-time search results with citations.

### Usage

```bash
node {baseDir}/scripts/valyu.mjs answer "What is quantum computing?" --fast
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Question or query (required) |
| `searchType` | string | Search scope: `"web"`, `"proprietary"`, `"news"`, `"all"` |
| `outputSchema` | object | JSON Schema for structured responses |


## 4. DeepResearch API

Launch async, multi-step research tasks that produce detailed reports with citations.

### Modes

| Mode | Duration | Use Case |
|------|----------|----------|
| `fast` | ~5 min | Quick answers, lightweight research |
| `standard` | ~10-20 min | Balanced research with deeper insights |
| `heavy` | ~90 min | In-depth, complex analysis |

### Usage

```bash
node {baseDir}/scripts/valyu.mjs deepresearch create "AI market trends" --mode heavy --pdf
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Research query (required) |
| `mode` | string | `"fast"`, `"standard"`, `"heavy"` |
| `outputFormats` | array | `["markdown"]`, `["pdf"]`, or JSON Schema object |
| `files` | array | File attachments (base64 encoded, max 10) |
| `urls` | string[] | URLs to analyze (max 10) |
| `webhookUrl` | string | HTTPS URL for completion notification |

## Choosing the Right API

| Need | API |
|------|-----|
| Quick facts, current events, citations | **Search** |
| Read/parse a specific URL | **Contents** |
| AI-synthesized answer with sources | **Answer** |
| In-depth analysis or report | **DeepResearch** |

## References

- [Valyu Docs](https://docs.valyu.ai)
- [Search API Reference](https://docs.valyu.ai/api-reference/endpoint/search)
- [Contents API Reference](https://docs.valyu.ai/api-reference/endpoint/contents)
- [Answer API Reference](https://docs.valyu.ai/api-reference/endpoint/answer)
- [DeepResearch Guide](https://docs.valyu.ai/guides/deepresearch)
