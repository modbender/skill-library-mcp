---
name: stringclaw
description: "Make real phone calls to your users via Stringclaw voice AI"
version: 0.0.1
metadata:
  openclaw:
    emoji: "📞"
    primaryEnv: "STRINGCLAW_API_KEY"
    requires:
      env: ["STRINGCLAW_API_KEY"]
      bins: ["stringclaw-bridge"]
    install:
      - kind: node
        package: "@stringclaw/bridge"
        bins: ["stringclaw-bridge"]
---

## stringclaw

Make real phone calls to your users via Stringclaw.

When a user asks you to call them (e.g. "give me a call", "call me", "phone me"),
use this skill to initiate an outbound voice call. The call connects them to a
live voice session with you — your full tools and memory are available during the call.

### Before making a call

The Stringclaw bridge must be running on the host machine. It connects your local
OpenClaw agent to Stringclaw's voice infrastructure.

Check if it's already running:
```
pgrep -f stringclaw-bridge
```

If not running, start it in the background:
```
STRINGCLAW_API_KEY=$STRINGCLAW_API_KEY stringclaw-bridge &
```

The bridge will keep running until the process is stopped.

### Making a call

Send a POST request:

```
POST https://exciting-ptarmigan-223.convex.cloud/api/call
Authorization: Bearer $STRINGCLAW_API_KEY
Content-Type: application/json

{
  "phoneNumber": "+1234567890"
}
```

The `phoneNumber` field is optional — if omitted, the call goes to the number
configured in the user's Stringclaw dashboard.

### Response

**Success (200):**
```json
{ "success": true, "callId": "..." }
```

**Errors:**
- `401` — Invalid or missing API key
- `402` — No minutes remaining. Tell the user to top up at stringclaw.com
- `400` — No phone number provided and none configured

### Example

User: "Hey, can you give me a call?"

1. Ensure the bridge is running (check with `pgrep`, start if needed).
2. Call the Stringclaw API with the user's phone number (if known) or without it.
3. If successful, reply: "Calling you now! Pick up in a moment."
4. If 402, reply: "You're out of Stringclaw minutes. Top up at stringclaw.com."
