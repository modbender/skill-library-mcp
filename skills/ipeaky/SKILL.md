---
name: ipeaky
description: Secure API key management for OpenClaw. Store, list, test, and delete API keys without exposing them in chat history. Keys are stored directly in openclaw.json via gateway config.patch — fully native integration. Use when a user needs to provide, manage, or test API keys (e.g., OpenAI, ElevenLabs, Anthropic, Brave, or any service). Triggers on phrases like "add API key", "store my key", "manage keys", "test my key", "set up API key", or when a skill requires an API key that isn't configured.
metadata:
  openclaw:
    platforms: [macos]
    requires:
      bins: [osascript]
    notes: "Secure input popup requires macOS (osascript). Linux/Windows users can pipe keys via stdin directly."
---

# ipeaky — Secure API Key Management

Keys are stored **directly in OpenClaw's native config** (`openclaw.json`) via `gateway config.patch`.
This means every skill that declares `primaryEnv` automatically picks up the key — zero manual wiring.

## Key Map — Service to Config Path

| Service | Config Path | primaryEnv |
|---------|------------|------------|
| OpenAI | `skills.entries.openai-whisper-api.apiKey` | OPENAI_API_KEY |
| ElevenLabs | `skills.entries.sag.apiKey` | ELEVENLABS_API_KEY |
| Brave Search | `tools.web.search.apiKey` | BRAVE_API_KEY |
| Gemini | `skills.entries.nano-banana-pro.apiKey` | GEMINI_API_KEY |
| Google Places | `skills.entries.goplaces.apiKey` | GOOGLE_PLACES_API_KEY |
| Notion | `skills.entries.notion.apiKey` | NOTION_API_KEY |
| ElevenLabs Talk | `talk.apiKey` | (direct) |
| Custom skill | `skills.entries.<skill-name>.apiKey` | (per skill) |
| Custom env | `skills.entries.<skill-name>.env.<VAR_NAME>` | (arbitrary) |

**Important:** Some keys serve multiple skills. OpenAI key is used by `openai-whisper-api`,
`openai-image-gen`, etc. ElevenLabs key is used by `sag` and `talk`. When storing, set ALL
relevant config paths for that key.

## Storing Keys (v4 — Single Paste, Zero Exposure) ⭐ PREFERRED

One popup. Paste everything. Regex parses. One save. One restart. Keys never touch chat or network.

```bash
bash {baseDir}/scripts/store_key_v4.sh "<SERVICE_NAME>" "<config_prefix>"
```

### Examples:
```bash
# X API keys (consumer key + secret + bearer in one paste)
bash {baseDir}/scripts/store_key_v4.sh "X API" "skills.entries.x-twitter.env"

# Any service — user pastes in any format:
#   consumer key: abc123
#   secret: xyz789
#   bearer token: AAAA...
```

The script:
1. Shows ONE macOS popup — user pastes all keys in any format
2. Local Python regex parses key-value pairs (no AI, no network)
3. Confirmation popup: "Found 3 keys: X, Y, Z — Store all?"
4. ONE `openclaw config set` batch → ONE gateway restart
5. Keys never appear in chat, logs, or shell history

### Supported input formats:
- `key_name: value` or `key_name = value`
- `KEY_NAME=value`
- Bare tokens on separate lines (auto-labeled in order)
- Mixed formats in one paste

---

## Storing a Key (v3 — Zero Exposure)

**Use the v3 script.** The agent NEVER sees the key. The script handles popup + storage directly.

```bash
bash {baseDir}/scripts/store_key_v3.sh "<SERVICE_NAME>" "<config_path1>" ["<config_path2>" ...]
```

### Examples:
```bash
# Brave Search
bash {baseDir}/scripts/store_key_v3.sh "Brave Search" "tools.web.search.apiKey"

# OpenAI (multiple paths)
bash {baseDir}/scripts/store_key_v3.sh "OpenAI" "skills.entries.openai-whisper-api.apiKey"

# ElevenLabs (sag + talk)
bash {baseDir}/scripts/store_key_v3.sh "ElevenLabs" "skills.entries.sag.apiKey" "talk.apiKey"
```

The script:
1. Shows macOS popup (hidden input)
2. Calls `openclaw config set` for each path
3. Restarts gateway
4. Returns ONLY "OK" or "ERROR" — key never appears in agent output or chat history

### Legacy Method (v2 — agent sees key, NOT recommended)

**Step 1:** Launch the secure input popup. On macOS:
```bash
bash {baseDir}/scripts/secure_input_mac.sh KEY_NAME
```

**Step 2:** Once you have the key value (from stdout of the script), store it via gateway config.patch.

Example for OpenAI:
```
gateway config.patch with raw: {"skills":{"entries":{"openai-whisper-api":{"apiKey":"THE_KEY"},"openai-image-gen":{"apiKey":"THE_KEY"}}}}
```

Example for ElevenLabs:
```
gateway config.patch with raw: {"skills":{"entries":{"sag":{"apiKey":"THE_KEY"}}},"talk":{"apiKey":"THE_KEY"}}
```

Example for Brave Search:
```
gateway config.patch with raw: {"tools":{"web":{"search":{"apiKey":"THE_KEY"}}}}
```

**Critical rules:**
- NEVER echo, print, or include any key value in chat messages or tool call arguments
- NEVER include key values in the `reason` field of config.patch
- If a user pastes a key directly in chat, store it immediately and tell them to delete the message
- The secure_input_mac.sh script outputs the key to stdout — capture it in a variable, use it in config.patch, never log it

## Listing Keys

Read from the live config using `gateway config.get`. Show masked values only (first 4 chars + ****).
Parse the config JSON and find all `apiKey` fields, display their config path and masked value.

## Testing a Key

Test endpoints:
- **OpenAI**: `curl -s -H "Authorization: Bearer $KEY" https://api.openai.com/v1/models | head`
- **ElevenLabs**: `curl -s -H "xi-api-key: $KEY" https://api.elevenlabs.io/v1/user`
- **Anthropic**: `curl -s -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" https://api.anthropic.com/v1/messages -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}'`
- **Brave Search**: `curl -s -H "X-Subscription-Token: $KEY" "https://api.search.brave.com/res/v1/web/search?q=test&count=1"`

Source the key from the config (via gateway config.get), test it, report result. Never show the key.

## Deleting a Key

Use `gateway config.patch` to set the key value to an empty string or remove the entry.

## 💎 Paid Tier (Coming Soon)

ipeaky core is free forever. A paid tier is in development with premium features:

- **Team key sharing** — Role-based access across team members
- **Key rotation reminders** — Automated expiry alerts
- **Usage analytics** — Track key usage across skills
- **Breach monitoring** — Leak database notifications
- **Cross-platform** — Linux & Windows secure input
- **Backup & sync** — Encrypted cloud backup

See `paid_tier/README-paid.md` for details. Billing is powered by Stripe.

```bash
# Set up Stripe integration (uses ipeaky to store its own key!)
bash {baseDir}/paid_tier/stripe-setup.sh

# Create a checkout session
bash {baseDir}/paid_tier/stripe-checkout.sh --price price_XXXXX --mode subscription
```

## Security Guarantees

- Keys go: secure popup → stdout pipe → config.patch → openclaw.json (never chat)
- Keys are automatically available to all skills via OpenClaw's native env injection
- No separate credential files to manage
- No manual `source` commands needed
- config.patch triggers a gateway reload so keys take effect immediately
