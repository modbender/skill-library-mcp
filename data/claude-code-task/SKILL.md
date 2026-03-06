---
name: claude-code-task
description: "Run Claude Code tasks in background with automatic result delivery. Use for coding tasks, research in codebase, file generation, complex automations. Zero OpenClaw tokens while Claude Code works."
---

# Claude Code Task (Async)

Run Claude Code in background — zero OpenClaw tokens while it works. Results delivered to WhatsApp or Telegram automatically.

## Important: Claude Code = General AI Agent

Claude Code is NOT just a coding tool. It's a full-powered AI agent with web search, file access, and deep reasoning. Use it for ANY complex task:

- **Research** — web search, synthesis, competitive analysis, user experience reports
- **Coding** — create tools, scripts, APIs, refactor codebases
- **Analysis** — read and analyze files, data, logs, source code
- **Content** — write docs, presentations, reports, summaries
- **Automations** — complex multi-step workflows with file system access

Give it prompts the same way you'd talk to a smart human — natural language, focused on WHAT you need, not HOW to do it.

**NOT for:**
- Quick questions (just answer directly)
- Tasks needing real-time interaction

## Quick Start

## Telegram Thread Safety (must-follow)

For Telegram thread runs, `run-task.py` is designed to either route correctly or fail immediately.

### Mandatory step before launch
Resolve the **current runtime session key** first (source of truth), then launch with it.

- Get current key via `sessions_list` (or existing runtime context)
- If key is `agent:main:main:thread:<THREAD_ID>` → use it directly in `--session`
- Never derive `--session` from `chat_id`/sender id heuristics

### Rules
- Use only `--session "agent:main:main:thread:<THREAD_ID>"` for thread tasks
- Never use `agent:main:telegram:user:<id>` for thread tasks
- If routing metadata is inconsistent (thread/session UUID/target mismatch), script exits with `❌ Invalid routing`
- Default mode is `--telegram-routing-mode auto`:
  - allows non-thread Telegram for setups without thread sessions
  - blocks ambiguous user-scope session key (`agent:main:telegram:user:<id>`) unless explicitly forced
  - blocks non-thread launch if a recent thread session exists for same target (likely misroute)
- Force strict thread-only behavior with `--telegram-routing-mode thread-only`
- Force non-thread behavior with `--telegram-routing-mode allow-non-thread` or `--allow-main-telegram`

This is intentional: **abort fast > silent misroute**.

⚠️ **ALWAYS launch via nohup** — exec timeout (2 min) will kill the process!

⚠️ **NEVER put the task text directly in the shell command** — quotes, special characters, and newlines WILL break argument parsing. Always save the prompt to a file first, then use `$(cat file)`.

### WhatsApp

```bash
# Step 1: Save prompt to a temp file
write /tmp/cc-prompt.txt with your task text

# Step 2: Launch with $(cat ...)
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:whatsapp:group:<JID>" \
  --timeout 900 \
  > /tmp/cc-run.log 2>&1 &
```

The `--session` key (e.g. `agent:main:whatsapp:group:120363425246977860@g.us`) is used to auto-detect the WhatsApp target.

### Telegram (thread-safe default)

```bash
# ALWAYS use the current thread session key from context:
# agent:main:main:thread:<THREAD_ID>
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/cc-run.log 2>&1 &
```

> Do **NOT** use `agent:main:telegram:user:<id>` for thread tests/runs.
> That routes to main chat scope and can drift from the source thread.

### Telegram Threaded Mode (1:1 DM with threads)

When Marvin is used in Telegram Threaded Mode, each thread has its own session key like `agent:main:main:thread:369520`.

**Fail-safe routing (NEW):** `run-task.py` now enforces strict thread routing.
- If `--session` contains `:thread:<id>`, the script **refuses to start** unless Telegram target + thread session UUID are resolved.
- It auto-resolves missing values from `sessions_list` when possible.
- If the session is inactive and not returned by API, it falls back to local session files: `~/.openclaw/agents/main/sessions/*-topic-<thread_id>.jsonl`.
- If provided `--notify-session-id` mismatches the session key, it exits with error.
- Result: misrouted launches/heartbeats to main chat are blocked before Claude starts.

Use `--notify-session-id` to wake the exact thread session:

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:369520" \
  --timeout 900 \
  > /tmp/cc-run.log 2>&1 &
```

All 5 notification types route to the DM thread when `--session` key contains `:thread:<id>` ✅

- `--notify-session-id` — optional override. Usually auto-resolved from session metadata/files.
- `--notify-thread-id` — optional override. Usually auto-extracted from `--session`.
- `--reply-to-message-id` — optional debug field; avoid for DM thread routing.
- `--validate-only` — resolve routing and exit (no Claude run). Use this to verify thread launch args safely.

- `--notify-channel` — optional override (`telegram`/`whatsapp`)
- `--notify-target` — optional override for chat ID / JID
- `--timeout` — max runtime in seconds (default: 7200 = 2 hours)
- Always redirect stdout/stderr to a log file

### Why file-based prompts?
Research/complex prompts contain single quotes, double quotes, markdown, backticks — any of these break shell argument parsing. Saving to a file and reading with `$(cat ...)` avoids all quoting issues.

## Channel Detection

The `detect_channel()` function determines where to send notifications:

1. **CLI override wins** — if `--notify-channel` and `--notify-target` are both provided, those are used exclusively
2. **WhatsApp auto-detect** — if the session key contains `@g.us` (WhatsApp group JID), WhatsApp is used
3. **No target** — if neither applies, notifications are silently skipped

```python
def detect_channel(session_key):
    if NOTIFY_CHANNEL_OVERRIDE and NOTIFY_TARGET_OVERRIDE:
        return NOTIFY_CHANNEL_OVERRIDE, NOTIFY_TARGET_OVERRIDE
    jid = extract_group_jid(session_key)
    if jid:
        return "whatsapp", jid
    return None, None
```

## How It Works

```
┌─────────────┐     nohup      ┌──────────────┐
│    Agent     │ ──────────────▶│  run-task.py  │
│  (OpenClaw)  │                │  (detached)   │
└─────────────┘                └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │  Claude Code  │  ← runs on Max subscription ($0 API)
                               │  (-p mode)    │
                               └──────┬───────┘
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                    Every 60s    On complete   On error/timeout
                    ┌────────┐  ┌──────────┐  ┌──────────────┐
                    │ ⏳ ping │  │ ✅ result │  │ ❌/⏰/💥 error│
                    │ silent │  │ channel  │  │   channel    │
                    └────────┘  └──────────┘  └──────────────┘
```

### WhatsApp notification flow:
1. **Heartbeat pings** (every 60s) → WhatsApp direct (informational, no agent wake)
2. **Final result** → WhatsApp direct (human sees immediately) + `sessions_send` (agent wakes up)
3. **Agent receives** `[CLAUDE_CODE_RESULT]` via sessions_send → processes it → sends summary via `message(send)` to WhatsApp group
4. Human sees both: raw result + agent's analysis/next steps

### Telegram notification flow (DM Threaded Mode — full pipeline):
1. 🚀 **Launch notification** → thread ✅ (silent; HTML; `<blockquote expandable>` for prompt; via `send_telegram_direct`)
2. ⏳ **Heartbeat** (every 60s) → thread ✅ (silent; plain text; via `send_telegram_direct`)
3. 📡 **Claude Code mid-task updates** → thread ✅ (on-disk Python script `/tmp/cc-notify-{pid}.py`; CC calls file; prefix `"📡 🟢 CC: "` auto-added)
4. ✅/❌/⏰/💥 **Result notification** → thread ✅ (HTML; `<blockquote expandable>` for result; via `send_telegram_direct`)
5. 🤖 **Agent summary** → main chat ⚠️ (known limitation: `openclaw agent --session-id` synthetic messages have no `currentThreadTs`; acceptable)

**`send_telegram_direct()`** is the core mechanism for all thread-targeted notifications from external scripts. It calls `api.telegram.org` directly with `message_thread_id` — bypasses the OpenClaw message tool entirely (which cannot route to DM threads from outside a session context).

**Fallback** — if agent wake fails (session locked/busy): `already_sent=True` is set after the direct send, so no duplicate is sent.

### Key detail: Telegram vs WhatsApp delivery

**WhatsApp:** Raw result sent directly (human sees it immediately) + `sessions_send` wakes agent for analysis.

**Telegram:** Result sent via `send_telegram_direct` → then agent woken via `openclaw agent --session-id` (no `--deliver`). The agent sends its response via `message(action=send)` and replies `NO_REPLY`. This avoids double messages — `--deliver` would deliver the agent's turn output *on top of* any `message(action=send)` calls inside the turn.

**Why not `sessions_send` for Telegram?** `sessions_send` is blocked in the HTTP `/tools/invoke` deny list by architectural design. The `openclaw agent` CLI bypasses this limitation.

## Reliability Features

### Timeout (default 2 hours)
- `--timeout 7200` → after 7200s: SIGTERM → wait 10s → SIGKILL
- Timeout notification sent to channel with tool call count and last activity
- Partial output saved to file

### Crash safety
- `try/except` wraps entire main → crash notification always sent
- Both channel notification and agent wake attempted on any failure

### PID tracking
- PID file written to `skills/claude-code-task/pids/`
- Stale PIDs cleaned on startup
- Can check running tasks: `ls skills/claude-code-task/pids/`

### Silent mode (Telegram only)
Telegram supports silent notifications (no sound). This is used for background/informational messages:
- Heartbeat pings → `silent=True`
- Launch notifications → `silent=True`
- Final results → `silent=False` (default, user attention needed)

WhatsApp does NOT support silent mode — the flag is ignored for WhatsApp.

### Telegram DM Threads vs Forum Groups

Telegram has two distinct thread models. The key difference for run-task.py is how to route messages to the thread.

**The core problem with external scripts:**
- The OpenClaw `message` tool's `threadId` parameter is **Discord-specific** — ignored for Telegram
- Target format `"chatId:topic:threadId"` is rejected by the message tool's target resolver
- Session auto-routing (`currentThreadTs`) works ONLY inside active sessions — external scripts have no session context
- **Solution:** `send_telegram_direct()` bypasses the message tool entirely; calls `api.telegram.org` directly with `message_thread_id`

**DM Threaded Mode** (bot-user private chat with threads):
- All notifications use `send_telegram_direct(chat_id, text, thread_id=..., parse_mode=...)` ✅
- `thread_id` auto-extracted from session key `*:thread:<id>` by `extract_thread_id()`
- Launch + finish: `parse_mode="HTML"` with `<blockquote expandable>` for prompt/result
- Heartbeats + mid-task: `parse_mode=None` (plain text, avoid Markdown parse errors)
- **`parse_mode="Markdown"` trap**: finish messages contain `**text**` (CommonMark bold); Telegram MarkdownV1 rejects this with HTTP 400 — messages silently don't arrive
- **`replyTo` trap**: combining `replyTo` + `message_thread_id` → Telegram rejects request → fallback strips thread_id → message lands in main chat
- Agent summary: `openclaw agent --session-id <uuid>` wakes thread session; response goes to main chat (no `currentThreadTs` in synthetic messages — known, acceptable limitation)

**Forum Groups** (supergroup with Forum topics enabled):
- Same `send_telegram_direct()` approach works; `message_thread_id` is standard Bot API for Forum topics
- Auto-detected from session key pattern `*:thread:<id>`

**Claude Code mid-task updates:**
- DO NOT embed bot tokens or curl commands in the task prompt — Claude Code flags this as prompt injection
- run-task.py writes `/tmp/cc-notify-{pid}.py` to disk before launching Claude Code
- Task prompt prepended with `[Automation context: ... python3 /tmp/cc-notify-{pid}.py 'msg' ...]`
- Claude Code calls the file (legitimate local script pattern, no safety warning)
- Script automatically prepends `"📡 🟢 CC: "` to all messages; cleaned up in `finally` block

### Notification types

| Event | Emoji | WhatsApp delivery | Telegram delivery | DM thread? |
|-------|-------|-------------------|-------------------|------------|
| Launch | 🚀 | send_channel (Markdown) | send_telegram_direct (HTML, silent) | ✅ message_thread_id |
| Heartbeat | ⏳ | send_channel (Markdown) | send_telegram_direct (plain, silent) | ✅ message_thread_id |
| CC mid-task update | 📡 | — | /tmp/cc-notify-{pid}.py (Bot API, silent) | ✅ message_thread_id |
| Success | ✅ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Error | ❌ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Timeout | ⏰ | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Crash | 💥 | send_channel + sessions_send | send_telegram_direct (HTML) + openclaw agent | ✅ message_thread_id |
| Agent summary | 🤖 | — | openclaw agent wake | ⚠️ main chat (no thread ctx) |

## Claude Code Flags

- `-p "task"` — print mode (non-interactive, outputs result)
- `--dangerously-skip-permissions` — no confirmation prompts
- `--verbose --output-format stream-json` — real-time activity tracking for heartbeats

### Why NOT exec/pty?
- `exec` has 2 min default timeout → kills long tasks
- Even with `pty:true`, output has escape codes, hard to parse
- `nohup` + `-p` mode: clean, detached, reliable

### Git requirement
Claude Code needs a git repo. `run-task.py` auto-inits if missing.

## Python 3.9 Compatibility

`run-task.py` uses `Optional[X]` from `typing` (not `X | None`) for compatibility with Python 3.9. The union syntax (`X | None`) requires Python 3.10+.

```python
# Correct (3.9+)
from typing import Optional
def foo(x: Optional[str]) -> Optional[str]: ...

# Would break on 3.9
def foo(x: str | None) -> str | None: ...
```

## Full E2E Test (reference)

Use this when you need to validate the **entire pipeline** in one run:
- launch notification in source thread
- heartbeat after >60s
- Claude mid-task progress update (📡 🟢 CC)
- final result in source thread
- agent wake attempt with summary step

### Pass criteria
1. Launch message appears in the same thread (with expandable prompt quote)
2. At least one wrapper heartbeat appears after ~60s
3. At least one mid-task CC update appears (via `/tmp/cc-notify-<pid>.py`)
4. Final result appears in the same thread (expandable result quote)
5. Agent wake is attempted (`openclaw agent --session-id ...`) and does not duplicate final result

### Canonical full test prompt pattern
- keep prompt **compact** (about 10 lines) for routine testing
- ensure prompt length is **>4500 chars** to verify quote truncation/collapse behavior in Telegram
- force runtime >60s (`sleep 70`) to trigger wrapper heartbeat
- explicitly instruct Claude to call the notify script at least twice
- include a short structured report so output is easy to verify

### Canonical launch (minimal mode)
```bash
cat > /tmp/cc-full-test-prompt.txt << 'EOF'
# ~10 lines, but total >4500 chars:
# 1) notify script now
# 2) create test file with repeated text (to exceed 4500 chars)
# 3) sleep 70 + notify script again
# 4) run several shell commands
# 5) return short structured report
EOF

python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-full-test-prompt.txt)" \
  --project /tmp/cc-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --validate-only

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-full-test-prompt.txt)" \
  --project /tmp/cc-e2e-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 900 \
  > /tmp/cc-full-test.log 2>&1 &
```

### Verification artifacts
- wrapper log: `/tmp/cc-full-test.log`
- Claude output: `/tmp/cc-YYYYMMDD-HHMMSS.txt`
- session registry entry in `~/.openclaw/claude_sessions.json`

## Examples

### WhatsApp: Create a tool
```bash
nohup python3 {baseDir}/run-task.py \
  -t "Create a Python CLI tool that converts markdown to HTML with syntax highlighting. Save as convert.py" \
  -p ~/projects/md-converter \
  -s "agent:main:whatsapp:group:120363425246977860@g.us" \
  > /tmp/cc-run.log 2>&1 &
```

### Telegram: Research codebase (thread-safe)
```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 1800 \
  > /tmp/cc-run.log 2>&1 &
```

### Telegram Threaded Mode: Research codebase
```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:369520" \
  --timeout 1800 \
  > /tmp/cc-run.log 2>&1 &
# thread_id auto-extracted from session key
# target + session UUID auto-resolved from API/local session files
```

### Telegram Threaded Mode: Mid-task updates from Claude Code

run-task.py automatically creates an on-disk notification script before launching Claude Code, so CC can send progress updates without seeing the bot token in the prompt (which triggers safety refusals):

```bash
# Just write a normal task prompt — run-task.py handles the rest
cat > /tmp/cc-prompt.txt << 'EOF'
STEP 1: Write analysis to /tmp/report.txt (600+ words)...

After step 1, send a progress notification using the script from the
automation context above: python3 /tmp/cc-notify-<PID>.py "Step 1 done."

STEP 2: Write summary to /tmp/summary.txt...
EOF

nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --timeout 1800 \
  > /tmp/cc-run.log 2>&1 &
# run-task.py writes /tmp/cc-notify-{pid}.py before launch
# Prepends "[Automation context: use python3 /tmp/cc-notify-{pid}.py 'msg']" to task
# Claude Code calls the file; prefix "📡 🟢 CC: " auto-added; file cleaned up on exit
```

> ⚠️ **Never embed bot tokens or curl commands in the task prompt** — Claude Code correctly identifies hardcoded tokens + external API calls as prompt injection and refuses. Use the on-disk script pattern above instead.

> **Quick reference: launching from a Telegram DM thread (minimal mode)**
> ```bash
> # 1) Validate routing first (no Claude run)
> python3 {baseDir}/run-task.py \
>   --task "probe" \
>   --project ~/projects/x \
>   --session "agent:main:main:thread:<THREAD_ID>" \
>   --validate-only
>
> # 2) Real launch (only 3 required params)
> nohup python3 {baseDir}/run-task.py \
>   --task "$(cat /tmp/prompt.txt)" \
>   --project ~/projects/x \
>   --session "agent:main:main:thread:<THREAD_ID>" \
>   --timeout 900 \
>   > /tmp/cc-run.log 2>&1 &
> ```
> - Required: `--task`, `--project`, `--session`
- Safety: Telegram launches without `:thread:<id>` are blocked by default (`❌ Unsafe routing blocked`)
- For non-thread Telegram deployments, use `--telegram-routing-mode allow-non-thread`.
> - `THREAD_ID` is auto-extracted from session key
> - Target + session UUID are auto-resolved (API, then local session-file fallback)
> - If routing is inconsistent/unresolved, script exits with `❌ Invalid routing` before run
> - All notifications from run-task (launch/heartbeat/result) stay on the source thread ✅

### Long task with extended timeout
```bash
nohup python3 {baseDir}/run-task.py \
  -t "Refactor the entire auth module to use JWT tokens" \
  -p ~/projects/backend \
  -s "agent:main:whatsapp:group:120363425246977860@g.us" \
  --timeout 3600 \
  > /tmp/cc-run.log 2>&1 &
```

## Cost

- Claude Code runs on Max subscription ($200/mo) — NOT API tokens
- Zero OpenClaw API cost while Claude Code works
- Only cost: message delivery + brief agent turn for summary

## Session Resumption

Claude Code sessions can be resumed to continue previous conversations. This is useful for:
- Follow-up tasks building on previous research
- Continuing after timeouts or interruptions
- Multi-step workflows where context matters

### How to Resume

When a task completes, the session ID is automatically captured and saved to the registry (`~/.openclaw/claude_sessions.json`).

To resume a session, use the `--resume` flag:

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "SESSION_KEY" \
  --resume <session-id> \
  > /tmp/cc-run.log 2>&1 &
```

### Session Labels

Use `--session-label` to give sessions human-readable names for easier tracking:

```bash
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/cc-prompt.txt)" \
  --project ~/projects/my-project \
  --session "SESSION_KEY" \
  --session-label "Research on Jackson Berler" \
  > /tmp/cc-run.log 2>&1 &
```

### Listing Recent Sessions

The agent can read the session registry to find recent sessions:

```python
# Python code (for agent automation)
from session_registry import list_recent_sessions, find_session_by_label

# List sessions from last 72 hours
recent = list_recent_sessions(hours=72)
for session in recent:
    print(f"{session['session_id']}: {session['label']} ({session['status']})")

# Find session by label (fuzzy match)
session = find_session_by_label("Jackson")
if session:
    print(f"Found: {session['session_id']}")
```

Or manually inspect the registry:

```bash
cat ~/.openclaw/claude_sessions.json
```

### When to Resume vs Start Fresh

**Resume when:**
- You need context from previous conversation
- Building on previous research/analysis
- Continuing interrupted work
- Following up with clarifications or next steps

**Start fresh when:**
- Completely unrelated task
- Previous session was exploratory/experimental
- You want a clean slate
- Previous session context might cause confusion

### Resume Failure Handling

If a session ID is invalid or expired:
- Error message sent to channel with suggestion to start fresh
- Process exits cleanly (no partial work)
- Check stderr in `/tmp/cc-run.log` for details

Common resume failures:
- Session expired (Claude Code has retention limits)
- Invalid session ID (typo, wrong format)
- Session from different project/context

### Example Workflow

**Step 1: Initial research**
```bash
# Save prompt
write /tmp/research-prompt.txt with "Research the codebase architecture for project X"

# Launch task (Telegram thread-safe example)
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/research-prompt.txt)" \
  --project ~/projects/project-x \
  --session "agent:main:main:thread:<THREAD_ID>" \
  --session-label "Project X architecture research" \
  > /tmp/cc-run.log 2>&1 &
```

**Step 2: Check result and find session ID**
```bash
# Session ID printed in stderr: "📝 Session registered: <id>"
tail /tmp/cc-run.log

# Or read from registry
cat ~/.openclaw/claude_sessions.json | grep "Project X"
```

**Step 3: Follow-up implementation**
```bash
# Save follow-up prompt
write /tmp/implement-prompt.txt with "Based on your research, implement the authentication module"

# Resume session
nohup python3 {baseDir}/run-task.py \
  --task "$(cat /tmp/implement-prompt.txt)" \
  --project ~/projects/project-x \
  --session "SESSION_KEY" \
  --resume <session-id-from-step-1> \
  --session-label "Project X auth implementation" \
  > /tmp/cc-run2.log 2>&1 &
```

## Files

```
skills/claude-code-task/
├── SKILL.md              # This file
├── run-task.py           # Async runner with notifications
├── session_registry.py   # Session metadata storage
└── pids/                 # PID files for running tasks (auto-managed)
```
