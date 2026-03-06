# WalletLens - Advanced Multi-Chain Wallet Analyzer

**Unlock deep wallet insights with USD pricing, ENS support, and sophisticated bot detection**

WalletLens is the most comprehensive wallet analysis tool for EVM chains, providing rich data about any wallet address with human-readable summaries and professional-grade bot detection.

## 🚀 Key Features

### 💰 **USD Price Integration**
- Real-time token valuations via CoinGecko API
- Shows native token balance with USD equivalent
- Graceful degradation if price feed unavailable

### 🏷️ **Collection Name Resolution**  
- Resolves NFT collection names via Alchemy API
- RPC fallback for maximum compatibility
- Clean display instead of raw contract addresses

### 🌐 **ENS Domain Support**
- Works with .eth names across all commands
- Automatic resolution via Ethereum mainnet
- Clear error messages if resolution fails

### 📋 **Natural Language Summaries**
- Pretty mode includes intelligent wallet insights
- Example: *"Active ApeChain wallet with ~$142 in APE, 21 NFTs across 6 collections."*
- Perfect for human review and reporting

### 🤖 **Advanced Bot Detection**
- Unique 5-factor scoring algorithm
- Identifies trading bots, wash traders, and automated accounts
- Detailed breakdown of behavioral patterns

### ⛓️ **Multi-Chain Coverage**
- 8 EVM networks supported
- ApeChain optimized with sub-second performance
- Cross-chain investigation capabilities

## 📊 Output Examples

### Wallet Analysis (Pretty Mode)
```
📋 Active ApeChain wallet with ~$142 in APE, 21 NFTs across 6 collections.

🔍 Wallet: 0x8dd6390be6dc732c92b161b9793a3948b56c0126
⛓️  Chain: ApeChain (33139)
💰 Balance: 10.14 APE (~$142.20)
📊 Transactions: 6,352
🎨 NFT Activity: 21 received, 3 sent
📦 Collections: 6
🏆 Top Collections:
   Mutant Ape Yacht Club: 8 NFTs
   Bored Ape Yacht Club: 5 NFTs
   CryptoPunks: 3 NFTs
```

### Bot Detection Results
```
🤖 Bot Analysis: 0xbotaddress...
⛓️  Chain: ApeChain
🎯 Score: 87/100 - DEFINITE BOT

📊 Score Breakdown:
   Wrapped Token Usage: 28/30 - 94% of buys use wrapped tokens
   Fast Flipping: 23/25 - 12 flips within 24h
   Fast Listing: 18/20 - 8 listed within 30min
   Cross-Collection Activity: 8/10 - Active in 15+ collections
```

## 🌍 Supported Networks

| Chain | Performance | Notes |
|-------|-------------|-------|
| **ApeChain** ⭐ | < 1s | Primary focus, fastest |
| **Ethereum** ✅ | 1-2s | Stable, high-value addresses |
| **Base** ✅ | < 1s | Fast L2 performance |
| **Arbitrum** ✅ | 1-2s | Reliable with official RPC |
| **Polygon** 🟡 | 1-5s | May timeout, use retry |
| **Optimism** 🟡 | 1-5s | Occasional performance issues |
| **Avalanche** 🟡 | 2-5s | Limited testing |
| **BNB Chain** 🟡 | 1-5s | Variable reliability |

## ⚡ Quick Start

```bash
# Basic wallet lookup with USD pricing
node scripts/wallet-lookup.js vitalik.eth --pretty

# Cross-chain analysis
node scripts/wallet-lookup.js 0x123... --chain ethereum --pretty

# NFT portfolio with collection names  
node scripts/nft-holdings.js 0x123... --pretty

# Bot detection analysis
node scripts/bot-detect.js 0x123... --pretty

# Transaction history
node scripts/tx-history.js 0x123... --limit 10 --pretty
```

## 🔧 Environment Variables

### Optional (Enhances Features)
- `ALCHEMY_API_KEY` - Enables collection name resolution for ApeChain
  - Get free key at [alchemy.com](https://alchemy.com)
  - Without key: falls back to RPC + short address format
  
### Not Required
- All scripts work with public RPC endpoints
- No registration or API keys needed for basic functionality

## 🎯 Why WalletLens?

### **Unique Bot Detection**
Unlike other tools that only check transaction patterns, WalletLens analyzes 5 distinct behavioral factors including wrapped token usage, cross-collection activity, and timing patterns. This provides the most accurate bot scoring available.

### **Human-First Design**  
While other tools dump raw JSON, WalletLens provides natural language summaries and readable collection names. Perfect for due diligence, airdrop filtering, and community verification.

### **Production Ready**
Built with enterprise-grade reliability: automatic retries, timeout protection, input validation, and graceful error handling. Zero dependencies beyond Node.js built-ins.

### **Multi-Chain Native**
Designed from the ground up for cross-chain analysis. Investigate the same address across 8 networks with consistent output formatting.

---

**Ready to get started?** WalletLens works out of the box with Node.js 16+. No setup, no registration - just install and analyze.