# deBridge MCP Skill

Enable AI agents to execute non-custodial cross-chain cryptocurrency swaps and transfers via the deBridge protocol.

## What It Does

- **Cross-chain swaps**: Find optimal routes and execute trades across 20+ chains
- **Transfer assets**: Move tokens between chains with better rates than traditional bridges
- **Fee estimation**: Check fees and conditions before executing
- **Non-custodial**: Assets never leave user control

## Installation

```bash
# Clone the MCP server
git clone https://github.com/debridge-finance/debridge-mcp.git ~/debridge-mcp
cd ~/debridge-mcp
npm install
npm run build

# Add to OpenClaw config
# See configuration below
```

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "mcp-adapter": {
        "enabled": true,
        "config": {
          "servers": [
            {
              "name": "debridge",
              "transport": "stdio",
              "command": "node",
              "args": ["/home/ubuntu/debridge-mcp/dist/index.js"]
            }
          ]
        }
      }
    }
  }
}
```

Then restart: `openclaw gateway restart`

## Available Tools

When MCP is connected, agents can use:

- **get_quote**: Get swap quote for cross-chain trade
- **create_order**: Create cross-chain order
- **get_status**: Check order status
- **get_supported_chains**: List supported chains

## Usage Example

```
Ask: "Swap 100 USDC from Ethereum to Arbitrum"

Agent uses MCP to:
1. Get quote for USDC → USDC on Arbitrum
2. Show estimated receive amount and fees
3. Create order if user confirms
4. Monitor until completion
```

## Security Notes

- Always verify quoted rates before executing
- Check slippage tolerance settings
- deBridge uses DLN (Decentralized Liquidity Network) - not a bridge
- No liquidity pools - uses order-based matching

## Chains Supported

Ethereum, Arbitrum, Optimism, Base, Polygon, Avalanche, BNB Chain, Solana, and 15+ more.

---

**Skill by**: Avi (github.com/aviclaw)