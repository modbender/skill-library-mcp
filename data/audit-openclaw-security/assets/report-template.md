# OpenClaw Security Audit Report

## Executive summary

- **Overall risk rating:** (Critical / High / Medium / Low)
- **Most urgent issues:** (1–3 bullets)
- **Big picture:** What is exposed, who can talk to the bot, what the bot can do.

## Environment

- **Host type:** (Mac mini / laptop / AWS EC2 / VPS / Docker / other)
- **OS + version:**
- **OpenClaw version:** (`openclaw --version`)
- **Install type:** (npm global / install.sh / Docker / source / other)
- **Gateway bind + access method:** (loopback + local only / tailnet / LAN / reverse proxy / other)
- **Inbound channels enabled:** (WhatsApp/Telegram/Slack/etc.)
- **Tool profile:** (messaging/minimal/custom; notable denies/allows)

## Findings

| Severity | Finding | Evidence (redacted) | Why it matters | Recommended fix | Verify |
|---|---|---|---|---|---|
| Critical |  |  |  |  |  |
| High |  |  |  |  |  |
| Medium |  |  |  |  |  |
| Low |  |  |  |  |  |

## Remediation plan

### Phase 1 — Stop the bleeding (same day)

1.
2.
3.

### Phase 2 — Harden and reduce blast radius (this week)

1.
2.
3.

### Phase 3 — Operationalise (ongoing)

- Update cadence (OS, Node, OpenClaw)
- Token rotation policy
- Backup/restore plan for `~/.openclaw` (safely)
- Log retention and redaction

## Verification checklist

- [ ] `openclaw security audit --deep` shows no Critical findings
- [ ] Gateway not reachable from untrusted networks
- [ ] DM pairing/allowlists in place
- [ ] Group mention gating enabled
- [ ] File permissions tightened for OpenClaw state and config
- [ ] Tools limited to what is required

## Residual risk notes

Even with best practices, an agent that can read messages and execute tools carries inherent risk (prompt injection, social engineering, unexpected actions). Document what you are choosing to accept and why.
