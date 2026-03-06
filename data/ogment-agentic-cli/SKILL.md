---
name: Ogment CLI Skill
description: Securely invoke MCP tools via the Ogment CLI. Access your connected
  SaaS tools (Linear, Notion, Gmail, PostHog, etc.) through Ogment's governance
  layer.
---

# Ogment CLI Skill

Securely invoke MCP tools via the Ogment CLI. Access your connected SaaS tools (Linear, Notion, Gmail, PostHog, etc.) through Ogment's governance layer.

---

## Quick Start (First-Time Onboarding)

**Follow this flow when first using Ogment with a user:**

### Step 1: Check Auth
```bash
ogment auth status
```
- If `loggedIn: true` → skip to Step 3
- If `loggedIn: false` → continue to Step 2

### Step 2: Login (if needed)
```bash
ogment auth login
```
Extract the code from the response and **send it to your human**.

⚠️ **Make links clickable!** Use markdown or full URLs so humans can tap/click directly.

> **🔐 Approve this code to connect Ogment: `XXXX-XXXX`**
> 👉 [dashboard.ogment.ai/cli/approve](https://dashboard.ogment.ai/cli/approve)

Wait for approval, then verify with `ogment auth status`.

### Step 3: Discover What's Available
```bash
ogment catalog
```
Then for each server:
```bash
ogment catalog <serverId> | jq '[.data.tools[].name]'
```

### Step 4: Summarize to Your Human
Tell them what you found:

> **✅ Connected to Ogment!** Here's what I can access:
> - **Linear:** 28 tools (issues, projects, teams, docs)
> - **Gmail:** 11 tools (messages, threads, drafts)
> - **Notion:** 5 tools (search, fetch, comments)
> - **Slack:** 7 tools (conversations, users)
>
> What would you like me to help with?

---

## Prerequisites

| Requirement | Install | Required |
|-------------|---------|----------|
| `ogment` CLI | `npm install -g @ogment-ai/cli` | ✅ Yes |
| `jq` | `brew install jq` / `apt install jq` | Optional (for filtering) |

## First-Time Setup (Login Flow)

⚠️ **IMPORTANT FOR AGENTS:** Don't tell the human to run `ogment auth login` — run it yourself and send them the code!

### Step 1: Check if already authenticated
```bash
ogment auth status
```
If `loggedIn: true`, skip to Core Workflow.

### Step 2: If not logged in, start device flow
```bash
ogment auth login
```
This returns JSON with a device code. Extract and send to the human:

**Example output:**
```json
{
  "data": {
    "event": "auth_login.pending",
    "verification": {
      "userCode": "ABCD-1234",
      "verificationUri": "https://dashboard.ogment.ai/cli/approve"
    }
  }
}
```

### Step 3: Send the code to your human
Tell them:
> **Approve this code: `ABCD-1234`**
> 👉 https://dashboard.ogment.ai/cli/approve

### Step 4: Wait for approval
The `ogment auth login` command will complete automatically once approved. Then verify:
```bash
ogment auth status
```

## Authentication & Credentials

- **Credentials location:** `~/.config/ogment/credentials.json`
- **Token management:** Ogment handles OAuth for all connected services
- **Scope:** Access depends on services connected in your [Ogment dashboard](https://dashboard.ogment.ai)
- **Per-agent permissions:** Each agent only sees tools you've explicitly granted

No credentials are stored in this skill — all auth is managed by the Ogment CLI.

## When to Use

- User asks to interact with their connected services (issues, docs, emails, analytics)
- You need to call MCP tools that require auth/credentials
- Discovering what integrations the user has available

## Core Workflow

```
status → catalog → catalog <server> → catalog <server> <tool> → invoke
```

### 1. Check connectivity (if issues suspected)

```bash
ogment status
```

Returns auth state, connectivity, and available servers. Check `summary.status` for quick health.

### 2. Discover servers

```bash
ogment catalog
```

Returns list of servers with `serverId` and `toolCount`. Use `serverId` in subsequent calls.

### 3. List tools on a server

```bash
ogment catalog <serverId>
```

Returns all tools with `name` and `description`. Scan descriptions to find the right tool.

### 4. Inspect tool schema

```bash
ogment catalog <serverId> <toolName>
```

Returns `inputSchema` with properties, types, required fields, and descriptions.

### 5. Invoke a tool

```bash
ogment invoke <serverId>/<toolName> --input '<json>'
```

**Input methods:**
- Inline JSON: `--input '{"query": "test"}'`
- File: `--input @path/to/input.json`
- Stdin: `echo '{}' | ogment invoke ... --input -`

### 6. Debug errors

```bash
ogment invoke <serverId>/<toolName> --input '{}' --debug
```

The `--debug` flag surfaces raw MCP error messages with field-level validation details.

## Security Considerations

### File Input Safety

The `--input @path` flag reads local files. **Avoid these paths:**
- `~/.ssh/*` — SSH keys
- `~/.aws/*` — AWS credentials  
- `~/.config/` — App configs and tokens
- `~/.bash_history`, `~/.zsh_history` — Shell history
- Browser profile directories

**Best practice:** Only use `--input @path` with files you've explicitly created for this purpose.

### Network Security

- All API calls route through `dashboard.ogment.ai`
- No direct connections to SaaS APIs
- TLS encrypted in transit

### Permission Model

- Tools are scoped per-agent in your Ogment dashboard
- Agents only see tools you've granted access to
- Write operations may be restricted based on agent permissions

## Output Format

All commands return structured JSON:

```json
{
  "ok": true,
  "data": { ... },
  "error": null,
  "meta": { "command": "..." },
  "next_actions": [
    { "command": "...", "title": "...", "reason": "..." }
  ]
}
```

- **Check `ok` first** — boolean success indicator
- **`next_actions`** — suggested follow-up commands
- **`error.category`** — `validation`, `not_found`, `remote`, `auth`, `internal`
- **`error.retryable`** — whether retry might help

## Common Patterns

### Find a tool by intent

```bash
ogment catalog <serverId> | jq '.data.tools[] | select(.name + .description | test("email"; "i"))'
```

### List issues assigned to user

```bash
ogment invoke openclaw/Linear_list_issues --input '{"assignee": "me"}'
```

### Search Notion

```bash
ogment invoke openclaw/Notion_notion-search --input '{"query": "quarterly review", "query_type": "internal"}'
```

### Get Gmail messages

```bash
ogment invoke openclaw/gmail_listMessages --input '{"q": "is:unread", "maxResults": 10}'
```

## Error Recovery

| Error Code | Meaning | Action |
|------------|---------|--------|
| `TOOL_NOT_FOUND` | Bad server/tool name | Run `ogment catalog` to rediscover |
| `VALIDATION_INVALID_INPUT` | Malformed JSON | Check JSON syntax |
| `TRANSPORT_REQUEST_FAILED` | Server rejected call | Add `--debug`, check schema |
| `AUTH_INVALID_CREDENTIALS` | Bad/expired API key | Run `ogment auth login` |
| `HTTP_401` | Service connection expired | Tell human to reconnect (see below) |
| `HTTP_502` | Server down | Retry after delay |

## Handling Expired Connections

When you get `HTTP_401` with a message like:
> "Your connection to [Service] has expired. Please reconnect..."

**Tell your human (with clickable link):**
> **⚠️ Your [Service] connection has expired.**
> Please reconnect it here: [dashboard.ogment.ai](https://dashboard.ogment.ai)
> (Go to Integrations → [Service] → Reconnect)
>
> Let me know when done and I'll retry!

## Handling Missing Permissions

If a tool you expect isn't available (e.g., `gmail_createDraft` not in catalog):
- **This is normal** — agents have scoped permissions
- Write tools may be disabled by default

**Tell your human (with clickable link):**
> **I don't have write access to [Service].**
> To enable it, go to: [dashboard.ogment.ai](https://dashboard.ogment.ai)
> (Agents → [Agent Name] → Permissions)
>
> Let me know when updated and I'll check again!

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | Validation/parse error |
| 5 | Not found |
| 7 | Remote/transport error |
| 9 | Internal error |

## Flags Reference

| Flag | Effect |
|------|--------|
| `--debug` | Include raw error diagnostics |
| `--human` | Human-readable output |
| `--yes` | Auto-confirm prompts |
| `--api-key <key>` | Override API key |

**Avoid:** `--quiet` (suppresses all output including data)

## Pre-flight Checklist

Before invoking a tool:

1. ✅ Confirmed server exists (`catalog`)
2. ✅ Confirmed tool exists (`catalog <server>`)
3. ✅ Checked required fields in schema
4. ✅ Matched types exactly (number vs string)
5. ✅ Used exact casing for IDs
6. ✅ If using `--input @path`, verified file doesn't contain sensitive data
