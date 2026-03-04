---
name: session-history
description: Search and browse past conversation history across all sessions. Use when recalling prior work, finding old discussions, resuming dropped threads, or when the user references something from a previous conversation that isn't in memory files. Also use when asked to "remember" something discussed before, find "that conversation about X", or continue work from a past session.
---

# Session History

Search through past OpenClaw session transcripts (JSONL files in `~/.openclaw/agents/*/sessions/`).

## Quick Reference

```bash
# Search for conversations about a topic
python3 scripts/search_sessions.py "gclid pipeline error"

# List recent sessions
python3 scripts/search_sessions.py --list --days 3

# Search specific agent's history
python3 scripts/search_sessions.py "flight monitor" --agent main

# Wider time range
python3 scripts/search_sessions.py "quantum encryption" --days 30 --max-results 5
```

## Workflow

1. Run `search_sessions.py` with the user's query terms to find relevant sessions
2. Use `sessions_history` tool with the `sessionKey` to pull full context from a match
3. If `sessions_history` doesn't work (old/closed sessions), read the JSONL file directly with `read`
4. Summarize what was found — don't dump raw transcripts

## When to Use

- User says "remember when we discussed X?" or "we talked about Y last week"
- Resuming a thread that isn't captured in memory files
- Finding a decision, code snippet, or error from a past session
- Cross-referencing what was said vs what's in MEMORY.md

## Tips

- Also check `memory_search` first — it indexes session transcripts too
- Combine both: `memory_search` for semantic matching, `search_sessions.py` for keyword/exact matching
- The script searches user AND assistant messages
- JSONL path format: `~/.openclaw/agents/{agent_id}/sessions/{session_uuid}.jsonl`
