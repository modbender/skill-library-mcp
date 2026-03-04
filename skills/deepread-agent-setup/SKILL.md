---
name: deepread-agent-setup
title: DeepRead Agent Setup
description: Authenticate AI agents with the DeepRead OCR API using OAuth device flow. The agent displays a code, the user approves it in their browser, and the agent receives a DEEPREAD_API_KEY stored as an environment variable.
disable-model-invocation: true
metadata:
  {"openclaw":{"produces":{"env":["DEEPREAD_API_KEY"]},"homepage":"https://www.deepread.tech"}}
---

# DeepRead Agent Setup

Authenticate AI agents with the DeepRead OCR API using the **OAuth 2.0 Device Authorization Flow** (RFC 8628). After setup, the agent has a `DEEPREAD_API_KEY` environment variable and can use the [DeepRead OCR skill](https://clawhub.ai/deepread-tech/deepread).

## How It Works

The device flow lets headless agents (no browser) authenticate securely:

```
Agent requests device code  →  User opens URL in browser  →  User approves  →  Agent receives API key
```

1. Agent calls `POST https://api.deepread.tech/v1/agent/device/code` to get a `device_code` and `user_code`
2. Agent displays the `user_code` and a verification URL to the user
3. User opens the URL in their browser, logs in, and enters the code
4. Agent polls `POST https://api.deepread.tech/v1/agent/device/token` until the user approves
5. Agent receives an `api_key` (prefixed `sk_live_`) and stores it as the `DEEPREAD_API_KEY` environment variable

**Only domain contacted:** `api.deepread.tech`

## Prerequisites

- A DeepRead account (free at https://www.deepread.tech/dashboard/?utm_source=clawdhub)
- Internet access to reach `api.deepread.tech`

## Setup Instructions

### Step 1: Request a Device Code

```bash
curl -s -X POST https://api.deepread.tech/v1/agent/device/code \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "my-ai-agent"}'
```

The `agent_name` field is optional — it is shown on the approval screen so the user knows which agent is requesting access.

**Response:**
```json
{
  "device_code": "GmRhmhcxhZAzk...EeNu5OfKhL79MQgN",
  "user_code": "WDJB-MJHT",
  "verification_uri": "https://www.deepread.tech/activate",
  "verification_uri_complete": "https://www.deepread.tech/activate?code=WDJB-MJHT",
  "expires_in": 900,
  "interval": 5
}
```

**Tell the user** (using the values from the response — they change every time):
> Open **{verification_uri}** and enter code **{user_code}**
>
> Or open this direct link: **{verification_uri_complete}**

### Step 2: Poll for Approval

Poll every `interval` seconds (default: 5) until the user approves:

```bash
curl -s -X POST https://api.deepread.tech/v1/agent/device/token \
  -H "Content-Type: application/json" \
  -d '{"device_code": "GmRhmhcxhZAzk...EeNu5OfKhL79MQgN"}'
```

**While waiting (user hasn't approved yet):**
```json
{
  "error": "authorization_pending",
  "api_key": null,
  "key_prefix": null
}
```

**After user approves:**
```json
{
  "error": null,
  "api_key": "sk_live_abc123def456...",
  "key_prefix": "sk_live_abc123de"
}
```

**The `api_key` is returned exactly once.** The next poll after retrieval will return `expired_token`. Save it immediately.

**If user denied:**
```json
{
  "error": "access_denied",
  "api_key": null,
  "key_prefix": null
}
```

**If code expired (15 minutes):**
```json
{
  "error": "expired_token",
  "api_key": null,
  "key_prefix": null
}
```

### Step 3: Store the API Key

Once you receive the `api_key`, set it for the current session:

```bash
export DEEPREAD_API_KEY="<api_key from response>"
```

**To persist across sessions, the user should choose one of these options:**

| Method | Command | Security |
|---|---|---|
| **Secrets manager (recommended)** | Use your OS keychain, 1Password CLI, or `pass` | Encrypted at rest |
| **Shell profile** | User manually adds `export DEEPREAD_API_KEY="..."` to `~/.zshrc` | Plaintext file — readable by local processes |

**Important:**
- The agent should set the env var for the current session only (`export`)
- Persistence is the **user's choice** — do not automatically write to shell profiles
- Never commit the key to source control or write it to project files
- The key prefix `sk_live_` confirms it is a valid DeepRead production key

### Step 4: Verify the Key Works

Submit a test document to confirm the key is valid:

```bash
curl -s -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@test.pdf"
```

A successful response returns a job ID confirming the key works:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

If the key is invalid you will get a `401 Unauthorized` response.

## Complete Flow (All Steps)

```bash
#!/bin/bash
# DeepRead Device Flow — complete example

# 1. Request device code
RESPONSE=$(curl -s -X POST https://api.deepread.tech/v1/agent/device/code \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "my-ai-agent"}')

DEVICE_CODE=$(echo "$RESPONSE" | jq -r '.device_code')
USER_CODE=$(echo "$RESPONSE" | jq -r '.user_code')
VERIFY_URI=$(echo "$RESPONSE" | jq -r '.verification_uri')
VERIFY_URI_COMPLETE=$(echo "$RESPONSE" | jq -r '.verification_uri_complete')
INTERVAL=$(echo "$RESPONSE" | jq -r '.interval')

echo "Open $VERIFY_URI and enter code: $USER_CODE"
echo "Or open directly: $VERIFY_URI_COMPLETE"

# 2. Poll for token
while true; do
  TOKEN_RESPONSE=$(curl -s -X POST https://api.deepread.tech/v1/agent/device/token \
    -H "Content-Type: application/json" \
    -d "{\"device_code\": \"$DEVICE_CODE\"}")

  ERROR=$(echo "$TOKEN_RESPONSE" | jq -r '.error // empty')

  if [ -z "$ERROR" ]; then
    export DEEPREAD_API_KEY=$(echo "$TOKEN_RESPONSE" | jq -r '.api_key')
    echo "Authenticated. DEEPREAD_API_KEY is set for this session."
    break
  elif [ "$ERROR" = "authorization_pending" ]; then
    sleep "$INTERVAL"
  elif [ "$ERROR" = "slow_down" ]; then
    INTERVAL=$((INTERVAL + 5))
    sleep "$INTERVAL"
  else
    echo "Error: $ERROR"
    exit 1
  fi
done
```

## Endpoints Used

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `https://api.deepread.tech/v1/agent/device/code` | POST | None | Request device code + user code |
| `https://api.deepread.tech/v1/agent/device/token` | POST | None | Poll for API key after user approval |
| `https://www.deepread.tech/activate` | — | Browser | User opens this URL to enter the code and approve |

**No other endpoints are contacted by this skill.**

## Troubleshooting

### "authorization_pending" keeps repeating
The user hasn't approved yet. Keep polling. The code expires after 15 minutes (`expires_in: 900`).

### "expired_token"
The device code expired before the user approved, or the API key was already retrieved (one-time retrieval). Start over from Step 1.

### "slow_down"
You're polling too fast. Increase the polling interval by 5 seconds.

### "access_denied"
The user clicked Deny on the approval screen. Start over from Step 1 if the user wants to retry.

### Key doesn't work after export
Ensure the shell session was not restarted. If persisting to `~/.zshrc`, run `source ~/.zshrc` to reload.

### "DEEPREAD_API_KEY not set"
The environment variable was not persisted. Re-run the device flow or manually set:
```bash
export DEEPREAD_API_KEY="sk_live_your_key_here"
```

## Security Notes

- The device flow follows [RFC 8628](https://datatracker.ietf.org/doc/html/rfc8628)
- The `user_code` is short-lived (15 minutes) and single-use
- The `api_key` is returned exactly once — subsequent polls return `expired_token`
- All communication is over HTTPS
- The agent sets `DEEPREAD_API_KEY` for the current session only — it does not write to disk
- For long-term storage, prefer a secrets manager (OS keychain, 1Password CLI, `pass`) over plaintext shell profiles
- Never commit the key to source control or write it to project files
- The agent never sees the user's password

## Support

- **Dashboard**: https://www.deepread.tech/dashboard
- **Issues**: https://github.com/deepread-tech/deep-read-service/issues
- **Email**: hello@deepread.tech
