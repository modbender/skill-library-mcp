# @arkade-os/skill

Arkade skills for agent integration - send and receive Bitcoin over Arkade, onchain via onboard/offboard, Lightning Network via Boltz, and swap USDC/USDT via LendaSwap.

## Features

- **Bitcoin on Arkade**: Instant offchain Bitcoin transactions
- **Onchain Payments**: Get paid onchain (onboard) and pay onchain (offboard)
- **Lightning Network**: Pay and receive via Boltz submarine swaps
- **Stablecoin Swaps**: Trade BTC for USDC/USDT on Polygon, Ethereum, Arbitrum
- **CLI for Agents**: Command-line interface designed for MoltBot and other agents

**Default Server:** https://arkade.computer

## Installation

### As an Agent Skill

Install directly into your coding agent using the [Vercel Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add arkade-os/skill
```

This discovers the `arkade` skill and installs it into supported agents (Claude Code, Cursor, etc.).

You can also target a specific agent or install globally:

```bash
# Install to a specific agent
npx skills add arkade-os/skill --agent claude-code

# Install globally (user-level)
npx skills add arkade-os/skill -g
```

### As an npm Package

```bash
npm install @arkade-os/skill
# or
pnpm add @arkade-os/skill
```

## Quick Start

### CLI Usage

```bash
# Initialize wallet
arkade init <private-key-hex>

# Check balance
arkade balance

# Send Bitcoin
arkade send <ark-address> 50000

# Create Lightning invoice
arkade ln-invoice 25000 "Coffee payment"

# Pay Lightning invoice
arkade ln-pay lnbc...
```

### SDK Usage

```typescript
import { Wallet, SingleKey } from "@arkade-os/sdk";
import {
  ArkadeBitcoinSkill,
  ArkaLightningSkill,
  LendaSwapSkill,
} from "@arkade-os/skill";

// Create wallet
const wallet = await Wallet.create({
  identity: SingleKey.fromHex(privateKeyHex),
  arkServerUrl: "https://arkade.computer",
});

// Bitcoin operations
const bitcoin = new ArkadeBitcoinSkill(wallet);
const balance = await bitcoin.getBalance();
await bitcoin.send({ address: "ark1...", amount: 50000 });

// Lightning operations
const lightning = new ArkaLightningSkill({ wallet, network: "bitcoin" });
const invoice = await lightning.createInvoice({ amount: 25000 });

// Stablecoin swaps
const lendaswap = new LendaSwapSkill({ wallet });
const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `ArkadeBitcoinSkill` | Send/receive BTC via Arkade offchain, get paid onchain (onboard), pay onchain (offboard) |
| `ArkaLightningSkill` | Lightning payments via Boltz swaps |
| `LendaSwapSkill` | USDC/USDT swaps via LendaSwap |

## CLI Commands

| Command | Description |
|---------|-------------|
| `init <key> [url]` | Initialize wallet |
| `address` | Show Ark address |
| `boarding-address` | Show boarding address |
| `balance` | Show balance breakdown |
| `send <addr> <amt>` | Send sats |
| `history` | Transaction history |
| `onboard` | Get paid onchain: convert received onchain BTC to offchain |
| `offboard <addr>` | Pay onchain: send offchain BTC to an onchain address |
| `ln-invoice <amt>` | Create Lightning invoice |
| `ln-pay <bolt11>` | Pay Lightning invoice |
| `ln-fees` | Show swap fees |
| `ln-limits` | Show swap limits |
| `swap-quote <amt> <from> <to>` | Get stablecoin quote |
| `swap-to-stable <amt> <token> <chain> <addr>` | Swap BTC to stablecoin |
| `swap-to-btc <amt> <token> <chain> <addr>` | Swap stablecoin to BTC |
| `swap-status <id>` | Check swap status |
| `swap-pending` | Show pending swaps |
| `swap-pairs` | Show trading pairs |

## Configuration

- **Data:** `~/.arkade-wallet/config.json`

## Documentation

See [SKILL.md](./SKILL.md) for detailed agent integration documentation.

## License

MIT
