# 🤖 Gekko — AI-Powered DeFi Portfolio Manager

AI-powered DeFi portfolio manager for Base network. Analyze yield opportunities, manage portfolio allocations, and provide market intelligence.

## � Quick Start

```bash
# Use via A2A API
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "yield_optimization",
    "parameters": {
      "asset": "USDC",
      "risk_tolerance": "medium"
    }
  }'
```

## 📋 Capabilities

### Portfolio Management
Analyze yield opportunities across Base DeFi protocols. Get real-time vault APY analysis from Morpho and Yearn.

### Token Analysis
Retrieve live price, volume, and liquidity data from DexScreener for any token.

### Yield Optimization
Find the best yields on Base. Compare APYs, TVL, and risk profiles across all monitored vaults.

### Market Intelligence
Get market insights, trend analysis, and trading signals. Analyze DeFi market conditions.

### Chat
Open-ended conversation about markets, strategies, tokens, and yields.

## 📊 Monitored Vaults

| Vault | Address |
|-------|---------|
| Seamless USDC | `0x616a4E1db48e22028f6bbf20444Cd3b8e3273738` |
| Moonwell USDC | `0xc1256Ae5FFc1F2719D4937adb3bbCCab2E00A2Ca` |
| Spark USDC | `0x7bFA7C4f149E7415b73bdeDfe609237e29CBF34A` |
| Gauntlet USDC Prime | `0xe8EF4eC5672F09119b96Ab6fB59C27E1b7e44b61` |
| Yo USDC | `0x0000000f2eB9f69274678c76222B35eEc7588a65` |

## 🔧 API Endpoint

```
https://gekkoterminal.ai/api/a2a?agent=gekko
```

## Requirements

- API access to Gekko endpoint
- Base network for vault data
- No wallet or private keys required (read-only)

## Security

All vault contracts are open-source, verified on-chain, and subject to third-party audits. Real-time monitoring ensures transparency at every layer.

---

**Built by Gekko AI. Powered by ERC-8004.**
