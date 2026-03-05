---
name: telegram-compose
description: |
  Format and deliver rich Telegram messages with HTML formatting via direct Telegram API.
  Auto-invoked by the main session for substantive Telegram output — no other skills need to call it.
  Decision rule: If your Telegram reply is >3 lines or contains structured data (lists, stats, sections, reports),
  spawn this as a Haiku sub-agent to format and send. Short replies (<3 lines) go directly via OpenClaw message tool.
  Handles: research summaries, alerts, status updates, reports, briefings, notifications — anything with visual hierarchy.
metadata: |
  {"openclaw":{
    "os": ["darwin", "linux"],
    "requires": {
      "binaries": ["jq", "curl"],
      "config": ["channels.telegram.accounts.<account>.botToken"]
    },
    "credentials": "Reads Telegram bot token from OpenClaw config file (~/.openclaw/openclaw.json or ~/.openclaw/clawdbot.json). The specific account name must be provided by the caller — the skill does not auto-select accounts.",
    "network": ["api.telegram.org"]
  }}
model-preference: claude-haiku-4-5
subagent: true
allowed-tools: exec, Read
---

# Telegram Compose

Format and deliver rich, scannable Telegram messages via direct API with HTML formatting.

## How This Skill Gets Used

**This skill is auto-invoked by the main session agent.** No other skills need to know about it.

### Decision Rule (for the main session agent)

Before sending a message to Telegram, check:

- **Short reply (<3 lines, no structure):** Send directly via OpenClaw `message` tool. Done.
- **Substantive content (>3 lines, or has lists/stats/sections/reports):** Spawn this skill as a sub-agent.

### Spawning the sub-agent

The main session agent calls `sessions_spawn` with:

```
sessions_spawn(
  model: "claude-haiku-4-5",
  task: "<task content — see template below>"
)
```

**Task template:**

```
Read the telegram-compose skill at {baseDir}/SKILL.md for formatting rules, then format and send this content to Telegram.

Bot account: <account_name>  (e.g., "main" — must match a key in channels.telegram.accounts)
Chat ID: <chat_id>
Thread ID: <thread_id>  (omit this line if not a forum/topic chat)

Content to format:
---
<raw content here>
---

After sending, reply with the message_id on success or the error on failure. Do NOT include the formatted message in your reply — it's already been sent to Telegram.
```

**IMPORTANT:** The caller MUST specify which bot account to use. The sub-agent must NOT auto-select or iterate accounts.

**CRITICAL:** The sub-agent announcement routes back to the main session, NOT to Telegram. So the main session should reply `NO_REPLY` after spawning to avoid double-messaging. The sub-agent's curl call is what delivers to Telegram.

### What the sub-agent receives

1. **Skill path** — so it can read the formatting rules
2. **Bot account name** — which Telegram bot account to use (must be specified, never auto-selected)
3. **Chat ID** — where to send
4. **Thread ID** — topic thread if applicable
5. **Raw content** — the unformatted text/data to turn into a rich message

---

## Credentials

**Bot token:** Stored in the OpenClaw config file under `channels.telegram.accounts.<name>.botToken`.

**The account name is always provided by the caller.** Never auto-select or iterate accounts.

```bash
# Auto-detect config path
CONFIG=$([ -f ~/.openclaw/openclaw.json ] && echo ~/.openclaw/openclaw.json || echo ~/.openclaw/clawdbot.json)

# ACCOUNT is provided by the caller (e.g., "main")
# Validate the account exists before extracting the token
ACCOUNT="<provided_account_name>"
BOT_TOKEN=$(jq -r ".channels.telegram.accounts.$ACCOUNT.botToken" "$CONFIG")

if [ "$BOT_TOKEN" = "null" ] || [ -z "$BOT_TOKEN" ]; then
  echo "ERROR: Account '$ACCOUNT' not found in config or has no botToken"
  exit 1
fi
```

---

## Sending

```bash
CONFIG=$([ -f ~/.openclaw/openclaw.json ] && echo ~/.openclaw/openclaw.json || echo ~/.openclaw/clawdbot.json)
# ACCOUNT provided by caller — never auto-select
BOT_TOKEN=$(jq -r ".channels.telegram.accounts.$ACCOUNT.botToken" "$CONFIG")

# Without topic thread
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg chat "$CHAT_ID" \
    --arg text "$MESSAGE" \
    '{
      chat_id: $chat,
      text: $text,
      parse_mode: "HTML",
      link_preview_options: { is_disabled: true }
    }')"

# With topic thread
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg chat "$CHAT_ID" \
    --arg text "$MESSAGE" \
    --argjson thread $THREAD_ID \
    '{
      chat_id: $chat,
      text: $text,
      parse_mode: "HTML",
      message_thread_id: $thread,
      link_preview_options: { is_disabled: true }
    }')"
```

---

## Formatting Rules

### HTML Tags

```
<b>bold</b>  <i>italic</i>  <u>underline</u>  <s>strike</s>
<code>mono</code>  <pre>code block</pre>
<tg-spoiler>hidden until tapped</tg-spoiler>
<blockquote>quote</blockquote>
<blockquote expandable>collapsed by default</blockquote>
<a href="url">link</a>
<a href="tg://user?id=123">mention by ID</a>
```

### Escaping

Escape these characters in **text content only** (not in your HTML tags):
- `&` → `&amp;`  (do this FIRST to avoid double-escaping)
- `<` → `&lt;`
- `>` → `&gt;`

Common gotcha: content containing `&` (e.g., "R&D", "Q&A") will break HTML parsing if not escaped.

### Structure Pattern

```
EMOJI <b>HEADING IN CAPS</b>

<b>Label:</b> Value
<b>Label:</b> Value

<b>SECTION</b>

• Bullet point
• Another point

<blockquote>Key quote or summary</blockquote>

<blockquote expandable><b>Details</b>

Hidden content here...
Long details go in expandable blocks.</blockquote>

<a href="https://...">Action Link →</a>
```

### Style Rules

1. **Faux headings:** `EMOJI <b>CAPS TITLE</b>` with blank line after
2. **Emojis:** 1-3 per message as visual anchors, not decoration
3. **Whitespace:** Blank lines between sections
4. **Long content:** Use `<blockquote expandable>`
5. **Links:** Own line, with arrow: `Link Text →`

### Examples

**Status update:**
```
📋 <b>TASK COMPLETE</b>

<b>Task:</b> Deploy v2.3
<b>Status:</b> ✅ Done
<b>Duration:</b> 12 min

<blockquote>All health checks passing.</blockquote>
```

**Alert:**
```
⚠️ <b>ATTENTION NEEDED</b>

<b>Issue:</b> API rate limit at 90%
<b>Action:</b> Review usage

<a href="https://dashboard.example.com">View Dashboard →</a>
```

**List:**
```
✅ <b>PRIORITIES</b>

• <s>Review PR #234</s> — done
• <b>Finish docs</b> — in progress
• Deploy staging

<i>2 of 3 complete</i>
```

---

## Mobile-Friendly Data Display

**Never use `<pre>` for stats, summaries, or visual layouts.** `<pre>` uses monospace font and wraps badly on mobile, breaking alignment and tree characters. Reserve `<pre>` for actual code/commands only.

**For structured data, use emoji + bold + separators:**

```
❌ BAD (wraps on mobile):
<pre>
├─ 🟠 Reddit  32 threads │ 1,658 pts
└─ 🌐 Web     8 pages
</pre>

✅ GOOD (flows naturally):
🟠 <b>Reddit:</b> 32 threads · 1,658 pts · 625 comments
🔵 <b>X:</b> 22 posts · 10,695 likes · 1,137 reposts
🌐 <b>Web:</b> 8 pages (supplementary)
🗣️ <b>Top voices:</b> @handle1 · @handle2 · r/subreddit
```

**Other patterns:**

Record cards:
```
<b>Ruby</b>
Birthday: Jun 16 · Age: 11

<b>Rhodes</b>
Birthday: Oct 1 · Age: 8
```

Bullet lists:
```
• <b>hzl-cli:</b> 1.12.0
• <b>skill:</b> 1.0.6
```

---

## Limits and Splitting

- **Message max:** 4,096 characters
- **Caption max:** 1,024 characters

**If formatted message exceeds 4,096 chars:**
1. Split at section boundaries (blank lines between `<b>HEADING</b>` blocks)
2. Each chunk must be valid HTML (don't split inside a tag)
3. Send chunks sequentially with a 1-second delay between them
4. First chunk gets the full heading; subsequent chunks get a continuation indicator: `<i>(continued)</i>`

---

## Error Handling

**If Telegram API returns an error:**

| Error | Action |
|-------|--------|
| `Bad Request: can't parse entities` | HTML is malformed. Strip all HTML tags and resend as plain text. |
| `Bad Request: message is too long` | Split per the rules above and retry. |
| `Bad Request: message thread not found` | Retry without `message_thread_id` (sends to General). |
| `Too Many Requests: retry after X` | Wait X seconds, then retry once. |
| Any other error | Report the error back; don't retry. |

**Fallback rule:** If HTML formatting fails twice, send as plain text rather than not sending at all. Delivery matters more than formatting.

---

## Sub-Agent Execution Checklist

When running as a sub-agent, follow this sequence:

1. **Parse the task** — extract Bot account name, Chat ID, Thread ID (if any), skill path, and raw content
2. **Read this SKILL.md** — load the formatting rules
3. **Format the content** — apply HTML tags, structure pattern, style rules, mobile-friendly data display
4. **Escape special chars** — `&` then `<` then `>` in text content only (not in your HTML tags)
5. **Check length** — if >4,096 chars, split at section boundaries
6. **Get bot token** — auto-detect config path, extract token for the specified account (error if not found)
7. **Send via curl** — use the appropriate template (with/without thread ID)
8. **Check response** — parse curl output for `"ok": true`
9. **Handle errors** — follow the error handling table above
10. **Report back** — reply with message_id on success, or error details on failure
