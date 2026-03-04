# Incident Response Playbook

**When:** Integrity check fails, quarantine triggered, or compromise suspected.  
**Goal:** Contain, investigate, recover, prevent recurrence.

---

## 1. Immediate (0–15 min)

| Step | Action |
|------|--------|
| 1.1 | **Quarantine** affected skill: `./scripts/quarantine-skill.sh <SKILL_NAME>` |
| 1.2 | **Stop** agent usage on this workspace until cleared |
| 1.3 | **Log** incident: `memory/security-incidents.md` is updated by scripts |
| 1.4 | **Check** SOUL.md, MEMORY.md, IDENTITY.md for unexpected edits |

## 2. Investigation

| Step | Action |
|------|--------|
| 2.1 | **Diff** changed files: `git diff SOUL.md MEMORY.md` (or your VCS) |
| 2.2 | **Review** quarantined skill: `cat skills/<NAME>.QUARANTINE/SKILL.md` |
| 2.3 | **Search** for IOCs: `91.92.242.30`, glot.io, base64\|bash, credential echoes |
| 2.4 | **Check** network/logs: outbound to C2 IPs, webhook.site, unknown domains |
| 2.5 | **Identify** scope: one skill vs multiple, memory poisoned vs not |

## 3. Recovery

| Step | Action |
|------|--------|
| 3.1 | **Restore** memory files from known-good baseline if poisoned |
| 3.2 | **Rotate** credentials (assume compromise): |
|      | Regenerate `.agent-private-key-SECURE` (ERC-8004) |
|      | Rotate API keys (OpenAI, Gemini, etc.) |
|      | Revoke/rotate any tokens in `~/.openclaw` or `~/.clawdbot` |
| 3.3 | **Update** integrity baseline after restoration: `sha256sum FILE > .integrity/FILE.sha256` |
| 3.4 | **Permanently remove** quarantined skill after evidence preserved: `rm -rf skills/<NAME>.QUARANTINE` |

## 4. Prevention

| Step | Action |
|------|--------|
| 4.1 | **Blocklist** add author/skill/infra to `references/blocklist.conf` (single source of truth); sync SKILL.md "Known Malicious Actors" if you document there too |
| 4.2 | **Document** pattern in `references/threat-patterns.md` |
| 4.3 | **Report** to OpenClaw community / ClawHub / Snyk (responsible disclosure) — see **ClawHub reporting** below |
| 4.4 | **Re-audit** all other skills: `for d in skills/*/; do ./scripts/audit-skills.sh "$d"; done` |

## ClawHub reporting

If the malicious skill came from ClawHub:

- **Report on ClawHub:** Signed-in users can flag a skill. Per [OpenClaw docs](https://docs.openclaw.ai/tools/clawhub#security-and-moderation): *"Each user can have up to 20 active reports at a time. Skills with more than 3 unique reports are auto-hidden by default."*
- **Report to maintainers:** OpenClaw security channel (Discord), ClawHub maintainers.
- **Responsible disclosure:** Snyk, Koi, or other researchers if you have new IOCs or campaign details.

## 5. Escalation

- **Widespread poisoning or exfil confirmed:** Treat as full compromise; rotate all secrets, consider fresh workspace.
- **Unknown C2 or new campaign:** Share IOCs with Snyk / Koi / OpenClaw security channel (anonymized if needed).
- **Legal/compliance:** Follow your org’s incident reporting policy.

---

## Quick Reference

```bash
# Quarantine
./scripts/quarantine-skill.sh SKILL_NAME

# Integrity check
~/.openclaw/workspace/bin/check-integrity.sh

# Re-audit all skills
for d in ~/.openclaw/workspace/skills/*/; do
  [ -d "$d" ] && ! [[ "$d" =~ \.QUARANTINE$ ]] && ./scripts/audit-skills.sh "$d"
done
```
