# Lark Troubleshooting

Battle-tested fixes from real production issues.

## Messages Not Arriving

**Symptom:** Bot webhook is running, but no messages come through.

**Check order:**
1. **Tunnel target port** — `curl http://127.0.0.1:4040/api/tunnels | jq` → verify the `config.addr` port matches the actual webhook port
2. **Webhook server listening** — `lsof -i :PORT` → confirm the gateway process owns it
3. **Competing processes** — A standalone webhook server (e.g. old `lark-bot-gateway.js`) may be occupying the port. Kill it and unload its LaunchAgent
4. **ngrok domain** — Free domains serve interstitial pages. Use paid domain
5. **App version** — Did you publish a new version after changing event subscriptions?
6. **Lark developer console** — Check event subscription status, look for red "FAIL" markers

## EADDRINUSE Loop

**Symptom:** Logs show `auto-restart attempt X/10` + `EADDRINUSE` on webhook port.

**Causes:**
- Another process on the same port (`lsof -i :PORT` to check)
- claw-lark auto-restart bug (monitorLarkProvider resolves immediately in webhook mode)

**Fix:**
1. Kill competing process: `kill PID && launchctl unload ~/Library/LaunchAgents/com.xxx.plist`
2. Apply the pending-promise fix in `monitor.js` (see [webhook-setup.md](webhook-setup.md))
3. Restart gateway: `openclaw gateway restart`

## Bot Doesn't Respond in Groups

**Symptom:** Bot works in DM but ignores group messages.

**Check:**
- `requireMention: true` in config → bot only responds when @mentioned
- Mention detection: check that `message.mentions` array contains bot's `open_id`
- Fallback: if mentions array is empty, check text for `@BotName`
- Bot must be a group member (not just invited but not added)

## Reply Not Creating Thread

**Symptom:** Reply goes to main chat instead of creating/continuing a thread.

**Fix:** Use the reply API with `reply_in_thread`:
```bash
POST /im/v1/messages/{message_id}/reply
{
  "msg_type": "text",
  "content": "{\"text\":\"reply\"}",
  "reply_in_thread": true    # boolean true, NOT just root_id
}
```

**Common mistake:** Using `im/v1/messages` (create) with `root_id` instead of the reply endpoint. `root_id` only threads an existing conversation, it doesn't create a new thread.

## Media Download Fails

**Symptom:** Bot receives image/file message but can't download the media.

**Check:**
- For images: `GET /im/v1/messages/{msg_id}/resources/{image_key}?type=image`
- For files: `GET /im/v1/messages/{msg_id}/resources/{file_key}?type=file`
- ⚠️ The `type` parameter must be `"image"` or `"file"` — passing `"audio"` or other values returns 400
- Verify permissions: `im:message` scope must be granted

## Token Expired

**Symptom:** API returns `code: 99991663` or `code: 99991664`

**Fix:** Re-fetch `tenant_access_token`. Cache for no more than 1.5 hours (actual validity ~2h, but buffer for safety):
```bash
curl -s https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id":"$APP_ID","app_secret":"$APP_SECRET"}'
```

## open_id Mismatch

**Symptom:** Sending messages to a user fails with "user not found" or message goes to wrong person.

**Root cause:** `open_id` is **per-app**. The same user has different open_ids for different Lark apps.

**Fix:** Get the open_id from the current app's perspective:
- From group member list: `GET /im/v1/chats/{chat_id}/members`
- From contacts: `POST /contact/v3/users/batch_get_id` with email or phone
- From incoming message: `event.sender.sender_id.open_id`

## Webhook Challenge Fails

**Symptom:** Lark developer console shows webhook verification failed.

**Check:**
1. Server must handle `POST` with `{"type":"url_verification","challenge":"xxx"}` → respond `{"challenge":"xxx"}`
2. If encryption is enabled, decrypt the payload first
3. Response must be JSON with correct Content-Type
4. Must respond within 5 seconds
5. Test locally: `curl -X POST http://127.0.0.1:PORT/ -d '{"type":"url_verification","challenge":"test"}' -H "Content-Type: application/json"`

## Lark vs Feishu Confusion

| | Lark (International) | Feishu (China) |
|--|---------------------|----------------|
| API | `open.larksuite.com` | `open.feishu.cn` |
| Web | `oa.larksuite.com` | `www.feishu.cn` |
| SDK domain | `"feishu"` (yes, even for Lark) | `"feishu"` |
| OpenClaw plugin | `claw-lark` | `claw-lark` (same) |

⚠️ Don't use `@openclaw/feishu` — that's a different (and possibly outdated) package. Use `claw-lark`.
