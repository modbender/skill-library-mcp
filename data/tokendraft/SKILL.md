---
name: tokendraft
description: Full suite for TokenDraft fantasy crypto tournaments — authenticate with a Solana wallet, query/join/auto-join tournaments, and manage auto-draft asset priority rankings.
env:
  - name: SOLANA_PRIVATE_KEY
    description: Base58-encoded Solana Ed25519 private key used to derive the wallet public key, sign authentication challenges, and sign on-chain buy-in transactions.
    required: true
    sensitive: true
---

# TokenDraft Authentication

Two-step challenge-response flow. Private key never leaves the local environment.

After successful login, store `TOKENDRAFT_USER_ID` (from `user.id`) and `TOKENDRAFT_JWT` (from `token`) as env vars. These are required by all other TokenDraft endpoints.

**If any TokenDraft endpoint returns 401, re-run this auth flow automatically and retry the failed request.**

## Step 1: Request a Nonce

```bash
curl -X POST https://tokendraft-production.up.railway.app/api/v2/agents/nonce \
  -H "Content-Type: application/json" \
  -d '{"walletPublicKey": "<WALLET_PUBLIC_KEY>"}'
```

Returns `{ nonce, message }`. The `message` is the exact string to sign. Nonce expires after 5 minutes, single-use.

## Step 2: Sign and Log In

Sign `message` locally with Ed25519, base58-encode the signature:

```bash
curl -X POST https://tokendraft-production.up.railway.app/api/v2/agents/login \
  -H "Content-Type: application/json" \
  -d '{
    "walletPublicKey": "<WALLET_PUBLIC_KEY>",
    "nonce": "<NONCE>",
    "signature": "<BASE58_SIGNATURE>"
  }'
```

Returns `{ token, user }`. First login auto-creates an account.

**On first login** (the user's `displayName` is a short hash like `"a3F9x"`), ask the user if they'd like to set a display name. If yes, call the Update Display Name endpoint below.

## Update Display Name

```bash
curl -X POST "https://tokendraft-production.up.railway.app/api/v2/users/displayName" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT" \
  -H "Content-Type: application/json" \
  -d '{"displayName": "<NEW_NAME>"}'
```

Constraints: display name must be unique across all users. Can only be changed once every 24 hours. HTTP 429 is returned with `retryAfterMs` if rate-limited.

## Signing Reference

```javascript
import nacl from 'tweetnacl';
import bs58 from 'bs58';

const secretKey = bs58.decode(process.env.SOLANA_PRIVATE_KEY);
const keyPair = nacl.sign.keyPair.fromSecretKey(secretKey);
const walletPublicKey = bs58.encode(keyPair.publicKey);

// Step 1
const { nonce, message } = await fetch('https://tokendraft-production.up.railway.app/api/v2/agents/nonce', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ walletPublicKey }),
}).then(r => r.json());

// Step 2
const messageBytes = new TextEncoder().encode(message);
const signature = nacl.sign.detached(messageBytes, keyPair.secretKey);
const signatureBase58 = bs58.encode(signature);

const { token, user } = await fetch('https://tokendraft-production.up.railway.app/api/v2/agents/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ walletPublicKey, nonce, signature: signatureBase58 }),
}).then(r => r.json());
```

## Token Usage

Include in all authenticated requests:

```
Authorization: Bearer $TOKENDRAFT_JWT
```

Token does not expire but may be invalidated on server secret rotation.

---

# TokenDraft Tournaments

All endpoints use base URL `https://tokendraft-production.up.railway.app` and require `Authorization: Bearer $TOKENDRAFT_JWT`. Re-authenticate via the auth flow above on 401.

## Query Tournaments

```bash
curl "https://tokendraft-production.up.railway.app/api/v2/agents/tournaments?<PARAMS>" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT"
```

| Param | Type | Description |
|-------|------|-------------|
| `isOpen` | boolean | Accepting registrations |
| `isInProgress` | boolean | Currently being played |
| `isFinished` | boolean | Completed |
| `isRegistered` | boolean | Filter by user's registration status |
| `finishedLookbackHours` | number | Hours to look back for finished (default: 24, 0 = all) |

Filters combine with AND. No state filter defaults to open tournaments only.

Returns array of `TournamentSummary`:

```typescript
{ id: string, name: string, buyInAmountSol: number, registrationStartTime: string,
  registrationEndTime: string, state: string, numPlayersRegistered: number,
  maxPlayers: number, amIRegistered: boolean,
  draftType: "snake" | "boosterPack" | "instantRoster",
  rosterSlots: { Chain?: number, Meme?: number, Utility?: number, NFT?: number, Flex?: number } }
```

## Join Free Tournament

If `buyInAmountSol` is 0:

```bash
curl -X POST "https://tokendraft-production.up.railway.app/api/v2/tournaments/join/<TOURNAMENT_ID>" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT"
```

HTTP 200 = registered. Relay any error to the user.

Update asset priority rankings if this is an instant roster tournament.

## Join Paid Tournament (Buy-In)

For `buyInAmountSol > 0`, verify SOL balance covers the buy-in + fees first.

**1. Initiate transaction:**

```bash
curl -X POST "https://tokendraft-production.up.railway.app/api/v2/buyIn/initiateTransaction" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT" \
  -H "Content-Type: application/json" \
  -d '{"tournamentId": "<ID>", "walletPublicKey": "<PUBKEY>"}'
```

Returns `{ transaction (base64), expectedSignature, tournamentInfo }`.

**2. Sign:** Deserialize `transaction` as `VersionedTransaction`, sign with wallet keypair, re-serialize to base64.

**3. Send signed transaction:**

```bash
curl -X POST "https://tokendraft-production.up.railway.app/api/v2/buyIn/sendSignedTransaction" \
  -H "Content-Type: application/json" \
  -d '{
    "signedTransactionBase64": "<BASE64>",
    "tournamentId": "<ID>",
    "expectedSignature": "<SIG>",
    "walletPublicKey": "<PUBKEY>"
  }'
```

HTTP 200 = registered. Relay errors (tournament full, already registered, on-chain failure).

Update asset priority rankings if this is an instant roster tournament.

## Instant Roster Tournaments

When `draftType` is `"instantRoster"`, the system auto-drafts the entire roster instantly from the player's asset priority rankings. There is no live draft — all picks happen at machine speed with 0-second turns. Duplicates between players are allowed (two players can have the same token), but a player cannot have the same token twice.

**After joining an instantRoster tournament, you MUST set asset priority rankings** so the auto-drafter knows what to pick.

### How to build rankings that fulfil roster slots

The tournament's `rosterSlots` tells you how many assets of each type are needed. Each asset from `GET /api/v2/assets` has an `assetType` field (e.g. `"Chain"`, `"Meme"`, `"Utility"`, `"NFT"`). The `"Flex"` slot accepts any type.

**Steps:**

1. Fetch assets: `GET /api/v2/assets` — returns `[{ id, name, ticker, assetType, priceUSD, marketcapUSD, dayChangePercent, dayVolumeUSD, ... }]`
2. Read `rosterSlots` from the tournament (e.g. `{ "Chain": 2, "Meme": 2, "Utility": 1, "NFT": 1, "Flex": 1 }`)
3. For each slot type (except Flex), pick the best assets of that `assetType` based on user strategy
4. For the Flex slot(s), pick the best remaining asset of any type
5. If a slot is not present, or has value <= 0, ignore all assets of that type when ranking.
6. Submit as ranked list via `PUT /api/v2/assetPriorityRankings`

**Example** — given `rosterSlots: { "Chain": 2, "Meme": 2, "Utility": 1, "NFT": 1, "Flex": 1 }` and a "highest market cap" strategy:

```
assets = GET /api/v2/assets
Sort assets by marketcapUSD descending within each assetType:
  chains  = assets.filter(a => a.assetType === "Chain").sort(by marketcapUSD desc)
  memes   = assets.filter(a => a.assetType === "Meme").sort(by marketcapUSD desc)
  utils   = assets.filter(a => a.assetType === "Utility").sort(by marketcapUSD desc)
  nfts    = assets.filter(a => a.assetType === "NFT").sort(by marketcapUSD desc)

Pick top N for each slot:
  rank 1: chains[0]    (Chain slot 1)
  rank 2: chains[1]    (Chain slot 2)
  rank 3: memes[0]     (Meme slot 1)
  rank 4: memes[1]     (Meme slot 2)
  rank 5: utils[0]     (Utility slot)
  rank 6: nfts[0]      (NFT slot)
  rank 7: best remaining asset of any type (Flex slot)

Anything set to rank 1 will be selected as "captain", and be worth double points, so set rank 1 as best overall pick within roster.

PUT /api/v2/assetPriorityRankings with:
  { "assets": [{"assetId":"<chains[0].id>","rank":1}, ...], "autoDraftStrategy": "MKT_CAP_DESC" }
```

### Full flow for instantRoster tournaments

1. Query open tournaments and find one with `draftType === "instantRoster"`
2. Join the tournament (free or paid flow as above)
3. Fetch assets from `GET /api/v2/assets`
4. Build a ranked list of 7 assets that fulfil the tournament's `rosterSlots`, using the user's preferred strategy (ask if not known)
5. Submit rankings via `PUT /api/v2/assetPriorityRankings`
6. **Report to the user** which assets were picked for each slot and ask if they want to make any changes before the draft starts
7. If the user requests changes, update rankings accordingly and re-submit

## Auto-Join (Cron)

Set up a cron job to join all open tournaments every 30 minutes:

```bash
openclaw cron add \
  --name "tokendraft-auto-join" \
  --cron "*/30 * * * *" \
  --session isolated \
  --message "Auto-join open TokenDraft tournaments. Steps:
1. Authenticate with TokenDraft (see auth section above).
2. GET /agents/tournaments?isOpen=true&isRegistered=false to find open tournaments.
3. For each: if buyInAmountSol is 0, POST /tournaments/join/<id>. If > 0, check SOL balance and follow buy-in flow.
4. If the joined tournament has draftType 'instantRoster', also set asset priority rankings that fulfil the rosterSlots.
5. Report results for each tournament (joined or error reason)."
```

Manage with `openclaw cron list`, `openclaw cron remove <id>`, `openclaw cron edit <id> --enabled false/true`.

---

# TokenDraft Asset Rankings

All endpoints use base URL `https://tokendraft-production.up.railway.app` and require `Authorization: Bearer $TOKENDRAFT_JWT`. Re-authenticate via the auth flow above on 401.

## Step 1: Ask the User for Ranking Advice

Ask how they want assets ranked before fetching data (e.g. by market cap, volume, buy the dip, memecoins first).

## Step 2: Fetch Assets

```bash
curl "https://tokendraft-production.up.railway.app/api/v2/assets" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT"
```

Returns array of assets with fields: `id`, `name`, `ticker`, `priceUSD`, `marketcapUSD`, `dayChangePercent`, `dayVolumeUSD`, `adpRanking`, `assetType`, `tags`.

## Step 3: Rank

Assign each asset a rank from 1 (drafted first) to N (last). Use the user's advice combined with financial data.

Built-in strategies (set as `autoDraftStrategy` to use instead of manual ranks):

`VOL_24H_DESC`, `VOL_24H_ASC`, `MKT_CAP_ASC`, `MKT_CAP_DESC`, `ADP`, `PERCENT_24H_ASC`, `PERCENT_24H_DESC`



## Step 4: Submit Rankings

```bash
curl -X PUT "https://tokendraft-production.up.railway.app/api/v2/assetPriorityRankings" \
  -H "Authorization: Bearer $TOKENDRAFT_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [{"assetId": "<ID>", "rank": 1}, ...],
    "autoDraftStrategy": "PERCENT_24H_DESC"
  }'
```

Include only the top 7 assets. Set `rank` to unique integers. `autoDraftStrategy` is required, so default to "PERCENT_24H_DESC" if not specified by user. This is the fallback if any assets are unavailable from rankings.

## Auto-Update Rankings (Cron)

Ask the user for ranking advice and update frequency, then create a cron job:

```bash
openclaw cron add \
  --name "tokendraft-auto-rank" \
  --cron "<CRON_EXPRESSION>" \
  --session isolated \
  --message "Update TokenDraft rankings. Steps:
1. Authenticate (see auth section above).
2. GET /api/v2/assets for current data.
3. Rank all assets 1-N based on: <USER_RANKING_ADVICE>.
4. PUT /api/v2/assetPriorityRankings with ranked list.
5. Report success or failure."
```

Manage with `openclaw cron list`, `openclaw cron remove <id>`, `openclaw cron edit <id> --enabled false/true`.
