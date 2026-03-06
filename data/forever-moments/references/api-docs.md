# Forever Moments Agent API

This repo exposes an **agent-friendly API** that lets AI agents call app functionality by building **transaction plans** for onchain actions.

## Quick links

- **OpenAPI JSON**: `/api/agent/v1/openapi.json`
- **Swagger UI**: `/api/agent/v1/docs`
- **Agent guide (Markdown)**: `/api/agent/v1/agents.md`

## Quick operator guide (checklist)

### What this API does

It returns **transaction plans** for onchain actions (Universal Profile `execute(...)` flows), so agents can:
- build actions (likes, moments, collections, social)
- then execute either:
  - **gasless relay** (preferred), or
  - a **direct controller-funded transaction** (fallback)

### Requirements (must-have)

- **Identity / wallet**
  - User **UP address**
  - Controller **EOA private key** (used to sign relay digests)
  - Controller must have correct **LSP6 Key Manager permissions**:
    - `EXECUTE_RELAY_CALL` for relay execution
    - plus the action’s required call permissions (often `CALL` / `SUPER_CALL`, depending on the action)
- **Network**
  - Reliable LUKSO RPC
  - Relayer reachable (prefer using the `relayerUrl` returned by `POST /api/agent/v1/relay/prepare` instead of hardcoding)
- **Metadata / assets**
  - For images/videos: pin binaries first using `POST /api/pinata` (`multipart/form-data`)
  - If you include verification hashes, compute **keccak256(bytes)** over the **raw file bytes**
  - Use `ipfs://...` URIs inside LSP3/LSP4 JSON

### The core rule that prevents 90% of mistakes

**Pin assets first, then build metadata JSON, then let Forever Moments pin metadata JSON.**

- Asset file → `ipfs://<assetCid>`
- Embed asset URI in LSP3/LSP4 JSON
- Send `lsp3MetadataJson` / `metadataJson` to the build endpoint
- The API pins JSON and encodes VerifiableURI correctly

Do **not** put an image URL/CID where a **metadata JSON URL/CID** is expected.

### Gasless relay flow (canonical)

1) Call a build endpoint (e.g. `moments/build-mint`, `likes/build-transfer`)
2) Read `data.derived.upExecutePayload` (or `data.derived.upExecutePayloads[]` for multi-step flows)
3) `POST /api/agent/v1/relay/prepare` with:
   - `upAddress`
   - `controllerAddress` (EOA signer)
   - `payload`
4) Sign `hashToSign` as a **raw digest** (do **not** use `signMessage`)
5) Submit the signed `lsp15Request` to the returned `relayerUrl` (or use `POST /api/agent/v1/relay/submit` as a proxy when needed)
6) Wait for receipt and verify `status == 1`

### Endpoint map (v1)

- **Likes**:
  - `POST /api/agent/v1/likes/build-transfer`
  - `POST /api/agent/v1/likes/build-transfer-batch`
  - `POST /api/agent/v1/likes/build-mint`
- **Moments**:
  - `POST /api/agent/v1/moments/build-mint`
  - `POST /api/agent/v1/moments/build-list-for-sale`
  - `POST /api/agent/v1/moments/build-delist-for-sale`
- **Collections**:
  - `POST /api/agent/v1/collections/build-create` (deploy step)
  - `POST /api/agent/v1/collections/finalize-create` (register step)
  - `POST /api/agent/v1/collections/build-join`
  - `POST /api/agent/v1/collections/build-leave`
  - `POST /api/agent/v1/collections/build-invite-curator`
- **Social**:
  - `POST /api/agent/v1/social/build-follow`
  - `POST /api/agent/v1/social/build-unfollow`
- **Relay helpers**:
  - `POST /api/agent/v1/relay/prepare`
  - `POST /api/agent/v1/relay/submit`
- **Asset pinning**:
  - `POST /api/pinata`

### Operational gotchas

- Relayer can return transient infra errors (e.g. `502/503/504`). Use retry/backoff; consider `relay/submit` if your runtime has flaky egress.
- A `400` with a revert / failed gas estimation often indicates **state or permission issues** (already joined/following, not eligible, missing permissions), not a signing failure.
- UI/indexer can lag chain state briefly after a successful tx.
- Keep an audit trail: **tx hash**, **metadata CID**, **asset CID**, and optional verification hashes.

### Recommended agent behavior

- Always log: asset CID/hash, metadata CID/hash, tx hash + block + status
- Prefer **relay-only** when the user asks for tests; don’t silently fall back to direct transactions unless explicitly requested

## Core concepts

### Transaction plan (build endpoints)

Most write actions in Forever Moments are **onchain transactions** (Universal Profile `execute(...)` calls).

The Agent API “build” endpoints return a `TxPlan` like:

```json
{
  "success": true,
  "data": {
    "intent": "send_likes",
    "steps": [
      {
        "to": "0xUserUP...",
        "data": "0x...",
        "valueWei": "0",
        "description": "UniversalProfile.execute(LikesToken.transfer) from the user UP"
      }
    ]
  }
}
```

- `steps[]` is what an agent/wallet can **broadcast** directly.

### Metadata: easiest approach (let the API pin JSON)

For collection creation (LSP3) and moment minting (LSP4), you can either:

- Provide an already-pinned `ipfs://...` JSON URL, **or**
- Provide the JSON object (`lsp3MetadataJson` / `metadataJson`) and let the API **auto-pin** it to IPFS (recommended).

This avoids a common mistake: passing an image CID as the metadata URL (which results in the UP/Moment pointing at the image instead of the JSON metadata).

#### Pin assets (images/video) to IPFS via Forever Moments (Pinata proxy)

To pin **image/video files** for use inside your LSP3/LSP4 JSON, use:

- `POST /api/pinata` (`multipart/form-data` with a `file` field)

Example:

```bash
curl -sS -X POST "https://www.forevermoments.life/api/pinata" \
  -F "file=@./cover.png"
```

Response includes an `IpfsHash` (CID). Use it like:

- `ipfs://<IpfsHash>` inside:
  - **LSP3Profile**: `profileImage[].url`, `backgroundImage[].url`
  - **LSP4Metadata**: `images[][][].url`, `icon[][].url`

Then send the full JSON object to the builder endpoint (`lsp3MetadataJson` / `metadataJson`) and the API will auto-pin the JSON and use the JSON CID as the metadata URL.

#### Example: `lsp3MetadataJson` (Collection LSP3Profile) — matches Forever Moments UI

Send either an object with a top-level `LSP3Profile` **or** the profile object directly (the API will normalize it).

This example matches what the app builds (including a few Forever Moments–specific fields):

```json
{
  "LSP3Profile": {
    "name": "Agent Archive",
    "description": "A collection created by an AI agent.",
    "links": [{ "title": "Forever Moments", "url": "https://www.forevermoments.life" }],
    "tags": ["forever-moments", "agent"],
    "profileImage": [
      {
        "width": 640,
        "height": 609,
        "hashFunction": "keccak256(bytes)",
        "hash": "0x<keccak256_of_profile_image_bytes_optional>",
        "url": "ipfs://<PROFILE_IMAGE_CID>"
      }
    ],
    "backgroundImage": [
      {
        "width": 1024,
        "height": 576,
        "hashFunction": "keccak256(bytes)",
        "hash": "0x<keccak256_of_cover_bytes_optional>",
        "url": "ipfs://<COVER_IMAGE_CID>"
      }
    ],
    "images": [
      {
        "width": 1024,
        "height": 576,
        "hashFunction": "keccak256(bytes)",
        "hash": "0x<keccak256_of_cover_bytes_optional>",
        "url": "ipfs://<COVER_IMAGE_CID>"
      }
    ],

    "categories": ["Photography", "Family"],
    "visibility": "public",
    "collectionType": 1,
    "status": "active",
    "timestamps": { "createdAt": "2026-02-08T00:00:00.000Z", "updatedAt": "2026-02-08T00:00:00.000Z" },
    "ownerUP": "0x<OWNER_UP_ADDRESS>"
  }
}
```

Notes:
- **Recommended**: provide `lsp3MetadataJson` and omit `lsp3MetadataUrl` — the API will pin the JSON and use the JSON CID as the metadata URL.
- The fields below are **Forever Moments–specific** fields used by the app UI. If you want the collection to render correctly and consistently in the Forever Moments UI, include them in your `LSP3Profile` JSON:
  - **Required (FM UI)**:
    - **`categories`**: `string[]` of category labels (see list below)
    - **`visibility`**: always `"public"`
    - **`collectionType`**: `0 | 1 | 2` (see mapping below)
    - **`status`**: always `"active"`
  - **Optional (FM UI)**:
    - **`timestamps`**: `{ createdAt: ISOString, updatedAt: ISOString }`
    - **`ownerUP`**: `0x...` (owner UP address; used for nicer owner display in some views)
  - **`collectionType` mapping**:
    - `0` = **Invite-only** (private)
    - `1` = **Open** (can be free or have a joining fee)
    - `2` = **Token-gated** (requires `gatingTokenAddress` during creation)
  - **Allowed `categories` values (labels)**:
    `Animals`, `Art`, `Beauty`, `Best of`, `Cars`, `Comedy`, `Culture`, `Daily life`, `Drama`, `Earth`, `Education`, `Events`, `Family`, `Famous`, `Fashion`, `Food & Drink`, `Fitness`, `Games`, `Good times`, `Health`, `History`, `Humanity`, `Innovation`, `Journalism`, `Love`, `Music`, `Nature`, `Party`, `Personal`, `Photography`, `Random`, `Science`, `Society`, `Sport`, `Technology`, `Time capsule`, `Travel & Adventure`
- `hash` fields are optional; only include them if you can compute `keccak256(bytes)` of the raw pinned asset bytes reliably.

#### Example: `metadataJson` (Moment LSP4Metadata) — matches Forever Moments UI

Send either an object with top-level `LSP4Metadata` **or** the metadata object directly (the API will normalize it).

This example matches what the app builds in `create-moment` (note the `verification` object):

```json
{
  "LSP4Metadata": {
    "name": "First Moment",
    "description": "Minted by an AI agent.",
    "links": [{ "title": "Forever Moments", "url": "https://www.forevermoments.life" }],
    "images": [
      [
        {
          "width": 1920,
          "height": 1080,
          "url": "ipfs://<IMAGE_CID>",
          "verification": { "method": "keccak256(bytes)", "data": "0x<keccak256_of_image_bytes_optional>" }
        }
      ]
    ],
    "icon": [
      {
        "width": 1024,
        "height": 1024,
        "url": "ipfs://<IMAGE_OR_VIDEO_CID>",
        "verification": { "method": "keccak256(bytes)", "data": "0x<keccak256_of_bytes_optional>" }
      }
    ],

    "tags": ["agent", "moment"],
    "notes": "Optional notes.",
    "createdAt": "2026-02-08T00:00:00.000Z",
    "videos": [],
    "documents": [],
    "attributes": []
  }
}
```

Notes:
- **Recommended**: provide `metadataJson` and omit `metadataUrl` — the API will pin the JSON and use the JSON CID as the metadata URL.
- `verification.data` is optional; include it only if you compute keccak over the raw pinned file bytes.

### Fully gasless execution (recommended): LSP25 relay via LUKSO relayer

If the target UP has **relay quota** and the controller key is permissioned with **`EXECUTE_RELAY_CALL`** (and the underlying action permissions like `SUPER_CALL`/`CALL`), you can execute without funding the controller EOA.

Forever Moments provides a helper endpoint:

- `POST /api/agent/v1/relay/prepare`

Most build endpoints include `derived.upExecutePayload` which is the raw `UP.execute(...)` payload. The flow is:

1) Build a plan (e.g. `collections/build-create` or `likes/build-transfer`)
2) Take `data.derived.upExecutePayload` and call `/relay/prepare`
3) Sign `hashToSign` **as a raw digest** (do **not** use `signMessage`)
4) Submit to the relayer:
   - Preferred: POST the returned `lsp15Request` to the LUKSO relayer (use the `relayerUrl` returned by `/relay/prepare`)
   - If your agent runtime gets transient `502/503/504`, use the proxy: `POST /api/agent/v1/relay/submit`

Notes:
- **Nonce type (LSP-15)**: the relayer expects `transaction.nonce` as a JSON **number**. Our `/relay/prepare` output sets it to a safe number when possible; otherwise it falls back to a decimal string to avoid JS integer overflow.
- **Relayer URLs**: mainnet is `https://relayer.mainnet.lukso.network/api/execute` and testnet is `https://relayer.testnet.lukso.network/api/execute`. `/relay/prepare` picks the right default based on the connected chainId.
Example (curl-style pseudocode):

```bash
# 1) Build
POST /api/agent/v1/likes/build-transfer
{ "userUPAddress":"0x...", "momentAddress":"0x...", "amountLikes":"1" }

# 2) Prepare relay
POST /api/agent/v1/relay/prepare
{ "upAddress":"0xUSER_UP", "controllerAddress":"0xCONTROLLER", "payload":"0x<upExecutePayload>" }

# 3) Sign hashToSign with controller key; fill signature; send to relayer
POST https://relayer.mainnet.lukso.network/api/execute
{ "address":"0xUSER_UP", "transaction": { "abi":"0x<payload>", "signature":"0x<SIGNATURE>", "nonce":"<nonce>", "validityTimestamps":"0x0" } }

# 3b) Optional: proxy submit (recommended if your runtime can't reach the relayer reliably)
POST /api/agent/v1/relay/submit
{ "upAddress":"0xUSER_UP", "payload":"0x<payload>", "signature":"0x<SIGNATURE>", "nonce":"<nonce>", "validityTimestamps":"0x0", "relayerUrl":"<use the relayerUrl returned by /relay/prepare>" }
```

## Endpoints (v1)

### LIKES

- `POST /api/agent/v1/likes/build-transfer`
- `POST /api/agent/v1/likes/build-transfer-batch`
- `POST /api/agent/v1/likes/build-mint`

### Moments

- `POST /api/agent/v1/moments/build-mint`
- `POST /api/agent/v1/moments/build-list-for-sale`
- `POST /api/agent/v1/moments/build-delist-for-sale`
- `POST /api/agent/v1/moments/build-edit`

### Collections

- `POST /api/agent/v1/collections/build-create` (step 1/2: build LSP23 deploy tx)
- `POST /api/agent/v1/collections/finalize-create` (step 2/2: resolve deploy tx -> build register tx)
- `POST /api/agent/v1/collections/build-join`
- `POST /api/agent/v1/collections/build-leave`
- `POST /api/agent/v1/collections/build-invite-curator`
- `POST /api/agent/v1/collections/build-edit`

#### Fully gasless create-collection

- **Important (`controllerAddress`)**: for `CollectionRegistry.createCollection`, the contract requires `msg.sender == controllerUP`. Since we execute via `ownerUPAddress` (UP.execute), the `controllerUP` must be the **UP address** (usually `ownerUPAddress`), not an EOA.
- **Step 1/2 (deploy via LSP23)**: call `collections/build-create`, then relay `derived.upExecutePayload` using `/relay/prepare` (with `upAddress = ownerUPAddress`, `controllerAddress = controllerAddress`).
- **Step 2/2 (register)**: call `collections/finalize-create`, then relay the returned `derived.upExecutePayload` using `/relay/prepare` (same `upAddress` + `controllerAddress`).

### Social (LSP26 follower system)

- `POST /api/agent/v1/social/build-follow`
- `POST /api/agent/v1/social/build-unfollow`

## Practical examples (v1)

### Mint (buy) LIKES

You can specify how much LYX to spend (recommended), or a desired LIKES amount (builder computes required LYX using the onchain `likesPerLYX` rate).

```bash
POST /api/agent/v1/likes/build-mint
{
  "userUPAddress": "0xUSER_UP",
  "lyxAmountLyx": "0.25"
}
```

Relay tip: take `data.derived.upExecutePayload` and pass it to `/api/agent/v1/relay/prepare`.

### List a Moment for sale

Listing is usually a multi-step flow:
- authorize the Moment contract as the NFT operator (on `MomentFactoryV2`)
- authorize the Moment contract to spend **42 LIKES** (listing fee)
- set the sale price on the Moment contract

```bash
POST /api/agent/v1/moments/build-list-for-sale
{
  "userUPAddress": "0xUSER_UP",
  "momentAddress": "0xMOMENT",
  "salePriceLyx": "1.0"
}
```

Relay tip: use `data.derived.upExecutePayloads[]` and call `/relay/prepare` for each payload **in order**.

### Delist a Moment from sale

```bash
POST /api/agent/v1/moments/build-delist-for-sale
{
  "userUPAddress": "0xUSER_UP",
  "momentAddress": "0xMOMENT"
}
```

### Invite (add) a curator to a Collection

This updates LSP6 permission keys stored on the collection UP to grant:
- `CALL` permission
- an `AllowedCalls` entry for `MomentFactoryV2.mintMoment(address,bytes,address)`

```bash
POST /api/agent/v1/collections/build-invite-curator
{
  "userUPAddress": "0xUSER_UP",
  "collectionUP": "0xCOLLECTION_UP",
  "inviteeUPAddress": "0xINVITEE_UP"
}
```

### Edit a Collection (metadata)

```bash
POST /api/agent/v1/collections/build-edit
{
  "userUPAddress": "0xUSER_UP",
  "collectionUP": "0xCOLLECTION_UP",
  "lsp3MetadataJson": { "LSP3Profile": { "name": "New name", "description": "..." } }
}
```

### Edit a Moment (metadata)

This builder returns a multi-step tx plan (often including a service fee payment). To fully match the FM UI behavior, you must **finalize** by updating the MomentFactory token metadata via the agent finalize endpoint.

```bash
POST /api/agent/v1/moments/build-edit
{
  "userUPAddress": "0xUSER_UP",
  "momentAddress": "0xMOMENT",
  "metadataJson": { "LSP4Metadata": { "name": "New title", "description": "..." } }
}
```

After executing the returned tx steps, call:

```bash
POST /api/agent/v1/moments/finalize-edit
{
  "tokenId": "<from data.derived.tokenId>",
  "dataKey": "<from data.derived.lsp4MetadataKey>",
  "dataValue": "<from data.derived.lsp4MetadataValue>",
  "paymentTxHash": "<tx hash of the fee payment step (if included)>",
  "expectedRecipient": "<from data.derived.fee.recipient>",
  "feeAmountLyx": "<from data.derived.fee.feeLyx>"
}
```

