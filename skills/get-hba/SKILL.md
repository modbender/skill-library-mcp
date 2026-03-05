---
name: Clank Human Bitcoin Address
description: Agent-first service to register and manage Human Bitcoin Addresses (BIP-353) on clank.money with L402 bitcoin payments.
---

# Clank Human Bitcoin Address Skill

Use this skill to register and update a Human Bitcoin Address under `clank.money` (BIP-353 DNS payment instructions pointing to a BIP-321 URI).

## CRITICAL FIRST

- `managementToken` is returned after successful paid registration (`201` or `202`).
- You must save `managementToken` immediately and securely.
- CRITICAL: If the token is lost, future updates to that address cannot be authenticated.

## API Endpoints

- `POST https://clank.money/api/v1/registrations`
- `GET https://clank.money/api/v1/registrations/{username}`
- `PATCH https://clank.money/api/v1/registrations/{username}`

## Required Registration Input

- `username`
  - lowercase letters, digits, hyphens
  - 3 to 32 chars
  - cannot start/end with `-`
- `bip321Uri`
  - required
  - must start with `bitcoin:`
  - should be valid BIP-321
  - strongly suggested: include a BOLT12 offer (`lno=...`)

## Strict Registration Checklist

Registration price is `999` sats.

1. Submit unauthenticated registration request (`POST /api/v1/registrations`).
   - Output: either `409 username_unavailable` or `402 payment_required`.
2. If `409`, pick another username and repeat step 1.
   - Output: `402 payment_required` response.
3. Read L402 challenge values from `402` response: `macaroon`, `invoice`, `paymentHash`, `amountSats`, `expiresAt`.
   - Output: invoice + macaroon.
4. Pay the Lightning invoice and obtain `preimage`.
   - Output: payment preimage.
5. Retry the exact same `POST /api/v1/registrations` with:
   - `Authorization: L402 <macaroon>:<preimage>`
   - Output: `201` or `202` with `managementToken`.
6. Save the management token immediately.
   - CRITICAL: If this token is lost, updates are impossible.
   - Output: secure local token file.

## Copy-Paste Happy Path (Bash)

```bash
set -euo pipefail

BASE="https://clank.money"
USERNAME="satoshi"
BIP321_URI='bitcoin:?lno=lno1examplebolt12offer'
TOKEN_FILE="$HOME/.clank/${USERNAME}.management_token"

mkdir -p "$(dirname "$TOKEN_FILE")"

# 1) Create challenge (or fail fast if name taken)
curl -sS -X POST "$BASE/api/v1/registrations" \
  -H "content-type: application/json" \
  --data "{\"username\":\"$USERNAME\",\"bip321Uri\":\"$BIP321_URI\"}" \
  > /tmp/clank_register_challenge.json

ERROR_CODE="$(python3 -c 'import json; d=json.load(open("/tmp/clank_register_challenge.json")); e=d.get("error"); print((e.get("code") if isinstance(e,dict) else e) or "")')"
if [ "$ERROR_CODE" = "username_unavailable" ]; then
  echo "Username is taken. Pick another USERNAME and rerun."
  exit 1
fi
if [ "$ERROR_CODE" != "payment_required" ]; then
  echo "Unexpected challenge response:"
  cat /tmp/clank_register_challenge.json
  exit 1
fi

MACAROON="$(python3 -c 'import json; print(json.load(open("/tmp/clank_register_challenge.json"))["macaroon"])')"
INVOICE="$(python3 -c 'import json; print(json.load(open("/tmp/clank_register_challenge.json"))["invoice"])')"
echo "Pay this invoice now:"
echo "$INVOICE"

# 2) After payment, paste your preimage
read -r -p "PASTE_PREIMAGE=" PREIMAGE

# 3) Complete paid registration
curl -sS -X POST "$BASE/api/v1/registrations" \
  -H "content-type: application/json" \
  -H "Authorization: L402 $MACAROON:$PREIMAGE" \
  --data "{\"username\":\"$USERNAME\",\"bip321Uri\":\"$BIP321_URI\"}" \
  > /tmp/clank_register_result.json

MGMT="$(python3 -c 'import json; d=json.load(open("/tmp/clank_register_result.json")); print(d.get("managementToken",""))')"
if [ -z "$MGMT" ]; then
  echo "No managementToken in final response:"
  cat /tmp/clank_register_result.json
  exit 1
fi

# 4) CRITICAL: persist token securely for future updates
printf '%s\n' "$MGMT" > "$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
echo "Saved management token to $TOKEN_FILE"
```

## Update Flow

1. Load stored token from your secure file.
2. Call `PATCH /api/v1/registrations/{username}` with:
   - `Authorization: Bearer <managementToken>`
   - JSON body with new `bip321Uri`

Example:

```bash
USERNAME="satoshi"
TOKEN_FILE="$HOME/.clank/${USERNAME}.management_token"
NEW_BIP321='bitcoin:?lno=lno1newbolt12offer'
MGMT="$(cat "$TOKEN_FILE")"

curl -sS -X PATCH "https://clank.money/api/v1/registrations/$USERNAME" \
  -H "content-type: application/json" \
  -H "Authorization: Bearer $MGMT" \
  --data "{\"bip321Uri\":\"$NEW_BIP321\"}"
```
