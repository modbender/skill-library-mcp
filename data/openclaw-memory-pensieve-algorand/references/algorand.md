# Algorand anchoring (external signer)

This skill keeps private keys out of runtime.

## Model

- Build unsigned 0-ALGO self-transfer with encrypted note.
- Sign externally (wallet/HSM).
- Submit signed tx bytes.

## Scripts

- `build_anchor_payload.py`
- `build_unsigned_anchor_tx.py`
- `algorand_anchor_tx.py`
- `record_anchor_map.py`
- `fetch_anchor_note.py`
- `decrypt_note_payload.py`
- `verify_anchor_against_ledger.py`
- `check_algorand_funding.py`
- `rotate_note_key.py`

## Encrypted note format

`NXP1 || nonce(12) || AES-256-GCM ciphertext+tag`

## TX volume

- default: 1 tx/day
- optional extra tx only for special events
