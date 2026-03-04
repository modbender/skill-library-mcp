# Setup Guide

## Requirements

- Node.js 18+ (Node 20 recommended for most features)
- npm or pnpm

## Installation

```bash
# Clone or copy the scripts folder
cd solana-funding-arb/scripts

# Install dependencies
npm install
```

## Configuration

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Configure RPC (Optional but Recommended)

For Zeta Markets support and faster scanning, use a dedicated RPC:

```env
# Helius (recommended - 100k free requests/day)
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_KEY

# Or Alchemy
SOLANA_RPC_URL=https://solana-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
```

Get free API keys:
- Helius: https://helius.xyz
- Alchemy: https://alchemy.com/solana

### 3. Wallet Setup (For Execution Only)

⚠️ **SECURITY WARNING**: Never share your private key!

For paper trading (simulation), no wallet is needed.

For live execution:
```env
# Base58 encoded private key
SOLANA_PRIVATE_KEY=your_private_key_here

# Or path to keypair file
SOLANA_KEYPAIR_PATH=/path/to/keypair.json
```

## Running

### CLI Scanner
```bash
npm run scan
```

### Web Dashboard
```bash
npm run start
# Open http://localhost:3456
```

### Zeta-Only Scanner (requires RPC)
```bash
npm run scan:zeta
```

## Troubleshooting

### Rate Limiting (429 errors)
Use a dedicated RPC instead of public endpoint.

### WebSocket Errors
Ensure Node.js 18+ is installed. The `rpc-websockets` package has compatibility issues with older versions.

### Missing Dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

## Architecture

```
scripts/
├── src/
│   ├── core/           # Aggregators for each DEX
│   ├── dashboard/      # Web UI
│   └── execution/      # Trade execution (future)
├── package.json
└── .env
```
