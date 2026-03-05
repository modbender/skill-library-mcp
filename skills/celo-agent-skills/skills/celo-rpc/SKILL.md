---
name: celo-rpc
description: Interact with Celo blockchain via RPC endpoints. Use when reading balances, transactions, blocks, and interacting with Celo via viem or cast.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Celo RPC Interactions

This skill covers interacting with the Celo blockchain via RPC endpoints.

## When to Use

- Reading account balances (CELO and tokens)
- Querying transaction data
- Getting block information
- Interacting with Celo via viem or cast

## Network Information

| Network | Chain ID | RPC Endpoint |
|---------|----------|--------------|
| Celo Mainnet | 42220 | https://forno.celo.org |
| Celo Sepolia | 11142220 | https://forno.celo-sepolia.celo-testnet.org |

Forno is a rate-limited, best-effort service. For production, use a dedicated RPC provider.

### Alternative RPC Providers

| Provider | Mainnet | Testnet |
|----------|---------|---------|
| Alchemy | https://celo-mainnet.g.alchemy.com/v2/{API_KEY} | https://celo-sepolia.g.alchemy.com/v2/{API_KEY} |
| Infura | https://celo-mainnet.infura.io/v3/{API_KEY} | https://celo-sepolia.infura.io/v3/{API_KEY} |
| Ankr | https://rpc.ankr.com/celo | https://rpc.ankr.com/celo_testnet |
| QuickNode | Custom endpoint via dashboard | Custom endpoint via dashboard |

## Block Explorers

- **Celo Mainnet:** https://celoscan.io
- **Celo Sepolia:** https://sepolia.celoscan.io

## Using viem with Celo

### Installation

```bash
npm install viem
```

### Basic Setup

```typescript
import { createPublicClient, http } from "viem";
import { celo, celoSepolia } from "viem/chains";

// Mainnet client
const publicClient = createPublicClient({
  chain: celo,
  transport: http("https://forno.celo.org"),
});

// Testnet client (Celo Sepolia)
const testnetClient = createPublicClient({
  chain: celoSepolia,
  transport: http("https://forno.celo-sepolia.celo-testnet.org"),
});
```

### Reading Balances

```typescript
// Get CELO balance
const balance = await publicClient.getBalance({
  address: "0x...",
});
console.log("Balance:", balance, "wei");

// Get token balance (e.g., cUSD)
const cUSD = "0x765de816845861e75a25fca122bb6898b8b1282a";
const tokenBalance = await publicClient.readContract({
  address: cUSD,
  abi: [
    {
      name: "balanceOf",
      type: "function",
      stateMutability: "view",
      inputs: [{ name: "account", type: "address" }],
      outputs: [{ type: "uint256" }],
    },
  ],
  functionName: "balanceOf",
  args: ["0x..."],
});
```

### Getting Block Data

```typescript
// Get latest block number
const blockNumber = await publicClient.getBlockNumber();

// Get block by number
const block = await publicClient.getBlock({
  blockNumber: 12345678n,
});

// Get block by hash
const blockByHash = await publicClient.getBlock({
  blockHash: "0x...",
});
```

### Getting Transaction Data

```typescript
// Get transaction by hash
const tx = await publicClient.getTransaction({
  hash: "0x...",
});

// Get transaction receipt
const receipt = await publicClient.getTransactionReceipt({
  hash: "0x...",
});
```

## Using cast (Foundry)

### Reading Data

```bash
# Get CELO balance
cast balance 0x... --rpc-url https://forno.celo.org

# Get block number
cast block-number --rpc-url https://forno.celo.org

# Get block details
cast block 12345678 --rpc-url https://forno.celo.org

# Get transaction
cast tx 0x... --rpc-url https://forno.celo.org

# Call view function
cast call 0x765de816845861e75a25fca122bb6898b8b1282a \
  "balanceOf(address)(uint256)" \
  0x... \
  --rpc-url https://forno.celo.org

# Get storage slot
cast storage 0x... 0 --rpc-url https://forno.celo.org
```

### Chain Information

```bash
# Get chain ID
cast chain-id --rpc-url https://forno.celo.org

# Get gas price
cast gas-price --rpc-url https://forno.celo.org
```

## Using curl (Raw RPC)

### Get Balance

```bash
curl -X POST https://forno.celo.org \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_getBalance",
    "params": ["0x...", "latest"],
    "id": 1
  }'
```

### Get Block Number

```bash
curl -X POST https://forno.celo.org \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
  }'
```

## Standard EVM RPC Methods

All standard Ethereum JSON-RPC methods are supported:

| Method | Description |
|--------|-------------|
| eth_blockNumber | Returns the current block number |
| eth_getBalance | Returns the balance of an address |
| eth_getTransactionByHash | Returns transaction by hash |
| eth_getTransactionReceipt | Returns transaction receipt |
| eth_call | Executes a call without creating a transaction |
| eth_estimateGas | Estimates gas for a transaction |
| eth_gasPrice | Returns current gas price |
| eth_getBlockByNumber | Returns block by number |
| eth_getBlockByHash | Returns block by hash |
| eth_getLogs | Returns logs matching filter |
| eth_sendRawTransaction | Sends a signed transaction |

## Additional Resources

- [rpc-providers.md](references/rpc-providers.md) - Full list of RPC providers
