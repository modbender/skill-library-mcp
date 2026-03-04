---
name: abaddon
description: Red team security mode for OpenClaw. Runs an adversarial audit on demand or nightly — checks exposed ports, credential leaks, file permissions, suspicious processes, and OpenClaw config posture. Assigns a letter grade. Built for macOS deployments.
---

# Abaddon ⚔️

Most security audits are defensive — they check what you've locked down. Abaddon runs the other direction. It thinks like an attacker. It looks for what an adversary would find, not just what you remember to check.

On demand or every night at 3:45 AM. Letter grade every time.

## What It Checks

**Network & Exposure**
- Listening ports — anything bound to 0.0.0.0 is flagged
- Gateway binding — should be loopback only
- SSH Remote Login state
- Active tunnels (ngrok, cloudflared, unexpected remote access)
- Firewall and stealth mode

**System Integrity**
- SIP, FileVault, Gatekeeper
- macOS version + pending updates
- XProtect / MRT definitions age

**OpenClaw Configuration**
- Exec security mode (full / allowlist / deny)
- Gateway auth enabled?
- Unexpected cron entries
- Unexpected plugins

**File Permissions**
- SOUL.md + AGENTS.md: root-owned, 444
- MEMORY.md, USER.md, AGENT_PROMPT.md, openclaw.json, cron/jobs.json, LaunchAgent plists: 600
- Flags anything 644 or wider on sensitive paths
- Plaintext key scan across workspace

**API Key Handling**
- Keys in Keychain or flat files?
- Keys leaking through env vars?
- Secrets in git history?
- Hardcoded tokens in .zshrc?

**Agent Behavior**
- Memory injection scan (prompt injection attempts in memory files)
- Sub-agent scope check
- Unexpected agent permissions

**Dependencies**
- Homebrew outdated (flags openclaw, ollama, node)
- npm global outdated

## Scoring

| Grade | Criteria |
|-------|----------|
| A | 0 CRITICAL, 0 HIGH |
| B | 0 CRITICAL, 1–2 HIGH |
| C | 1 CRITICAL or 3+ HIGH |
| D | 2+ CRITICAL |
| F | Active compromise indicators |

## Installation

### Step 1 — Copy the Abaddon prompt into your agent

If you have Gideon (the OpenClaw observer agent), append the red team section:

```bash
cat skills/abaddon/templates/abaddon-prompt.md >> ~/.openclaw/workspace/agents/observer/AGENT_PROMPT.md
```

If you don't have Gideon, use the standalone agent prompt:

```bash
cp skills/abaddon/templates/abaddon-prompt.md ~/.openclaw/workspace/agents/abaddon/AGENT_PROMPT.md
```

### Step 2 — Add the nightly cron

```bash
bash skills/abaddon/setup/cron-seed.sh
```

This adds a 3:45 AM CST cron job to `~/.openclaw/cron/jobs.json`. Delivers to Telegram Security topic if configured.

### Step 3 — Lock the agent prompt

```bash
chmod 600 ~/.openclaw/workspace/agents/observer/AGENT_PROMPT.md
```

Your detection playbook should never be world-readable.

## Usage

**Manual trigger** — say any of:
- "run red team"
- "run Abaddon"
- "run full assessment"
- "Abaddon report"

**Nightly** — fires automatically at 3:45 AM CST after the standard defensive audit (3:30 AM).

## Output

Every run produces two things:

1. **Technical report** → `memory/audits/abaddon-YYYY-MM-DD.md` — full command output, evidence, remediation steps
2. **Summary** → posted to Telegram Security topic with letter grade

CRITICAL findings trigger an immediate DM alert.

## Notes

- Designed for macOS (Darwin arm64). Most checks work on Linux with minor path adjustments.
- Assumes OpenClaw gateway is running locally. Remote deployments may need adjusted port/binding checks.
- Pairs with `enoch-tuning` — run `lock-identity.sh` after install to enforce all file permission baselines in one pass.
