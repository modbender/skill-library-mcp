# MerchantGuard OpenClaw Skill

**The Compliance Layer for the AI Agent Economy**

Security scanning, adversarial testing, compliance scoring, and certification for AI agents.

## Quick Install

```bash
# From ClawHub
openclaw skill install merchantguard

# Or manual
mkdir -p ~/.openclaw/skills/merchantguard
cd ~/.openclaw/skills/merchantguard
curl -LO https://merchantguard.ai/skills/guard/guard.py
curl -LO https://merchantguard.ai/skills/guard/SKILL.md
curl -LO https://merchantguard.ai/skills/guard/claw.json
pip install requests
```

## Commands

```bash
guard scan .                              # Scan code for 102 security patterns (local)
guard shopper MyAgent                     # Run 10 adversarial probes
guard score --chargeback-ratio 0.8        # Calculate GuardScore
guard coach crypto "My question"          # Ask a compliance coach
guard alerts --critical                   # Get compliance alerts
guard certify MyAgent --wallet 0x1234...  # Full certification
```

## npm (Node.js/TypeScript)

```bash
npm install @merchantguard/guard            # Main SDK
npx @merchantguard/guardscan .              # Scan code
npx @merchantguard/mystery-shopper MyAgent  # Probe an agent
```

## What's Included

- **GuardScan** — 102 security patterns, runs 100% locally
- **Mystery Shopper** — 10 adversarial probes (ethical boundary, PII leaks, double-charge, injection)
- **GuardScore** — Merchant compliance health 0-100
- **14 AI Coaches** — CBD, crypto, nutra, adult, gaming, travel, VAMP, Mexico, and more
- **Compliance Alerts** — Real-time Visa/Mastercard rule changes
- **Certification** — TrustVerdict tiers: Verified → Gold → Diamond

## Links

- **Website:** [merchantguard.ai](https://merchantguard.ai)
- **Moltbook:** [@MerchantGuardBot](https://www.moltbook.com/u/MerchantGuardBot)
- **GitHub:** [MerchantGuard/agent-skills](https://github.com/MerchantGuard/agent-skills)
- **npm:** [@merchantguard/guard](https://www.npmjs.com/package/@merchantguard/guard)

## License

MIT
