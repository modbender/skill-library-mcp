---
name: session-memory
version: 1.0.0
description: Write session summaries to daily memory files and search session history so OpenClaw can recall and cite past conversations.
metadata: { "openclaw": { "emoji": "📅", "requires": { "bins": ["node"] } } }
---

# session-memory

Use this skill when the user asks to **remember yesterday’s (or a date’s) chat**, to **summarize a day’s sessions into memory**, or to **search past conversations** (by keyword or date). It bridges session logs and the memory store so OpenClaw can answer “what did we talk about on …?” and use session context in replies.

## When to use

- User asks: “把昨天的聊天记到记忆里” / “总结一下 2 月 27 日的对话并写入 memory”
- User asks: “查一下之前我们说过关于 XXX 的对话” / “搜索会话里关于 discord/股票 的内容”
- User wants past chats to be **searchable via memory/citations** → run the summarize script for that day first, then normal memory search will include it.

## Paths (default agent)

- **Sessions**: `~/.openclaw/agents/main/sessions/`  
  - `sessions.json` = index; `<session-id>.jsonl` = full transcript.
- **Memory**: `<workspace>/memory/`  
  - Daily file: `memory/YYYY-MM-DD.md`. Create or append a `## Session summary` section.

Run scripts from the **workspace root** (e.g. `~/.openclaw/workspace`), or pass `--workspace` so `memory/` is resolved correctly.

## 1. Summarize a day’s sessions → memory (session-to-memory)

Writes a **session summary** for the given date into `memory/YYYY-MM-DD.md` (creates the file or appends a section). Memory citations and RAG will then include that day’s chat.

```bash
node skills/session-memory/scripts/session-to-memory.js --date YYYY-MM-DD
```

Optional:

- `--date YYYY-MM-DD` — date to summarize (default: yesterday in local time).
- `--workspace /path/to/workspace` — workspace root; memory dir is `<workspace>/memory` (default: cwd or `~/.openclaw/workspace`).
- `--sessions-dir /path` — override sessions dir (default: `~/.openclaw/agents/main/sessions`).
- `--append` — append a “Session summary” section if the file exists; otherwise replace (default: append).
- `--max-messages 200` — cap messages per session when building summary (default: 200).

Example:

```bash
cd ~/.openclaw/workspace
node skills/session-memory/scripts/session-to-memory.js --date 2026-02-27 --append
```

Then answer the user with: “已把 2026-02-27 的会话摘要写入 memory/2026-02-27.md，之后你问当天的对话我就能通过记忆检索到。”

## 2. Search sessions (session-search)

Searches session JSONL by **keyword** and optional **date range**, returns snippets (session id, date, role, snippet) so the agent can use them in context. Does **not** write to memory; use this to answer “之前我们说过 XXX 吗？” or to gather context before summarizing.

```bash
node skills/session-memory/scripts/session-search.js --query "关键词" [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--limit 20]
```

Optional:

- `--query "..."` — search phrase (required).
- `--since YYYY-MM-DD` — only sessions that started on or after this date.
- `--until YYYY-MM-DD` — only sessions that started on or before this date.
- `--limit N` — max number of snippets (default: 20).
- `--sessions-dir /path` — override sessions dir.

Output: JSON array of `{ sessionId, date, role, snippet, timestamp }` to stdout. Use the result in your reply or to decide whether to run session-to-memory for that day.

Example:

```bash
node skills/session-memory/scripts/session-search.js --query "discord 断联" --since 2026-02-26 --limit 10
```

## 3. List sessions by date (for discovery)

To see which days have sessions (e.g. before summarizing or searching):

```bash
for f in ~/.openclaw/agents/main/sessions/*.jsonl; do
  [ -f "$f" ] && echo "$(head -1 "$f" | jq -r '.timestamp' | cut -dT -f1) $(basename "$f" .jsonl)"
done | sort -r
```

If `jq` is not available, use the session-search script with a very broad query and `--limit 1` per day, or run the summarize script with `--date` for a specific date (it will report “no sessions” if none).

## Tips

- Summarize **after** the day ends (or when the user asks) so `memory/YYYY-MM-DD.md` contains that day’s session summary; then OpenClaw’s memory/citation search will find it.
- Session search is **read-only** over JSONL; it does not change memory. Use it to answer “有没有说过 XXX” or to prepare a summary.
- Large sessions are truncated by `--max-messages` when summarizing to avoid huge memory files.
