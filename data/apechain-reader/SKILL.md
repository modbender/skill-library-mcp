---
name: walletlens
description: "Advanced multi-chain wallet analyzer with USD pricing, collection names, ENS support, and sophisticated bot detection across 8 EVM networks. Use when you need to: (1) analyze wallet profiles with USD valuations and natural language summaries, (2) inspect smart contract details and token information, (3) track NFT portfolios with resolved collection names, (4) examine transaction history and transfer patterns, (5) detect potential bot accounts through advanced behavioral analysis, (6) perform due diligence on addresses with comprehensive insights, (7) investigate cross-chain activity with ENS domain support. Supports ApeChain (primary), Ethereum, Base, Arbitrum, Polygon, Optimism, Avalanche, and BNB Chain with automatic retry logic and human-readable output."
metadata:
  openclaw:
    requires:
      env: []
    credentialNotes: "No API keys required for basic usage (uses public RPC endpoints). Optional: set ALCHEMY_API_KEY for enhanced NFT collection name resolution and faster queries."
---

# WalletLens

An advanced multi-chain wallet analyzer that provides detailed wallet profiles with USD pricing, human-readable NFT collection names, ENS domain support, and sophisticated bot detection across 8 major EVM networks.

## Key Features

- **Multi-Chain Support**: 8 EVM networks with ApeChain as primary focus
- **USD Price Integration**: Real-time token prices via CoinGecko with graceful degradation
- **ENS Domain Support**: Resolve .eth names across all commands automatically
- **Collection Name Resolution**: Human-readable NFT collection names via Alchemy API + RPC fallback
- **Natural Language Summaries**: Pretty mode includes intelligent wallet insights
- **Advanced Bot Detection**: Sophisticated scoring algorithm to identify automated accounts
- **Reliable Performance**: Automatic retry logic with exponential backoff for network resilience
- **Dual Output Formats**: JSON (default) for agents, `--pretty` flag for human-readable output
- **Minimal Dependencies**: Uses public RPC endpoints, optional Alchemy API key for enhanced features

## Installation

This skill requires Node.js (v16+). No additional dependencies needed - uses built-in `fetch` API.

```bash
# Verify Node.js version
node --version
```

## Quick Start

Basic wallet lookup on ApeChain:
```bash
node scripts/wallet-lookup.js 0x8dd6390be6dc732c92b161b9793a3948b56c0126
```

Same query with human-readable output:
```bash
node scripts/wallet-lookup.js 0x8dd6390be6dc732c92b161b9793a3948b56c0126 --pretty
```

Cross-chain lookup on Ethereum:
```bash
node scripts/wallet-lookup.js 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --chain ethereum --pretty
```

## Commands Reference

All commands support `--chain <name>` (defaults to `apechain`) and `--pretty` flag for human-readable output.

### Wallet Lookup
**Purpose**: Complete wallet profile with balance, transaction count, and NFT activity summary

```bash
node scripts/wallet-lookup.js <address> [--chain <name>] [--pretty]
```

**Returns**: Native token balance, transaction count, NFT activity (received/sent), collection count, top holdings

**Example Output (JSON)**:
```json
{
  "address": "0x8dd6390be6dc732c92b161b9793a3948b56c0126",
  "chain": "ApeChain",
  "chainId": 33139,
  "isContract": false,
  "balance": { "APE": 10.1398 },
  "transactionCount": 6352,
  "nftActivity": { "received": 2, "sent": 1 },
  "nftCollectionsHeld": 1,
  "topHoldings": [
    { "contract": "0x6f2a21a8b9cf699d7d3a713a9d7cfbb9e9760f97", "count": 2 }
  ],
  "explorer": "https://apescan.io/address/0x8dd6390be6dc732c92b161b9793a3948b56c0126"
}
```

**Example Output (Pretty)**:
```
🔍 Wallet: 0x8dd6390be6dc732c92b161b9793a3948b56c0126
⛓️  Chain: ApeChain (33139)
💰 Balance: 10.1398 APE
📊 Transactions: 6,352
🎨 NFT Activity: 2 received, 1 sent
📦 Collections: 1
🔗 Explorer: https://apescan.io/address/0x8dd6390be6dc732c92b161b9793a3948b56c0126
```

### Contract Information
**Purpose**: Detailed smart contract analysis including type detection and metadata

```bash
node scripts/contract-info.js <address> [--chain <name>] [--pretty]
```

**Returns**: Contract type (ERC-20/721/1155), name, symbol, total supply, decimals, owner

**Use Cases**: Token research, contract verification, due diligence

### Transaction History
**Purpose**: Recent transfer activity with timestamps and transaction details

```bash
node scripts/tx-history.js <address> [--chain <name>] [--limit <number>] [--pretty]
```

**Returns**: Recent ERC-20 and NFT transfers with direction (IN/OUT), timestamps, contract addresses

**Use Cases**: Activity analysis, transaction tracking, wallet monitoring

### NFT Holdings
**Purpose**: Current NFT collection with detailed token information

```bash
node scripts/nft-holdings.js <address> [--chain <name>] [--collection <contract>] [--pretty]
```

**Returns**: NFTs currently held, grouped by collection, token IDs, transfer statistics

**Use Cases**: NFT portfolio analysis, collection tracking, investment research

### Bot Detection
**Purpose**: Advanced behavioral analysis to identify potential automated accounts

```bash
node scripts/bot-detect.js <address> [--chain <name>] [--pretty]
```

**Returns**: Bot score (0-100), verdict classification, detailed breakdown of scoring factors

**Scoring Factors**:
- **Wrapped Token Usage** (30pts): Frequency of using wrapped native tokens
- **Fast Flipping** (25pts): Quick buy-sell cycles within 24 hours  
- **Fast Listing** (20pts): Immediate listing after purchase (within 30 minutes)
- **Aggressive Pricing** (15pts): Price manipulation patterns
- **Cross-Collection Activity** (10pts): Activity spread across many collections

**Score Interpretation**:
- 75-100: Definite bot
- 60-74: Likely bot  
- 40-59: Suspicious
- 20-39: Probably human
- 0-19: Human

**Use Cases**: Due diligence, airdrop filtering, community verification

## Supported Networks

See [references/CHAINS.md](references/CHAINS.md) for comprehensive chain information including reliability status and performance characteristics.

### Reliable Chains ✅
- **ApeChain** (primary) - Fastest, most reliable
- **Ethereum** - Stable, high-value addresses
- **Base** - Fast L2 performance
- **Arbitrum** - Reliable L2 with official RPC

### Intermittent Chains 🟡
- **Polygon** - May timeout, use with retry logic
- **Optimism** - Occasional performance issues
- **BNB Chain** - Variable reliability
- **Avalanche** - Limited testing, use with caution

## Output Formats

All scripts support two output modes:

### JSON Format (Default)
Structured data ideal for programmatic consumption and agent workflows:
```bash
node scripts/wallet-lookup.js <address>
# Returns formatted JSON
```

### Pretty Format (Human-Readable)
Clean, emoji-enhanced output for human review:
```bash
node scripts/wallet-lookup.js <address> --pretty
# Returns formatted text with emojis and clear sections
```

## Environment Variables

No environment variables required. The skill uses public RPC endpoints configured in `scripts/lib/rpc.js`.

### Custom RPC Endpoints (Advanced)
To use custom RPC endpoints, modify the `CHAINS` object in `scripts/lib/rpc.js`:

```javascript
const CHAINS = {
  apechain: { 
    id: 33139, 
    rpc: "your-custom-rpc-url", 
    name: "ApeChain", 
    symbol: "APE", 
    explorer: "https://apescan.io" 
  },
  // ... other chains
};
```

## Error Handling & Reliability

### Automatic Retry Logic
- 3 retry attempts with exponential backoff (500ms, 1s, 2s)
- 10-second timeout per request
- Graceful failure with clean error messages

### Input Validation
- Address format validation (0x + 40 hex characters)
- Chain name validation against supported list
- Clean error messages without stack traces

### Common Error Messages
```json
{"error": "Invalid address format. Address must be 0x followed by 40 hexadecimal characters"}
{"error": "Unsupported chain \"invalidchain\". Supported chains: apechain, ethereum, base, arbitrum, polygon, optimism, avalanche, bsc"}
{"error": "RPC request timed out after 10000ms"}
```

## Performance & Limitations

### Response Times
- **Fast (< 1s)**: ApeChain, Arbitrum
- **Good (1-2s)**: Ethereum, Base  
- **Variable (1-5s)**: Polygon, Optimism, BSC, Avalanche

### Data Coverage
- **Recent Activity**: 500K-2M blocks depending on chain performance
- **Historical Limitations**: Very old transactions may not appear
- **NFT Detection**: ERC-721 and ERC-1155 support via Transfer events
- **Bot Analysis**: Requires minimum 3 NFT purchases for scoring

### Resource Usage
- **Memory**: Minimal - processes data in streams
- **Network**: Burst usage during queries, then idle
- **CPU**: Low - mostly I/O bound operations

## Troubleshooting

### Network Issues
```bash
# If RPC timeouts occur, try different chain:
node scripts/wallet-lookup.js <address> --chain ethereum

# For intermittent chains, retry usually succeeds:
node scripts/wallet-lookup.js <address> --chain polygon
```

### Empty Results
- Verify address is active on the selected chain
- Try different chain if cross-chain activity expected
- Increase block scan range for older activity

### Performance Optimization
- Use `--limit` parameter to reduce transaction history size
- Choose reliable chains (ApeChain, Ethereum, Base, Arbitrum) for consistent performance
- Monitor response times and adjust expectations per chain

## Advanced Usage

### Batch Analysis
```bash
# Analyze multiple addresses
for addr in 0xaddr1 0xaddr2 0xaddr3; do
  echo "=== Analysis for $addr ==="
  node scripts/wallet-lookup.js $addr --pretty
  node scripts/bot-detect.js $addr --pretty
  echo
done
```

### Cross-Chain Investigation
```bash
# Check same address across multiple chains
for chain in apechain ethereum base arbitrum; do
  echo "=== $chain ==="
  node scripts/wallet-lookup.js 0x8dd6390be6dc732c92b161b9793a3948b56c0126 --chain $chain --pretty
done
```

### Collection Analysis
```bash
# Focus on specific NFT collection
node scripts/nft-holdings.js <address> --collection 0x<contract> --pretty
```

## References

- **Chain Details**: [references/CHAINS.md](references/CHAINS.md) - Comprehensive chain status and performance data
- **Bot Scoring**: [references/bot-scoring.md](references/bot-scoring.md) - Detailed bot detection methodology

## Version History

- **v2.0**: Added retry logic, input validation, pretty formatting, comprehensive chain documentation
- **v1.0**: Initial release with basic multi-chain support and bot detection

---

*Need help? Check the references directory for detailed documentation or run any command without arguments for usage instructions.*