# Multi-Wallet Management

## Wallet Format

```json
"wallets": [
  { "privateKey": "0x...", "label": "wallet-1" },
  { "privateKey": "0x...", "label": "wallet-2" }
]
```

## Generating Wallets

```javascript
import { ethers } from "ethers";
const count = 50;
const wallets = [];
for (let i = 1; i <= count; i++) {
  const w = ethers.Wallet.createRandom();
  wallets.push({ privateKey: w.privateKey, label: `wallet-${i}` });
}
console.log(JSON.stringify(wallets, null, 2));
```

## Funding Wallets

Each wallet needs ETH for gas + mint price. For a free mint with 0.5 gwei gas:
- ~0.001-0.005 ETH per wallet for gas
- For 200 wallets: ~0.2-1 ETH total gas budget

Use a script or multisend contract to distribute ETH from a funding wallet.

## Scaling Tips

- **Batch sizes**: The bot signs transactions in batches (default 10) to avoid overwhelming RPCs
- **RPC rate limits**: Free RPCs rate-limit at ~25-50 req/s. Use paid endpoints for 100+ wallets.
- **Nonce management**: The bot fetches nonces in parallel before signing
- **Testing**: Use `batch-test.js` to verify all wallets can sign and connect before a live mint

## Security

- **Never commit private keys** to version control
- Store wallet files outside the project directory
- Use separate wallets for minting (not your main holdings)
- Consider hardware wallet for the funding wallet
