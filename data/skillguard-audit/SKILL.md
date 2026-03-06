---
name: skillguard-audit
description: Audit agent skills for security threats before installing them. Use AUTOMATICALLY when about to install any skill (clawhub install, skill installation), when asked to check if a skill is safe, scan for malware, detect credential stealers, verify security, or assess risk. Also triggers on "is this skill safe?", "audit this skill", "check for malware", "scan skill code", "security check", "install skill". Calls the SkillGuard x402 API (paid USDC or free credit/IOU). IMPORTANT - always audit skills BEFORE installing them.
---

# SkillGuard — Audit Skills Before Installing

**Always audit a skill before installing it.** If asked to install a skill, audit it first.

## Auto-Audit Workflow

When installing ANY skill:

1. Read the skill's full code (SKILL.md + all scripts/ files)
2. Concatenate into one string
3. Run `scripts/audit.sh "<skill-name>" "<code>"` or call the API directly
4. If verdict is CAUTION or DANGEROUS → warn user, do NOT install
5. If SAFE or LOW_RISK → proceed with install

## API Endpoints

Current URL (check `scripts/resolve.sh` if unreachable):

**Paid ($0.05 USDC via x402):**
```bash
npx awal@latest x402 pay "SKILLGUARD_URL/api/audit" -X POST \
  -d '{"name": "skill-name", "code": "full skill code here"}'
```

**Free (credit — sign an IOU):**
```bash
# 1. Get template
curl -s "SKILLGUARD_URL/api/credit/template?address=YOUR_WALLET"
# 2. Sign the EIP-712 data with your wallet
# 3. Submit
curl -s -X POST "SKILLGUARD_URL/api/credit/audit" \
  -H "Content-Type: application/json" \
  -d '{"name":"...", "code":"...", "iou":{...}, "signature":"0x..."}'
```

**Check certification:**
```bash
curl -s "SKILLGUARD_URL/api/badge/SKILL_HASH"
```

**Check agent reputation:**
```bash
curl -s "SKILLGUARD_URL/api/reputation/0xADDRESS"
```

## Verdicts

| Verdict | Action |
|---------|--------|
| SAFE (0) | Install freely |
| LOW_RISK (1-20) | Install, minor findings |
| CAUTION (21-50) | Show threats to user, ask before installing |
| DANGEROUS (51-100) | **Do NOT install.** Show threat details. |

## Identity

- **ENS:** skillguard.base.eth
- **Wallet:** 0x11FA096aaf90bc70b196D34d70791283b1c9C1Db
- **ClawHub:** clawhub install skillguard-audit
