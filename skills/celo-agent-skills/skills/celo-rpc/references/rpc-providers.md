# Celo RPC Providers

## Forno (Default)

Free, rate-limited RPC service operated by cLabs.

| Network | Endpoint |
|---------|----------|
| Mainnet | https://forno.celo.org |
| Sepolia | https://forno.celo-sepolia.celo-testnet.org |

Best for development and testing. Use a dedicated provider for production.

## Third-Party Providers

### Alchemy

| Network | Endpoint |
|---------|----------|
| Mainnet | https://celo-mainnet.g.alchemy.com/v2/{API_KEY} |
| Sepolia | https://celo-sepolia.g.alchemy.com/v2/{API_KEY} |

### Infura

| Network | Endpoint |
|---------|----------|
| Mainnet | https://celo-mainnet.infura.io/v3/{API_KEY} |
| Sepolia | https://celo-sepolia.infura.io/v3/{API_KEY} |

### Ankr

| Network | Endpoint |
|---------|----------|
| Mainnet | https://rpc.ankr.com/celo |
| Sepolia | https://rpc.ankr.com/celo_alfajores |

### QuickNode

Custom endpoints via dashboard at quicknode.com.

### Chainstack

| Network | Endpoint |
|---------|----------|
| Mainnet | Custom via dashboard |

### dRPC

| Network | Endpoint |
|---------|----------|
| Mainnet | https://celo.drpc.org |

## Choosing a Provider

| Use Case | Recommendation |
|----------|----------------|
| Development | Forno |
| Production (low traffic) | Alchemy free tier |
| Production (high traffic) | QuickNode or Alchemy paid |
| Maximum reliability | Multiple providers with fallback |

## Rate Limits

Forno has rate limits that may affect high-traffic applications. For production use:

1. Use a paid RPC provider
2. Implement request caching
3. Use WebSocket connections where possible
4. Consider running your own node
