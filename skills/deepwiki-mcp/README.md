# DeepWiki MCP

An [OpenClaw](https://openclaw.ai) skill that gives agents instant access to [DeepWiki](https://deepwiki.com), an AI-powered documentation and Q&A service for any public GitHub repository.

No API key. No auth. Free.

## What It Does

DeepWiki crawls public GitHub repos and builds a searchable, AI-grounded wiki. This skill exposes three capabilities via the [DeepWiki MCP server](https://mcp.deepwiki.com):

| Action | Description |
|--------|-------------|
| `ask` | Ask any natural-language question about a repo — get a sourced, grounded answer |
| `topics` | List all documentation topics DeepWiki has indexed for a repo |
| `docs` | Fetch the full wiki contents for a repo |

## Installation

Copy the skill directory to your OpenClaw workspace skills folder:

```bash
cp -r deepwiki ~/.openclaw/<workspace>/skills/
```

OpenClaw auto-discovers skills in `<workspace>/skills/`. Restart the gateway to activate.

### Requirements

- bash, curl, python3 (standard on most systems)
- No API keys or authentication needed

## Usage

The skill triggers automatically when asking about repository source code, architecture, or internals.

### Example prompts

- "How does session compaction work in OpenClaw?"
- "Ask DeepWiki about React's concurrent mode"
- "Look up the config schema in the codebase"
- "What's the architecture of torvalds/linux?"

### Helper script

```bash
# Ask a question (defaults to openclaw/openclaw)
scripts/deepwiki.sh ask "How does session compaction work?"

# Ask about a specific repo
scripts/deepwiki.sh ask facebook/react "How does concurrent mode work?"

# List documentation topics
scripts/deepwiki.sh topics openclaw/openclaw

# Get full wiki contents
scripts/deepwiki.sh docs openclaw/openclaw
```

## How It Works

DeepWiki exposes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server at `https://mcp.deepwiki.com/mcp` using Streamable HTTP (JSON-RPC over SSE).

The helper script:
1. Builds the JSON-RPC payload
2. Posts to the MCP endpoint via curl
3. Filters the SSE response stream for the result event
4. Extracts and prints the text content

## Quality Scorecard

| Category | Score | Details |
|----------|-------|---------|
| Completeness (SQ-A) | 8/8 | All checks pass |
| Clarity (SQ-B) | 5/5 | Clear workflow with fallback |
| Balance (SQ-C) | 5/5 | Script/AI split appropriate |
| Integration (SQ-D) | 5/5 | Standard exec-based, portable |
| Scope (SCOPE) | 3/3 | Clean boundaries |
| OPSEC | 2/2 | No violations |
| References (REF) | 3/3 | DeepWiki, MCP sources cited |
| Architecture (ARCH) | 2/2 | Script for HTTP/parsing |
| **Total** | **33/33** | |

*Scored by skill-engineer Reviewer (iteration 1)*

## Limitations

- **Latency:** 10-30s per query (AI generates answers server-side)
- **Freshness:** DeepWiki crawls repos periodically — may lag a few days behind latest commits
- **Public repos only:** Private repo support requires a paid [Devin](https://devin.ai) account
- **Rate limits:** No documented limits for free tier, but avoid excessive requests

## Related

- [DeepWiki](https://deepwiki.com)
- [DeepWiki MCP docs](https://docs.devin.ai/work-with-devin/deepwiki-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [OpenClaw](https://openclaw.ai)
