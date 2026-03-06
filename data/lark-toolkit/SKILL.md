---
name: lark-toolkit
description: "Comprehensive Lark/Feishu API skill for OpenClaw agents. Covers all Lark operations via three access paths: claw-lark plugin (message tool), MCP tools (mcporter), and direct Open API (curl). Use when: (1) sending/receiving Lark messages, (2) managing groups or members, (3) listing department users or contacts, (4) creating calendar events, (5) working with docs/bitable/wiki/OKR/tasks, (6) setting up a new Lark bot, (7) debugging webhook/connection issues, (8) any Lark Open API operation the message tool or MCP doesn't support. Covers both Lark International (open.larksuite.com) and Feishu China (open.feishu.cn)."
---

# Lark Toolkit

## Prerequisites & Security

This skill is a **documentation-only** reference guide. It contains no executable code that accesses credentials automatically.

**Required credentials (user-provided, never bundled):**
- **Lark App ID** (`app_id`) — from [Lark Developer Console](https://open.larksuite.com/app)
- **Lark App Secret** (`app_secret`) — from the same console

**How credentials are used:**
- All API examples in SKILL.md use **placeholders** (`<APP_ID>`, `<APP_SECRET>`, `CHAT_ID`, etc.) — no real secrets
- The `scripts/get_token.sh` helper obtains a temporary `tenant_access_token` from Lark's auth API. It reads credentials from (in order):
  1. Command-line arguments
  2. `LARK_APP_ID` / `LARK_APP_SECRET` **environment variables**
  3. **`~/.openclaw/openclaw.json`** (standard OpenClaw config, path `channels.lark.accounts.default.appId/appSecret`)
- The script prints the config source to stderr when falling back to the config file
- **No credentials are hardcoded, cached to disk, logged, or transmitted** beyond the single Lark auth API call
- The token is exported as `LARK_TOKEN` env var for subsequent commands in the same shell session

## Three Access Paths

| Need | Path | When |
|------|------|------|
| Send/receive messages | **claw-lark plugin** (message tool) | Basic text, media, reactions — simplest |
| Structured CRUD ops | **MCP tools** via mcporter | Bitable, calendar, docs, tasks, OKR — 38 tools |
| Everything else | **Direct API** (curl) | Contacts, member mgmt, anything MCP doesn't cover |

**Rule:** claw-lark first → MCP second → direct API as fallback.

## Authentication (Direct API)

```bash
TOKEN=$(curl -s -X POST 'https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")
```

Or use the helper: `bash scripts/get_token.sh`

Token validity: ~2 hours. Cache it.

## API Base URLs

| Platform | API Base | Dev Console |
|----------|----------|-------------|
| **Lark International** | `https://open.larksuite.com/open-apis/` | `https://open.larksuite.com/app` |
| **Feishu (China)** | `https://open.feishu.cn/open-apis/` | `https://open.feishu.cn/app` |

⚠️ Lark ≠ Feishu. Always confirm which platform the tenant uses.

## Common API Patterns

### Send a Message

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"receive_id":"CHAT_ID","msg_type":"text","content":"{\"text\":\"hello\"}"}'
```

### Reply in Thread

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/messages/MSG_ID/reply" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":"{\"text\":\"reply\"}","reply_in_thread":true}'
```

### Add Reaction

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/messages/MSG_ID/reactions" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"reaction_type":{"emoji_type":"THUMBSUP"}}'
```

Emoji types: `THUMBSUP` `HEART` `LAUGH` `OK` `COOL` `FINGERHEART` `SMILE` `JIAYOU`

### List Department Users (MCP gap — direct API only)

```bash
# List root departments
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://open.larksuite.com/open-apis/contact/v3/departments?parent_department_id=0&page_size=50&fetch_child=true'

# List users in a department
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://open.larksuite.com/open-apis/contact/v3/users?department_id=<DEPT_ID>&page_size=50'
```

Key fields: `name`, `open_id`, `employee_type` (1=regular, 2=intern), `department_ids`

### Read Chat History

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://open.larksuite.com/open-apis/im/v1/messages?container_id_type=chat&container_id=<CHAT_ID>&page_size=20&sort_type=ByCreateTimeDesc'
```

### Add Bot to Group

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/chats/<CHAT_ID>/members?member_id_type=app_id" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"id_list":["<BOT_APP_ID>"]}'
```

## MCP Tools (38 available)

```bash
mcporter call lark-mcp.<tool_name> key=value
```

Full catalog with parameters: [references/mcp-tools.md](references/mcp-tools.md)

### MCP Coverage

| Module | Key Tools |
|--------|-----------|
| **Bitable** | create apps/tables, CRUD records, list fields |
| **Calendar** | create/get/patch events, free/busy, primary calendar |
| **Docs** | read content, search, import, set permissions |
| **IM** | create/list groups, get members, send messages, list history |
| **OKR** | batch get, list periods, CRUD progress, query reviews |
| **Report** | query rules/tasks, manage views |
| **Task** | create/patch tasks, add members/reminders |
| **Wiki** | search nodes, get node details |
| **Contacts** | batch get user IDs by email/phone |

### MCP Gaps (use direct API)

- List users by department — `GET /contact/v3/users?department_id=`
- List departments — `GET /contact/v3/departments`
- Add/remove group members — `POST /im/v1/chats/{chat_id}/members`
- Send reactions — `POST /im/v1/messages/{msg_id}/reactions`
- Upload images/files — `POST /im/v1/images` / `POST /im/v1/files`

## Pagination

Most list APIs use cursor-based pagination:

```
?page_size=50&page_token=<token_from_previous_response>
```

Check `has_more` in response.

## Error Handling

| Code | Meaning |
|------|---------|
| 0 | Success |
| 99991663 | Token expired — refresh |
| 99991664 | Token invalid |
| 99991400 | Bad request |
| 99991403 | No permission — check app permissions |

## Critical Pitfalls

1. **Lark ≠ Feishu** — International uses `open.larksuite.com`, China uses `open.feishu.cn`
2. **open_id is per-app** — Same user has different open_id across different Lark apps
3. **Webhook 5s timeout** — Return 200 immediately, process async
4. **Event dedup** — Use `event_id` (Lark retries up to 3x)
5. **Bot-to-bot blind spot** — Lark does NOT push Bot A's messages to Bot B's webhook
6. **Publishing required** — Permission/event changes only take effect after publishing a new app version
7. **ngrok IPv6 trap** — Use `127.0.0.1:PORT` not `localhost:PORT` in ngrok config
8. **ngrok free domain** — Returns interstitial HTML that Lark rejects. Use paid domain.

## Detailed References

- **Bot setup playbook**: [references/bot-setup.md](references/bot-setup.md)
- **API reference**: [references/api-reference.md](references/api-reference.md)
- **MCP tools catalog**: [references/mcp-tools.md](references/mcp-tools.md)
- **Webhook & tunnel**: [references/webhook-setup.md](references/webhook-setup.md)
- **Troubleshooting**: [references/troubleshooting.md](references/troubleshooting.md)
- **Permissions**: [references/permissions.md](references/permissions.md)
