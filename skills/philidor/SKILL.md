---
name: philidor
description: >
  DeFi vault intelligence: risk scores, yield comparison, portfolio analysis,
  and oracle monitoring across Morpho, Yearn, Aave, Beefy, and Spark.
  Use when the user wants to find safe DeFi vaults, compare yields,
  check vault risk scores, analyze a wallet's DeFi positions, search for
  yield opportunities, monitor oracle freshness, or get DeFi market overview stats.
  Covers Ethereum, Base, Arbitrum, Polygon, Optimism, and Avalanche.
version: 0.1.1
metadata:
  {
    'openclaw':
      {
        'emoji': '🏰',
        'homepage': 'https://philidor.io',
        'requires': { 'bins': ['philidor'] },
        'install':
          [
            {
              'kind': 'node',
              'package': '@philidorlabs/cli',
              'bins': ['philidor'],
              'label': 'Install Philidor CLI',
            },
          ],
      },
  }
---

# Philidor — DeFi Vault Intelligence

Institutional-grade risk scores, yield comparison, portfolio analysis, and oracle monitoring for DeFi vaults across five major protocols and six chains.

## Quick Start

```bash
# Platform overview — total TVL, vault counts, risk distribution
philidor stats

# Search vaults by name, symbol, or asset
philidor search "USDC"

# Analyze all DeFi positions for a wallet address
philidor portfolio 0xYourWalletAddress
```

## Core Concepts

### Risk Tiers

Every vault receives a composite risk score from 0 to 10, grouped into three tiers:

| Tier        | Score Range | Meaning                                                                                        |
| ----------- | ----------- | ---------------------------------------------------------------------------------------------- |
| **Prime**   | 8.0 - 10.0  | Institutional-grade. Battle-tested protocols, blue-chip assets, strong governance controls.    |
| **Core**    | 5.0 - 7.9   | Solid fundamentals with some trade-offs in asset quality, audit coverage, or decentralisation. |
| **Edge**    | 0.0 - 4.9   | Higher risk. Newer protocols, exotic assets, weaker control structures, or recent incidents.   |
| **Unrated** | N/A         | Insufficient data to score. Treated as high-risk by default.                                   |

Scores are derived from three weighted vectors:

- **Asset Quality (40%)** — collateral quality, oracle reliability, liquidity depth, peg stability
- **Platform & Strategy (40%)** — smart contract maturity, audit coverage, TVL track record, incident history
- **Control & Governance (20%)** — timelock presence, multisig configuration, upgradeability, admin powers

### APR (Annual Percentage Rate)

APR values are stored as **decimals**: `0.05` means **5%**.

- **`apr_net`** — total APR including base yield plus any incentive rewards
- **`base_apr`** — native protocol yield only (lending rate, share price accrual), before rewards
- **Invariant**: `apr_net = base_apr + SUM(reward APRs)`

Reward types include `token_incentive` (MORPHO, ARB, SPK), `points`, `trading_fee` (LP fees), and `strategy` (Yearn sub-strategies).

### Protocols

| Protocol     | Description                                                                          |
| ------------ | ------------------------------------------------------------------------------------ |
| **Morpho**   | Optimised lending with curated vaults (Ethereum, Base)                               |
| **Yearn v3** | Automated yield strategies (Ethereum, Polygon, Arbitrum, Base, Optimism)             |
| **Aave v3**  | Blue-chip lending/borrowing (Ethereum, Polygon, Arbitrum, Avalanche, Optimism, Base) |
| **Beefy**    | Multi-chain yield optimiser (12+ chains)                                             |
| **Spark**    | MakerDAO lending markets (Ethereum)                                                  |

### Chains

Ethereum, Base, Arbitrum, Polygon, Optimism, and Avalanche.

## Commands

### Discovery & Search

```bash
# List vaults with filters
philidor vaults
philidor vaults --chain ethereum
philidor vaults --protocol morpho
philidor vaults --risk-tier prime
philidor vaults --asset USDC
philidor vaults --min-tvl 1000000
philidor vaults --stablecoin --audited
philidor vaults --high-confidence             # Only vaults with high data confidence
philidor vaults --no-il                       # Exclude vaults with impermanent loss risk
philidor vaults --sort apr_net:desc --limit 10 --page 2

# Search vaults by name, protocol, asset, or address
philidor search "USDC"
philidor search "Aave"
philidor search "Gauntlet"
philidor search "USDC" --limit 20             # Control result count (default: 10)

# For filtered queries, use `vaults` with flags instead of search:
philidor vaults --asset USDC --chain base --risk-tier prime
philidor vaults --asset WETH --protocol morpho --sort apr_net:desc
```

### Vault Detail

```bash
# By vault ID
philidor vault <vault-id>

# By network slug + contract address
philidor vault ethereum 0x1234...

# Sub-resources (require network + address form)
philidor vault ethereum 0x1234... --events       # Event history (incidents, parameter changes)
philidor vault ethereum 0x1234... --markets      # Morpho market allocations
philidor vault ethereum 0x1234... --strategies   # Yearn strategies
philidor vault ethereum 0x1234... --rewards      # Reward breakdown (base + incentives)
```

### Portfolio

```bash
# All positions across all chains
philidor portfolio 0xWalletAddress

# Filter to a specific chain
philidor portfolio 0xWalletAddress --chain base
```

Returns: vault details, chain, balance in USD, APR, risk score, risk tier for each position. Includes aggregates: total value, weighted risk, position count, risk distribution.

### Comparison & Risk

```bash
# Side-by-side vault comparison (2-5 vault IDs)
philidor compare <vault-id-1> <vault-id-2> <vault-id-3>

# Detailed risk vector breakdown for a specific vault
philidor risk breakdown <vault-id>
philidor risk breakdown ethereum 0x1234...

# Explain the risk scoring methodology — tiers, vectors, weights
philidor risk explain

# Vaults with recent critical security incidents
philidor risk incidents
```

### Reference Data

```bash
# List all supported protocols with vault counts and TVL
philidor protocols

# Protocol detail — audit status, chain coverage, incident history
philidor protocol <id>

# List curators (Morpho vault managers)
philidor curators
philidor curators --sort tvl_total:desc --limit 10 --page 1

# Curator detail — managed vaults, TVL, performance
philidor curator <id>

# Platform overview — total TVL, vault counts, risk distribution
philidor stats

# Supported chains
philidor chains

# Supported assets
philidor assets

# Oracle feed freshness and deviation data
philidor oracles freshness
```

### Output Formats

All commands support three output formats:

```bash
philidor vaults --json       # Structured JSON (best for agents and scripting)
philidor vaults --table      # Human-readable table (default in TTY)
philidor vaults --csv        # CSV for spreadsheets and data pipelines
```

When output is piped (non-TTY), JSON is the default. Use `--json` explicitly in agent workflows for consistency.

Additional global flags:

```bash
--api-url <url>              # Override API base URL (default: https://api.philidor.io)
                             # Also respects PHILIDOR_API_URL environment variable
```

## Agent Workflows

### Workflow 1: Find the Best Vault for a User's Needs

Step-by-step pattern for recommending a vault based on user criteria.

```bash
# Step 1: Search for matching vaults
philidor search "stablecoin vault on base" --json
# Returns matched vaults with TVL, APR, risk tier

# Step 2: Compare the top candidates side-by-side
philidor compare <vault-id-1> <vault-id-2> <vault-id-3> --json
# Compares TVL, APR (base + rewards), risk score, audited status, curator

# Step 3: Deep-dive into the risk profile of the chosen vault
philidor risk breakdown <chosen-vault-id> --json
# Full risk vector breakdown:
#   - Asset risk (collateral quality, oracle reliability, liquidity depth)
#   - Platform risk (smart contract maturity, audit coverage, incident history)
#   - Control risk (governance, timelock, upgradeability, admin powers)

# Step 4: Check recent events for any red flags
philidor vault <network> <address> --events --json
# Recent events: incidents, parameter changes, pauses

# Decision: Recommend the vault with the best risk-adjusted yield.
# Flag any Edge-tier vaults or recent incidents to the user.
```

### Workflow 2: Compare Protocols for Yield Farming

Step-by-step pattern for cross-protocol yield comparison.

```bash
# Step 1: Get protocol overview
philidor protocols --json
# Lists all protocols with vault counts, TVL, risk distribution

# Step 2: Get top vaults per protocol (can run in parallel)
philidor vaults --protocol morpho --sort apr_net:desc --limit 5 --json
philidor vaults --protocol aave-v3 --sort apr_net:desc --limit 5 --json
philidor vaults --protocol yearn-v3 --sort apr_net:desc --limit 5 --json
# Top 5 vaults per protocol ranked by yield

# Step 3: Compare the best vaults across protocols
philidor compare <best-morpho-id> <best-aave-id> <best-yearn-id> --json
# Cross-protocol comparison for the same asset class

# Step 4: Get protocol-level details
philidor protocol morpho --json
# Protocol detail: audit status, versions, incident history, chain coverage

# Decision: Compare yield vs risk across protocols.
# Note audited vs unaudited versions and flag incident history.
```

### Workflow 3: Analyze Portfolio Risk

Step-by-step pattern for assessing and improving a wallet's DeFi risk profile.

```bash
# Step 1: Get all positions
philidor portfolio 0xWalletAddress --json
# All positions: vault, chain, balance_usd, APR, risk_score, risk_tier
# Aggregates: total value, weighted risk, position count, risk distribution

# Step 2: Identify risky positions
# Filter results for positions with risk_tier = "Edge" or risk_score < 5

# Step 3: Investigate each risky position
philidor risk breakdown <risky-vault-id> --json
# What is driving the low score? Asset? Platform? Control?

# Step 4: Find safer alternatives for the same asset
philidor search "USDC prime audited" --json
# Or use:
philidor vaults --asset USDC --risk-tier prime --audited --json
# Find Prime-tier alternatives for the same asset

# Decision: Present a portfolio risk summary to the user.
# Highlight Edge-tier positions and suggest Prime alternatives
# with comparable or better yield.
```

### Workflow 4: Monitor Vault Safety

Step-by-step pattern for ongoing safety monitoring.

```bash
# Step 1: Check for active incidents across all protocols
philidor risk incidents --json
# Vaults with recent critical incidents

# Step 2: Check oracle health
philidor oracles freshness --json
# Oracle feed freshness: stale feeds, deviation alerts

# Step 3: Check event history for a specific vault
philidor vault <network> <address> --events --json
# Event timeline: incidents, parameter changes, pauses

# Decision: Flag vaults with active incidents or stale oracle feeds.
# Recommend pausing deposits until issues are resolved.
```

## Interpreting Output

Key fields and their formats:

| Field            | Format          | Example                                   | Notes                                                            |
| ---------------- | --------------- | ----------------------------------------- | ---------------------------------------------------------------- |
| `apr_net`        | Decimal         | `0.0523`                                  | Total APR = 5.23%. Includes base yield + rewards.                |
| `base_apr`       | Decimal         | `0.0340`                                  | Base yield only = 3.40%. Native protocol rate before incentives. |
| `tvl_usd`        | Number (string) | `"12500000.50"`                           | Total value locked in USD. Returned as string for precision.     |
| `total_score`    | Number or null  | `8.3`                                     | Composite risk score 0-10. Null means unrated.                   |
| `risk_tier`      | String          | `"Prime"`                                 | Derived from total_score: Prime (>=8), Core (5-7.9), Edge (<5).  |
| `risk_vectors`   | Object          | `{"asset":{"score":8.5},...}`             | Breakdown: asset (40%), platform (40%), control (20%).           |
| `is_audited`     | Boolean         | `true`                                    | Whether the protocol version has been audited.                   |
| `last_synced_at` | ISO 8601        | `"2026-02-26T12:00:00Z"`                  | When the vault data was last refreshed from on-chain.            |
| `rewards`        | Array           | `[{"token_symbol":"MORPHO","apr":0.018}]` | Individual reward token APRs. Sum + base_apr = apr_net.          |

## Error Handling

| Error                   | Cause                                     | Fix                                                                                                                      |
| ----------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `Connection refused`    | API server unreachable                    | Check network connectivity. Verify `--api-url` if using a custom endpoint. The default is `https://api.philidor.io`.     |
| `404 Not Found`         | Invalid vault ID, protocol ID, or address | Verify the vault ID exists with `philidor vaults`. Check that the network slug is correct (e.g., `ethereum`, not `eth`). |
| `429 Too Many Requests` | Rate limit exceeded                       | Wait and retry. The public API allows generous read limits but has per-IP throttling. Space out bulk queries.            |
| `Request timeout`       | API response took too long                | Retry the request. For large result sets, use `--limit` to reduce page size.                                             |
| `Invalid chain`         | Unsupported chain slug                    | Run `philidor chains` to see valid chain slugs.                                                                          |

## Best Practices

1. **Always use `--json` in agent workflows.** JSON output is structured, stable, and machine-parseable. Table output is for human consumption only and may change format between versions.

2. **Check risk before recommending any vault.** Never recommend a vault based on APR alone. Always run `philidor risk breakdown <id>` and check for Edge-tier scores or recent incidents via `philidor risk incidents`.

3. **Note data freshness timestamps.** The `last_synced_at` field indicates when vault data was last refreshed from on-chain sources. Data older than a few hours may not reflect current APR or TVL. Flag stale data to users.

4. **Cross-reference incidents and oracle health.** Before recommending a vault, check `philidor risk incidents` for active security events and `philidor oracles freshness` for stale price feeds. These can materially affect vault safety.

5. **Use portfolio context for personalised advice.** When a user has a wallet address, start with `philidor portfolio <address>` to understand their existing positions before suggesting new vaults. This enables risk-aware recommendations that consider concentration and diversification.

## Resources

- **Website**: [https://philidor.io](https://philidor.io)
- **API Documentation**: [https://api.philidor.io/v1/docs](https://api.philidor.io/v1/docs)
- **Risk Methodology**: `philidor risk explain` or [https://philidor.io/risk](https://philidor.io/risk)
