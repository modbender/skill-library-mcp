# Openscan Crypto OpenClaw Skill

An OpenClaw skill for querying blockchain data via [OpenScan](https://openscan.eth.link) infrastructure.

Supports Ethereum, Arbitrum, Optimism, Base, Polygon, BNB, Sepolia, and Bitcoin. All results include a direct `explorerLink` to the OpenScan explorer.

## Installation

Install via [ClawHub](https://clawhub.com):

```bash
clawhub install openscan-crypto
```

Or manually, by cloning this repo into your workspace `skills/` folder and running:

```bash
bash install.sh
```

This installs the `@openscan/network-connectors` npm dependency required by the skill.

## Usage

Once installed, OpenClaw will automatically make the skill available to the agent. Just ask naturally:

- "What's vitalik.eth's ETH balance?"
- "Show me the latest Ethereum block"
- "What's gas like on Arbitrum?"
- "Did this transaction succeed? 0x..."
- "How much USDC does 0x... have on Base?"
- "What's the Bitcoin mempool looking like?"
- "Check this BTC address: 1A1z..."

## CLI

The underlying CLI can also be run directly:

```
node scripts/crypto-cli.mjs <command> [args]
```

### Metadata

```bash
networks                                    # List supported networks
rpcs <chain> [--private]                    # RPC endpoints (--private: tracking:none only)
token <symbol|address> [--chain <chain>]    # Token lookup
events [--chain <chain>]                    # Known event signatures
decode-event <topic_hash>                   # Decode event topic
addresses [--chain <chain>]                 # Labeled addresses
profile <type> <id>                         # Network/app/token profile
```

### EVM Queries

All EVM commands accept `--chain <chain>` (default: ethereum) and `--private`.
Address fields accept ENS names (e.g. `vitalik.eth`).

```bash
balance <address> [--token <sym>]           # Native + optional ERC20 balance
multi-balance <address>                     # Balance across all mainnet chains
block [number|hash|latest]                  # Block info
tx <0xhash>                                 # Transaction details
receipt <0xhash>                            # Receipt + decoded logs
gas                                         # Gas price + base fee
call <to> <calldata> [--block <tag>]        # eth_call
logs --address <addr> [--topic <t>]         # Event logs
code <address>                              # Contract code / EOA check
nonce <address>                             # Transaction count
```

### Bitcoin

```bash
btc-info                                    # Overview: height, mempool, fees
btc-block [height|hash|latest]              # Block details
btc-tx <txid>                               # Transaction details
btc-mempool                                 # Mempool state
btc-fee                                     # Recommended fee rates
btc-address <address>                       # Address balance + tx count
```

### Chain Aliases

| Alias | Chain |
|-------|-------|
| `ethereum`, `eth`, `mainnet` | Ethereum (1) |
| `arbitrum`, `arb` | Arbitrum One (42161) |
| `optimism`, `op` | Optimism (10) |
| `base` | Base (8453) |
| `polygon`, `matic` | Polygon (137) |
| `bnb`, `bsc` | BNB Smart Chain (56) |
| `sepolia` | Sepolia Testnet (11155111) |
| `bitcoin`, `btc` | Bitcoin Mainnet |

Numeric chain IDs also work (e.g. `1`, `42161`).

## Output

All commands output JSON. EVM and Bitcoin entity commands include an `explorerLink` field pointing to the OpenScan explorer:

```json
{
  "address": "0xd8dA...",
  "nativeBalance": "1234.5 ETH",
  "explorerLink": "https://openscan.eth.link/#/1/address/0xd8dA..."
}
```

Explorer URL patterns:
- EVM: `https://openscan.eth.link/#/{chainId}/{type}/{id}`
- Bitcoin mainnet: `https://openscan.eth.link/#/btc/{type}/{id}`
- Bitcoin testnet4: `https://openscan.eth.link/#/tbtc/{type}/{id}`

## Security

- **Read-only** — no transaction signing, no private key handling
- **No API keys** — uses public RPC endpoints
- `--private` flag restricts to tracking:none RPCs
- Metadata cached locally in `~/.cache/openscan-crypto/` (6h TTL)
