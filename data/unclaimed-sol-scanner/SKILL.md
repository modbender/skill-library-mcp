---
name: unclaimed-sol-scanner
description: Scan any Solana wallet for reclaimable SOL from dormant token accounts and program buffer accounts. Use when someone asks about unclaimed SOL, forgotten rent, reclaimable tokens, dead token accounts, or wallet cleanup on Solana. Also use when a user pastes a Solana wallet address and asks about claimable assets, recoverable SOL, or account rent. Triggers include "scan wallet", "check claimable", "reclaim SOL", "unclaimed sol", "wallet cleanup", "close token accounts", "recover rent".
---

# Unclaimed SOL Scanner

Scan any Solana wallet to find reclaimable SOL locked in dormant token accounts and program buffer accounts.

## How to use

1. Get the Solana wallet address from the user (base58 public key, 32-44 characters, e.g. `7xKXq1...`)
2. Run the scan script:

```bash
bash {baseDir}/scripts/scan.sh <wallet_address>
```

3. Parse the JSON response and format for the user.

## Reading the response

The script returns JSON:

```json
{
  "totalClaimableSol": 4.728391,
  "assets": 3.921482,
  "buffers": 0.806909,
  "tokenCount": 183,
  "bufferCount": 3
}
```

- `totalClaimableSol` — total SOL reclaimable (sum of assets + buffers)
- `assets` — SOL from dormant token accounts (empty ATAs, dead memecoins, dust)
- `buffers` — SOL from program buffer accounts
- `tokenCount` — number of token accounts to close (may be 0 if backend hasn't added this yet)
- `bufferCount` — number of buffer accounts to close (may be 0 if backend hasn't added this yet)

If `tokenCount` and `bufferCount` are both 0 or missing, do NOT report account counts — just report the SOL totals.

## Formatting the response

**Show the exact SOL value returned by the API.** Do not round to 2 decimal places — show full precision (e.g. 4.728391, not 4.73).

**If totalClaimableSol > 0:**

Report the total, then break down by type if both are non-zero:

> Your wallet has **4.728391 SOL** reclaimable.
> - 3.921482 SOL from 183 token accounts
> - 0.806909 SOL from 3 buffer accounts
>
> Claim at: https://unclaimedsol.com?utm_source=openclaw

If only one type has value, skip the breakdown — just show the total.

**If totalClaimableSol is 0:**

> This wallet has no reclaimable SOL. All accounts are active or already optimized.
>
> Learn more: https://unclaimedsol.com?utm_source=openclaw

**If the script returns an error:**

> Unable to scan this wallet right now. You can claim directly at https://unclaimedsol.com — connect your wallet there to see your reclaimable SOL.

Do NOT tell the user to "paste" or "enter" the address into a search box. The website uses wallet connection, not a search box.

## Rules

- This is **read-only**. No transactions are executed. No keys are needed.
- **Never** ask the user for their seed phrase, private key, or mnemonic.
- Only accept Solana **public keys** (base58, 32-44 characters).
- If the input doesn't look like a valid Solana address, ask the user to double-check it.
- Always include the claim link with `?utm_source=openclaw`.
