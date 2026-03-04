# ARGUS Intelligence Skill for ClawHub

**AI-native blockchain intelligence & security for AI agents.**

## Required Environment Variable

```bash
export ARGUS_ENDPOINT="https://argus.getfailsafe.com"
```

## Quick Start

```bash
# Install via ClawHub
clawhub install argus-intelligence
```

## What is ARGUS?

ARGUS is a blockchain intelligence agent that provides:

- **Token Analysis** — Rug pull detection, risk scoring ($0.42)
- **Address Risk** — Sanctions, AML, compliance ($0.42)
- **Smart Money Tracking** — Whale movements ($0.42)
- **Prompt Security** — Injection attack detection ($0.10)
- **Social Verification** — Username/project legitimacy check ($0.25)
- **Webhooks** — Real-time event alerts ($0.10/month)
- **Free Tier** — 3 queries/day, 1-minute cooldown, no payment needed!

## Try It Free

```bash
curl -X POST https://argus.getfailsafe.com/api/v1/free/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is 0x1234... safe?", "agentId": "my-agent"}'
```

## Pricing

| Service | Cost |
|---------|------|
| Free Tier | 3/day FREE (1 min cooldown) |
| Intelligence Query | $0.42 USDC |
| Prompt Security | $0.10 USDC |
| Social Verification | $0.25 USDC |
| Watchlist Monitoring | $0.10/month |
| Webhook Subscription | $0.10/month |

## Payment Options

**Option 1 — Stripe (easiest, no crypto needed):**
Buy 20 credits for $9 → receive a token → pass `X-Stripe-Token: <token>` header.
[Buy credits →](https://buy.stripe.com/4gM28r6zseQlbJp72d4F202)

**Option 2 — x402 (USDC on Base):**
Send USDC to treasury, attach `X-Payment-Proof` header.
Treasury: `0x8518E91eBcb6bE76f478879720bD9759e01B7954`

## Links

- **Live API:** [argus.getfailsafe.com](https://argus.getfailsafe.com)
- **Agent Card (A2A):** [/.well-known/agent.json](https://argus.getfailsafe.com/.well-known/agent.json)
- **Capabilities:** [/api/v1/capabilities](https://argus.getfailsafe.com/api/v1/capabilities)
- **Full Docs:** See [SKILL.md](./SKILL.md)
- **Website:** [getfailsafe.com](https://getfailsafe.com)

## Version

**v1.9.2** — Prompt security hardened (is_safe/base64 fixes), Stripe-first payments, A2A message routing, social verification transparency, webhook event docs, status endpoint crash fix.

## Changelog

| Version | Highlights |
| ------- | ---------- |
| v1.9.2 | Security: is_safe fix, base64 decode, error handler hardening; A2A real routing; social verification transparency |
| v1.9.1 | Stripe credits, deprecated referral/leaderboard, model upgrade (Gemini), SDR heartbeat |
| v1.9.0 | Batch analysis, watchlist, webhook delivery, x402 Solana support |
| v1.5.0 | Initial ClawHub release, HTTPS via Cloudflare |

## Payment Verification

| Network | Address | Verify On |
|---------|---------|-----------|
| Base | `0x8518E91eBcb6bE76f478879720bD9759e01B7954` | [BaseScan](https://basescan.org/address/0x8518E91eBcb6bE76f478879720bD9759e01B7954) |
| Solana | `Ntx61j81wkQFLT5MGEKvMtazxH4wh6iXUNMtidgxXYH` | [Solscan](https://solscan.io/account/Ntx61j81wkQFLT5MGEKvMtazxH4wh6iXUNMtidgxXYH) |

---

Built by [Failsafe Security Inc.](https://getfailsafe.com)
