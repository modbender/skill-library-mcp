# EVM Payment Deeplink — Reference

## MetaMask Deeplink Formats

### Native ETH
```
https://link.metamask.io/send/<recipientAddress>@<chainId>?value=<amountInWei>
```

### ERC20 Transfer
```
https://link.metamask.io/send/<tokenAddress>@<chainId>/transfer?address=<recipient>&uint256=<amountBaseUnits>
```

## Default USDC Addresses

| Chain | ID | USDC Contract |
|-------|----|---------------|
| Ethereum | 1 | `0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` |
| Base | 8453 | `0x833589fCD6eDb6E08f4c7C32D4f71b54bDa02913` |
| Sepolia | 11155111 | `0x1c7d4b196cb0c7b01d743fbc6116a902379c7238` |
| Base Sepolia | 84532 | `0x036CbD53842c5426634e7929541eC2318f3dCf7e` |

## Unit Conversions

- ETH: 1 ETH = 10^18 wei
- USDC: 1 USDC = 10^6 base units

## On-Chain Verification

### Native ETH
Scan recent blocks for transactions where `from`, `to`, and `value` match the intent.

### ERC20
Use `eth_getLogs` with the Transfer event signature:
```
0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
```
Filter by `from` (topic[1]), `to` (topic[2]), and `data` (amount).

## RPC Endpoints (Public)

| Chain | RPC |
|-------|-----|
| Ethereum | `https://eth.llamarpc.com` |
| Base | `https://mainnet.base.org` |
| Sepolia | `https://1rpc.io/sepolia` |
| Base Sepolia | `https://sepolia.base.org` |

## Security Notes

- Agent never holds private keys.
- Wallet approval screen is the trust boundary.
- On-chain receipt is the source of truth — never trust client-side claims alone.
- No backend policy enforcement in this POC.
