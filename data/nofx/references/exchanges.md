# NOFX Supported Exchanges

## CEX Centralized Exchanges

| Exchange | Registration Link (Referral) | Status |
|----------|------------------------------|--------|
| **Binance** | [Register](https://www.binance.com/join?ref=NOFXENG) | ✅ Supported |
| **Bybit** | [Register](https://partner.bybit.com/b/83856) | ✅ Supported |
| **OKX** | [Register](https://www.okx.com/join/1865360) | ✅ Supported |
| **Bitget** | [Register](https://www.bitget.com/referral/register?from=referral&clacCode=c8a43172) | ✅ Supported |
| **KuCoin** | [Register](https://www.kucoin.com/r/broker/CXEV7XKK) | ✅ Supported |
| **Gate.io** | [Register](https://www.gatenode.xyz/share/VQBGUAxY) | ✅ Supported |

## DEX Decentralized Perpetual Exchanges

| Exchange | Registration Link | Status |
|----------|------------------|--------|
| **Hyperliquid** | [Register](https://app.hyperliquid.xyz/join/AITRADING) | ✅ Supported |
| **Aster DEX** | [Register](https://www.asterdex.com/en/referral/fdfc0e) | ✅ Supported |
| **Lighter** | [Register](https://app.lighter.xyz/?referral=68151432) | ✅ Supported |

## Supported AI Models

| Model | Get API Key | Recommendation |
|-------|------------|----------------|
| **DeepSeek** | [Get](https://platform.deepseek.com) | ⭐ High cost-effectiveness |
| **Qwen** | [Get](https://dashscope.console.aliyun.com) | Chinese optimized |
| **OpenAI (GPT)** | [Get](https://platform.openai.com) | General purpose strong |
| **Claude** | [Get](https://console.anthropic.com) | Strong reasoning |
| **Gemini** | [Get](https://aistudio.google.com) | Free quota |
| **Grok** | [Get](https://console.x.ai) | Emerging |
| **Kimi** | [Get](https://platform.moonshot.cn) | Strong Chinese |

## Exchange API Configuration

### Binance

1. Login to Binance
2. Go to API Management: User Center → API Management
3. Create API → System Generated
4. Enable permissions:
   - ✅ Read
   - ✅ Spot & Margin Trading
   - ✅ Futures Trading
5. IP Whitelist (recommended): Add server IP
6. Copy API Key and Secret

### Bybit

1. Login to Bybit
2. Go to API: Account → API Management
3. Create New API
4. Permission settings:
   - ✅ Derivatives - Order
   - ✅ Derivatives - Position
5. Bind IP (optional)

### OKX

1. Login to OKX
2. Go to API: User Center → API
3. Create V5 API
4. Permissions:
   - ✅ Read
   - ✅ Trade
5. Set Passphrase (must remember)

### Gate.io

1. Login to Gate.io
2. Go to API: User Center → API Management
3. Create API Key
4. Permissions:
   - ✅ Spot Trading
   - ✅ Futures Trading
   - ✅ Withdrawal (optional, recommended to disable)

### Hyperliquid

1. Visit [Hyperliquid](https://app.hyperliquid.xyz)
2. Connect wallet
3. Go to API: Settings → API
4. Create API Key (requires signature authorization)

### Aster DEX

1. Visit [Aster DEX](https://www.asterdex.com)
2. Connect wallet
3. Settings → API Management
4. Create Trading API

## Security Recommendations

1. **Enable IP Whitelist** - Only allow server IP access
2. **Principle of Least Privilege** - Only enable necessary permissions
3. **Disable Withdrawal Permission** - Unless absolutely necessary
4. **Regular API Key Rotation** - Update monthly
5. **Use Independent Sub-accounts** - Isolate trading funds
6. **Set Reasonable Leverage** - Recommend ≤5x