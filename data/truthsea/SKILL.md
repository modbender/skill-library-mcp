---
name: truthsea
description: Verify claims, build epistemological dependency graphs, and earn
  TRUTH tokens on Base L2. Security-hardened contracts (V2.5) with
  ReentrancyGuard, era emission caps, and Slither-audited code.
---


# TruthSea Verifier

Verify claims, build epistemological dependency graphs, and earn TRUTH tokens on Base L2. Security-hardened contracts (V2.5) with ReentrancyGuard, era emission caps, and Slither-audited code.

**Runs in read-only mode by default.** Supply `DEPLOYER_PRIVATE_KEY` to enable write operations (submit quanta, create edges, dispute). Use a dedicated hot wallet with minimal funds — never your main wallet.

## Setup

This skill requires the `truthsea-mcp-server` MCP server. It will be configured automatically when installed.

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEPLOYER_PRIVATE_KEY` | **Yes, for write ops** | Wallet private key for on-chain transactions. Without it, the server runs in **read-only mode**. Use a dedicated hot wallet, not your main wallet. |
| `TRUTHSEA_NETWORK` | No | Network to use. Default: `base_sepolia` |
| `TRUTH_DAG_ADDRESS` | **Yes, for V2 DAG** | TruthDAG contract address. Without it, V2 DAG tools are disabled. |
| `TRUTH_STAKING_ADDRESS` | **Yes, for V2 DAG** | TruthStaking contract address. Required for edge creation and staking. |

> **Security note:** `DEPLOYER_PRIVATE_KEY` grants on-chain transaction authority. Always use a dedicated hot wallet with minimal funds. The server never transmits or logs this key — it is used only for signing transactions locally.

## Tools

### Truth Verification (V1)

- **`truthsea_submit_quantum`** — Submit a new truth quantum with a claim, 4-pillar truth scores, and 8-dimensional moral vector. Requires wallet.
- **`truthsea_verify_quantum`** — Submit verification scores for an existing quantum. Requires wallet.
- **`truthsea_query`** — Query and search quanta by discipline, score threshold, or claim text. Read-only.
- **`truthsea_dispute`** — Challenge a quantum with counter-evidence. Creates a fork and slashes the original host. Requires wallet.

### Bounty Bridge (CrowdedSea)

- **`crowdedsea_list_bounties`** — List bounties filtered by status, discipline, and minimum reward. Read-only.
- **`crowdedsea_claim_bounty`** — Claim a bounty for investigation. Requires wallet.

### Dependency Graph (V2 DAG)

- **`truthsea_create_edge`** — Create a dependency edge between two quanta. Stakes TRUTH tokens as collateral. Requires wallet + DAG configured.
- **`truthsea_dispute_edge`** — Challenge a dependency edge. If justified, earn TRUTH from the proposer's slashed stake. Requires wallet.
- **`truthsea_get_chain_score`** — Get the propagated chain score for a quantum. Shows how dependency strength, contradiction penalties, and weakest links affect the score. Read-only.
- **`truthsea_explore_dag`** — Navigate the epistemological dependency graph in ancestors, descendants, or both directions via BFS traversal. Read-only.
- **`truthsea_find_weak_links`** — Find weak foundations in the dependency chain — edges below confidence or score thresholds. Read-only.
- **`truthsea_flag_weak_link`** — Flag a weak edge for the bounty program. Earn 100 TRUTH if the edge is later invalidated within 30 days. Requires wallet.

### Chain Score Formula

```
chainScore = intrinsicScore * (floor + damping * weakestDepChainScore / 10000) / 10000
```

Where:
- `intrinsicScore` = weighted average of 4 truth frameworks (30% correspondence, 25% coherence, 25% convergence, 20% pragmatism)
- `floor` = 3000 (0.30 minimum preservation)
- `damping` = 7000 (0.70 attenuation factor)
- Contradiction penalty: -15% per contradicting edge (min 40% preservation)

## Scoring System

### Truth Frameworks (0-100 each)

1. **Correspondence** — Maps to observable reality
2. **Coherence** — Fits the web of known truths
3. **Convergence** — Independent sources agree over time
4. **Pragmatism** — Works in practice

### Moral Vector (-100 to +100 each)

1. **Care** / Harm
2. **Fairness** / Cheating
3. **Loyalty** / Betrayal
4. **Authority** / Subversion
5. **Sanctity** / Degradation
6. **Liberty** / Oppression
7. **Epistemic Humility** / Dogmatism
8. **Temporal Stewardship** / Short-term Extraction

## Commands

### Truth Verification (V1)

| Command | Description |
|---------|-------------|
| `/verify <claim>` | Submit a claim for multi-dimensional truth verification |
| `/truth query <search>` | Search verified truth quanta |
| `/dispute <id> <claim>` | Challenge a quantum with counter-evidence |

### Dependency Graph (V2)

| Command | Description |
|---------|-------------|
| `/edge create <sourceId> <targetId>` | Create a dependency edge between quanta |
| `/edge dispute <edgeId>` | Challenge an edge — earn TRUTH if justified |
| `/dag explore <quantumId>` | Navigate the dependency graph |
| `/dag score <quantumId>` | Get the propagated chain score |
| `/dag weak-links <quantumId>` | Find weak foundations in the dependency chain |
| `/dag flag <edgeId>` | Flag a weak edge — earn 100 TRUTH bounty if validated |

### Bounties (CrowdedSea)

| Command | Description |
|---------|-------------|
| `/bounty list` | List available truth bounties with ETH rewards |
| `/bounty claim <id>` | Claim a bounty for investigation |

> **Note:** V2 DAG commands require TruthDAG contract address to be configured.

## Token Incentives

| Action | Reward |
|--------|--------|
| Host a quantum | 100 TRUTH |
| Verify a quantum | 10 TRUTH |
| Create an edge (survives 7 days) | 20 TRUTH |
| Trigger score propagation | 2 TRUTH |
| Validated weak-link flag | 100 TRUTH |
| Win edge dispute | 60% of proposer's stake + 20 TRUTH |

## Contracts (Base Sepolia)

- **TruthToken**: `0x18D825cE88089beFC99B0e293f39318D992FA07D`
- **TruthRegistryV2**: `0xbEE32455c12002b32bE654c8E70E876Fd557d653`
- **BountyBridge**: `0xA255A98F2D497c47a7068c4D1ad1C1968f88E0C5`

## Security (V2.5)

- ReentrancyGuard on all ETH transfer functions
- Per-era emission caps enforced (halving schedule)
- Slither static analysis with 0 high/critical findings
- API rate limiting, CORS whitelist, CSP headers

## Links

- [GitHub](https://github.com/turfptax/TruthSea)
- [Website](https://truthsea.io)
- [API Docs](https://truthsea.io/api/v1)
- [Contracts on Basescan](https://sepolia.basescan.org/address/0xbEE32455c12002b32bE654c8E70E876Fd557d653)
