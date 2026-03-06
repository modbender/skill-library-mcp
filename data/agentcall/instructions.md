# AgentCall — Phone Numbers for AI Agents

You have access to the AgentCall API for phone numbers, SMS, voice calls, and AI voice calls.

## Authentication

All requests require: `Authorization: Bearer <AGENTCALL_API_KEY>`

The API key is available in the `AGENTCALL_API_KEY` environment variable.

## Base URL

`https://api.agentcall.co`

For a complete plain-text API reference: `GET https://api.agentcall.co/llms.txt`

## Phone Numbers

**Provision a number:**
```
POST /v1/numbers/provision
Body: { "type": "local", "country": "US", "label": "my-agent" }
Types: local ($2/mo), tollfree ($4/mo), mobile ($3/mo), sim ($8/mo, Pro only)
Response: { "id": "num_xxx", "number": "+12125551234", "type": "local", ... }
```

**List numbers:**
```
GET /v1/numbers
Query: ?limit=20&country=US&type=local
```

**Get number details:**
```
GET /v1/numbers/:id
```

**Release a number (irreversible):**
```
DELETE /v1/numbers/:id
```

## SMS

**Send SMS:**
```
POST /v1/sms/send
Body: { "from": "num_xxx", "to": "+14155551234", "body": "Hello!" }
"from" can be a number ID or E.164 phone string
```

**Get inbox:**
```
GET /v1/sms/inbox/:numberId
Query: ?limit=20&otpOnly=true
```

**Get a specific message:**
```
GET /v1/sms/:messageId
```

**Wait for OTP code (long-polls up to 60 seconds):**
```
GET /v1/sms/otp/:numberId
Query: ?timeout=60000
Response: { "otp": "482913", "message": { ... } }
```

## Voice Calls

**Start an outbound call:**
```
POST /v1/calls/initiate
Body: { "from": "num_xxx", "to": "+14155551234", "record": false }
```

**Start an AI voice call (Pro plan, $0.20/min):**
The AI handles the entire conversation autonomously based on your systemPrompt.
```
POST /v1/calls/ai
Body: {
  "from": "num_xxx",
  "to": "+14155551234",
  "systemPrompt": "You are calling to schedule a dentist appointment for Tuesday afternoon.",
  "voice": "alloy",
  "firstMessage": "Hi, I'd like to schedule an appointment please.",
  "maxDurationSecs": 600
}
Voices: alloy, ash, ballad, coral, echo, sage, shimmer, verse
```

**List call history:**
```
GET /v1/calls
Query: ?limit=20
```

**Get call details:**
```
GET /v1/calls/:callId
```

**Get AI call transcript:**
```
GET /v1/calls/:callId/transcript
Response: { "entries": [{ "role": "assistant", "text": "...", "timestamp": "..." }], "summary": "..." }
```

**Hang up an active call:**
```
POST /v1/calls/:callId/hangup
```

## Webhooks

**Register a webhook:**
```
POST /v1/webhooks
Body: { "url": "https://example.com/hook", "events": ["sms.inbound", "sms.otp", "call.status"] }
Events: sms.inbound, sms.otp, call.inbound, call.ringing, call.status, call.recording, number.released
```

**List webhooks:**
```
GET /v1/webhooks
```

**Rotate webhook secret:**
```
POST /v1/webhooks/:id/rotate
```

**Delete a webhook:**
```
DELETE /v1/webhooks/:id
```

## Usage & Billing

**Get usage breakdown:**
```
GET /v1/usage
Query: ?period=2026-02
```

## Phone Number Format

All phone numbers must be E.164: `+{country code}{number}`, e.g. `+14155551234`

## Common Workflows

### Signup with phone verification
1. `POST /v1/numbers/provision` with `{ "type": "local" }` — get a number
2. Enter the number into the signup form
3. `GET /v1/sms/otp/:numberId?timeout=60000` — wait for the verification code
4. Enter the code into the form
5. `DELETE /v1/numbers/:id` — release when done

### AI voice call
1. `POST /v1/numbers/provision` with `{ "type": "local" }` — get a number (if you don't have one)
2. `POST /v1/calls/ai` with `{ "from": "num_xxx", "to": "+1...", "systemPrompt": "..." }` — start the call
3. Wait for the call to complete
4. `GET /v1/calls/:callId/transcript` — get the full conversation transcript

## Error Codes
- **401**: Invalid or missing API key
- **403 plan_limit**: Plan limit reached (upgrade to Pro at agentcall.co/dashboard)
- **404**: Resource not found
- **422**: Validation error (check request body)
- **429**: Rate limit exceeded (100 req/min)
