# MCP Servers for Web3 Data

This document lists MCP (Model Context Protocol) servers that provide Web3 data.

## What is MCP?

Model Context Protocol is a standardized way for AI models to access external data sources. MCP servers act as bridges between AI agents and blockchain data.

## Recommended MCP Servers

### 1. Ethereum MCP
- **Repository**: https://github.com/your-org/ethereum-mcp
- **Capabilities**: Balance queries, transaction simulation, contract reads
- **Setup**: `npx ethereum-mcp --rpc-url YOUR_RPC_URL`
- **Free**: Yes (uses your RPC)

### 2. Etherscan MCP
- **Repository**: https://github.com/your-org/etherscan-mcp
- **Capabilities**: Transaction history, contract verification, token info
- **Setup**: `ETHERSCAN_API_KEY=xxx npx etherscan-mcp`
- **Free**: Yes (free tier available)

### 3. DefiLlama MCP
- **Repository**: https://github.com/your-org/defillama-mcp
- **Capabilities**: TVL data, yield rankings, protocol info
- **Setup**: `npx defillama-mcp`
- **Free**: Yes (no API key required)

### 4. Dune Analytics MCP
- **Repository**: https://github.com/your-org/dune-mcp
- **Capabilities**: Custom SQL queries on blockchain data
- **Setup**: `DUNE_API_KEY=xxx npx dune-mcp`
- **Free**: Free tier available (limited queries)

## Integration Pattern

```python
# Check MCP availability first, fall back to direct API
async def get_tvl(protocol: str) -> float:
    if mcp_available("defillama"):
        return await mcp_query("defillama", "get_tvl", protocol)
    else:
        return await defillama_api_get_tvl(protocol)
```

## Adding New MCP Servers

When adding new MCP servers:
1. Verify the server supports standard MCP protocol
2. Test with `mcp-inspector` tool
3. Document required environment variables
4. Add fallback logic for when MCP is unavailable