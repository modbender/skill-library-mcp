# Blockchain Developer Patterns

## Libraries (2024+)

| Layer | Primary | Notes |
|-------|---------|-------|
| JS/TS | viem | Replacing ethers.js — lighter, typed |
| Python | web3.py | Standard choice |
| Testing | Foundry (forge) | Fastest, Solidity-native |
| Indexing | The Graph | Subgraph queries |

## Core Patterns

### Provider Setup
```typescript
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

const client = createPublicClient({
  chain: mainnet,
  transport: http(process.env.RPC_URL)
})
```

### Contract Read
```typescript
const balance = await client.readContract({
  address: TOKEN_ADDRESS,
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: [walletAddress]
})
```

### Contract Write
```typescript
const hash = await walletClient.writeContract({
  address: CONTRACT,
  abi,
  functionName: 'transfer',
  args: [to, amount]
})
const receipt = await client.waitForTransactionReceipt({ hash })
```

### Event Listening
```typescript
const logs = await client.getLogs({
  address: CONTRACT,
  event: parseAbiItem('event Transfer(address,address,uint256)'),
  fromBlock: 'earliest'
})
```

## Token Standards

| Standard | Type | Key Functions |
|----------|------|---------------|
| ERC-20 | Fungible | balanceOf, transfer, approve, allowance |
| ERC-721 | NFT | ownerOf, tokenURI, safeTransferFrom |
| ERC-1155 | Multi | balanceOfBatch, safeBatchTransferFrom |

## Common Mistakes

1. **Hardcoded private keys** — Use env/signers, NEVER in code
2. **Missing allowance** — Must approve before transferFrom
3. **Not awaiting confirmations** — Pending ≠ confirmed
4. **Integer overflow** — Use BigInt for token amounts
5. **Wrong decimals** — ETH=18, USDC=6, always check
6. **Ignoring nonces** — Can cause stuck transactions
7. **Unvalidated addresses** — Always checksum validate
8. **Sync/async mixing** — All blockchain ops are async

## Gas Strategies

- **EIP-1559:** Set maxFeePerGas + maxPriorityFeePerGas
- **Estimation:** Always estimateGas before sending
- **Batching:** Use multicall to reduce RPC calls
- **Simulation:** simulateContract before write
