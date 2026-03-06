---
name: bnbot
description: Control Twitter/X via BNBOT Chrome Extension - scrape tweets, post, reply, navigate, and analyze accounts.
version: 0.3.1
homepage: https://github.com/jackleeio/bnbot-mcp-server
metadata:
  openclaw:
    emoji: "\U0001F916"
    os: [darwin, linux, windows]
    requires:
      bins: [bnbot-mcp-server]
    install:
      - id: node
        kind: node
        package: bnbot-mcp-server
        bins: [bnbot-mcp-server]
        label: Install bnbot-mcp-server (npm)
---

# BNBOT - Control Twitter/X with AI

BNBOT lets you control Twitter/X directly from your AI assistant through the BNBOT Chrome Extension.

## Auto Setup (IMPORTANT - Run on first use)

When the user first asks you to use BNBOT or control Twitter, you MUST automatically configure the MCP server before doing anything else. Follow these steps silently:

1. Check if `bnbot` is already configured in `~/.openclaw/openclaw.json` by reading the file.
2. If NOT configured, read the existing config, add the `bnbot` MCP server entry, and write it back:

```json
{
  "mcpServers": {
    "bnbot": {
      "command": "npx",
      "args": ["bnbot-mcp-server"]
    }
  }
}
```

Merge this into the existing `mcpServers` object (do not overwrite other servers). If the file doesn't exist, create it with this content.

3. After writing the config, tell the user: "BNBOT MCP server has been configured. Please restart OpenClaw to activate the connection."

Once configured, the MCP server starts automatically with OpenClaw. No manual setup needed.

## Error Handling (IMPORTANT)

After any BNBOT tool call, check the result. If the tool call fails or returns a connection error (e.g. WebSocket not connected, extension not responding, timeout), you MUST diagnose and guide the user:

### Connection failed / Extension not connected

Tell the user:

> BNBOT Chrome Extension is not connected. Please check:
>
> 1. **Install the extension** (if not installed):
>    Download from Chrome Web Store: https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln
>
> 2. **Open Twitter/X** in Chrome (https://x.com)
>
> 3. **Enable the OpenClaw toggle**:
>    Open the BNBOT sidebar on Twitter → click **Settings** → turn on **OpenClaw**
>
> After completing these steps, try again.

### MCP Server not running

If the MCP tools are not available at all, tell the user:

> BNBOT MCP server is not running. Please restart OpenClaw to activate the connection.
> If the problem persists, try reinstalling: `npm install -g bnbot-mcp-server`

### General rules

- Always call `get_extension_status` first before executing other tools, to verify the extension is connected.
- If `get_extension_status` shows `connected: false`, show the connection guide above BEFORE attempting any other action.
- Never silently fail. Always explain what went wrong and how to fix it.

## Architecture

```
User (OpenClaw) → bnbot-mcp-server (stdio) → WebSocket (localhost:18900) → BNBOT Chrome Extension → Twitter/X
```

## Available Tools

### Scraping

- `scrape_timeline` - Scrape tweets from the timeline (params: `limit`, `scrollAttempts`)
- `scrape_bookmarks` - Scrape bookmarked tweets (params: `limit`)
- `scrape_search_results` - Search and scrape results (params: `query`, `limit`)
- `scrape_current_view` - Scrape currently visible tweets
- `account_analytics` - Get account analytics (params: `startDate`, `endDate` in YYYY-MM-DD)

### Posting

- `post_tweet` - Post a tweet (params: `text`, optional `images` array of URLs)
- `post_thread` - Post a thread (params: `tweets` array of `{text, images?}`)
- `submit_reply` - Reply to a tweet (params: `text`, optional `tweetUrl`, optional `image`)

### Navigation

- `navigate_to_tweet` - Go to a specific tweet (params: `tweetUrl`)
- `navigate_to_search` - Go to search page (params: optional `query`)
- `navigate_to_bookmarks` - Go to bookmarks
- `navigate_to_notifications` - Go to notifications
- `return_to_timeline` - Go back to home timeline

### Status

- `get_extension_status` - Check if extension is connected
- `get_current_page_info` - Get info about the current Twitter/X page

## Usage Examples

- "Scrape my Twitter timeline and summarize the top topics"
- "Search for tweets about AI agents and collect the most engaging ones"
- "Post a tweet saying: Just discovered an amazing AI tool!"
- "Navigate to my bookmarks and export them"
- "Go to @elonmusk's latest tweet and reply with a thoughtful comment"
- "Post a thread about the top 5 productivity tips"
