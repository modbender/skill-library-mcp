# 🚀 Solana Funding Rate Arbitrage Scanner

## Put Your Idle Coins to Work!

This tool scans funding rates across Solana perpetual DEXes to find **delta-neutral arbitrage opportunities**.

## 💡 How It Works

Perpetual futures have a "funding rate" mechanism:
- **Positive rate**: Longs pay Shorts
- **Negative rate**: Shorts pay Longs

Different DEXes can have different funding rates for the same asset. By exploiting this difference:

```
DEX A: SOL Funding = -500% APY (Longs earn)
DEX B: SOL Funding = +800% APY (Shorts earn)

Strategy:
→ Open Long on DEX A (receive funding)
→ Open Short on DEX B (receive funding)
→ Zero price risk (hedged)
→ Collect funding from both sides!
```

## 📊 Supported DEXes

| DEX | Markets | Features |
|-----|---------|----------|
| Drift Protocol | 64 | Largest Solana perp DEX |
| Flash Trade | 19 | Low fees |
| GMTrade | 37 | GMX on Solana |
| Zeta Markets | 24 | Options + Perps |

## 🛠️ Installation

### 1. Requirements
- Node.js 18 or higher
- npm or pnpm

### 2. Setup
```bash
cd scripts
npm install
```

### 3. Configuration (Optional)

Create a `.env` file:
```bash
cp .env.example .env
```

**Recommended:** Get a free Helius RPC key:
1. Go to https://helius.xyz
2. Create a free account
3. Copy your API key
4. Add to `.env`:
```env
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
```

## 🚀 Usage

### CLI Scanner
```bash
npm run scan
```

Output:
```
═══════════════════════════════════════════════════════════════
⚡ SOLANA DEX FUNDING RATE COMPARISON
═══════════════════════════════════════════════════════════════

Symbol  | Drift APY    | Flash APY    | Spread   | Arbitrage
────────────────────────────────────────────────────────────────
SOL     | 🟢 -3037%   | 🔴 +3626%   | 6663%   | Long Drift, Short Flash
BTC     | 🟢 -617%    | 🔴 +2330%   | 2947%   | Long Drift, Short Flash
```

### Web Dashboard
```bash
npm run start
```
Open in browser: http://localhost:3456

## 📈 Implementing the Strategy

### Step 1: Find Opportunity
Use the dashboard or CLI to find high-spread assets.

### Step 2: Open Hedged Position
Example: SOL with 1300% spread

| DEX | Position | Size | Funding |
|-----|----------|------|---------|
| Drift | Long | 10 SOL | Receiving |
| Flash | Short | 10 SOL | Receiving |

### Step 3: Collect Funding
Receive funding payments every 8 hours (varies by DEX).

### Step 4: Close When Done
Close positions when spread narrows or reverses.

## ⚠️ Risks

1. **Spread Reversal**: Rates can flip direction quickly
2. **Execution Risk**: Slippage when opening/closing
3. **Liquidity**: Large positions may face issues
4. **Liquidation**: Be careful with leverage!
5. **Platform Risk**: Smart contract risks exist

## 💰 Expected Returns

- High spreads (>500% APY diff): ~1-2% daily
- Medium spreads (>100% APY diff): ~0.1-0.5% daily
- Subtract fees and slippage from estimates

## 🔐 Security

- **Never share your private key!**
- Add `.env` to `.gitignore`
- Start with small amounts
- DYOR (Do Your Own Research)

## 🔧 Advanced Configuration

### Custom RPC Providers
```env
# Helius (recommended)
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY

# Alchemy
SOLANA_RPC_URL=https://solana-mainnet.g.alchemy.com/v2/YOUR_KEY

# QuickNode
SOLANA_RPC_URL=https://your-quicknode-endpoint.com
```

### Wallet Setup (For Future Execution)
```env
# Base58 private key (KEEP SECRET!)
SOLANA_PRIVATE_KEY=your_private_key

# Or keypair file path
SOLANA_KEYPAIR_PATH=/path/to/keypair.json
```

## 🤝 Support

- Discord: [Clawdbot Community](https://discord.com/invite/clawd)
- Issues: Open on GitHub

---

*This tool is for informational purposes only. Not financial advice. Do your own research and only trade with funds you can afford to lose.*
