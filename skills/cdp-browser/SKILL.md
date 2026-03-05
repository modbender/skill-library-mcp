---
name: cdp-browser
description: CDP browser control at localhost:9222. Use when you need to inspect tabs, take screenshots, navigate, scroll, post to X, or run JS in a persistent browser session (e.g. logged into X, Gmail).
---

# cdp-browser

CLI for Chrome/Chromium at localhost:9222. Inspect tabs, take screenshots, navigate, scroll, post to X, or run JS in a persistent browser session.

**Repo:** https://github.com/gostlightai/cdp-browser

**Prerequisites:** Chromium running with `--remote-debugging-port=9222`. Docker Compose or a local Chrome with remote debugging enabled.

## Commands

Run from the skill dir (`bin/` scripts):

| Command | Description |
|---------|-------------|
| `status` | List all tabs (JSON from CDP) |
| `tabs` | Same as status |
| `new <url>` | Open new tab |
| `goto <tabId> <url>` | Navigate tab to URL |
| `snapshot <tabId>` | Full-page screenshot (PNG) |
| `close-popup <tabId>` | Dismiss dialogs/modals |
| `scroll <tabId> <px\|sel> [down\|up]` | Scroll by pixels or selector |
| `query <tabId> getUrl` | Return current page URL |
| `query <tabId> getText [selector]` | Return element text (or body) |
| `query <tabId> getHtml [selector]` | Return element HTML (or body) |
| `tweet-draft <tabId> "text"` | Fill compose box only; does NOT post |
| `tweet-post <tabId> --confirm "text"` | Post tweet (requires `--confirm` as second arg) |
| `tweet <tabId> "text"` | Alias for tweet-draft (fills compose only) |

## Tweet flow

- **tweet-draft** (default): Fills the compose box; user reviews in browser and posts manually.
- **tweet-post**: Requires `--confirm` as second arg (strict). Use when user explicitly approves ("go ahead", "post it", or Telegram confirm button).
- **Optional Telegram confirm:** When `tweet.confirmButton` is enabled in config, the agent can run `tweet-draft --save-pending` to write pending state, then send a message with an inline "Confirm Post" button. On confirm, the agent runs `tweet-post --confirm`.

### Config (required for Telegram confirm button)

The Telegram "Confirm Post" button **only works if config exists**. Copy the example and place it in your workspace:

```bash
# From the skill dir (e.g. ~/.openclaw/workspace/skills/cdp-browser):
cp .cdp-browser.json.example ~/.openclaw/workspace/.cdp-browser.json
```

**Location:** `~/.openclaw/workspace/.cdp-browser.json` (or `$OPENCLAW_WORKSPACE/.cdp-browser.json`)

| Key | Default | Description |
|-----|---------|-------------|
| `tweet.confirmButton` | `false` | When `true`, agent sends draft with inline "Confirm Post" button in Telegram. User clicks to approve or says "go ahead". |

Without this config, the agent uses plain tweet-draft (no button); user confirms via text only.

### Telegram confirm button (agent instructions)

When `tweet.confirmButton` is true (config present) and you are in a Telegram session:

1. **Draft:** Run `tweet-draft --save-pending <tabId> "text"` from the skill dir. This fills the compose box and writes `~/.openclaw/workspace/.cdp-browser/pending-tweet.json`.
2. **Send with button:** Run from the skill dir:
   ```bash
   ./scripts/send-tweet-confirm.sh <chat_id> "<tweet_text>"
   ```
   Or use `openclaw message send` directly with `--buttons '[[{"text":"Confirm Post","callback_data":"cdp:tweet:confirm"}]]'`. Use the current session's reply target as `<chat_id>`.
3. **On confirm:** When the user clicks the button, OpenClaw delivers `callback_data: cdp:tweet:confirm`. Or the user says "go ahead"/"post it". Treat either as approval. Then:
   - Read `~/.openclaw/workspace/.cdp-browser/pending-tweet.json` for `text` and `tabId`
   - Run `tweet-post <tabId> --confirm "<text>"`
   - Edit or delete the message with the button (optional)
   - Delete the pending file

## Scripts

- **cdp.js** — Fetch-only wrapper for CDP HTTP API (`/json`, `/json/list`, `/json/new`); no shell.
- **pw.js** — Playwright connect to browser; runs snapshot/goto/scroll/query/tweet-draft/tweet-post. Compose launcher: SideNav_NewTweet_Button, /compose/post, Post only (avoids reply buttons). Post button: tweetButton, tweetButtonInline.

## Security

See [SECURITY.md](SECURITY.md) for mitigations and operational notes.
