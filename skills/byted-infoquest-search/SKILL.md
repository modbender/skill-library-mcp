---
name: byted-infoquest-search
description: AI-optimized web search and content extraction via BytePlus InfoQuest API. Returns concise, relevant results for AI agents with time filtering and site-specific search. Get API key from https://console.byteplus.com/infoquest/infoquests
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["INFOQUEST_API_KEY"]},"primaryEnv":"INFOQUEST_API_KEY"}}
---

# Byted InfoQuest Search

AI-optimized web search and content extraction using BytePlus InfoQuest API. Returns concise, relevant results with time filtering and site-specific search capabilities.

## Search

```bash
node {baseDir}/search.mjs "query"
node {baseDir}/search.mjs "query" -d 7
node {baseDir}/search.mjs "query" -s github.com
```

## Options

- `-d, --days <number>`: Search within last N days (default: all time)
- `-s, --site <domain>`: Search within specific site (e.g., `github.com`)

## Extract content from URL

```bash
node {baseDir}/extract.mjs "https://example.com/article"
```

## Examples

### Recent News Search
```bash
# Search for AI news from last 3 days
node search.mjs "artificial intelligence news" -d 3
```

### Site-Specific Research
```bash
# Search for Python projects on GitHub
node search.mjs "Python machine learning" -s github.com
```

### Content Extraction
```bash
# Extract content from a single article
node extract.mjs "https://example.com/article"
```

## Notes

### API Access
- **API Key**: Get from https://console.byteplus.com/infoquest/infoquests
- **Documentation**: https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest
- **About**: InfoQuest is AI-optimized intelligent search and crawling toolset independently developed by BytePlus

### Search Features
- **Time Filtering**: Use `-d` for searches within last N days (e.g., `-d 7`)
- **Site Filtering**: Use `-s` for site-specific searches (e.g., `-s github.com`)

## Quick Setup

1. **Set API key:**
   ```bash
   export INFOQUEST_API_KEY="your-api-key-here"
   ```

2. **For Node.js < 18, install fetch support:**
   ```bash
   # Node.js 18+ includes fetch natively
   # For older versions, install node-fetch
   npm install node-fetch
   ```

3. **Test the setup:**
   ```bash
   node search.mjs "test search"
   ```

## Error Handling

The API returns error messages starting with `"Error:"` for:
- Authentication failures
- Network timeouts
- Empty responses
- Invalid response formats