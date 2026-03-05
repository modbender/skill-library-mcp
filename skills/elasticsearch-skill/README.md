# Elasticsearch Skill for Claude Code

A markdown-based skill that teaches Claude Code how to interact with Elasticsearch clusters via REST API. No SDK, no client library, no MCP server — just `curl` and knowledge.

## What's in it

| File | What it covers |
|------|---------------|
| `SKILL.md` | Auth, search, CRUD, bulk ops, index management, cluster health, ILM, ES\|QL, ingest pipelines |
| `references/query-dsl.md` | Full Query DSL — bool, match, term, range, nested, geo, wildcards, runtime fields, search_after |
| `references/aggregations.md` | Metric, bucket, and pipeline aggregations — plus SRE patterns (error rates, top-N leaderboards) |

## Installation

Claude Code loads skills from local directories, not from GitHub URLs. Clone this repo, then copy the files to one of the supported skill locations.

### Option A: Personal skill (available in all projects)

```bash
git clone https://github.com/davidgeorgehope/elasticsearch-skill.git
mkdir -p ~/.claude/skills/elasticsearch
cp elasticsearch-skill/SKILL.md ~/.claude/skills/elasticsearch/
cp -r elasticsearch-skill/references ~/.claude/skills/elasticsearch/
```

### Option B: Project skill (available in one repo only)

From within your project's root directory:

```bash
git clone https://github.com/davidgeorgehope/elasticsearch-skill.git /tmp/elasticsearch-skill
mkdir -p .claude/skills/elasticsearch
cp /tmp/elasticsearch-skill/SKILL.md .claude/skills/elasticsearch/
cp -r /tmp/elasticsearch-skill/references .claude/skills/elasticsearch/
```

Then commit the `.claude/skills/elasticsearch/` directory to your repo so your team gets it too.

### Verify

Restart Claude Code, then check the skill is loaded:

```
/skills
```

You should see `elasticsearch` in the list.

> **Note:** Adding a GitHub URL to the `skills` array in `~/.claude/settings.json` does **not** work. Skills must be local files — there is no remote fetching.

## Configuration

Set your cluster credentials as environment variables before starting Claude Code:

```bash
export ES_URL="https://your-cluster.es.cloud.elastic.co:443"
export ES_API_KEY="your-base64-api-key"
```

Optionally, for Kibana API access:

```bash
export KIBANA_URL="https://your-cluster.kb.cloud.elastic.co:443"
```

No server to run, no dependencies to install, no Docker container to spin up.

## Why a Skill and Not MCP?

This is a deliberate choice, not a limitation.

### The token tax

MCP servers expose tools via JSON schemas that get injected into the LLM's context window on every request. Anthropic's own testing found that a modest five-server setup with 58 tools consumed **~55,000 tokens before the conversation even started**. That's your context window being eaten alive by tool definitions you might not even use.

A skill loads its main instructions only when triggered, and deeper reference files only when the LLM actually needs them. Progressive disclosure by design — not by workaround.

### The full circle

The industry trajectory looks something like this:

1. We had OpenAPI specs for describing APIs
2. LLMs couldn't reliably call them, so MCP was created as an intermediary
3. Models got better at calling APIs directly
4. Now people are generating OpenAPI specs *from* MCP servers
5. Meanwhile, Anthropic's own proposed fix is: give the agent a code execution tool and let it write TypeScript that calls APIs directly

We went full circle. MCP solved "LLMs can't reliably call APIs" right before that problem got solved by better models.

### What a skill actually is

A skill is a markdown file that tells the LLM:

- Here's how authentication works
- Here's the curl pattern for every operation
- Here's a reference for the query language (load it when you need it)
- Here are common patterns and gotchas

The LLM reads this, then writes and executes the actual API calls. No protocol translation layer, no tool schema overhead, no server process to maintain.

As [Mario Zechner put it](https://marioslab.io/posts/codex/primitives-not-frameworks/): *"Skills achieve the same progressive disclosure Anthropic describes, but without needing MCP as the underlying protocol… I could replace their MCPs with markdown files that explain how to correctly call their APIs or use their CLIs."*

### The practical argument

An MCP server for Elasticsearch would mean:

- A Node.js/Python process to run and maintain
- Tool schemas consuming context tokens on every turn
- Version compatibility issues between the MCP server and your ES cluster
- Another dependency in your stack

This skill is:

- **Three markdown files** (~26KB total)
- Zero dependencies
- Zero processes
- Works with any Elasticsearch version (it's just REST)
- Loaded into context only when needed
- The LLM writes the actual curl commands, adapting to your specific cluster

### When MCP *does* make sense

MCP isn't pointless — it shines when you need:

- **Stateful connections** (database sessions, websockets)
- **Binary protocols** that can't be called via curl
- **Complex auth flows** (OAuth dance, token refresh)
- **Non-HTTP tools** (local file systems, hardware interfaces)

Elasticsearch is a REST API with a single auth header. It doesn't need a protocol translation layer. It needs a good explanation.

## License

MIT
