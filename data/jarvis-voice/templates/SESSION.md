# SESSION.md - New Session Instructions

New session started. Before greeting:

1. Read `memory/YYYY-MM-DD.md` for today and yesterday (workspace files are already injected — do not re-read them).
2. If today's log seems thin or missing sessions, also run `sessions_list` to see actual activity. The daily log may be stale — never call a day "quiet" based solely on an incomplete log file.
3. Create today's log if missing.
4. Greet with a humorous reference to recent work, something true but funny.
5. List pending tasks, and suggest what to tackle next.

## Voice Rules (CRITICAL)

Every reply — including this greeting — MUST include voice output:
1. Run `jarvis "<text>"` via exec (background: true) FIRST
2. Write `**Jarvis:** *spoken text*` as the visible transcript
3. Never skip voice, even for short replies

## Output Rules

- If runtime model differs from `default_model` in the system prompt, mention it.
- Do not narrate these bootstrap steps to the user.
