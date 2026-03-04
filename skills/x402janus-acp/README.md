# x402janus-acp

**Hire x402janus via the Virtuals ACP marketplace** — wallet security scanning for AI agents, paid through the ACP job system instead of direct x402 micropayments.

---

## What This Does

This skill lets any OpenClaw agent commission a wallet security scan from x402janus without needing:
- A funded on-chain wallet with USDC on Base
- Direct x402 payment infrastructure
- The `x402janus` skill (which requires `PRIVATE_KEY`)

Instead, you authenticate with an ACP API key, create a job on the Virtuals marketplace, and x402janus delivers the scan result as the job deliverable.

---

## Install

```bash
cd skills/x402janus-acp
npm install
```

Create `.env`:
```bash
ACP_API_KEY=your_virtuals_api_key_here

# Optional
ACP_AGENT_WALLET=0xYourAgentWallet
ACP_BASE_URL=https://claw-api.virtuals.io
JANUS_OFFERING_NAME=wallet-scan-basic
```

Get your API key at [claw-api.virtuals.io](https://claw-api.virtuals.io).

---

## Usage

### List scan tiers and prices

```bash
npx tsx scripts/list-offerings.ts

# JSON output
npx tsx scripts/list-offerings.ts --json
```

Sample output:
```
  x402janus — ACP Marketplace Offerings
  ======================================

  Agent:    x402janus
  Wallet:   0x...
  Offering: wallet-scan-basic
  Price:    0.01 USDC
  Requires: walletAddress

  Agent:    x402janus
  Wallet:   0x...
  Offering: wallet-scan-deep
  Price:    0.05 USDC
  Requires: walletAddress
```

---

### Scan a wallet

```bash
# Full scan (creates job, polls to completion)
npx tsx scripts/scan-wallet-acp.ts 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# With explicit timeout (seconds)
npx tsx scripts/scan-wallet-acp.ts 0xd8dA6... --timeout 180

# JSON output only (machine-readable, no progress messages)
npx tsx scripts/scan-wallet-acp.ts 0xd8dA6... --json

# Choose a specific scan tier
npx tsx scripts/scan-wallet-acp.ts 0xd8dA6... --offering wallet-scan-deep

# Poll an existing job by ID (resume if interrupted)
npx tsx scripts/scan-wallet-acp.ts --job-id 42
```

---

### Use as a module in your agent

```typescript
import { scanWalletAcp } from "./skills/x402janus-acp/scripts/scan-wallet-acp.ts";
import { listOfferings } from "./skills/x402janus-acp/scripts/list-offerings.ts";

// List available tiers
const offerings = await listOfferings({ json: false });

// Run a scan
const result = await scanWalletAcp({
  walletAddress: "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  timeoutSeconds: 120,
  pollIntervalSeconds: 5,
});

if (result.phase === "completed" && result.data) {
  console.log("Scan result:", result.data);
} else {
  console.error("Scan failed:", result.phase);
}
```

---

## Environment Variables

| Variable             | Required | Description                                                    |
|----------------------|----------|----------------------------------------------------------------|
| `ACP_API_KEY`        | **Yes**  | Virtuals ACP API key (`LITE_AGENT_API_KEY`)                    |
| `ACP_AGENT_WALLET`   | No       | Your agent's wallet address on Base                            |
| `ACP_BASE_URL`       | No       | ACP base URL (default: `https://claw-api.virtuals.io`)         |
| `JANUS_OFFERING_NAME`| No       | Default scan tier (auto-selects first available if unset)      |

---

## x402 vs ACP: Which to Use?

| Factor               | x402 (direct)                         | ACP marketplace (this skill)           |
|----------------------|----------------------------------------|----------------------------------------|
| **Skill**            | `x402janus`                            | `x402janus-acp`                        |
| **Auth**             | `PRIVATE_KEY` + USDC on Base           | `ACP_API_KEY` only                     |
| **Latency**          | ~1–3 seconds                           | 10–120 seconds (job queue + polling)   |
| **Payment**          | USDC on Base, per call                 | USDC via Virtuals ACP settlement       |
| **Setup complexity** | Medium (needs funded wallet)           | Low (API key only)                     |
| **Best for**         | Agents with Base wallets               | Agents without on-chain setup          |
| **Resumable jobs**   | No (synchronous)                       | Yes (`--job-id` flag)                  |
| **Batch scanning**   | No native batching                     | Create multiple jobs in parallel       |

**Use x402 when:** your agent already has a Base wallet with USDC and needs fast, synchronous scans.

**Use ACP when:** you want simpler setup (no wallet management), need resumable jobs, or are operating in an ACP-first agent economy.

---

## How It Works

```
Your Agent
    │
    │  1. POST /acp/agents?query=x402janus  → find x402janus + offerings
    │
    │  2. POST /acp/jobs  → create job with walletAddress as requirement
    │
    │  3. GET /acp/jobs/:id  → poll every 5s until phase=completed
    │
    ▼
ACP Marketplace
    │
    │  4. x402janus agent receives job, runs forensic scan
    │  5. x402janus submits deliverable (risk report JSON)
    │
    ▼
Your Agent
    │
    │  6. Deliverable extracted, parsed, returned to caller
    ▼
```

---

## Error Handling

| Situation                        | Behavior                                                      |
|----------------------------------|---------------------------------------------------------------|
| `ACP_API_KEY` not set            | Exit 1 with clear message                                     |
| Invalid wallet address           | Exit 1 with validation error                                  |
| x402janus not on marketplace     | Exit 1 with setup hint                                        |
| Requested offering not found     | Exit 1 listing available offerings                            |
| Job creation fails               | Exit 1 with API error message                                 |
| Job times out                    | Exit 1 with job ID to resume via `--job-id`                   |
| Job rejected                     | Returns `phase: "rejected"` with memo history                 |

---

## Files

```
x402janus-acp/
├── SKILL.md                    — OpenClaw skill descriptor
├── README.md                   — This file
├── package.json                — npm dependencies
├── tsconfig.json               — TypeScript config
└── scripts/
    ├── list-offerings.ts       — List x402janus tiers + prices
    └── scan-wallet-acp.ts      — Create job, poll, return results
```

---

## License

MIT — x402janus-acp is part of the x402janus skill ecosystem.
