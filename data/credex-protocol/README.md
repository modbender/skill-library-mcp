# Credex Protocol Skill

OpenClaw skill for interacting with the Credex Protocol—unsecured credit lines for AI agents on Arc Network.

## Features

- **Borrower Commands**: Check credit status, borrow USDC, repay debt
- **LP Commands**: Deposit liquidity, withdraw with yield, check pool metrics
- **Cross-Chain**: Bridge USDC between Arc and Base via Circle Bridge

## Installation

The skill is automatically installed when placed in `~/.openclaw/workspace/skills/credex-protocol/`.

## Quick Start

### Setup Environment

```bash
export WALLET_PRIVATE_KEY=0x...
export CREDEX_POOL_ADDRESS=0x60C04c09ee252C4e99C1B56580F7A0D3c65a3b36
export RPC_URL=https://rpc.testnet.arc.network
```

### Borrower (Client)

```bash
# Check your credit status
npx ts-node scripts/client.ts status

# Borrow 5 USDC
npx ts-node scripts/client.ts borrow 5

# Repay all debt
npx ts-node scripts/client.ts repay all

# Bridge to Base
npx ts-node scripts/client.ts bridge 10 arc base
```

### Liquidity Provider (LP)

```bash
# Check pool status
npx ts-node scripts/lp.ts pool-status

# Deposit 100 USDC
npx ts-node scripts/lp.ts deposit 100

# Withdraw all shares
npx ts-node scripts/lp.ts withdraw all
```

## Files

```
credex-protocol/
├── SKILL.md              # Main skill documentation
├── README.md             # This file
├── scripts/
│   ├── client.ts         # Borrower CLI
│   └── lp.ts             # LP CLI
└── references/
    └── contracts.md      # ABIs and contract info
```

## Dependencies

- `ethers` (v6)
- `@circle-fin/bridge-kit`
- `@circle-fin/adapter-viem-v2`
- `tsx` or `ts-node`

## Networks

- **Arc Testnet**: Chain ID 1328
- **Base Sepolia**: Chain ID 84532

## License

MIT
