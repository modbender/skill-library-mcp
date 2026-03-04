# OpenClaw Exa MCP Skill 🔍

[OpenClaw](https://github.com/openclaw/openclaw) skill for Exa MCP integration — advanced web search, code context, company research, and more.

## 🌐 Live Demo

**Documentation Site:** https://claireaicodes.github.io/openclaw-skill-exa-tool/

---

## Features

- ✅ **8 Exa MCP tools** in one unified interface
- ✅ **SSE streaming** handled automatically
- ✅ **Clean JSON output** for easy parsing
- ✅ **Agent-ready** — call from any OpenClaw agent
- ✅ **Secure** — API key managed via OpenClaw config

## Quick Start

### 1. Prerequisites

- OpenClaw 2026.2.9+
- Exa API key from [dashboard.exa.ai/api-keys](https://dashboard.exa.ai/api-keys)

### 2. Installation

Copy the `exa-tool` directory to your OpenClaw skills path:

```bash
# If using global node_modules (default)
cp -r exa-tool /path/to/openclaw/skills/
```

Or as a symlink:

```bash
ln -s /path/to/exa-tool /path/to/openclaw/skills/exa-tool
```

### 3. Configuration

Add to your `openclaw.json` config:

```json
{
  "skills": {
    "entries": {
      "exa-tool": {
        "apiKey": "your_exa_api_key_here"
      }
    }
  }
}
```

Then restart OpenClaw:

```bash
openclaw gateway restart
```

### 4. Usage

#### Basic Web Search

```bash
exec exa-search web_search_exa '{"query":"Step-3.5 Flash benchmarks"}'
```

Or use the simplified wrapper:

```bash
exec exa-web-search '{"query":"AI agents 2026"}'
```

#### Company Research

```bash
exec exa-search company_research_exa '{"companyName":"OpenAI"}'
```

#### Code Search

```bash
exec exa-search get_code_context_exa '{"query":"OpenClaw agent implementation"}'
```

#### Advanced Search

```bash
exec exa-search web_search_advanced_exa '{
  "query": "OpenClaw AI",
  "count": 10,
  "freshness": "pw",
  "includeDomains": ["github.com", "docs.openclaw.ai"]
}'
```

## Available Tools

| Tool | Description |
|------|-------------|
| `web_search_exa` | Basic web search with clean content |
| `web_search_advanced_exa` | Advanced filters: domains, dates, text includes/excludes |
| `get_code_context_exa` | Search code examples, docs, StackOverflow |
| `crawling_exa` | Crawl a specific URL to get full content |
| `company_research_exa` | Research companies: info, news, financials |
| `people_search_exa` | Find professional profiles |
| `deep_researcher_start` | Start AI research agent for detailed reports |
| `deep_researcher_check` | Check status of deep research task |

## Output Format

All tools return JSON with the Exa MCP response structure:

```json
{
  "content": [
    {
      "title": "Result Title",
      "url": "https://example.com/page",
      "text": "Snippet with relevant information..."
    }
  ]
}
```

Some tools (like `company_research_exa`) include additional structured data.

## Using in Agents

Agents can invoke these tools naturally:

```
/exec exa-search web_search_exa '{"query":"latest AI news"}'
```

Or through agent prompts:

> "Search for recent developments in AI agents and summarize."

The agent will automatically use the exa-search tool if it's in its allowed tools.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EXA_API_KEY` | Yes | Your Exa API key from dashboard.exa.ai |

The key is injected by OpenClaw from the config, so agents don't need to handle credentials.

## Troubleshooting

### "EXA_API_KEY not set"
- Verify the key is in your `openclaw.json` under `skills.entries.exa-tool.apiKey`
- Restart the gateway after config changes

### No results returned
- Check your API key has available credits at https://dashboard.exa.ai
- Verify your query parameters match the tool's expected schema
- Some tools require specific parameters (e.g., `companyName` for company_research_exa)

### 406 Not Acceptable
Should not occur with this wrapper — it sets proper headers. If seen, check your OpenClaw version.

## Development

The skill consists of two binaries:

- `exa-search` — Generic wrapper for all 8 tools
- `exa-web-search` — Simplified wrapper for web search only

Both handle SSE streaming and error reporting consistently.

## References

- [Exa MCP Documentation](https://exa.ai/docs/reference/exa-mcp)
- [OpenClaw Skills Guide](https://docs.openclaw.ai/skills/)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)

## License

MIT — see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for OpenClaw agents**
