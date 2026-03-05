# AGIRAILS Payments — OpenClaw Skill

**Give your AI agent a wallet. Let it earn and pay USDC — settled on-chain, gasless, in under 2 seconds.**

> **Quick start**: Tell your agent: *"Read SKILL.md and set up AGIRAILS payments"* — the onboarding flow will guide you interactively.

AGIRAILS is the open settlement layer for AI agents on Base L2. This skill turns any [OpenClaw/Clawdbot](https://openclaw.ai) agent into a full participant in the agent economy — earning, paying, and settling in USDC with on-chain guarantees.

## Why This Exists

AI agents need to pay each other. Not with API keys and invoices — with real money, real escrow, real dispute resolution. AGIRAILS handles the hard parts:

- **Gasless transactions** — Smart Wallet (ERC-4337) + Paymaster. Your agent never needs ETH.
- **USDC settlement** — real stablecoin, $1 = $1. On Base L2.
- **Encrypted wallet** — auto-generated keystore (AES-128-CTR, chmod 600, gitignored). No keys in code, ever.
- **Two payment modes** — ACTP escrow for complex jobs. x402 instant for API calls. Same SDK.
- **On-chain identity** — ERC-8004 portable identity + reputation. Follows your agent across marketplaces.
- **Deployment security** — fail-closed key policy, `ACTP_KEYSTORE_BASE64` for containers, `actp deploy:check` secret scanning.
- **10,000 test USDC** — `actp init` in mock mode. Testnet: 1,000 USDC minted gaslessly during registration.
- **1% transparent fee** — `max(amount * 1%, $0.05)`. Same on both payment paths. No subscriptions.

## ACTP or x402? Pick the Right Payment Mode

```
Need time to do the work?  →  ACTP (escrow)
  Lock USDC → work → deliver → dispute window → settle
  Think: hiring a contractor

Instant API call?  →  x402 (instant)
  Pay → get response. One step. No escrow. No disputes.
  Think: buying from a vending machine
```

Both modes are in the same SDK. Your agent can use both simultaneously.

## Quick Start

```bash
# Install the skill
git clone https://github.com/agirails/openclaw-skill.git ~/.openclaw/skills/agirails
```

Then just tell your agent:

> "Pay 10 USDC to 0xProviderAddress for translation service"

Or use the SDK directly:

```bash
npx actp init --mode mock
npx actp init --scaffold --intent earn --service code-review --price 5
npx ts-node agent.ts
```

Three commands. Mock mode. No keys, no gas, no config.

## Prerequisites

1. **AGIRAILS SDK**:
   ```bash
   npm install @agirails/sdk   # TypeScript
   pip install agirails        # Python
   ```

2. **Wallet setup** (needed for testnet/mainnet only; mock mode needs no secrets. SDK auto-detects: keystore → `ACTP_KEYSTORE_BASE64` → `ACTP_PRIVATE_KEY` → `PRIVATE_KEY`):
   ```bash
   # Option A: Encrypted keystore (recommended)
   npx actp init -m testnet
   export ACTP_KEY_PASSWORD="your-keystore-password"

   # Option B: For Docker/Railway/serverless
   export ACTP_KEYSTORE_BASE64="$(base64 < .actp/keystore.json)"
   export ACTP_KEY_PASSWORD="your-keystore-password"
   ```
   > **Note:** raw keys (`ACTP_PRIVATE_KEY` / `PRIVATE_KEY`) are high-risk; mainnet policy paths require encrypted keystores.

## Networks

**Mock**
- Cost to start: Free
- Gas: Simulated
- USDC: 10,000 auto-minted
- Escrow: `request()` auto-releases; `client.pay()` manual
- Tx limit: None

**Testnet (Base Sepolia)**
- Cost to start: Free (1,000 USDC minted during registration)
- Gas: Sponsored
- USDC: 1,000 minted gaslessly on registration
- Escrow: Manual `release()`
- Tx limit: None

**Mainnet (Base)**
- Cost to start: Real USDC
- Gas: Sponsored
- USDC: bridge.base.org
- Escrow: Manual `release()`
- Tx limit: $1,000

## What's Inside

```
openclaw-skill/
├── SKILL.md                         # Full protocol reference + interactive onboarding
├── README.md                        # This file
├── references/
│   ├── state-machine.md             # 8-state machine reference
│   ├── requester-template.md        # Full requester agent template
│   └── provider-template.md         # Full provider agent template
├── examples/
│   ├── simple-payment.md            # All 3 API levels explained
│   └── full-lifecycle.md            # Complete transaction flow
├── openclaw/                        # OpenClaw-specific integration
│   ├── QUICKSTART.md                # 5-minute setup guide
│   ├── agent-config.json            # Ready-to-use configs
│   ├── SOUL-treasury.md             # Buyer agent template
│   ├── SOUL-provider.md             # Seller agent template
│   ├── SOUL-agent.md                # Full autonomous agent (earn + pay + x402)
│   ├── cron-examples.json           # Automation jobs
│   ├── validation-patterns.md       # Delivery validators
│   └── security-checklist.md        # Pre-launch audit
└── scripts/
    ├── setup.sh                     # Automated setup
    ├── test-balance.ts              # Check wallet balance
    └── test-purchase.ts             # Test on testnet
```

## State Machine

```
INITIATED ─┬──> QUOTED ──> COMMITTED ──> IN_PROGRESS ──> DELIVERED ──> SETTLED
            │                  │              │              │
            └──> COMMITTED     │              │              └──> DISPUTED
                               v              v                    │    │
                           CANCELLED      CANCELLED            SETTLED  CANCELLED
```

8 states. Forward-only transitions. SETTLED and CANCELLED are terminal.

## Links

- [SDK (npm)](https://www.npmjs.com/package/@agirails/sdk) | [SDK (pip)](https://pypi.org/project/agirails/)
- [GitHub](https://github.com/agirails) | [Docs](https://docs.agirails.io) | [Examples](https://github.com/agirails/sdk-js/tree/main/examples)
- [Discord](https://discord.gg/nuhCt75qe4) | [Issues](https://github.com/agirails/openclaw-skill/issues)
- Security: security@agirails.io

## License

MIT
