---
name: govee-control
description: Script-free Govee OpenAPI setup and control guide. Use when the user wants to get a Govee API key, connect Govee, list devices, check state, or send power/brightness/color commands with secure key handling.
metadata:
  clawdbot:
    emoji: 💡
    requires:
      bins:
        - bash
        - curl
      env:
        - GOVEE_API_KEY
    primaryEnv: GOVEE_API_KEY
---

# Govee OpenAPI (No Scripts)

Control Govee devices using manual `curl` commands only.

## Linux System Requirements

- Linux shell with `bash` available.
- `curl` installed.
- Internet access to `https://developer-api.govee.com` and `https://developer.govee.com`.
- Govee account with supported devices linked.
- Optional: `jq` for pretty-printing JSON responses.

Quick check:

```bash
bash --version | head -n 1
curl --version | head -n 1
command -v jq >/dev/null && jq --version || echo "jq not installed (optional)"
```

## Required Credential

- `GOVEE_API_KEY` (required)

## Autonomous Use Guardrails

- Only read `GOVEE_API_KEY` from your chosen per-user secrets file.
- Do not read unrelated secret files or system credentials.
- Restrict outbound requests to:
  - `https://developer-api.govee.com`
  - `https://developer.govee.com`
- Ask before controlling multiple devices or performing bulk changes.

## Get a Govee API Key

1. Open `https://developer.govee.com/`.
2. Sign in with the same Govee account that owns your devices.
3. Go to the API key section in the developer console.
4. Generate/apply for a key and copy it.
5. Keep it private (treat it like a password).

If the portal UI changes, use the same flow: sign in to Govee Developer → find API key management → create key.

## Secure Local Storage (Per-User)

Never store API keys in skill files, git, or chat logs.

Create a per-user secrets file (avoid `/root` unless intentionally running as root):

```bash
mkdir -p "$HOME/.openclaw/secrets"
cat > "$HOME/.openclaw/secrets/govee.env" <<'EOF'
export GOVEE_API_KEY='<YOUR_API_KEY>'
EOF
chmod 600 "$HOME/.openclaw/secrets/govee.env"
```

Load only this variable into the current shell (no `set -a`):

```bash
source "$HOME/.openclaw/secrets/govee.env"
```

## API Base URL

```bash
https://developer-api.govee.com/v1
```

## Discover Devices First

Before controlling lights, list devices and copy your own `device` + `model`:

```bash
curl -sS -X GET "https://developer-api.govee.com/v1/devices" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json"
```

## View Device State

```bash
curl -sS -X GET "https://developer-api.govee.com/v1/devices/state?device=<DEVICE>&model=<MODEL>" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json"
```

## Control Commands

### Turn on

```bash
curl -sS -X PUT "https://developer-api.govee.com/v1/devices/control" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"device":"<DEVICE>","model":"<MODEL>","cmd":{"name":"turn","value":"on"}}'
```

### Turn off

```bash
curl -sS -X PUT "https://developer-api.govee.com/v1/devices/control" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"device":"<DEVICE>","model":"<MODEL>","cmd":{"name":"turn","value":"off"}}'
```

### Brightness (1-100)

```bash
curl -sS -X PUT "https://developer-api.govee.com/v1/devices/control" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"device":"<DEVICE>","model":"<MODEL>","cmd":{"name":"brightness","value":75}}'
```

### RGB color

```bash
curl -sS -X PUT "https://developer-api.govee.com/v1/devices/control" \
  -H "Govee-API-Key: $GOVEE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"device":"<DEVICE>","model":"<MODEL>","cmd":{"name":"color","value":{"r":120,"g":180,"b":255}}}'
```

## Response Check

Success usually returns:

```json
{"code":200,"message":"Success"}
```

If `code` is not `200`, treat it as failure.

## Troubleshooting

- `401` / unauthorized: key missing, expired, or invalid.
- `429` / rate limit: slow retries.
- command rejected: model does not support that command (`supportCmds`).
- empty device list: account has no supported linked devices.

## Safety Rules

- Use placeholders in docs only (`<DEVICE>`, `<MODEL>`, `<YOUR_API_KEY>`).
- Do not include real keys or device IDs in published artifacts.
- Prefer one-device-at-a-time actions over bulk changes.
- Avoid pasting API keys into chat.
