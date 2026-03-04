---
name: Keys
description: Secure API key management with broker. Keys never exposed to agent context.
metadata: {"clawdbot":{"emoji":"🔑","requires":{"bins":["curl","jq","bash"]},"os":["linux","darwin"]}}
---

## Usage

Make authenticated API calls without seeing the key:

```bash
keys-broker call '{"action":"call","service":"openai","url":"https://api.openai.com/v1/chat/completions","method":"POST","body":{"model":"gpt-4","messages":[{"role":"user","content":"Hello"}]}}'
```

Response:
```json
{"ok": true, "status": 200, "body": {...}}
```

## Supported Services

Only preconfigured services work (security: prevents key exfiltration):
- `openai` → api.openai.com
- `anthropic` → api.anthropic.com  
- `stripe` → api.stripe.com
- `github` → api.github.com

To add services, edit `ALLOWED_URLS` in `keys-broker.sh`.

## Rules

1. **Never retrieve keys directly** — always use `keys-broker call`
2. **Never ask user to paste keys in chat** — guide them to keychain commands

## Other Tasks

- First time setup → see `setup.md` (install `keys-broker.sh`)
- Add/remove/rotate keys → see `manage.md`

## Limitations

Does NOT work in: Docker containers, WSL, headless Linux servers (no keychain access).
