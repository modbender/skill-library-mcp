# Algorand anchoring (full lifecycle)

## 1) Create/import wallet (external signer)

Create/import a dedicated anchor wallet in an external wallet app or HSM.
This skill intentionally does not generate/store mnemonics.

Inputs needed by this skill:
- wallet address (`<ADDR>`)
- externally signed transaction blob (`<SIGNED_TX_B64>`) when submitting

## 2) Fund and check readiness

- Send ALGO to the generated address.
- Script: `scripts/check_algorand_funding.py`

Example:
```bash
scripts/check_algorand_funding.py --algod-url https://mainnet-api.algonode.cloud --address <ADDR>
```

## 3) Rotate note encryption key (recommended)

- Script: `scripts/rotate_note_key.py`
- Produces versioned key file + registry.

Example:
```bash
scripts/rotate_note_key.py --keyring-dir <workspace>/.secrets
```

## 4) Build consolidation payload

- Script: `scripts/build_anchor_payload.py`

Example:
```bash
scripts/build_anchor_payload.py --root <workspace>/memory > payload.json
```

## 5) Build unsigned tx + external signing + submit

- Build unsigned tx with encrypted note:
```bash
scripts/build_unsigned_anchor_tx.py \
  --algod-url https://mainnet-api.algonode.cloud \
  --address <ADDR> \
  --payload-file payload.json \
  --note-key-file <workspace>/.secrets/algorand-note-key-v1.bin
```

- Sign externally (wallet app/HSM), then submit signed tx blob:
```bash
scripts/algorand_anchor_tx.py --algod-url https://mainnet-api.algonode.cloud --signed-tx-b64 <SIGNED_TX_B64>
```

Note format remains: `NXP1 || nonce(12) || AES-256-GCM ciphertext+tag`

## 6) Record local tx map

- Script: `scripts/record_anchor_map.py`

Example:
```bash
scripts/record_anchor_map.py --root <workspace>/memory --date YYYY-MM-DD --txid <TXID> --root-hash <ROOT_HASH>
```

## 7) Retrieve + decrypt + verify

- Fetch tx note: `scripts/fetch_anchor_note.py`
- Decrypt note: `scripts/decrypt_note_payload.py`
- Verify against local ledger: `scripts/verify_anchor_against_ledger.py`

Example:
```bash
scripts/fetch_anchor_note.py --indexer-url https://mainnet-idx.algonode.cloud --txid <TXID>
```

## Security requirements

- Never commit note keys or signed transaction artifacts.
- Keep `.secrets/` local and permission-restricted.
- Keep on-chain notes encrypted only; no plaintext memory.
- Use dedicated anchor wallet separate from other funds.

## TX volume guidance

- Normal mode: 1 tx/day (daily consolidation anchor)
- Busy mode: 2 tx/day (daily + contradiction/emergency)
