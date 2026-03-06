# Mint Club V2 — Agent Skills

AI agent skill for interacting with [Mint Club V2](https://mint.club) bonding curve tokens on Base.

## What is this?

This is an agent skill that enables AI agents (OpenClaw, Claude, etc.) to:

- **Query** token info, prices, and wallet balances
- **Trade** bonding curve tokens (buy/sell/zap)
- **Swap** any token pair via Uniswap V3/V4
- **Create** new bonding curve tokens with preset curves
- **Transfer** ETH and ERC-20 tokens

## Installation

### For OpenClaw agents

Copy the `SKILL.md` file to your agent's skills directory, or install via ClawHub:

```bash
clawhub install mintclub
```

### Manual setup

1. Install the CLI globally:
```bash
npm install -g mint.club-cli
```

2. Set up a wallet:
```bash
mc wallet --generate          # Generate new wallet
mc wallet --set-private-key 0x...  # Or import existing
```

3. Fund the wallet with ETH on Base for gas fees.

## Usage

See [SKILL.md](./SKILL.md) for the full command reference.

### Quick examples

```bash
# Check a token's price
mc price 0xDF2B673Ec06d210C8A8Be89441F8de60B5C679c9

# Buy 10 SIGNET with HUNT
mc buy SIGNET -a 10

# Swap ETH for HUNT
mc swap -i ETH -o HUNT -a 0.01

# Get wallet balances
mc wallet
```

## How Agents Use This

An AI agent reads `SKILL.md` to learn available commands, then executes them via shell. The CLI handles:

- Wallet management (`~/.mintclub/.env`)
- Auto swap routing (finds best V3/V4 path)
- ERC-20 approvals (auto-approves when needed)
- Transaction confirmation and error handling

## Links

- [Mint Club V2 Docs](https://docs.mint.club)
- [CLI Package (npm)](https://www.npmjs.com/package/mint.club-cli)
- [Community (OnChat)](https://onchat.sebayaki.com/mintclub)
