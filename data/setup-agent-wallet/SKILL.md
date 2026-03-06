---
name: setup-agent-wallet
description: Set up an agent wallet for Uniswap operations. Use when user needs to provision a wallet for an autonomous agent. Supports Privy (development), Turnkey (production), and Safe (maximum security). Configures spending limits, token allowlists, and funds the wallet for gas.
model: opus
allowed-tools: [Task(subagent_type:wallet-provisioner)]
---

# Set Up Agent Wallet

## Overview

Provision and configure a wallet for autonomous Uniswap agent operations. Supports three wallet providers at different security tiers. Handles the full lifecycle: provision wallet, configure safety policies, fund for gas, and validate the setup.

## When to Use

Activate when the user says:

- "Set up a wallet"
- "Configure agent wallet"
- "Provision wallet"
- "Initialize wallet"
- "Set up a wallet for my agent"
- "Create a new agent wallet"

## Parameters

Extract these from the user's request:

| Parameter       | Required | Default       | Description                                                                                  |
| --------------- | -------- | ------------- | -------------------------------------------------------------------------------------------- |
| `provider`      | No       | `privy`       | Wallet provider: `privy` (development), `turnkey` (production), or `safe` (maximum security) |
| `chains`        | No       | `all`         | Chains to configure — chain names or "all" for all supported chains                          |
| `environment`   | No       | `development` | Either `development` or `production`                                                         |
| `spendingLimit` | No       | `$1000/day`   | Daily spending limit (e.g., "$1000/day", "$500/day")                                         |

### Provider Selection Guide

- **Privy**: Best for development and testing. Fast setup, easy to manage. Not recommended for production with significant funds.
- **Turnkey**: Production-grade key management with TEE (Trusted Execution Environment). Use for real trading with moderate funds.
- **Safe**: Maximum security via multi-sig smart account. Use for high-value operations or institutional setups.

## Workflow

1. **Parse user intent**: Determine the wallet provider, target chains, environment, and spending limit from the user's request. Apply defaults for any unspecified parameters.

2. **Delegate to `wallet-provisioner` agent**: Hand off the provisioning task with the extracted parameters. The agent handles the full setup pipeline:
   - **Provision**: Create the wallet via the selected provider's API
   - **Configure policies**: Set spending limits (per-tx and daily), token allowlists, and rate limits
   - **Fund**: Send gas tokens to the wallet on each requested chain
   - **Validate**: Confirm the wallet is operational by verifying balances and policy configuration

3. **Report results**: Present the wallet setup summary to the user.

## Agent Delegation

This skill delegates to the `wallet-provisioner` agent:

```
Task(subagent_type:wallet-provisioner)
  provider: <privy|turnkey|safe>
  chains: <chain list>
  environment: <development|production>
  spendingLimit: <daily limit>
```

The agent internally handles all provisioning steps and returns the final wallet configuration.

## Output Format

```text
Agent Wallet Configured

  Address:    0x1234...ABCD
  Provider:   Privy (development)
  Chains:     Ethereum, Base, Arbitrum
  Limits:     $1,000/day, $500/tx
  Allowlist:  USDC, WETH, UNI, ARB (4 tokens)
  Gas:        Funded on all 3 chains

  Config: .uniswap/agent-wallet.json
```

## Error Handling

| Error                  | User-Facing Message                                              | Suggested Action                                     |
| ---------------------- | ---------------------------------------------------------------- | ---------------------------------------------------- |
| `PROVIDER_AUTH_FAILED` | "Could not authenticate with [provider]. Check API keys."        | Verify provider credentials in environment variables |
| `FUNDING_FAILED`       | "Could not fund wallet on [chain]. Insufficient source balance." | Fund the source wallet first                         |
| `CHAIN_NOT_SUPPORTED`  | "[chain] is not supported by [provider]."                        | Choose a different chain or provider                 |
