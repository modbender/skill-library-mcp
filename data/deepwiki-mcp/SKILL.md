---
name: deepwiki
description: >
  Query DeepWiki MCP to get AI-grounded answers about any public GitHub repository.
  Use when answering questions about a repo's source code, architecture, configuration,
  or internals. Triggers on "how does X work in <repo>", "deepwiki", "look up in codebase",
  "ask deepwiki", "check the source code".
triggers:
  - deepwiki
  - look up in codebase
  - ask deepwiki
  - check the source
  - how does X work in
  - openclaw source
  - repo architecture
  - codebase question
---

# DeepWiki MCP

Query any public GitHub repository using DeepWiki's AI-powered documentation and Q&A service. No API key, no auth, free.

**MCP endpoint:** `https://mcp.deepwiki.com/mcp`

## Scope & Boundaries

**This skill handles:**
- Asking natural-language questions about any public GitHub repo
- Listing documentation topics indexed by DeepWiki
- Fetching full wiki contents for a repo
- Running queries via the included helper script

**This skill does NOT handle:**
- Private repository access (requires paid Devin account)
- Modifying repositories or submitting PRs
- Real-time code analysis (DeepWiki may lag a few days behind latest commits)
- Local code search or grep (use standard file tools for that)

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Question | Yes | Natural-language question about a repo |
| Repository | No | `owner/repo` format. Defaults to `openclaw/openclaw` |
| Action | No | `ask` (default), `topics`, or `docs` |

## Outputs

- AI-grounded text answer with source references from the repo
- Or a structured list of documentation topics
- Or full wiki contents (large output)

## Workflow

### Step 1 — Run the helper script

The script is located in this skill's directory at `scripts/deepwiki.sh`.

```bash
# Ask a question (defaults to openclaw/openclaw)
<skill_dir>/scripts/deepwiki.sh ask "How does session compaction work?"

# Ask about a specific repo
<skill_dir>/scripts/deepwiki.sh ask facebook/react "How does concurrent mode work?"

# List documentation topics
<skill_dir>/scripts/deepwiki.sh topics openclaw/openclaw

# Get full wiki contents (large output — prefer ask for targeted queries)
<skill_dir>/scripts/deepwiki.sh docs openclaw/openclaw
```

Replace `<skill_dir>` with the directory containing this SKILL.md.

### Step 2 — Interpret and relay the answer

DeepWiki returns AI-generated answers grounded in the repo's actual source code. The response typically includes:
- Direct answer to the question
- References to specific files and code paths
- Context about related functionality

Relay the answer to the user, adding your own context if you have additional knowledge.

### Step 3 — Follow up if needed

If the answer is incomplete or raises new questions:
- Ask a more specific follow-up question
- Use `topics` to find relevant documentation sections
- Use `docs` for broader context (but note: output can be very large)

## Direct curl (fallback)

If the helper script is unavailable:

```bash
curl -s -X POST https://mcp.deepwiki.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "ask_question",
      "arguments": {
        "repoName": "owner/repo",
        "question": "YOUR QUESTION"
      }
    }
  }' | grep '^data:' | grep '"id":1' | sed 's/^data: //' | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d['result']['content'][0]['text'])"
```

## MCP Tools Reference

| Tool | Purpose | Arguments |
|------|---------|-----------|
| `ask_question` | Ask any question, get AI-grounded answer | `repoName`, `question` |
| `read_wiki_structure` | List documentation topics for a repo | `repoName` |
| `read_wiki_contents` | Get full wiki docs for a repo | `repoName` |

## Error Handling

| Problem | Detection | Action |
|---------|-----------|--------|
| Timeout (>60s) | curl hangs or no response | Retry once; DeepWiki may be under load |
| Empty response | No `data:` lines in SSE stream | Check if repo exists and is public |
| Repo not indexed | Error message about unknown repo | Try again — DeepWiki indexes on first request |
| Rate limited | HTTP 429 or error response | Wait 30s and retry |
| Script not found | File not at expected path | Use direct curl fallback |

## Success Criteria

- DeepWiki returns a substantive answer (not an error or empty response)
- Answer references actual code/files from the repository
- User's question is addressed with grounded information

## Configuration

No persistent configuration required. The skill uses:
- `exec` tool to run the helper script (bash + curl + python3)
- No API keys or authentication needed
- Works for any public GitHub repository

**System dependencies:**

| Dependency | Purpose |
|------------|---------|
| bash | Script execution |
| curl | HTTP requests to MCP endpoint |
| python3 | JSON parsing of SSE responses |

## Notes

- Responses take 10-30s (AI generates answers server-side)
- `ask_question` is the most useful tool — use it first
- DeepWiki crawls repos periodically; may lag behind very recent commits
- Works for any public GitHub repo, not just OpenClaw
- For private repos, a paid [Devin](https://devin.ai) account is required
