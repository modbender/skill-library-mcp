---
name: MerchantGuard — Compliance Layer for AI Agents
description: MerchantGuard is the compliance and security layer for the agent
  economy. Before your agent touches money, processes PII, or gets deployed to
  production — verify it.
---

# MerchantGuard — Compliance Layer for AI Agents

**Version:** 2.0.0
**Author:** MerchantGuard (https://merchantguard.ai)
**Purpose:** Security scanning, adversarial testing, compliance scoring, and certification for AI agents that handle payments or sensitive data.

---

## What This Skill Does

MerchantGuard is the compliance and security layer for the agent economy. Before your agent touches money, processes PII, or gets deployed to production — verify it.

This skill gives you:

1. **GuardScan** — Scan your code or skills directory for 102 security patterns (hardcoded keys, prompt injection, PCI violations). Runs locally, nothing uploaded.
2. **Mystery Shopper** — Run 10 adversarial probes against any agent (ethical boundary, PII leaks, double-charge, injection, timeout). Get a trust score 0-100.
3. **GuardScore** — Merchant compliance health score (chargeback rate, fraud stack, auth optimization, volume, PSP risk).
4. **14 AI Compliance Coaches** — Ask vertical-specific compliance questions (CBD, crypto, nutra, adult, gaming, travel, subscriptions, telehealth, BNPL, Mexico, VAMP, high-risk, PSP matching, ecommerce).
5. **Compliance Alerts** — Real-time alerts on Visa/Mastercard rule changes, VAMP threshold updates, regulatory shifts.
6. **Certification** — Full TrustVerdict: Mystery Shopper + GuardScan + identity verification. Tiers: Unverified → Verified (50+) → Gold (70+) → Diamond (90+).

---

## Commands

### `guard scan [path]`

Scan a directory for security issues. Checks 102 patterns including:
- Hardcoded API keys and secrets
- Prompt injection vulnerabilities
- PCI DSS violations
- Sensitive file access (.ssh, .env, private keys)
- Unsigned or unverified dependencies

```
guard scan .
guard scan ~/.openclaw/skills/
guard scan /path/to/agent/code
```

Output: Risk score 0-100, categorized findings, remediation steps.

### `guard shopper <agent_name>`

Run 10 adversarial probes against an agent:

| Probe | What It Tests |
|-------|--------------|
| basic_task | Can it follow instructions? |
| malformed_input | Does it handle garbage safely? |
| ethical_boundary | Will it refuse fraud requests? |
| timeout_test | Does it respond in time? |
| data_handling | Does it leak PII? |
| capability_verify | Can it do what it claims? |
| idempotency | Will it double-charge? |
| concurrency | Does it handle parallel requests? |
| statefulness | Does it maintain context? |
| resource_consumption | Is it efficient? |

```
guard shopper MyCoolAgent
guard shopper MyCoolAgent --endpoint https://myagent.com/api/probe
```

Output: Score 0-100, pass/fail per probe, trust tier.

### `guard score`

Calculate GuardScore for a merchant:

```
guard score --chargeback-ratio 0.8 --vertical crypto --volume 50000
```

Output: Score 0-100, health band (SAFE/WARNING/ELEVATED/CRITICAL), factor breakdown, action items.

### `guard coach <vertical> "<question>"`

Ask one of 14 compliance coaches:

```
guard coach crypto "Do I need a BitLicense to process crypto payments in New York?"
guard coach vamp "My chargeback ratio is 1.2%. What should I do immediately?"
guard coach mexico "What are CNBV requirements for fintech lending in Mexico?"
guard coach cbd "Can I use Stripe for CBD payments?"
```

Verticals: cbd, crypto, nutra, adult, gaming, travel, ticketing, subscriptions, ecommerce, bnpl, mexico, vamp, high-risk, psp-match, telehealth

Output: Structured Decision Object with risk level, required actions, policy citations, and disclaimer.

### `guard alerts`

Get latest compliance alerts:

```
guard alerts
guard alerts --critical
guard alerts --vertical crypto,cbd
```

Output: Alert feed with severity, category, affected industries, action required.

### `guard certify <agent_name>`

Run full certification pipeline (Mystery Shopper + GuardScan + identity):

```
guard certify MyAgent --wallet 0x1234... --endpoint https://myagent.com/api/probe
```

Output: TrustVerdict score, tier (Verified/Gold/Diamond), on-chain attestation option.

---

## API

All commands call the MerchantGuard API at `https://merchantguard.ai/api`.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v2/guard` | POST | Unified Guard API (7 intents) |
| `/api/v2/mystery-shopper` | POST | Run adversarial probes |
| `/api/v2/coach/{vertical}` | POST | Ask compliance coach |
| `/api/v2/guardscore/assess` | POST | Calculate GuardScore |
| `/api/v2/certify` | POST | Full certification |
| `/api/guardscan/scan` | POST | Code security scan |
| `/api/alerts/public` | GET | Compliance alerts |

Authentication: `MERCHANTGUARD_API_KEY` environment variable (optional for free tier — 3 probes/month, basic scan, alerts).

---

## npm Packages

For programmatic integration (Node.js/TypeScript):

```bash
npm install @merchantguard/guard          # Main SDK — everything in one package
npm install @merchantguard/mystery-shopper # Standalone Mystery Shopper client
npm install @merchantguard/guardscan       # Standalone code scanner
npm install @merchantguard/probe-handler   # Drop-in handler for receiving probes
```

---

## VAMP Thresholds (Visa)

- **< 0.9%** — SAFE (no action needed)
- **0.9% - 1.5%** — WARNING (early warning, take preventive action)
- **1.5% - 1.8%** — ELEVATED (fines start, implement RDR + 3DS immediately)
- **> 1.8%** — CRITICAL (MATCH list risk, contact acquirer immediately)

Merchants have 45 days for remediation plans after entering the warning zone.

---

## Trust Tiers (Agent Certification)

| Tier | Score | What It Means |
|------|-------|--------------|
| Unverified | 0-49 | Not yet tested |
| Verified | 50-69 | Passed basic probes |
| Gold | 70-89 | Strong compliance posture |
| Diamond | 90-100 | Full adversarial audit passed |

Diamond-certified agents can access: Mastercard Agent Pay, Visa Tap to Phone, autonomous payment routing, Durango high-risk processing.

---

## Installation

### For OpenClaw Agents (ClawHub)

```bash
# From ClawHub
openclaw skill install merchantguard

# Or manual install
mkdir -p ~/.openclaw/skills/merchantguard
cd ~/.openclaw/skills/merchantguard
curl -LO https://merchantguard.ai/skills/guard/SKILL.md
curl -LO https://merchantguard.ai/skills/guard/guard.py
curl -LO https://merchantguard.ai/skills/guard/claw.json
pip install requests
```

### For any agent with npm

```bash
npx @merchantguard/guardscan .              # Scan current directory
npx @merchantguard/mystery-shopper MyAgent   # Probe an agent
npm install @merchantguard/guard             # Full SDK
```

---

## Security Notes

This skill:
- Does NOT store or transmit your private keys
- Does NOT access files outside the specified scan directory
- GuardScan runs 100% locally — no code leaves your machine
- Uses HTTPS for all API communications
- All attestations signed with MerchantGuard's verified key (0x8E144D07e1F5490a1840d23FCE1D73266406AaF3)

---

## Support

- **Moltbook:** @MerchantGuardBot
- **Website:** https://merchantguard.ai
- **GitHub:** https://github.com/MerchantGuard/agent-skills
- **Telegram:** @merchantguard
- **X:** @GuardClawbot

---

*MerchantGuard — The Compliance Layer for the Agent Economy*
