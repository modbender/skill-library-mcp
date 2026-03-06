---
name: promptdome
description: "Integrate PromptDome prompt injection screening into OpenClaw. Use when setting up automatic protection against prompt injection, jailbreaks, and PII exfiltration on incoming messages. Installs two components: (1) a hook that auto-scans every incoming message before the model processes it, and (2) an agent tool (promptdome_scan) agents can call explicitly on untrusted content. Run setup.sh to configure in under 60 seconds."
metadata:
  openclaw:
    requires:
      bins: [curl, python3, openclaw]
      env: [PROMPTDOME_API_KEY]
---

# PromptDome × OpenClaw

> **API key required** — Get yours free at **https://promptdome.cyberforge.one/dashboard/api-keys**
> (Sign up → Dashboard → API Keys → Create Key)

Adds automatic prompt injection detection to any OpenClaw agent. Two components work together:

| Component | What it does | When it fires |
|---|---|---|
| **`promptdome-gate` hook** | Auto-scans every incoming message; injects ⚠️ warning if injection detected | Every `message:received` — zero agent code required |
| **`promptdome_scan` tool** | Explicit scan agent can call on any content | On demand — web content, files, tool outputs |

---

## Quick Setup (60 seconds)

```bash
bash skills/promptdome/scripts/setup.sh --api-key sk_shield_live_YOUR_KEY
```

That's it. The script:
1. Tests your API key against the PromptDome API
2. Installs `promptdome-gate` hook → `~/.openclaw/hooks/promptdome-gate/`
3. Installs `promptdome_scan` plugin → `~/.openclaw/extensions/promptdome/`
4. Saves API key to `openclaw.json` env block
5. Enables the hook automatically
6. Prompts you to restart the gateway

**Get an API key:** https://promptdome.cyberforge.one/dashboard/api-keys

---

## Manual Setup

### 1. Copy files

```bash
# Hook (auto-scanning)
mkdir -p ~/.openclaw/hooks/promptdome-gate
cp skills/promptdome/hook/HOOK.md   ~/.openclaw/hooks/promptdome-gate/
cp skills/promptdome/hook/handler.ts ~/.openclaw/hooks/promptdome-gate/

# Plugin (explicit tool)
mkdir -p ~/.openclaw/extensions/promptdome
cp skills/promptdome/plugin/index.ts ~/.openclaw/extensions/promptdome/
```

### 2. Set API key

Add to `~/.openclaw/openclaw.json`:
```json
{
  "env": {
    "PROMPTDOME_API_KEY": "sk_shield_live_YOUR_KEY"
  }
}
```

Or set `PROMPTDOME_API_KEY` in your shell environment.

### 3. Enable hook and restart

```bash
openclaw hooks enable promptdome-gate
openclaw gateway restart
```

---

## What Happens After Install

- Every incoming message → scanned automatically before the model processes it
- **BLOCK** (score ≥ 70): `[PROMPTDOME BLOCK]` warning injected into conversation
- **WARN** (score ≥ 40): Soft caution note injected
- **ALLOW**: Silent — no overhead in conversation history
- Scan log: `~/.openclaw/logs/promptdome-gate.log`
- Fail-open: if API is unreachable, messages pass through unblocked

---

## Using the Agent Tool

Enable `promptdome_scan` in your agent's tool allowlist:
```json
{
  "agents": {
    "list": [{ "id": "main", "tools": { "allow": ["promptdome_scan"] } }]
  }
}
```

Then agents call it like any tool — before processing web fetches, search results, uploaded files, or any external content.

---

## Self-Hosted PromptDome

Override the API endpoint:
```json
{
  "env": {
    "PROMPTDOME_API_KEY": "sk_shield_live_...",
    "PROMPTDOME_API_URL": "https://your-instance.com/api/v1/shield"
  }
}
```

---

## Detection Coverage

PromptDome engine covers 32 attack categories including:
- Prompt injection & jailbreaks
- Fake system events / gateway spoofing
- PII & credential exfiltration
- ClickFix / social engineering
- HTML/DOM injection (browser agents)
- Agentic chain poisoning
- Multilingual evasion (18 languages)

Full category list: https://promptdome.cyberforge.one/docs
