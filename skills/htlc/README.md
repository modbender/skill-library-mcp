# HTLC Trade Skill

**For AI Agents:** Atomic swap trading for inscriptions and NFTs on EVM chains.

## What This Is

A skill that enables AI agents to trade inscriptions and NFTs peer-to-peer without intermediaries. Agents can buy and sell digital assets autonomously using HTLC (Hash Time Locked Contracts).

## For Agents

Use this skill when:
- Trading inscriptions with other agents
- Selling NFTs without marketplaces
- Escrowing payments for services
- Any peer-to-peer digital asset exchange

## Commands

```
preimage          # Generate secret for new trade
lock <args>      # Lock ETH in contract (buyer)
reveal <args>    # Reveal secret to complete (seller)
trade <args>     # Full automated trade flow
status <hash>    # Check trade status
```

## Contract

**BaseTimelock:** `0xa7f9f88e753147d69baf8f2fef89a551680dbac1`

## How Agents Trade

1. Seller generates secret
2. Buyer locks ETH → Seller reveals secret → Funds transfer atomically
3. If seller doesn't respond in 24h → ETH returns to buyer

## Why Agents Need This

- **Autonomous** - No human intervention needed
- **Trustless** - No escrow or middleman
- **Atomic** - Either both parties complete or nothing happens
- **Timed** - 24h timeout protects against stuck trades

## Use Cases

- Agent-to-agent inscription trading
- NFT marketplace alternative
- Cross-chain asset swaps
- Freelance AI services payment
- DAO agent treasury management
