---
name: bocha-search
description: Search the web using Bocha AI Search API (博查AI搜索) - a Chinese search engine optimized for Chinese content. Requires BOCHA_API_KEY. Supports web pages, images, and news with high-quality summaries.
metadata: {"openclaw":{"emoji":"🔍","requires":{"bins":["node"]},"primaryEnv":"BOCHA_API_KEY"}}
---

# Bocha Search Skill for OpenClaw

🔍 **博查AI搜索** - 专为中文内容优化的智能搜索工具

## Overview

This skill provides web search capabilities through the Bocha AI Search API (博查AI搜索). It's particularly effective for:
- ✅ Chinese language searches (中文搜索)
- ✅ Domestic Chinese content (国内内容)
- ✅ News and current events (新闻资讯)
- ✅ Encyclopedia and knowledge queries (百科知识)
- ✅ High-quality AI-generated summaries (AI智能摘要)

## Requirements

- **API Key**: You need a Bocha API key from https://open.bocha.cn/
- **Node.js**: Required to run the search script
- **Environment Variable**: Set `BOCHA_API_KEY` or configure via OpenClaw settings

## Configuration

### Step 1: Get API Key

1. Visit [博查AI开放平台](https://open.bocha.cn/)
2. Register an account (注册账号)
3. Create an application and get your API KEY
4. Recharge if needed (充值以获得搜索额度)

### Step 2: Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "bocha-search": {
        "enabled": true,
        "apiKey": "your-bocha-api-key-here",
        "env": {
          "BOCHA_API_KEY": "your-bocha-api-key-here"
        }
      }
    }
  }
}
```

Or set environment variable:
```bash
export BOCHA_API_KEY="your-bocha-api-key-here"
```

## Usage

Once configured, you can use this skill by asking in Chinese or English:

```
"搜索北京今天的天气"
"用博查查找人工智能的最新进展"
"bocha search: 量子计算发展趋势"
"查找特朗普的最新新闻"
```

The skill will automatically route Chinese queries or explicit "bocha" / "博查" / "search" requests to this search provider.

## Features

| Feature | Description |
|---------|-------------|
| **Chinese Optimized** | Better results for Chinese language queries |
| **High-Quality Summaries** | AI-generated article summaries (when `summary: true`) |
| **Multi-Modal** | Returns web pages, images, and related content |
| **Time Filtering** | Filter results by time range (day/week/month/year) |
| **Fast Response** | Typically returns results within 1-2 seconds |
| **Rich Metadata** | Includes publish date, site name, favicon, etc. |

## API Parameters

When calling the underlying tool directly:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query (supports Chinese and English) |
| `count` | number | No | 10 | Number of results (1-50) |
| `freshness` | string | No | "noLimit" | Time filter: "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit" |
| `summary` | boolean | No | true | Whether to include AI-generated summaries |

### Example Tool Call

```javascript
// Search for recent AI news in Chinese
{
  "query": "人工智能最新进展",
  "count": 10,
  "freshness": "oneWeek",
  "summary": true
}

// Search for Trump news
{
  "query": "特朗普 Trump 最新新闻",
  "count": 5,
  "freshness": "oneDay"
}
```

## Response Format

The API returns structured data including:

- **Web Pages**: Title, URL, snippet, summary, site name, publish date
- **Images**: Thumbnail URL, full image URL, dimensions
- **Total Matches**: Estimated total number of matching results
- **Related Queries**: Suggested related search terms

### Sample Response Structure

```json
{
  "_type": "SearchResponse",
  "queryContext": {
    "originalQuery": "search term"
  },
  "webPages": {
    "totalEstimatedMatches": 1908646,
    "value": [
      {
        "name": "Article Title",
        "url": "https://example.com/article",
        "snippet": "Short description...",
        "summary": "Full AI-generated summary...",
        "siteName": "Example Site",
        "datePublished": "2026-01-30T07:19:14+08:00"
      }
    ]
  },
  "images": {
    "value": [...]
  }
}
```

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `BOCHA_API_KEY is required` | API key not configured | Add API key to config or environment |
| `Invalid API KEY` | Wrong API key | Check your API key at https://open.bocha.cn/ |
| `Insufficient balance` | Out of credits | Recharge your account |
| `Rate limit exceeded` | Too many requests | Wait before making more requests |

## Pricing

- Visit https://open.bocha.cn/pricing for current pricing
- New users typically get free credits to start
- Pay-as-you-go based on search volume

## Technical Details

### API Endpoint
- **URL**: `https://api.bocha.cn/v1/web-search`
- **Method**: POST
- **Auth**: Bearer token in Authorization header

### Script Location
```
skills/bocha-search/
├── SKILL.md              # This file
├── README.md             # Full documentation
├── LICENSE               # MIT License
└── scripts/
    ├── package.json      # Node.js config
    ├── tool.json         # OpenClaw tool definition
    └── bocha_search.js   # Main search script ⬅️ Entry point
```

## Comparison with Other Search Tools

| Feature | Bocha Search | Brave Search | Perplexity |
|---------|--------------|--------------|------------|
| Chinese Content | ⭐⭐⭐ Excellent | ⭐⭐ Good | ⭐⭐ Good |
| Speed | ⭐⭐⭐ Fast | ⭐⭐⭐ Fast | ⭐⭐ Moderate |
| Summaries | ⭐⭐⭐ AI-powered | ❌ No | ⭐⭐⭐ AI-powered |
| Images | ⭐⭐⭐ Included | ⭐⭐ Separate | ⭐ Limited |
| Pricing | 💰 Affordable | 🆓 Free tier | 💰 Moderate |

## Best Practices

1. **Use Chinese queries** for better Chinese content results
2. **Enable summaries** (`summary: true`) for better context
3. **Set appropriate freshness** based on your needs:
   - Breaking news: `"oneDay"`
   - Recent developments: `"oneWeek"`
   - General research: `"noLimit"`
4. **Start with count=10**, increase if needed (max 50)
5. **Handle rate limits gracefully** in production use

## Troubleshooting

### No results returned
- Try different keywords or synonyms
- Remove time restrictions (`freshness: "noLimit"`)
- Check if your query is too specific

### Slow response
- Reduce `count` parameter
- Disable summaries if not needed (`summary: false`)
- Check network connectivity to `api.bocha.cn`

### API errors
- Verify API key is correct and active
- Check account balance at https://open.bocha.cn/
- Ensure you're not exceeding rate limits

## Links

- 🔗 [博查AI开放平台](https://open.bocha.cn/)
- 🔗 [API Documentation](https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK)
- 🔗 [OpenClaw Docs](https://docs.openclaw.ai)
- 🔗 [ClawdHub](https://clawdhub.com)

## License

MIT License - See LICENSE file for details

---

**Note**: This skill is specifically designed for OpenClaw and uses the official Bocha AI Search API. It is not affiliated with or endorsed by Bocha AI.