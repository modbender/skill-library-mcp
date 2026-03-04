---
name: openscan-crypto
description: Navigate and query crypto networks via OpenScan infrastructure. Use when the user asks about blockchain data — balances (ETH, ERC20, BTC), blocks, transactions, gas prices, mempool, fee estimates, token lookups, event decoding, RPC endpoints, or ENS resolution. Supports Ethereum, Bitcoin, Arbitrum, Optimism, Base, Polygon, BNB and Sepolia. Powered by @openscan/network-connectors and @openscan/metadata.
---

# OpenScan Crypto Network Skill

Navigate and query crypto networks using OpenScan's infrastructure. Data comes from `@openscan/metadata` (CDN) and `@openscan/network-connectors` (RPC).

## CLI Location

```
skills/openscan-crypto/scripts/crypto-cli.mjs
```

Run with: `node <skill_dir>/scripts/crypto-cli.mjs <command> [args]`

## Metadata Commands

### List networks
```bash
crypto-cli.mjs networks
```

### List RPC endpoints
```bash
crypto-cli.mjs rpcs <chain>              # All public RPCs
crypto-cli.mjs rpcs <chain> --private    # Only tracking:none RPCs
```

### Look up token
```bash
crypto-cli.mjs token <symbol|address>                # Search all mainnets
crypto-cli.mjs token <symbol|address> --chain <chain> # Specific chain
```

### Event signatures
```bash
crypto-cli.mjs events [--chain <chain>]     # List known events
crypto-cli.mjs decode-event <topic_hash>    # Decode one topic
```

### Labeled addresses & profiles
```bash
crypto-cli.mjs addresses [--chain <chain>]
crypto-cli.mjs profile networks ethereum
crypto-cli.mjs profile apps openscan
```

## RPC Management Commands

RPCs are persisted in `~/.config/openscan-crypto/rpc-config.json`. On first use, the skill auto-fetches from `@openscan/metadata` and selects privacy-first RPCs. All subsequent commands use the persisted config.

### Fetch/sync RPCs from metadata
```bash
crypto-cli.mjs rpc-fetch                # Sync all networks from @openscan/metadata
crypto-cli.mjs rpc-fetch ethereum       # Sync a specific network
```
Resolves the latest metadata version dynamically from npm. Auto-selects RPCs (privacy-first, open-source preferred).

### List RPCs
```bash
crypto-cli.mjs rpc-list ethereum              # Show active (configured) RPCs
crypto-cli.mjs rpc-list ethereum --all        # Show ALL available RPCs from metadata
crypto-cli.mjs rpc-list ethereum --all --private  # Only privacy (tracking:none)
```

### Configure RPCs
```bash
crypto-cli.mjs rpc-set ethereum --strategy race         # Set strategy: fallback|race|parallel
crypto-cli.mjs rpc-set ethereum --add https://my-rpc.com  # Add custom RPC
crypto-cli.mjs rpc-set ethereum --remove https://rpc.com  # Remove an RPC
crypto-cli.mjs rpc-set ethereum --rpcs url1 url2 url3   # Replace all RPCs
crypto-cli.mjs rpc-set ethereum --private-only           # Keep only tracking:none
crypto-cli.mjs rpc-set ethereum --reset                  # Reset to metadata defaults
crypto-cli.mjs rpc-set --default-strategy parallel       # Set global default strategy
crypto-cli.mjs rpc-set --max-rpcs 3                      # Set global max RPCs per network
```

### Reorder RPCs
```bash
crypto-cli.mjs rpc-order ethereum --benchmark            # Auto-sort by latency (fastest first)
crypto-cli.mjs rpc-order ethereum --swap 1 3             # Swap positions 1 and 3
crypto-cli.mjs rpc-order ethereum <url> --position 1     # Move URL to position 1
```

### Test/benchmark RPCs
```bash
crypto-cli.mjs rpc-test ethereum              # Test all configured RPCs
crypto-cli.mjs rpc-test ethereum --all        # Test ALL available from metadata
crypto-cli.mjs rpc-test ethereum <url>        # Test a specific URL
```
Tests latency, block number, client version. Detects out-of-sync nodes via block delta.

### View/set default strategy
```bash
crypto-cli.mjs rpc-strategy                   # View defaults + per-network overrides
crypto-cli.mjs rpc-strategy parallel           # Set global default to parallel
```

## Address Info Command

### Aggregate address information
```bash
crypto-cli.mjs address-info <address>              # Full address info
crypto-cli.mjs address-info vitalik.eth            # ENS name supported
crypto-cli.mjs address-info <address> --chain base # On another chain
crypto-cli.mjs address-info <address> --private    # Privacy RPCs only
```

Returns in a single call:
- **type**: `EOA` or `contract` (with `codeSize` if contract)
- **balance**: native balance (ETH/MATIC/BNB, etc.)
- **txCount**: total transaction count (nonce)
- **ensName**: primary ENS name via reverse lookup (Ethereum mainnet only)
- **label**: metadata label if the address is a known entity (name, tags, description, website)
- **explorerLink**: direct link to the OpenScan explorer

This command fires `balance`, `code`, and `nonce` in parallel, then enriches the result with ENS reverse resolution and metadata label lookup.

## Price Commands

### On-chain token price (100% on-chain, no CoinGecko)
```bash
crypto-cli.mjs price                    # ETH price (default)
crypto-cli.mjs price BTC                # BTC price (via WBTC pools on mainnet)
crypto-cli.mjs price --chain polygon    # MATIC price
crypto-cli.mjs price --chain bnb        # BNB price
crypto-cli.mjs price --chain arbitrum   # ETH price (fetched from mainnet for L2s)
```
Fetches prices from Uniswap V2-style DEX pools. Uses median of multiple pools for manipulation resistance. Returns per-pool breakdown.

### Decode transaction (function call + events)
```bash
crypto-cli.mjs decode-tx <0xhash>                  # Decode function + events
crypto-cli.mjs decode-tx <0xhash> --chain arbitrum  # On another chain
```
Decodes transaction input data into human-readable function name + parameters. Also decodes all event logs in the receipt. Uses local database of known selectors + 4byte.directory fallback. Identifies tx type: transfer, contract_call, or contract_creation.

**Strategies:**
- `fallback` — Try RPCs in order, move to next on failure. Default. Most conservative.
- `race` — Fire all RPCs simultaneously, use fastest response. Best for latency.
- `parallel` — Fire all, compare results, detect inconsistencies. Trustless verification.

## EVM Query Commands

All EVM commands accept `--chain <chain>` (default: ethereum) and `--private` (use tracking:none RPCs only).

### Check balance
```bash
crypto-cli.mjs balance <address>                           # Native balance (ETH)
crypto-cli.mjs balance vitalik.eth                          # ENS name supported
crypto-cli.mjs balance <address> --token USDC              # + ERC20 balance
crypto-cli.mjs balance <address> --chain arbitrum           # On Arbitrum
crypto-cli.mjs balance <address> --token USDC --chain base  # USDC on Base
```
Returns native balance in human-readable format (e.g., "32.12 ETH") plus raw wei. Token balance includes symbol, decimals, and formatted amount.

### Multi-chain balance
```bash
crypto-cli.mjs multi-balance <address>                     # All mainnet chains
crypto-cli.mjs multi-balance vitalik.eth                    # ENS supported
crypto-cli.mjs multi-balance <address> --private           # Privacy RPCs only
```
Queries the same address across ALL mainnet EVM chains in parallel. Shows balances sorted by chains with funds first.

### Get block info
```bash
crypto-cli.mjs block                    # Latest block
crypto-cli.mjs block latest             # Same
crypto-cli.mjs block 19000000           # By number
crypto-cli.mjs block 0xabcdef...        # By hash (66 chars)
```
Returns: number, hash, timestamp, gasUsed, gasLimit, baseFee, txCount, miner.

### Transaction details
```bash
crypto-cli.mjs tx <0xhash>
crypto-cli.mjs tx <0xhash> --chain arbitrum
```
Returns: hash, blockNumber, from, to, value (in ETH), gasPrice, nonce, input data.

### Transaction receipt
```bash
crypto-cli.mjs receipt <0xhash>
```
Returns: status (success/reverted), gasUsed, effectiveGasPrice, contract address (if deploy), logs with decoded event names from metadata.

### Gas prices
```bash
crypto-cli.mjs gas                      # Ethereum gas
crypto-cli.mjs gas --chain base         # Base gas
crypto-cli.mjs gas --chain arbitrum     # Arbitrum gas
```
Returns: gasPrice, maxPriorityFeePerGas, baseFee — all in gwei.

### Read contract (eth_call)
```bash
crypto-cli.mjs call <to_address> <calldata_hex> [--block <tag>]
```
For raw contract reads. Use for custom ABI calls.

### Event logs
```bash
crypto-cli.mjs logs --address <contract> --topic <topic_hash> [--from <block>] [--to <block>]
```
Returns up to 50 logs. Default range: latest block only.

### Check if address is contract
```bash
crypto-cli.mjs code <address>
```
Returns: isContract (bool), codeSize, truncated bytecode.

### Transaction count (nonce)
```bash
crypto-cli.mjs nonce <address>
```

## Bitcoin Commands

Bitcoin queries use the mempool.space REST API (no JSON-RPC needed).

### Blockchain overview
```bash
crypto-cli.mjs btc-info
```
Returns: block height, best hash, difficulty, mempool stats, recommended fees — all in one call.

### Block details
```bash
crypto-cli.mjs btc-block                # Latest block
crypto-cli.mjs btc-block 800000         # By height
crypto-cli.mjs btc-block 0000000...     # By hash (64 chars)
```

### Transaction details
```bash
crypto-cli.mjs btc-tx <txid>
```
Returns: confirmation status, fee (sats + BTC), fee rate (sat/vB), inputs/outputs with addresses and values.

### Mempool state
```bash
crypto-cli.mjs btc-mempool
```
Returns: tx count, vsize, total fees, recommended fee rates, 5 most recent txs.

### Fee estimates
```bash
crypto-cli.mjs btc-fee
```
Returns: fastest, halfHour, hour, economy, minimum — all in sat/vB.

### Address balance
```bash
crypto-cli.mjs btc-address <address>
```
Returns: balance (BTC + sats), total received/sent, tx count, UTXO count.

## Chain Aliases

| Alias | Chain ID | Network |
|-------|----------|---------|
| ethereum, eth, mainnet | 1 | Ethereum |
| optimism, op | 10 | Optimism |
| bnb, bsc | 56 | BNB Smart Chain |
| polygon, matic, pol | 137 | Polygon |
| base | 8453 | Base |
| arbitrum, arb | 42161 | Arbitrum One |
| sepolia | 11155111 | Sepolia Testnet |
| bitcoin, btc | bip122:... | Bitcoin Mainnet |

Numeric chain IDs also work (e.g., `1`, `42161`).

## Output

All commands output JSON to stdout. The agent can parse and format as needed.

Numeric values are pre-formatted:
- Balances: human-readable (e.g., "32.12 ETH") + raw wei
- Gas: in gwei
- Timestamps: ISO 8601
- Hex numbers: converted to decimal strings

### Explorer Links

EVM commands that return on-chain entities include an `explorerLink` field with a direct URL to [openscan.eth.link](https://openscan.eth.link):

| Command | explorerLink points to |
|---------|------------------------|
| `balance` | address page |
| `multi-balance` | address page per chain |
| `block` | block page |
| `tx` | transaction page |
| `receipt` | transaction page |
| `code` | address page |
| `nonce` | address page |
| `token` | token contract address page |
| `logs` | transaction page per log |
| `btc-block` | Bitcoin block page |
| `btc-tx` | Bitcoin transaction page |
| `btc-address` | Bitcoin address page |
| `address-info` | address page |

URL patterns:
- EVM: `https://openscan.eth.link/#/{chainId}/{type}/{id}`
- Bitcoin mainnet: `https://openscan.eth.link/#/btc/{type}/{id}`
- Bitcoin testnet4: `https://openscan.eth.link/#/tbtc/{type}/{id}`

Always show this link to the user so they can explore the data further in the UI.

## Caching

Metadata cached in `~/.cache/openscan-crypto/` (6h TTL). RPC responses are NOT cached.

## ENS Support

All EVM address commands accept `.eth` names (e.g., `vitalik.eth`). ENS is resolved on Ethereum mainnet automatically. Works with: `balance`, `multi-balance`, `code`, `nonce`.

## Security

- **READ-ONLY** — no transaction signing, no private key handling
- **Public RPCs** — no API keys needed
- `--private` flag restricts to tracking:none RPCs
- Dangerous methods (sendTransaction, etc.) are NOT exposed

## Natural Language Mapping

| User says | Command |
|-----------|---------|
| "What's Vitalik's ETH balance?" | `balance 0xd8dA...96045` |
| "How much USDC does 0x... have on Base?" | `balance 0x... --token USDC --chain base` |
| "Show the latest Ethereum block" | `block latest` |
| "What's gas like on Arbitrum?" | `gas --chain arbitrum` |
| "Look up this transaction" | `tx 0x...` |
| "Did this tx succeed?" | `receipt 0x...` |
| "Is 0x... a contract?" | `code 0x...` |
| "What networks does OpenScan support?" | `networks` |
| "What's the USDC contract address?" | `token USDC` |
| "Show privacy-friendly Polygon RPCs" | `rpcs polygon --private` |
| "Show vitalik.eth balance on all chains" | `multi-balance vitalik.eth` |
| "What's the latest Bitcoin block?" | `btc-info` or `btc-block` |
| "Tell me everything about this address" | `address-info 0x...` |
| "Is 0x... a wallet or a contract?" | `address-info 0x...` |
| "What's the ENS name for 0x...?" | `address-info 0x...` (reverse ENS) |
| "Show me info for vitalik.eth" | `address-info vitalik.eth` |
| "How full is the Bitcoin mempool?" | `btc-mempool` |
| "What are Bitcoin fees right now?" | `btc-fee` |
| "Look up this Bitcoin transaction" | `btc-tx <txid>` |
| "Check Satoshi's balance" | `btc-address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` |
| "Show Bitcoin block 800000" | `btc-block 800000` |
