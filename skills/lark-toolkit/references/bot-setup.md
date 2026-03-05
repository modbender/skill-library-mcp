# Lark Bot Setup Playbook

Complete guide: from zero to a working Lark bot.

## 1. Create App

1. Go to https://open.larksuite.com/app (international) or https://open.feishu.cn/app (China)
2. Create enterprise custom app (企业自建应用)
3. Fill name, description, icon
4. Record **App ID** and **App Secret**

## 2. Add Bot Capability

- App Capabilities → Add → Bot (机器人)

## 3. Permissions (Minimum Set)

| Permission | Purpose |
|-----------|---------|
| `im:message` | Send & receive messages (DM + group) |
| `im:message.p2p_msg:readonly` | Read user-to-bot DMs |
| `im:message.group_msg:readonly` | Receive @bot messages in groups |
| `im:message.group_at_msg:readonly` | Receive all group messages |
| `im:chat` | Get/update group info |
| `im:chat.members:write_only` | Manage group members (optional) |

For advanced features, add:
- `calendar:calendar` — Calendar read/write
- `docs:doc` — Docs access
- `bitable:app` — Bitable access
- `task:task` — Task management

## 4. Event Subscription

1. Events & Callbacks → Subscription method: **Developer Server**
2. Set **Request URL**: your webhook endpoint (e.g. `https://yourdomain.com/webhook/event`)
3. Add event: `im.message.receive_v1` (Receive messages v2.0)
4. Encryption: default "no encryption" is fine. If enabled, server must handle AES-256-CBC decryption.

## 5. Set Availability

- Version Management → Create Version → Set availability to "All Employees" (or specific departments)

## 6. Publish

- Enterprise custom apps are usually "review-free"
- Create version → Apply for release
- **⚠️ Must publish a new version whenever permissions or event subscriptions change**

## 7. Network Setup

### Option A: claw-lark Plugin (Recommended for OpenClaw)

Set in `~/.openclaw/openclaw.json`:
```json
{
  "channels": {
    "lark": {
      "accounts": {
        "default": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "connectionMode": "webhook",
          "webhookPort": 3003,
          "domain": "feishu",
          "requireMention": true
        }
      }
    }
  }
}
```

Or use env vars: `LARK_APP_ID`, `LARK_APP_SECRET`, `LARK_ENCRYPT_KEY`, `LARK_VERIFICATION_TOKEN`

### Option B: Standalone Webhook Server

Build a Node.js/Python HTTP server that:
1. Handles URL challenge verification (`type: "url_verification"` → return `{ challenge }`)
2. Returns 200 immediately on event receipt (process async)
3. Deduplicates events by `event_id`
4. Ignores its own messages (check `sender.open_id`)
5. Caches `tenant_access_token` (~2h validity)

### Tunnel Setup (ngrok)

```yaml
# ngrok.yml
tunnels:
  lark:
    proto: http
    addr: 127.0.0.1:3003  # ⚠️ Use 127.0.0.1, NOT localhost
    domain: yourdomain.ngrok-free.app  # Paid domain recommended
```

**⚠️ Free ngrok domains** return interstitial HTML that Lark rejects as webhook failure.

## 8. Add Bot to Groups

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/chats/{chat_id}/members?member_id_type=app_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_list":["cli_bot_app_id"]}'
```

## 9. Initialize DM

Bot doesn't appear in user's message list until it sends the first message:

```bash
curl -X POST "https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id":"USER_OPEN_ID","msg_type":"text","content":"{\"text\":\"Hello! I am ready.\"}"}'
```

## Quick Checklist

- [ ] Create app, record App ID + Secret
- [ ] Add bot capability
- [ ] Grant minimum permissions
- [ ] Add event subscription `im.message.receive_v1`
- [ ] Set webhook URL
- [ ] Publish new version
- [ ] Set up tunnel (ngrok) with correct port
- [ ] Add bot to target groups
- [ ] Send initial DM to users
- [ ] Test: human message → bot response
