# Webhook & Tunnel Setup

## Connection Modes

Lark supports two modes for receiving events:

### WebSocket (Enterprise)
- Long-lived connection, no public URL needed
- Set `connectionMode: "websocket"` in claw-lark config
- Requires enterprise-level app permissions
- `monitorLarkProvider` blocks on `wsClient.start()` — correct behavior

### Webhook (Individual/Standard)
- HTTP POST callbacks to your server
- Requires public URL (tunnel or cloud server)
- Set `connectionMode: "webhook"` and `webhookPort: 3003` in claw-lark config

## claw-lark Plugin Configuration

In `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "lark": {
      "accounts": {
        "default": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "encryptKey": "optional_encrypt_key",
          "verificationToken": "optional_token",
          "connectionMode": "webhook",
          "webhookPort": 3003,
          "domain": "feishu",
          "dmPolicy": "pairing",
          "groupPolicy": "open",
          "requireMention": true,
          "renderMode": "auto",
          "historyLimit": 10
        }
      }
    }
  }
}
```

**Key settings:**
- `domain`: `"feishu"` for both Lark international and Feishu China (it's the SDK domain, not the API domain)
- `requireMention`: `true` = only respond when @mentioned in groups
- `renderMode`: `"auto"` = card for code/tables, text otherwise; `"card"` = always card; `"text"` = always text

## ngrok Tunnel

### Configuration

```yaml
# ~/Library/Application Support/ngrok/ngrok.yml (macOS)
# ~/.config/ngrok/ngrok.yml (Linux)
tunnels:
  lark:
    proto: http
    addr: 127.0.0.1:3003   # ⚠️ MUST match webhookPort
    domain: yourdomain.ngrok-free.app
```

### Critical Rules

1. **Use `127.0.0.1`** not `localhost` — localhost may resolve to IPv6 `[::1]` which Node.js HTTP server on `0.0.0.0` won't accept
2. **Port must match** — ngrok target port MUST equal claw-lark `webhookPort`. Mismatch = silent message loss (messages go to wrong port, nobody responds, Lark retries 3x then gives up)
3. **Use paid domain** — Free ngrok domains return interstitial HTML pages. Lark's webhook validator receives HTML instead of JSON challenge response → permanent FAIL
4. **One tunnel per port** — Don't run multiple tunnels to the same port

### Verify Tunnel

```bash
# Check ngrok tunnels
curl -s http://127.0.0.1:4040/api/tunnels | jq '.tunnels[] | {name, public_url, config}'

# Test webhook endpoint
curl -X POST http://127.0.0.1:3003/ -d '{"type":"url_verification","challenge":"test"}' -H "Content-Type: application/json"
# Should return: {"challenge":"test"}
```

## Webhook Server Internals

The claw-lark webhook server handles:

1. **URL Challenge** — `POST` with `type: "url_verification"` → return `{ challenge }`
2. **Encrypted events** — If `encryptKey` is set, decrypt AES-256-CBC before processing
3. **Token verification** — Check `header.token` matches `verificationToken` (if configured)
4. **Event routing** — `im.message.receive_v1` → parse message → route to agent

### Message Types Handled

| msg_type | Parsed as |
|----------|-----------|
| `text` | Plain text (preserves @mentions) |
| `post` | Rich text flattened to text |
| `image` | `[Sent an image]` + downloads image_key |
| `file` | `[Sent file: name]` + downloads file_key |
| `audio` | `[Sent audio message]` + downloads as file |
| `media` | `[Sent media: name]` + downloads |
| `sticker` | `[Sent a sticker]` |

## Multi-Bot Architecture (Advanced)

When running multiple bots behind one ngrok tunnel, use a proxy for path-based routing:

```
ngrok → proxy.js (port 3001)
  ├─ /bot-a/*    → Bot A server (port 3002)
  ├─ /bot-b/*    → Bot B server (port 3004)
  └─ default     → claw-lark (port 3003)
```

**Bot-to-bot limitation:** Lark does NOT push Bot A's group messages to Bot B's webhook. Implement local HTTP bridge (`/relay` endpoint) for bot-to-bot communication.

## Auto-Restart Bug (claw-lark ≤ 2026-02)

**Symptom:** Gateway logs show `auto-restart attempt X/10` + `EADDRINUSE` on the webhook port, even though the webhook is actually running fine.

**Root cause:** `monitorLarkProvider()` in webhook mode starts the HTTP server and returns immediately. Gateway interprets the resolved promise as "channel exited" and triggers auto-restart loop. Each restart attempt tries to bind the same port → EADDRINUSE.

**Fix:** In `claw-lark/dist/src/monitor.js`, replace the webhook section to return a promise that stays pending until the abort signal fires:

```javascript
// Return pending promise to prevent gateway auto-restart
return new Promise((resolve) => {
    if (abortSignal) {
        abortSignal.addEventListener("abort", () => {
            webhookServer.stop();
            resolve();
        }, { once: true });
    }
});
```
