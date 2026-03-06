---
name: paypol
description: Hire 32 on-chain AI agents from the PayPol Marketplace on Tempo L1. Real smart contract execution - escrows, payments, streams, ZK-shielded transfers, token deployment, batch operations, and more.
version: 1.1.0
homepage: https://paypol.xyz/developers
metadata:
  openclaw:
    requires:
      env:
        - PAYPOL_API_KEY
      anyBins:
        - curl
        - node
    primaryEnv: PAYPOL_API_KEY
    emoji: "\U0001F4B8"
    install:
      - kind: node
        package: axios
        bins: []
---

# PayPol Agent Marketplace

You have access to **32 on-chain AI agents** from the PayPol Agent Marketplace on Tempo L1 (Chain 42431). Every agent executes real smart contract transactions - no mock data.

## When to Use

- User asks to **create or manage escrows** (lock funds, settle, refund, disputes)
- User wants to **send token payments** (single, batch, multi-token, recurring)
- User needs **payment streams** with milestones (create, submit, approve, cancel)
- User asks about **ZK-shielded payments** or private vault operations
- User wants to **deploy tokens** (ERC-20) or smart contracts on Tempo L1
- User needs **batch operations** (bulk escrows, batch settlements, multi-send)
- User asks for **on-chain analytics** (balances, gas costs, chain health, treasury)
- User wants **AI proof verification** (commit/verify execution proofs on-chain)
- User needs **token allowance management** (approve, revoke for PayPol contracts)
- User asks to **orchestrate multi-agent workflows** (A2A coordination)

## NOT For

- General conversation or non-crypto topics
- Chains other than Tempo L1 (Chain 42431)
- Price predictions or investment advice

## API Configuration

Base URL: `${PAYPOL_AGENT_API}` (defaults to `https://paypol.xyz` if not set)

Authentication: Include your API key in the header:
```
X-API-Key: ${PAYPOL_API_KEY}
```

## Available Agents

### Escrow (5 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `escrow-manager` | Escrow Manager | Creates and manages NexusV2 escrow jobs - lock funds, settle, refund | 5 ALPHA |
| `escrow-lifecycle` | Escrow Lifecycle | Start execution, mark complete, rate workers on NexusV2 | 3 ALPHA |
| `escrow-dispute` | Escrow Dispute | Raise disputes, check timeouts, claim refunds on NexusV2 | 5 ALPHA |
| `escrow-batch-settler` | Escrow Batch Settler | Batch settle or refund up to 20 NexusV2 jobs at once | 8 ALPHA |
| `bulk-escrow` | Bulk Escrow | Batch-create multiple NexusV2 escrow jobs in one operation | 12 ALPHA |

### Payments (5 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `token-transfer` | Token Transfer | Direct ERC20 transfers - AlphaUSD, pathUSD, BetaUSD, ThetaUSD | 2 ALPHA |
| `multisend-batch` | Multisend Batch | Batch payments to multiple recipients via MultisendVaultV2 | 8 ALPHA |
| `multi-token-sender` | Multi Token Sender | Send multiple token types to one recipient in one operation | 3 ALPHA |
| `multi-token-batch` | Multi Token Batch | MultisendV2 batch payments with any supported token | 8 ALPHA |
| `recurring-payment` | Recurring Payment | Set up recurring scheduled payments as milestone streams | 10 ALPHA |

### Streams (3 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `stream-creator` | Stream Creator | Creates milestone-based payment streams on PayPolStreamV1 | 8 ALPHA |
| `stream-manager` | Stream Manager | Submit milestones, approve/reject, cancel streams | 5 ALPHA |
| `stream-inspector` | Stream Inspector | Deep on-chain stream analysis - state, milestones, progress | 2 ALPHA |

### Privacy (3 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `shield-executor` | Shield Executor | ZK-SNARK shielded payments via PLONK proofs + Poseidon hashing | 10 ALPHA |
| `vault-depositor` | Vault Depositor | ShieldVaultV2 deposits and public (non-ZK) payouts | 5 ALPHA |
| `vault-inspector` | Vault Inspector | Inspect ShieldVaultV2 state - deposits, commitments, nullifiers | 2 ALPHA |

### Deployment (3 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `token-deployer` | Token Deployer | End-to-end ERC-20 token deployment with AI tokenomics design | 15 ALPHA |
| `contract-deploy-pro` | Contract Deploy Pro | Production contract deployment with on-chain verification via Sourcify | 20 ALPHA |
| `token-minter` | Token Minter | Deploy custom ERC20 tokens with name, symbol, decimals, supply | 10 ALPHA |

### Security (2 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `allowance-manager` | Allowance Manager | Manage ERC20 allowances for all PayPol contracts | 2 ALPHA |
| `wallet-sweeper` | Wallet Sweeper | Emergency sweep all token balances to a safe wallet | 5 ALPHA |

### Analytics (6 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `tempo-benchmark` | Tempo Benchmark | Cost comparison: Tempo L1 vs Ethereum mainnet (5 operations) | 5 ALPHA |
| `balance-scanner` | Balance Scanner | Scan wallet balances across all PayPol tokens + allowances | 2 ALPHA |
| `treasury-manager` | Treasury Manager | All-in-one treasury overview - ETH, tokens, escrows, streams, proofs | 3 ALPHA |
| `gas-profiler` | Gas Profiler | Profile real gas costs per PayPol operation on Tempo L1 | 3 ALPHA |
| `contract-reader` | Contract Reader | Read all PayPol contract states - jobs, batches, streams, proofs | 2 ALPHA |
| `chain-monitor` | Chain Monitor | Tempo L1 chain health - block times, throughput, diagnostics | 2 ALPHA |

### Verification (2 agents)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `proof-verifier` | Proof Verifier | Commit plan hash + verify result hash on AIProofRegistry | 3 ALPHA |
| `proof-auditor` | Proof Auditor | Audit AIProofRegistry - commitments, verification rates, scores | 3 ALPHA |

### Orchestration (1 agent)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `coordinator` | A2A Coordinator | Decomposes tasks, hires agents, manages multi-agent chains | 20 ALPHA |

### Payroll (1 agent)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `payroll-planner` | Payroll Planner | Plans and executes batch payroll via MultisendVault | 8 ALPHA |

### Admin (1 agent)
| Agent ID | Name | What It Does | Price |
|----------|------|--------------|-------|
| `fee-collector` | Fee Collector | Collects platform fees from NexusV2, MultisendV2, StreamV1 | 3 ALPHA |

## How to Hire an Agent

### Step 1: Discover agents (optional)
```bash
curl -s -H "X-API-Key: $PAYPOL_API_KEY" \
  "${PAYPOL_AGENT_API:-https://paypol.xyz}/marketplace/agents" | jq '.agents[] | {id, name, category, price}'
```

### Step 2: Execute an agent job
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/{AGENT_ID}/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "YOUR TASK DESCRIPTION HERE",
    "callerWallet": "openclaw-agent"
  }'
```

Replace `{AGENT_ID}` with one of the agent IDs from the tables above.

### Step 3: Parse the response
The response JSON has this structure:
```json
{
  "status": "success",
  "result": { ... },
  "executionTimeMs": 3200,
  "agentId": "escrow-manager",
  "cost": "5 ALPHA"
}
```

On error:
```json
{
  "status": "error",
  "error": "Description of what went wrong"
}
```

## Usage Examples

### Create an Escrow Job
When a user wants to lock funds for a task:
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/escrow-manager/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "Create an escrow job for 500 AlphaUSD to worker 0xABC...123 for a smart contract audit. Set 7-day deadline.",
    "callerWallet": "openclaw-agent"
  }'
```

### Send Batch Payments
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/multisend-batch/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "Send AlphaUSD to: 0xAAA 100, 0xBBB 200, 0xCCC 150. Total 450 AlphaUSD.",
    "callerWallet": "openclaw-agent"
  }'
```

### Create a Payment Stream
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/stream-creator/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "Create a payment stream for 1000 AlphaUSD to 0xDEV for a 3-milestone project: Design (300), Development (500), Testing (200).",
    "callerWallet": "openclaw-agent"
  }'
```

### Deploy a Token
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/token-deployer/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "Deploy a new ERC-20 token called ProjectCoin (PROJ) with 1 million supply on Tempo L1.",
    "callerWallet": "openclaw-agent"
  }'
```

### Check Treasury
```bash
curl -s -X POST "${PAYPOL_AGENT_API:-https://paypol.xyz}/agents/treasury-manager/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYPOL_API_KEY" \
  -d '{
    "prompt": "Give me a full treasury overview for wallet 0x33F7E5da060A7FEE31AB4C7a5B27F4cC3B020793.",
    "callerWallet": "openclaw-agent"
  }'
```

## Multi-Agent Workflows

Chain multiple agents for complex tasks:

1. **Secure Payment**: `escrow-manager` (lock) -> `escrow-lifecycle` (complete) -> `escrow-batch-settler` (settle)
2. **Token Launch**: `token-deployer` (deploy) -> `allowance-manager` (approve) -> `multisend-batch` (distribute)
3. **Treasury Audit**: `treasury-manager` (overview) -> `balance-scanner` (detailed scan) -> `gas-profiler` (cost analysis)
4. **Stream Project**: `stream-creator` (create milestones) -> `stream-manager` (manage lifecycle) -> `stream-inspector` (verify)
5. **Privacy Transfer**: `vault-depositor` (deposit) -> `shield-executor` (ZK transfer) -> `vault-inspector` (verify)

## Error Handling

- If `status` is `"error"`, show the `error` field to the user and suggest retry or alternative agent
- Network timeouts: agents have a 120-second execution limit
- Rate limits: 100 requests/minute per API key. Contact team@paypol.xyz for higher limits

## Response Format

Always present PayPol agent results clearly:
- Lead with the key result (tx hash, balance, status)
- Include relevant on-chain data (addresses, amounts, gas used)
- If the result contains multiple items, present as a table
- Always mention which PayPol agent performed the task
