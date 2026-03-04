---
name: sergei-mikhailov-tg-channel-reader
description: Read and summarize posts from Telegram channels via MTProto (Pyrogram or Telethon). Fetch recent messages from public or private channels by time window.
metadata: {"openclaw": {"emoji": "📡", "requires": {"bins": ["tg-reader", "tg-reader-check"], "env": ["TG_API_ID", "TG_API_HASH"]}, "primaryEnv": "TG_API_HASH"}}
---

# tg-channel-reader

Read posts from Telegram channels using MTProto (Pyrogram or Telethon).
Works with any public channel and private channels the user is subscribed to.

> **Security notice:** This skill requires `TG_API_ID` and `TG_API_HASH` from [my.telegram.org](https://my.telegram.org). The session file grants full Telegram account access — store it securely and never share it.

---

## Exec Approvals

OpenClaw may require the user to **approve command execution** before `tg-reader` or `tg-reader-check` can run. If the command hangs or the user says nothing is happening:

1. Tell the user to open **[Control UI](https://docs.openclaw.ai/web/control-ui)** at `http://localhost:18789/` — there should be a pending approval request in the exec approvals panel. Click **"Always allow"** to add the command to the allowlist.
2. If the user works via a messenger (Telegram, Slack, Discord) — the OpenClaw bot may send the approval request as a message in the chat. The user can reply with `/approve <id> allow-always` (the bot provides the `<id>`). Other options: `/approve <id> allow-once` or `/approve <id> deny`.

The approval prompt appears in the **Control UI or as a bot message** — not as part of the agent's conversation. This is a common source of confusion.

---

## When to Use

- User asks to "check", "read", or "monitor" a Telegram channel
- Wants a digest or summary of recent posts
- Asks "what's new in @channel" or "summarize last 24h from @channel"
- Wants to track or compare multiple channels
- Wants channel info (title, description, subscribers) — use `tg-reader info`

---

## Quick Start

```bash
# 1. Run pre-flight diagnostic (fast, no Telegram connection)
tg-reader-check

# 2. Get channel info
tg-reader info @channel_name

# 3. Fetch recent posts
tg-reader fetch @channel_name --since 24h
```

---

## Commands

### `tg-reader-check` — Pre-flight Diagnostic

**Always run before fetching.** Fast offline check — no Telegram connection needed.

```bash
tg-reader-check
tg-reader-check --config-file /path/to/config.json
tg-reader-check --session-file /path/to/session
```

Returns JSON with `"status": "ok"` or `"status": "error"` plus a `problems` array.

Verifies:
- Credentials available (env vars or `~/.tg-reader.json`)
- Session file exists on disk (with size, modification date)
- At least one MTProto backend installed (Pyrogram or Telethon)
- Detects stale sessions (config points to older file while a newer one exists)

### `tg-reader info` — Channel Info

```bash
tg-reader info @channel_name
```

Returns title, description, subscriber count, and link.

### `tg-reader fetch` — Read Posts

```bash
# Last 24 hours (default)
tg-reader fetch @channel_name --since 24h

# Last 7 days, up to 200 posts
tg-reader fetch @channel_name --since 7d --limit 200

# Multiple channels (fetched sequentially with 10s delay between each)
tg-reader fetch @channel1 @channel2 @channel3 --since 24h

# Custom delay between channels (seconds)
tg-reader fetch @channel1 @channel2 @channel3 --since 24h --delay 5

# Fetch posts with comments (single channel only, limit auto-drops to 30)
tg-reader fetch @channel_name --since 7d --comments

# More comments per post, custom delay between posts
tg-reader fetch @channel_name --since 24h --comments --comment-limit 20 --comment-delay 5

# Skip posts without text (media-only, no caption)
tg-reader fetch @channel_name --since 24h --text-only

# Human-readable output
tg-reader fetch @channel_name --since 24h --format text

# Write output to file instead of stdout (saves tokens)
tg-reader fetch @channel_name --since 24h --output
tg-reader fetch @channel_name --since 24h --comments --output comments.json

# Use Telethon instead of Pyrogram (one-time)
tg-reader fetch @channel_name --since 24h --telethon
```

### `tg-reader auth` — First-time Authentication

```bash
tg-reader auth
```

Creates a session file. Only needed once.

---

## Output Format

### `info`

```json
{
  "id": -1001234567890,
  "title": "Channel Name",
  "username": "channel_name",
  "description": "About this channel...",
  "members_count": 42000,
  "link": "https://t.me/channel_name"
}
```

### `fetch`

```json
{
  "channel": "@channel_name",
  "fetched_at": "2026-02-22T10:00:00Z",
  "since": "2026-02-21T10:00:00Z",
  "count": 12,
  "messages": [
    {
      "id": 1234,
      "date": "2026-02-22T09:30:00Z",
      "text": "Post content...",
      "views": 5200,
      "forwards": 34,
      "link": "https://t.me/channel_name/1234",
      "has_media": true,
      "media_type": "MessageMediaType.PHOTO"
    }
  ]
}
```

### `fetch` with `--comments`

```json
{
  "channel": "@channel_name",
  "fetched_at": "2026-02-28T10:00:00Z",
  "since": "2026-02-27T10:00:00Z",
  "count": 5,
  "comments_enabled": true,
  "comments_available": true,
  "messages": [
    {
      "id": 1234,
      "text": "Post content...",
      "has_media": false,
      "comment_count": 2,
      "comments": [
        {
          "id": 5678,
          "date": "2026-02-28T09:35:00Z",
          "text": "Great post!",
          "from_user": "username123"
        }
      ]
    }
  ]
}
```

**Notes:**
- `comments_available: false` — channel has no linked discussion group (no comments possible)
- `comments_error` on a message — rate limit hit for that post's comments
- `from_user` may be `null` for anonymous comments
- Images/videos in comments are **not analyzed** — only text is captured
- Default post limit drops to 30 when `--comments` is active (override with `--limit`)

---

## After Fetching

1. Parse the JSON output
2. Posts with images/videos have `has_media: true` and a `media_type` field. Their text is in the `text` field (from the caption). **Do not skip posts just because they have media** — they often contain important text.
3. Images and videos are **not analyzed** (no OCR/vision) — only the text/caption is returned.
4. Summarize key themes, top posts by views, notable links
5. If `comments_enabled: true`, analyze comment sentiment and key themes alongside the main posts
6. Save summary to `memory/YYYY-MM-DD.md` if user wants to track over time

### Saving to File (Token Economy)

Use `--output` when the result is large (especially with `--comments`) and you don't need to analyze it immediately. The full data goes to a file, and stdout returns only a short confirmation — **this saves tokens**.

**Periodic updates pattern:** set up a cron task that runs `tg-reader fetch @channel --comments --output comments.json` on schedule. The file gets updated regularly. When the user asks to analyze comments — read the file instead of re-fetching. This avoids consuming tokens on every fetch.

When `--output` is used without a filename, the default is `tg-output.json`. Stdout confirmation:
```json
{"status": "ok", "output_file": "/absolute/path/to/tg-output.json", "count": 12}
```

### Saving Channel List

Store tracked channels in `TOOLS.md`:

```markdown
## Telegram Channels
- @channel1 — why tracked
- @channel2 — why tracked
```

---

## Error Handling

Errors include an `error_type` and `action` field to help agents decide what to do automatically.

### Channel Errors

| `error_type` | Meaning | `action` |
|--------------|---------|----------|
| `access_denied` | Channel is private, you were kicked, or access is restricted | `remove_from_list_or_rejoin` — ask user if they still have access; if not, remove the channel |
| `banned` | You are banned from this channel | `remove_from_list` — remove the channel, tell the user |
| `not_found` | Channel doesn't exist or username is wrong | `check_username` — verify the @username with the user |
| `invite_expired` | Invite link is expired or invalid | `request_new_invite` — ask user for a new invite link |
| `flood_wait` | Telegram rate limit | `wait_Ns` — waits ≤ 60 s are retried automatically; longer waits return this error |
| `comments_multi_channel` | `--comments` used with multiple channels | `remove_extra_channels_or_drop_comments` — use one channel at a time |

### System Errors

| Error | Action |
|-------|--------|
| `Session file not found` | Run `tg-reader-check` — use the `suggestion` from output |
| `Missing credentials` | Guide user through Setup (Step 1-2 below) |
| `tg-reader: command not found` | Use `python3 -m tg_reader_unified` instead |
| `AUTH_KEY_UNREGISTERED` | Session expired — delete and re-auth (see below) |

### Session Expired

```bash
rm -f ~/.tg-reader-session.session
tg-reader auth
```

### Auth Code Not Arriving

Use the verbose debug script for full MTProto-level logs:

```bash
python3 debug_auth.py
```

> **Warning:** `debug_auth.py` deletes existing session files before re-authenticating. It will ask for confirmation first.

---

## Library Selection

Two MTProto backends are supported:

| Backend | Command | Notes |
|---------|---------|-------|
| **Pyrogram** (default) | `tg-reader` or `tg-reader-pyrogram` | Modern, actively maintained |
| **Telethon** | `tg-reader-telethon` | Alternative if Pyrogram has issues |

Switch persistently: `export TG_USE_TELETHON=true`
Switch one-time: `tg-reader fetch @channel --since 24h --telethon`

---

## Setup & Installation

Full details in [README.md](./README.md).

### Step 1 — Get API Credentials

Go to https://my.telegram.org → **API Development Tools** → create an app → copy `api_id` and `api_hash`.

### Step 2 — Save Credentials

**Recommended** (works in agents and servers):
```bash
cat > ~/.tg-reader.json << 'EOF'
{
  "api_id": YOUR_ID,
  "api_hash": "YOUR_HASH"
}
EOF
chmod 600 ~/.tg-reader.json
```

**Alternative** (interactive only): add `export TG_API_ID=...` and `export TG_API_HASH=...` to `~/.bashrc` or `~/.zshrc`.

> **Note:** Agents and servers typically don't load shell profiles. If credentials aren't found after setting env vars, use `~/.tg-reader.json` instead.

### Step 3 — Install

```bash
npx clawhub@latest install sergei-mikhailov-tg-channel-reader
cd ~/.openclaw/workspace/skills/sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto telethon && pip install .
```

On Linux with managed Python (Ubuntu/Debian), use a venv:

```bash
python3 -m venv ~/.venv/tg-reader
~/.venv/tg-reader/bin/pip install pyrogram tgcrypto telethon && ~/.venv/tg-reader/bin/pip install .
echo 'export PATH="$HOME/.venv/tg-reader/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

### Step 4 — Authenticate

```bash
tg-reader auth
```

Pyrogram will ask to confirm the phone number — answer `y`. The code arrives in the Telegram app (not SMS).

### Step 5 — Secure the Session

```bash
chmod 600 ~/.tg-reader-session.session
```

---

## Scheduled Tasks & Cron

This skill needs network access (MTProto connection to Telegram servers) and a session file. How you configure OpenClaw cron depends on the session target.

> **Important:** When setting up a scheduled task that uses `tg-reader`, tell the user which approach you're using and what it means — so they can make an informed choice.

### Option A — `sessionTarget: "main"` (recommended)

The cron task sends a **reminder** to the main agent session. The agent then runs `tg-reader` in the main environment where the skill, credentials, and session file are already available.

**Pros:** No extra configuration — everything works out of the box.
**Cons:** Not fully autonomous — the task sends a system event, the agent picks it up and executes. Requires `payload.kind: "systemEvent"` (OpenClaw cron API limitation for main target).

**How to set up:**
1. Create a cron task with `sessionTarget: "main"` and `payload.kind: "systemEvent"`
2. In the task description, include the exact `tg-reader` command to run
3. The agent receives the reminder and executes the command in its main session

### Option B — `sessionTarget: "isolated"` (autonomous, complex setup)

The cron task runs in a **Docker container** — fully autonomous, no agent interaction needed. However, the container starts empty: no skill, no credentials, no session file.

**Pros:** Fully autonomous — runs on schedule without agent involvement.
**Cons:** Requires Docker setup; session file must be mounted into the container (may not work reliably — session files are tied to the machine and Telegram may invalidate them in a new environment).

**Required configuration in `~/.openclaw/openclaw.json`:**

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "setupCommand": "clawhub install sergei-mikhailov-tg-channel-reader && cd ~/.openclaw/workspace/skills/sergei-mikhailov-tg-channel-reader && pip install pyrogram tgcrypto telethon && pip install .",
          "env": {
            "TG_API_ID": "YOUR_ID",
            "TG_API_HASH": "YOUR_HASH"
          }
        }
      }
    }
  }
}
```

**Session file caveat:** The Telegram session file (`~/.tg-reader-session.session`) must also be available inside the container. This may require Docker volume mounting and might not work reliably — Telegram can invalidate sessions when they appear from a different environment. If you encounter `AUTH_KEY_UNREGISTERED` errors in isolated mode, switch to Option A.

### Explicit paths (both options)

When `~/` is not available or points to a different location, use explicit paths:

```bash
tg-reader-check \
  --config-file /home/user/.tg-reader.json \
  --session-file /home/user/.tg-reader-session

tg-reader fetch @channel --since 6h \
  --config-file /home/user/.tg-reader.json \
  --session-file /home/user/.tg-reader-session
```

Both flags work with all subcommands and both backends.

---

## Security

- Session file (`~/.tg-reader-session.session`) grants **full account access** — keep it safe
- Never share or commit `TG_API_HASH` or session files
- `TG_API_HASH` is a secret — store in env vars or config file, never in git
