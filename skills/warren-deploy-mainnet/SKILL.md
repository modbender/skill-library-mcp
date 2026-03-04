---
name: warren-deploy
description: Deploy websites and files permanently on MegaETH mainnet using SSTORE2. Agents use their own wallet and pay gas.
metadata: {"openclaw":{"emoji":"⛓️","homepage":"https://thewarren.app","source":"https://github.com/planetai87/warren-tools","requires":{"anyBins":["node"],"env":["PRIVATE_KEY"]},"primaryEnv":"PRIVATE_KEY"}}
user-invocable: true
---

# Warren - On-Chain Website Deployment

Deploy websites and files permanently on MegaETH mainnet.

**Network**: MegaETH Mainnet (Chain ID: 4326)
**RPC**: `https://mainnet.megaeth.com/rpc`
**Explorer**: https://megaeth.blockscout.com

## Setup (One Time)

```bash
cd {baseDir}
bash setup.sh
```

## Contract Addresses (Mainnet)

| Contract | Address |
|----------|---------|
| Genesis Key NFT (0xRabbitNeo) | `0x0d7BB250fc06f0073F0882E3Bf56728A948C5a88` |
| 0xRabbit.agent Key NFT | `0x3f0CAbd6AB0a318f67aAA7af5F774750ec2461f2` |
| MasterNFT Registry | `0xf299F428Efe1907618360F3c6D16dF0F2Bf8ceFC` |

## Prerequisites

### 1. Wallet + MegaETH ETH

You need a wallet with real ETH on MegaETH mainnet for gas fees.

- Bridge ETH from Ethereum via the official MegaETH bridge.
- Approximate cost: ~0.001 ETH per site deploy.

Set your private key:

```bash
export PRIVATE_KEY=0xYourPrivateKey
```

### 2. Genesis Access Requirement

The deploy script checks access in this order:

1. Human Genesis Key (0xRabbitNeo) ownership
2. 0xRabbit.agent Key ownership
3. If missing, auto-mint 0xRabbit.agent Key (free)

Default `RABBIT_AGENT_ADDRESS`: `0x3f0CAbd6AB0a318f67aAA7af5F774750ec2461f2` (override via env).
If you override or unset it, mint a human key manually at:

- https://thewarren.app/mint

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `PRIVATE_KEY` | **Yes** | — | Wallet private key for signing transactions |
| `RPC_URL` | No | `https://mainnet.megaeth.com/rpc` | MegaETH RPC endpoint |
| `CHAIN_ID` | No | `4326` | MegaETH mainnet chain ID |
| `GENESIS_KEY_ADDRESS` | No | `0x0d7B...5a88` | Genesis Key NFT contract |
| `RABBIT_AGENT_ADDRESS` | No | `0x3f0C...61f2` | 0xRabbit.agent NFT contract |
| `MASTER_NFT_ADDRESS` | No | `0xf299...eFC` | MasterNFT registry contract |
| `CHUNK_SIZE` | No | `15000` | Bytes per chunk (15KB) |
| `GROUP_SIZE` | No | `500` | Max addresses per tree node |

## Deploy

### Deploy HTML string

```bash
cd {baseDir}
PRIVATE_KEY=0x... node deploy.js \
  --html "<html><body><h1>Hello Warren!</h1></body></html>" \
  --name "My First Site"
```

### Deploy HTML file

```bash
PRIVATE_KEY=0x... node deploy.js \
  --file ./my-site.html \
  --name "My Website"
```

### Deploy via stdin

```bash
echo "<h1>Hello</h1>" | PRIVATE_KEY=0x... node deploy.js --name "Piped"
```

### CLI Options

```
--private-key <key>   Wallet private key (or PRIVATE_KEY env)
--html <string>       HTML content to deploy
--file <path>         Path to file to deploy
--name <name>         Site name (default: "Untitled")
--type <type>         file|image|video|audio|script (default: "file")
```

### Output

```json
{
  "tokenId": 102,
  "rootChunk": "0x019E5E...",
  "depth": 0,
  "url": "https://thewarren.app/v/site=102"
}
```

## Example Workflows

### Quick deploy loop

```bash
cd {baseDir}
for i in $(seq 1 5); do
  HTML="<html><body><h1>Site #$i</h1><p>$(date)</p></body></html>"
  PRIVATE_KEY=0x... node deploy.js --html "$HTML" --name "Site $i"
  sleep 2
done
```

### Deploy a file

```bash
cd {baseDir}
PRIVATE_KEY=0x... node deploy.js --file ./my-site.html --name "Large Site"
```

## View Sites

```
https://thewarren.app/v/site={TOKEN_ID}
```

## Troubleshooting

**"No ETH balance"**
- Bridge ETH to MegaETH mainnet and retry.

**"No Genesis Key found and RABBIT_AGENT_ADDRESS is not configured"**
- Set `RABBIT_AGENT_ADDRESS=0x3f0CAbd6AB0a318f67aAA7af5F774750ec2461f2`, or mint human Genesis Key at `https://thewarren.app/mint`.

**"RPC rate limit"**
- The script retries automatically. Add `sleep 5` between repeated deployments.

**Site does not load immediately**
- Wait 10-30 seconds and retry the viewer URL.

## Notes

- Mainnet content is permanent and immutable.
- Max 500KB per deployment.
- Default chunk size is 15KB (`CHUNK_SIZE=15000`).
- You pay gas from your own wallet.

## Security & Privacy

- **No data exfiltration**: Content is sent only as blockchain transactions to the configured RPC endpoint. No intermediary servers.
- **PRIVATE_KEY handling**: Used solely to sign transactions. Never logged, stored on disk, or transmitted to third parties.
- **Network endpoints**: Only the configured `RPC_URL` (default: `mainnet.megaeth.com/rpc`). No other outbound connections.
- **File access**: Reads only the single file specified by `--file`. No directory scanning or glob expansion.
- **No telemetry**: No analytics, tracking, or usage reporting.
