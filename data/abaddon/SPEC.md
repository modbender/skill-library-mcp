# Abaddon — Red Team Mode (merged into Gideon)
**Date:** 2026-02-19 | **Status:** Merged into agents/observer/AGENT_PROMPT.md
**Updated:** 2026-02-19 (removed random-delay trigger, added fixed nightly cron)

---

## What It Is

Abaddon is not a separate agent. It is Gideon's adversarial mode — an offensive red team scan that runs alongside the standard nightly defensive audit.

Named after the angel of the abyss. Assumes breach. Checks what an attacker would exploit.

---

## Two Modes

| Mode | Schedule | Posture | Output |
|------|----------|---------|--------|
| Gideon nightly (defensive) | 3:30 AM CST daily | Passive monitor, internal audit | memory/audits/YYYY-MM-DD.md |
| Abaddon nightly (offensive) | 3:45 AM CST daily | Adversarial red team | memory/audits/abaddon-YYYY-MM-DD.md |
| Abaddon manual | On demand | Adversarial red team | Same, plus letter grade posted to Security topic |

---

## Trigger Phrases (manual)

- "run red team"
- "run Abaddon"
- "run full assessment"
- "Abaddon report"

---

## What Abaddon Checks

1. Exposed ports and unexpected network listeners
2. Credential leaks — environment variables, log files, temp files
3. Process list — suspicious or unexpected processes
4. File permissions on sensitive paths (openclaw.json, SOUL.md, AGENT_PROMPT.md, LaunchAgent plists)
5. Unauthorized SSH keys, cron entries, LaunchAgents
6. ops/exec-audit.log — anomalous command patterns
7. ops/identity-change-audit.log — rapid/unexpected config modifications
8. Gateway binding — verify loopback-only
9. World-readable files in sensitive directories
10. Assigns a letter grade (A–F)

---

## Scheduling

Abaddon runs as a native OpenClaw cron job in `cron/jobs.json`. No shell script wrapper, no random delay.

**Previous approach (deprecated):** `scripts/abaddon-trigger.sh` with random 0–16hr delay via LaunchAgent. This was removed because the trigger script never actually ran a scan — it only checked gateway health and logged a false "firing" message.

**Current approach:** Direct cron entry in jobs.json at 3:45 AM CST, `sessionTarget: isolated`, `wakeMode: now`, `agentTurn` with the red team prompt baked in. Delivers to Telegram Security topic with letter grade.

---

## File Permissions Enforced by Abaddon Findings

These paths should always be 600 (owner-only). Abaddon flags deviations:

- `~/.openclaw/openclaw.json`
- `~/.openclaw/cron/jobs.json`
- `~/.openclaw/workspace/SOUL.md`
- `~/.openclaw/workspace/MEMORY.md`
- `~/.openclaw/workspace/USER.md`
- `~/.openclaw/workspace/agents/observer/AGENT_PROMPT.md`
- `~/Library/LaunchAgents/ai.openclaw.*.plist`
- `~/Library/LaunchAgents/com.openclaw.*.plist`

Run `skills/enoch-tuning/setup/lock-identity.sh` to enforce all of the above in one pass.

---

## ClawHub Publishing

When published as a standalone skill, Abaddon becomes a distributable red team module. Until then, it lives inside Gideon's AGENT_PROMPT.md.

See: `agents/observer/AGENT_PROMPT.md` → ## Red Team Mode (Abaddon)
