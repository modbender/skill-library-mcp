---
name: Linkfuse
description: Create a Linkfuse affiliate short link from any URL. Trigger this skill when the user wants to create a Linkfuse link, shorten an affiliate URL, or says "/linkfuse". Requires LINKFUSE_TOKEN environment variable.
compatibility: Requires Node.js 18+, network access and valid Linkfuse API key
metadata:
  source: https://www.linkfuse.net
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - LINKFUSE_TOKEN
  env:
    - name: LINKFUSE_TOKEN
      required: true
      description: Bearer token from https://app.linkfuse.net/user/external-token
---
# Linkfuse Skill

Creates an affiliate short link via the Linkfuse REST API — same API used by the Chrome and Firefox extensions.

## Trigger Conditions

Use this skill when the user:
- Says `/linkfuse [url]`
- Asks to "create a Linkfuse link" for a URL
- Wants to shorten an affiliate/Amazon URL via Linkfuse

## Authentication

This skill reads the Bearer token exclusively from the `LINKFUSE_TOKEN` environment variable. If it is not set, tell the user:

> `LINKFUSE_TOKEN` is not set. Get your token from `https://app.linkfuse.net/user/external-token` and add it to your environment:
> ```
> export LINKFUSE_TOKEN=your_token_here
> ```
> Then retry.

Do not proceed without a token.

## Workflow

### Step 1 — Get the URL

If the user did not provide a URL, ask for one before proceeding.

### Step 2 — Create the link

```bash
node scripts/create-link.js --url "<url>"
```

- **Exit 0**: stdout contains JSON `{ "url": "...", "title": "..." }` — proceed to Step 3.
- **Exit 2 (Unauthorized)**: Tell the user their `LINKFUSE_TOKEN` is invalid or expired and they should update it.
- **Exit 1**: Display the stderr error message to the user.

### Step 3 — Display result

Show the user:
```
✓ Link created: <short-url>
  Title: <title>
```

Offer to copy the short URL to the clipboard:
```bash
echo -n "<short-url>" | xclip -selection clipboard 2>/dev/null || echo -n "<short-url>" | pbcopy 2>/dev/null || true
```

## Notes

- `allowRecycle: true` is sent with every request — if the same URL was shortened before, the existing link is returned rather than creating a duplicate.
- The `X-API-CLIENT: claude-skill` header identifies this client to the server.
