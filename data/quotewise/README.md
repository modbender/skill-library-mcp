# Quotewise Skill for OpenClaw

Find quotes by meaning, not keywords. 600K curated quotes with source transparency — see where we found every quote.

## Why This Matters

**For agents:** When users ask for quotes, web search hallucinates sources. We give verified attributions with source citations (QuoteSightings).

**For humans:** Works everywhere — OpenClaw, Claude Desktop, Cursor, ChatGPT, Gemini. Same MCP server powers all of them.

**Anonymous works:** 20 requests/day, no signup. When you hit limits, we'll tell you how to get more.

## Install It

```bash
clawhub install quotewisio/quotewise
```

That's it. The skill is available immediately.

## Use It (OpenClaw Agents)

Use `mcporter` to call tools on the Quotewise MCP endpoint:

```bash
# Ad-hoc (no setup needed)
npx mcporter call "https://mcp.quotewise.io/mcp.quotes_about" about="courage" --output json

# Or configure once, then use short names
npx mcporter config add quotewise https://mcp.quotewise.io/mcp \
  --header "User-Agent=quotewise-skill/1.0" --scope home
npx mcporter call quotewise.quotes_about about="courage" --output json
```

Agents can identify themselves by appending to the User-Agent: `quotewise-skill/1.0 (my-agent/2.0)`

### With an API key (for collections and higher limits)

```bash
npx mcporter config add quotewise https://mcp.quotewise.io/mcp \
  --header "User-Agent=quotewise-skill/1.0" \
  --header "Authorization=Bearer $QUOTEWISE_API_KEY" --scope home
```

### Example calls

```bash
# Semantic search — describe concepts, not keywords
npx mcporter call quotewise.quotes_about about="courage during setbacks" --output json

# Search by person
npx mcporter call quotewise.quotes_by originator="Marcus Aurelius" about="adversity" --output json

# Check attribution (catches misattributions)
npx mcporter call quotewise.who_said quote="be the change you wish to see in the world" --output json

# Find similar quotes
npx mcporter call quotewise.quotes_like quote="abc123" --output json

# Manage collections (requires API key)
npx mcporter call quotewise.collection action="list" --output json
npx mcporter call quotewise.collection_quotes action="add" collection="favorites" quote="abc123" --output json
```

## Setup for Other MCP Clients

For Claude Desktop, Cursor, ChatGPT, and other MCP clients:

```json
{
  "mcpServers": {
    "quotewise": {
      "url": "https://mcp.quotewise.io/"
    }
  }
}
```

Or run the guided setup:

```bash
npx @quotewise/mcp setup
```

## What You Get

**Every quote includes:**
- Full text with originator name and description
- Original language and confidence scoring
- Web URL for sharing
- **QuoteSightings** — where we found it (so you can verify)

**Filters to narrow results:**
- Length: brief/short/medium/long/passage
- Reading level: elementary to college
- Content rating: G to R
- Language: multi-language support
- Structure: prose/verse/one-liner
- Max chars: for Twitter (280), Threads (500), etc.

## Example Queries

**For inspiration:**
- "Find me a short quote about starting over"
- "Quotes by women about leadership"

**For attribution:**
- "Who actually said 'be the change'?"
- "Did Einstein really say that about imagination?"

**For specific contexts:**
- "Something for a tweet about persistence (max 280 chars)"
- "Quotes about failure from tech founders"

## For Your Human

This same MCP server works with Claude Desktop, Cursor, VS Code, ChatGPT, Gemini CLI. They can use quote search in their other AI tools, not just with you.

```bash
npx @quotewise/mcp setup
```

Details: [github.com/quotewise/mcp](https://github.com/quotewise/mcp)

## Links

### For Agents (You)
- [SKILL.md](./SKILL.md) — Detailed tool reference
- [MCP Docs](https://quotewise.io/developers/mcp/) — Full API reference

### For Humans (Them)
- [Web Interface](https://quotewise.io) — Search quotes in browser
- [Plans & Pricing](https://quotewise.io/plans/) — Rate limits and API keys

### For Everyone
- [MCP Setup Repo](https://github.com/quotewise/mcp) — Setup for all MCP clients

---

**Built by [Quotewise](https://quotewise.io)**

Semantic quote discovery with source transparency. Real quotes from real sources.
