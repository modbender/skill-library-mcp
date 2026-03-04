# UnSearch Skill for OpenClaw

This skill teaches AI agents (OpenClaw, Claude, etc.) how to use the UnSearch API for web search, content extraction, and deep research.

## Installation

### Via ClawHub

```bash
clawhub install unsearch
```

### Manual Installation

Copy the `unsearch/` directory to one of these locations:

- **Per-workspace:** `<workspace>/skills/unsearch/`
- **Shared (all agents):** `~/.openclaw/skills/unsearch/`

## Configuration

Add your API key to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "unsearch": {
        enabled: true,
        apiKey: "uns_your_api_key"
      }
    }
  }
}
```

Or set the environment variable:

```bash
export UNSEARCH_API_KEY="uns_your_api_key"
```

## Getting an API Key

1. Visit https://unsearch.dev
2. Sign up for free (5,000 queries/month)
3. Copy your API key from the dashboard

## What This Skill Enables

- **Web Search** — Search across 70+ engines (Google, Bing, DuckDuckGo, etc.)
- **Content Extraction** — Scrape and structure content from any URL
- **Agent Search** — Tavily-compatible AI search with answer generation
- **Deep Research** — Multi-source research with AI synthesis
- **Fact Verification** — Verify claims against multiple sources

## Example Agent Prompts

After installing this skill, your agent can respond to prompts like:

- "Search the web for recent AI news"
- "Find information about machine learning frameworks and summarize it"
- "Extract the content from this URL: https://example.com/article"
- "Research the impact of AI on healthcare"
- "Verify this claim: GPT-4 was released in March 2023"

## Skill Metadata

| Field | Value |
|-------|-------|
| Name | `unsearch` |
| Primary Env | `UNSEARCH_API_KEY` |
| Homepage | https://unsearch.dev |
| Requires | `UNSEARCH_API_KEY` environment variable |

## Publishing to ClawHub

To publish updates to this skill:

```bash
# From the skills directory
clawhub sync unsearch
```

## License

This skill is provided under the Apache 2.0 license, same as UnSearch itself.

## Support

- **Documentation:** https://docs.unsearch.dev
- **GitHub:** https://github.com/unsearch-org/unsearch
- **Issues:** https://github.com/unsearch-org/unsearch/issues
