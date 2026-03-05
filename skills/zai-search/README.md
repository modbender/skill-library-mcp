# Z.AI Web Search

Web search skill using [Z.AI Web Search API](https://docs.z.ai/guides/tools/web-search). Returns structured results (title, URL, summary, site name) optimized for LLM processing.

## Setup

1. Get an API key from [Z.AI Platform](https://chat.z.ai)
2. Set environment variable: `export ZAI_API_KEY="your-api-key"`

## Usage

### Search

```bash
node scripts/search.mjs "your search query"
node scripts/search.mjs "economic news" -n 15
node scripts/search.mjs "news" --domain sohu.com --days 7
```

### Extract (basic)

```bash
node scripts/extract.mjs "https://example.com/article"
```

Note: Z.AI has no extract API. The extract script uses native fetch + HTML stripping as a fallback.

## Options

| Option | Description |
|--------|-------------|
| `-n <count>` | Number of results (1–50, default 10) |
| `--domain <domain>` | Limit to domain (e.g. `sohu.com`) |
| `--recency <filter>` | `oneDay`, `oneWeek`, `oneMonth`, `oneYear`, `noLimit` |
| `--days <n>` | Shorthand for recency |

## API Reference

- [Web Search Guide](https://docs.z.ai/guides/tools/web-search)
- [Web Search API](https://docs.z.ai/api-reference/tools/web-search)
