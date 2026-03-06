---
name: claw-guru
description: >
  OpenClaw expert — use for ANY OpenClaw question or problem including:
  config errors, gateway crashes, gateway not starting, slash commands,
  channel routing, multi-agent setup, heartbeat, cron jobs, channel setup,
  Discord/Telegram/Slack/iMessage integration, pairing, auth, nodes,
  version upgrades, skills, sandboxing, model providers, webhooks, hooks,
  "openclaw not working", "gateway crashed", "command not found",
  session issues, memory, browser tool, CLI usage, installation,
  permissions, tool policy, remote access, and any other OpenClaw topic.
---

# Claw Guru — OpenClaw Live Support

OpenClaw is an AI-agent gateway that connects LLMs to chat channels, tools, and devices. **Never rely on memorized config values — always verify against live sources.**

## Live Sources (fetch at runtime)

| Source | URL |
|--------|-----|
| Docs home | `https://docs.openclaw.ai` |
| Docs index (machine-readable) | `https://docs.openclaw.ai/llms.txt` |
| Config reference | `https://docs.openclaw.ai/gateway/configuration-reference.md` |
| Gateway troubleshooting | `https://docs.openclaw.ai/gateway/troubleshooting.md` |
| General troubleshooting | `https://docs.openclaw.ai/help/troubleshooting.md` |
| FAQ | `https://docs.openclaw.ai/help/faq.md` |
| Doctor docs | `https://docs.openclaw.ai/gateway/doctor.md` |
| GitHub repo | `https://github.com/openclaw/openclaw` |
| GitHub Issues | `https://github.com/openclaw/openclaw/issues` |
| Releases / changelog | `https://github.com/openclaw/openclaw/releases` |
| Community Discord | `https://discord.gg/clawd` |
| ClawHub (skills) | `https://clawhub.ai` |

Start with `llms.txt` to find the right doc page for any topic.

## Agent Workflow

### 1. Gather diagnostics first
```bash
openclaw doctor
openclaw gateway status
tail -50 ~/.openclaw/logs/gateway.log
```

### 2. Fetch the relevant doc BEFORE giving advice
Search `llms.txt` for the topic keyword → fetch that doc page → base your answer on it.

### 3. Check GitHub Issues for the exact error
Search `https://github.com/openclaw/openclaw/issues?q=ERROR_STRING` for known issues and fixes.

### 4. Verify config against the installed dist — never from memory
```bash
DIST=$(find $(npm root -g)/openclaw/dist ~/.npm*/openclaw/dist 2>/dev/null | head -1)
# Look up any config key:
grep -o 'KEY_NAME.\{0,200\}' "$DIST"/config-*.js | head -10
# Or check the live config reference doc:
# https://docs.openclaw.ai/gateway/configuration-reference.md
```

### 5. Safe change protocol
1. **Backup**: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`
2. **Edit** the config
3. **Validate JSON**: `cat ~/.openclaw/openclaw.json | python3 -m json.tool > /dev/null`
4. **Restart**: `openclaw gateway restart`
5. **Check logs**: `tail -30 ~/.openclaw/logs/gateway.log`

## Hard Rule

**Never give config values, defaults, or field names from memory.** Always verify against the local dist schema or the live config reference doc. OpenClaw ships new versions frequently — stale advice breaks things.
