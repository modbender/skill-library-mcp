---
name: Setup
description: Configure OpenClaw installations with optimized settings, channel setup, security hardening, and production recommendations.
---

## Quick Reference

| Task | Load |
|------|------|
| Messaging channels (Telegram, WhatsApp, Discord, etc.) | `channels.md` |
| Agent settings, models, workspaces | `agents.md` |
| Security, auth, DM policies, allowlists | `security.md` |
| Tools: exec, browser, web, media | `tools.md` |
| Cron, hooks, heartbeats, automation | `automation.md` |
| Recommendations by use case | `recommendations.md` |
| Memory search, embeddings, QMD | `memory.md` |
| Gateway: port, TLS, Tailscale, remote | `gateway.md` |

---

## First Setup Checklist

Before any config, run:
```bash
openclaw onboard --install-daemon  # Full wizard
openclaw doctor                    # Check issues
```

**Minimum viable config:**
- [ ] At least one channel connected (Telegram recommended for testing)
- [ ] Model configured (Anthropic Claude or OpenAI)
- [ ] Workspace path set (`agents.defaults.workspace`)
- [ ] Owner allowlist configured (your user ID in `channels.*.allowFrom`)

---

## Config Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/openclaw.json` | Main config |
| `~/.openclaw/.env` | Environment variables |
| `~/.openclaw/workspace/` | Default workspace |
| `~/.openclaw/sessions/` | Session storage |

**Hot reload:** Most settings apply instantly. Gateway settings (port, TLS) require restart.

---

## Common Mistakes to Avoid

1. **Open DM policy without allowlist** → Anyone can message your bot
2. **No auth token on remote gateway** → Exposed to internet
3. **Model without fallbacks** → Single point of failure
4. **Heartbeat without delivery target** → Lost proactive messages
5. **exec.security: "full" in groups** → Dangerous command access

---

## When You're Done

```bash
openclaw doctor       # Verify config
openclaw status       # Check runtime
openclaw health       # Gateway health
```
