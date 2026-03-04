---
name: exa-tool
description: Exa MCP integration for advanced search, research, and crawling.
homepage: https://exa.ai
metadata:
  {
    "openclaw": {
      "emoji": "🔍",
      "requires": { "env": ["EXA_API_KEY"] },
      "primaryEnv": "EXA_API_KEY",
      "bins": ["exa-search", "exa-web-search"]
    }
  }
---

# Exa MCP Tool

This skill provides access to Exa's powerful search and research capabilities through the Exa MCP server.

## Available Tools

### General Purpose
- `exa-search <tool> '{"json":"args"}'` - Generic wrapper for any Exa MCP tool

### Specialized Wrappers
- `exa-web-search '{"query":"...", "count":10, "freshness":"pw", ...}'` - Web search with optional filters

## Full Tool List (via exa-search)

All tools from the Exa MCP server are available:

| Tool | Description |
|------|-------------|
| `web_search_exa` | Search the web for any topic, get clean content |
| `web_search_advanced_exa` | Advanced search with filters (domains, dates, content options) |
| `get_code_context_exa` | Find code examples, documentation, programming solutions |
| `crawling_exa` | Get full content of a specific webpage from a known URL |
| `company_research_exa` | Research any company for business information and news |
| `people_search_exa` | Find people and their professional profiles |
| `deep_researcher_start` | Start an AI research agent that writes detailed reports |
| `deep_researcher_check` | Check status and get results from deep research task |

## Setup

1. Get your Exa API key from https://dashboard.exa.ai/api-keys

2. Set the environment variable:
   ```bash
   export EXA_API_KEY="your_exa_api_key_here"
   ```

   Or add to your shell profile (`~/.bashrc` or `~/.zshrc`):
   ```bash
   export EXA_API_KEY="your_exa_api_key_here"
   ```

   Or create a `.env` file in your workspace:
   ```bash
   echo "EXA_API_KEY=your_exa_api_key_here" > ~/.openclaw/workspace/.env
   source ~/.openclaw/workspace/.env
   ```

3. Restart OpenClaw to load the skill:
   ```bash
   openclaw gateway restart
   ```

## Usage Examples

### Basic Web Search
```bash
exa-web-search '{"query":"Step-3.5 Flash benchmarks"}'
```

### Advanced Search with Filters
```bash
exa-search web_search_advanced_exa '{
  "query": "OpenClaw AI",
  "count": 10,
  "freshness": "pw",
  "includeDomains": ["github.com", "docs.openclaw.ai"]
}'
```

### Code Search
```bash
exa-search get_code_context_exa '{
  "query": "OpenClaw agent implementation",
  "count": 5
}'
```

### Crawl Specific URL
```bash
exa-search crawling_exa '{
  "url": "https://docs.openclaw.ai/",
  "maxPages": 10
}'
```

### Company Research
```bash
exa-search company_research_exa '{
  "company": "OpenClaw",
  "includeNews": true,
  "newsDays": 30
}'
```

### People Search
```bash
exa-search people_search_exa '{
  "query": "Phil openclaw creator",
  "count": 10
}'
```

### Deep Research (Two-Step)
```bash
# Start research
TASK_ID=$(exa-search deep_researcher_start '{
  "query": "Current state of AI agents in 2026",
  "maxSources": 20
}' | jq -r '.taskId')

# Check status (poll until complete)
while true; do
  exa-search deep_researcher_check '{"taskId":"'"$TASK_ID"'"}'
  sleep 5
done
```

## Output Format

All tools return JSON with the Exa MCP response structure. The actual content is in the `result` field, which varies by tool but typically includes:

- `content`: Array of result items with `title`, `url`, `text` (snippet)
- Sometimes additional metadata like `cost`, `duration`, `sources`

Example web search output:
```json
{
  "content": [
    {
      "title": "Step 3.5 Flash - MathArena",
      "url": "https://matharena.ai/models/stepfun_3_5_flash",
      "text": "Step 3.5 Flash benchmarks and performance metrics..."
    }
  ]
}
```

## Using in OpenClaw Agents

Agents can use these tools directly:

```javascript
// In an agent session
/exec exa-search web_search_exa '{"query":"latest news"}'

// Or via API
{
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Search for recent AI developments using exa-search"
  }
}
```

## Notes

- Rate limits apply based on your Exa plan
- The MCP server uses Server-Sent Events (SSE) streaming; the wrapper handles this
- All tools accept various optional parameters; see Exa docs for full schema
- Errors are returned with proper exit codes and messages to stderr

## Troubleshooting

**"EXA_API_KEY not set"**
- Ensure the environment variable is exported in the same session where OpenClaw runs
- If using systemd/systemctl, set the key in the service file or `/etc/environment`

**"406 Not Acceptable"**
- The tool already sets the correct Accept header; this shouldn't occur in the wrapper

**Empty or no results**
- Verify your API key has credits/quota
- Check the Exa dashboard: https://dashboard.exa.ai

## References

- Exa MCP Docs: https://exa.ai/docs/reference/exa-mcp
- MCP Server: https://mcp.exa.ai/mcp
- API Keys: https://dashboard.exa.ai/api-keys
