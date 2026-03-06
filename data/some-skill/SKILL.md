---
name: blueclaw1
description: Search and discover AI agents via the OpenClaw (8004scan.io) API. Use when the user mentions OpenClaw, wants to find agents, search for agents, discover MCP servers, browse an agent registry. On first use, prompts for an API key and stores it securely.
---

# OpenClaw

Skill for interacting with the OpenClaw agent registry at 8004scan.io.

## Setup (first use)

On **every invocation**, check whether the API key file exists:

```bash
cat ~/.openclaw/api_key 2>/dev/null
```

- **If the file exists and is non-empty** — read the key from it and proceed.
- **If the file is missing or empty** — run the setup flow:

### Setup flow

1. Ask the user to provide their OpenClaw API key (conversationally or via AskQuestion).
2. Save the key:

```bash
mkdir -p ~/.openclaw && chmod 700 ~/.openclaw
echo "USER_PROVIDED_KEY" > ~/.openclaw/api_key
chmod 600 ~/.openclaw/api_key
```

3. Confirm to the user that the key has been saved to `~/.openclaw/api_key`.

> **Security**: the directory and file permissions restrict access to the current OS user only. Never commit or log the API key.

---

## Finding agents

When the user asks to find, search for, or discover agents:

1. Extract search keywords from the user's request.
2. Make the API call (replace `KEYWORDS` and `API_KEY`):

```bash
curl -s -H "X-API-Key: API_KEY" \
  "https://www.8004scan.io/api/v1/agents?search=KEYWORDS&limit=10"
```

3. Parse the JSON response and present results in a clear, readable format:
   - Agent name
   - Short description
   - Any other useful fields returned by the API

If the request fails with a 401/403 status, inform the user that their API key may be invalid and offer to re-enter it (delete `~/.openclaw/api_key` and re-run setup).

---

## Error handling

| Scenario | Action |
|----------|--------|
| Network error | Inform user, suggest retrying |
| 401 / 403 | API key invalid — offer to reset via setup flow |
| Empty results | Let user know nothing matched, suggest broader keywords |
| Rate limit (429) | Inform user, suggest waiting before retrying |
