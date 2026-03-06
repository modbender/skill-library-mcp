# Patch Details

## Lessons Learned (Do NOT Repeat These Mistakes)

### Event Path
- ❌ `event.event.message` → keys are empty, nothing works
- ✅ `event.message` → correct path in claw-lark's webhook handler

### Mention Detection
- ❌ `/@_user_\d+/.test(rawText)` → ALL bot @'s have placeholders, not just ours
- ❌ `!m.id.user_id` → ALL bots have empty user_id
- ✅ Exact match `m.id.open_id === BOT_OPEN_ID`

### Thread Reply
- ❌ `client.im.message.create()` + `root_id` → only associates, doesn't create thread
- ❌ `thread_id` as `receive_id` → 400 error
- ✅ `client.im.message.reply()` + `reply_in_thread: true` → creates thread

### Code Paths
- `sendTextMessage` in provider.js is the ACTUAL send function (not send.js's `sendMessageLark`)
- monitor.js deliver callback ALSO has its own send logic (bypasses provider.js)
- Both need to be patched independently

## Bot Identity
- App ID: `cli_a91a798291789ed4`
- Bot name: 霄子在呢
- Bot open_id: `ou_e5c78e1c33641591d76db4e60877b018`
- Get via: `GET /bot/v3/info` with tenant_access_token

## File Locations
- `~/.openclaw/extensions/claw-lark/dist/src/monitor.js`
- `~/.openclaw/extensions/claw-lark/dist/src/provider.js`
- `~/.openclaw/extensions/claw-lark/dist/src/send.js`
