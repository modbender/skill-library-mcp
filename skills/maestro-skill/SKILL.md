---
name: maestro-bitcoin
description: Query Maestro Bitcoin APIs directly over HTTP using x402 USDC payments, with Ethereum mainnet as the default production path. Support either PRIVATE_KEY signing or CDP Agent Wallet, and ask for only minimal wallet prerequisites.
---

# Maestro Bitcoin Skill

This skill is intentionally simple: query Maestro APIs directly with x402.

## Default Production Mode (Use First)

- Preferred network for production calls: `eip155:1` (Ethereum mainnet).
- Secondary network: `eip155:8453` (Base mainnet), only when user asks for Base or approves fallback.
- Use production hosts by default.
- Use `dev.` host variants only when user explicitly asks for testing/staging.
- Do not switch to testnet automatically for mainnet requests.

## Minimal Prerequisites To Request

Ask for the smallest possible set of inputs:

- Wallet path A (raw signer): `PRIVATE_KEY` for a dedicated EVM wallet.
- Wallet path B (managed signer): CDP Agent Wallet already provisioned in runtime.
- Optional `WALLET_NETWORK` (default to `eip155:1` if omitted).

Funding requirements (only what is needed to pay):

- Enough `USDC` on the selected network for the current challenge amount.
- Small `ETH` balance for gas on that same network.

Never ask for API keys for x402 flow. Never ask for more wallet data than required.

## CDP Agent Wallet Option

Agents may use Coinbase CDP Agent Wallet instead of raw private keys when user/runtime already supports it:

- Docs: `https://docs.cdp.coinbase.com/agentic-wallet/welcome`
- Use CDP-provided signer/account for x402 signing.
- Keep the same network-selection rule: prefer `eip155:1` for mainnet.
- Request only missing CDP prerequisites if unavailable; do not request both CDP secrets and `PRIVATE_KEY` unless user asks.

## Workflow

1. Read endpoint specs from `https://docs.gomaestro.org/bitcoin` (or linked REST references there). All docs pages are available as markdowns by simply appending `.md` to the URL path, e.g. `https://docs.gomaestro.org/bitcoin/blockchain-indexer-api/addresses/utxos-by-address.md`.
2. Send the endpoint request without `api-key`.
3. If the gateway returns `402 Payment Required`, parse `PAYMENT-REQUIRED` (or response body equivalent).
4. Select the payment option that matches `WALLET_NETWORK` (default `eip155:1`).
5. Sign and retry with payment header(s): `PAYMENT-SIGNATURE` and/or `X-PAYMENT` depending client implementation.
6. Return the API body and payment settlement metadata (`PAYMENT-RESPONSE` or `X-PAYMENT-RESPONSE`) when present.

## x402 Headers

- `PAYMENT-REQUIRED`: payment challenge from the gateway.
- `PAYMENT-SIGNATURE`: signed payment proof from the client.
- `PAYMENT-RESPONSE`: payment/settlement metadata on success.
- `X-PAYMENT` / `X-PAYMENT-RESPONSE`: alternate header pair used by some clients.

## Explorer Transaction Lookup

After successful payment, extract `transaction` and `network` from `PAYMENT-RESPONSE` (or `X-PAYMENT-RESPONSE`) and return an explorer link.

- `eip155:1` (Ethereum mainnet): `https://etherscan.io/tx/<transaction_hash>`
- `eip155:8453` (Base mainnet): `https://basescan.org/tx/<transaction_hash>`

If explorer mapping is unknown, still return:

- raw transaction hash
- network id from response
- note that explorer URL could not be resolved automatically

## Recommended Client Stack

Prefer current `@x402/*` client packages for compatibility with CAIP-2 networks such as `eip155:1` and `eip155:8453`.

- Recommended: `@x402/fetch` + `@x402/evm`.
- Avoid older `x402-fetch`/`x402` v1-only assumptions when challenge uses CAIP-2 network IDs.

## General Transaction Initiation (Without x402 SDK)

If `@x402/*` is unavailable, agents may initiate payment manually with any EVM signer.

1. Send request and capture `402` challenge (`PAYMENT-REQUIRED` header or JSON body).
2. Pick the payment option matching `WALLET_NETWORK` (default `eip155:1`).
3. Build EIP-712 `TransferWithAuthorization` message using challenge fields:
   `asset`, `payTo`, `amount`, `maxTimeoutSeconds`, and token metadata in `extra`.
4. Sign typed data with wallet key.
5. Build payment payload with:
   `x402Version`, `scheme`, `network`, and signed authorization payload.
6. Base64-encode the payload and retry request with `PAYMENT-SIGNATURE` and/or `X-PAYMENT`.
7. Verify success via HTTP `200` and `PAYMENT-RESPONSE`/`X-PAYMENT-RESPONSE`.

Manual flow is valid, but preferred only as fallback because protocol/encoding details are easy to get wrong.

## Rules For Agents

- Do not hardcode payment amount, recipient, or network; use `PAYMENT-REQUIRED` each time.
- If user asked for mainnet, enforce `eip155:1` selection unless user explicitly requested Base mainnet.
- Ask before any fallback network (`eip155:8453`) or any move to testnet.
- Support both wallet modes: `PRIVATE_KEY` signer or CDP Agent Wallet signer.
- If user intent is unclear, confirm before sending the first paid mainnet request (real USDC spend).
- Re-run challenge flow if payment verification fails or challenge details change.
- If no funded wallet is available, stop and ask only for missing minimum inputs.
- Keep implementation direct and endpoint-specific.

## Minimal Failure Handling

If paid retry returns `402` again, report concise diagnostics:

1. Selected payment network.
2. Challenge amount and token.
3. Wallet address used for signing.
4. Next required user action:
   fund USDC and gas on the selected mainnet network, then retry.

## Primary Source

- `https://docs.gomaestro.org/bitcoin`
