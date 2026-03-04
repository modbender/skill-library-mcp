# Wallet & Transactions

## How Your Wallet Works

You have a **Privy server wallet** on Monad. No private key export — you control it via API. Sign messages via `/wallet/sign`, send transactions via `/wallet/send`. Tools requiring `EVM_PRIVATE_KEY` won't work.

## Check Wallet & Balance

```bash
GET {BASE_URL}/agents/YOUR_NAME/wallet                    # Address + network
GET {BASE_URL}/agents/YOUR_NAME/wallet/balance             # MON balance
GET {BASE_URL}/agents/YOUR_NAME/wallet/balance?token=0x... # Token balance
```

Balance response includes `hasGas` (bool) and optional `warning`. If `hasGas` is false, don't attempt transactions.

## Portfolio Check

Check all known tokens and present:
```
My Wallet:
0xYOUR_ADDRESS

Holdings:

• 0.325 MON (has gas)
• 0 USDC
• 0 USDT

Ready to swap or send?
```

Blank lines after "Holdings:" and after last bullet. Dust (< $0.01): note as `(dust)`.

## Sign a Message

```bash
curl -X POST {BASE_URL}/agents/YOUR_NAME/wallet/sign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Hello from my agent!"}'
```

## Send MON

```bash
curl -X POST {BASE_URL}/agents/YOUR_NAME/wallet/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"to": "0xRecipientAddress", "value": "0x2386F26FC10000"}'
```

Value in wei (hex). `0x2386F26FC10000` = 0.01 MON.

**Inter-agent:** If recipient is registered, `toAgent` is included and logged on both sides.

**Withdrawal protection:** Sends to non-agent wallets get `202` with `status: "pending_approval"`. Operator must approve. Check: `GET /agents/YOUR_NAME/withdrawals`.

## Send with Contract Data

```bash
curl -X POST {BASE_URL}/agents/YOUR_NAME/wallet/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"to": "0xContract", "value": "0x0", "data": "0x..."}'
```

## Sending Tokens (ERC-20)

Data field for `transfer(address,uint256)`:
```
0xa9059cbb000000000000000000000000[RECIPIENT_NO_0x][AMOUNT_HEX_PADDED_64]
```

Example — 1 USDC (6 decimals, 1000000 = 0xF4240):
```bash
curl -X POST {BASE_URL}/agents/YOUR_NAME/wallet/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"to": "0x754704Bc059F8C67012fEd69BC8A327a5aafb603", "value": "0x0", "data": "0xa9059cbb000000000000000000000000RECIPIENT00000000000000000000000000000000000000000000000000000000000f4240"}'
```

Decimals: USDC/USDT = 6, MON/WETH/most = 18.

## Pre-Checks

| Check | If Missing | Action |
|-------|------------|--------|
| MON > 0 | No gas | "Need MON for gas. Send to [address]" |
| Token balance sufficient | Can't send | "Only have X, not enough" |
| Valid address | Invalid tx | "Not a valid address" |

## Gas Estimates

- MON transfer: ~0.0001 MON
- ERC-20 transfer: ~0.0003 MON
- Contract call: ~0.001+ MON
- Rule of thumb: keep 0.01 MON minimum

## Transaction Response

```json
{"success": true, "hash": "0x...", "explorer": "https://monadexplorer.com/tx/0x..."}
```

Report: "Sent 0.5 MON to 0xB900...2058 — [explorer link]"
