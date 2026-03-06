# Pinwin API reference

**Base URL:** `https://api.pinwin.xyz`  
All requests: `Content-Type: application/json`. On error (4xx/5xx), body may have `error` or `message`.

## POST /agent/bet

**Request:** `amount` (number, USDT smallest units, 6 decimals), `minOdds` (positive integer, 12 decimals), `chain: "polygon"`, `selections` (array of `{ conditionId: string, outcomeId: number }`). Single: minOdds = one outcome’s odds × 1e12. Combo: minOdds = product of each selection’s odds in 12-decimal space (e.g. (o1×1e12 × o2×1e12) / 1e12).

**Response 200:** `{ "encoded": "<base64>" }`. Decode: `payload = JSON.parse(atob(response.encoded))`.

**Decoded payload:** `signableClientBetData`, `apiClientBetData`, `domain`, `types`, `apiUrl`, `environment`.

**Decoded payload structure (Azuro-aligned).** Top-level: `signableClientBetData`, `apiClientBetData`, `domain`, `types`, `apiUrl`, `environment`. **clientData** (under either): `attention`, `affiliate`, `core`, `expiresAt`, `chainId`, `relayerFeeAmount`, `isFeeSponsored`, `isBetSponsored`, `isSponsoredBetReturnable`. **Bet data:** Always use **`signableClientBetData.bets`** (array): one element = single, multiple = combo. Each element has `conditionId`, `outcomeId`, `amount`, `minOdds`, `nonce`. Azuro’s order API has ordinar (single) and combo (bets[]); Pinwin sets `apiUrl` and `apiClientBetData` accordingly—submit as returned.

**Before signing:** (1) **Display to the user** amount and selections from `signableClientBetData.bets` (with human-readable names from data-feed/dictionaries), `relayerFeeAmount`, `apiUrl`, `environment`, and all **clientData** fields. (2) Give a short **human-readable summary**: stake, selection/market names, relayer fee. (3) **Verify:** amount and selections (from `bets`) match the user’s request; **clientData.core** (lowercase) equals **claimContract** in [polygon.md](polygon.md). Use only the **relayer** from [polygon.md](polygon.md) for allowance/approve. If anything does not match, do not sign and report to the user.

**EIP-712 primaryType:** Use `primaryType: 'ClientComboBetData'` if `payload.types.ClientComboBetData` exists, otherwise `primaryType: 'ClientBetData'`. Pass this to viem `signTypedData` along with `domain`, `types`, and `message: payload.signableClientBetData`.

**After sign:** POST to `payload.apiUrl` with body: `environment`, `bettor`, `betOwner`, `clientBetData` (= `payload.apiClientBetData`), `bettorSignature` (hex with `0x`). The `apiUrl` in the payload may point to the Azuro/OnchainFeed order API (e.g. `https://api.onchainfeed.org/...`); use the URL returned in the payload.

**Order submission response (Azuro order API):** JSON with `id` (string, **order id**), `state` (e.g. `Created`, `Rejected`, `Canceled`, `Accepted`), and optional `errorMessage`, `error`. The order id is **always this response `id`** — use it for polling. On 4xx/5xx the response body may still be JSON with `state`, `error`, `errorMessage` (e.g. 409 and "Different games in one order" for invalid combo); when submission fails, show the user the status and body (or at least `errorMessage` / `error`).

**Poll order status (when you have an order id):** Same base URL as `apiUrl` (e.g. strip `/bet/orders/ordinar` or `/bet/orders/combo` to get the base). Request: **GET** `{apiBase}/bet/orders/{orderId}`. Poll until terminal: **success** = response includes `txHash`; **failure** = `state` is `Rejected` or `Canceled` (use `errorMessage` if present). Stop polling when you get `txHash` or a failure state.

## POST /agent/claim

**Request:** `betIds` (number[], on-chain bet ids — e.g. from bets subgraph where `isRedeemable: true`), `chain: "polygon"`.

**Response 200:** `{ "encoded": "<base64>" }`. Decode: `payload = JSON.parse(atob(response.encoded))`.

**Decoded payload:** `to` (contract address), `data` (hex calldata), `value` ("0"), `chainId` (number). **Explain to the user in human-readable terms** what the claim tx does: e.g. claiming winnings for bet IDs [X, Y], transaction target (Azuro ClientCore on Polygon), no value sent. You may also display the full decoded payload. Verify `payload.to` (lowercase) equals the **claimContract** (ClientCore) for Polygon in [polygon.md](polygon.md)—this is the redeem contract for won/canceled bets. If it does not match, do not send. Then send tx with viem: `sendTransaction({ to: payload.to, data: payload.data, value: 0n, chainId: payload.chainId })`. Wait for receipt.
