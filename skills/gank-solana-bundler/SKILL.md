# gank — solana trading terminal for agents

gank is a multi-wallet solana trading terminal. launch tokens on pump.fun, run swarm buys, volume bots, copy trades, manage wallets. we literally have the most toxic platform atm and now your agents can take full advantage of it lol.

base url: `https://gank.dev/api/v2`

auth: `Authorization: Bearer <GANK_API_KEY>`

get your key at gank.dev > settings > api keys. keys start with `pb_`.

errors always come back as `{ "success": false, "error": "..." }`.

---

## wallet types

gank uses typed wallets. each type is locked to its module — don't mix them up.

| type | what it's for |
|------|--------------|
| `dev` | launching tokens (pump.fun creator wallet) |
| `regular` | buying/selling, transfers |
| `bundle` | bundle buys at launch |
| `snipe` | sniping new launches |
| `swarm` | coordinated multi-wallet buys |
| `volume` | volume bot |
| `pug` | privacy protocol — clean funds via bnb/eth swap |

---

## wallets

**list your wallets**
```
GET /wallets/user
```
returns everything grouped by type.

```json
{
  "dev": [{ "id": 1, "wallet_address": "...", "label": "main dev" }],
  "regular": [...],
  "swarm": [...],
  "volume": [...]
}
```

**wallet balance**
```
GET /wallets/{id}/balance
```

**batch balances**
```
POST /wallets/balances
{ "addresses": ["addr1...", "addr2..."] }
```

**positions (all token holdings)**
```
GET /user/positions
```

**search tokens**
```
GET /search?q=pepe&limit=10
```

---

## launching a token

three steps: reserve mint → upload image → launch.

**1. reserve a vanity mint** (optional but worth it)
```
POST /launch/reserve-mint
```
gives you a `...pump` address upfront. the `keypair` field is the **mint keypair** (token contract address keypair, not a wallet private key), pass it straight to `/launch` as `reserved_mint_keypair`. don't store it beyond that.

```json
{ "success": true, "address": "AbcD...pump", "keypair": "base58..." }
```

**2. upload image + metadata to ipfs**
```
POST /ipfs/upload
Content-Type: multipart/form-data
```
fields: `file`, `name`, `symbol`, `description`, `twitter`, `telegram`, `website`

```json
{ "success": true, "metadata_uri": "https://ipfs.io/ipfs/Qm..." }
```

**3. launch**
```
POST /launch
```

```json
{
  "token_name": "my token",
  "token_ticker": "MTK",
  "metadata_uri": "https://ipfs.io/ipfs/Qm...",
  "dev_wallet_address": "DevWallet...",
  "dev_buy_sol": 0.5,
  "jito_tip": 0.0003,
  "reserved_mint_keypair": "base58_from_step1",
  "regular_wallets": [
    { "wallet_address": "Wallet1...", "amount": 0.1 },
    { "wallet_address": "Wallet2...", "amount": 0.2 }
  ],
  "bundle_groups": [
    {
      "block_target": 1,
      "wallets": [{ "wallet_address": "BundleWallet1...", "amount": 0.05 }]
    }
  ],
  "sniper_wallets": [
    { "wallet_address": "SnipeWallet1...", "amount": 0.1, "block_target": 2 }
  ]
}
```

```json
{ "success": true, "launch_id": "uuid", "token_mint": "...", "tx_signature": "..." }
```

**check launch status**
```
GET /launch/{launch_id}
```

**launch history**
```
GET /launch/history?limit=20
```

**save a launch config/preset**
```
PUT /launch/configs
{ "name": "my template", "config": { ...launch_params... } }
```

---

## buy & sell

**buy**
```
POST /phases/regular/buy
```
```json
{
  "wallet_address": "RegularWallet...",
  "token_mint": "TokenMint...",
  "amount_sol": 0.1,
  "slippage_bps": 500
}
```

**sell**
```
POST /phases/regular/sell
```
```json
{
  "wallet_address": "RegularWallet...",
  "token_mint": "TokenMint...",
  "sell_percentage": 100,
  "slippage_bps": 500
}
```

---

## swarm

swarm = hit a token from multiple wallets at the same time. useful for coordinated entries.

**swarm buy**
```
POST /phases/swarm/buy
```
```json
{
  "token_mint": "TokenMint...",
  "wallets": [
    { "wallet_address": "SwarmWallet1...", "amount_sol": 0.05 },
    { "wallet_address": "SwarmWallet2...", "amount_sol": 0.1 }
  ],
  "slippage_bps": 500
}
```

**swarm sell**
```
POST /phases/swarm/sell
```
```json
{
  "token_mint": "TokenMint...",
  "wallets": ["SwarmWallet1...", "SwarmWallet2..."],
  "sell_percentage": 100,
  "slippage_bps": 500
}
```

**consolidate sol back to one wallet**
```
POST /phases/swarm/consolidate
{ "source_wallets": ["..."], "destination_wallet": "MainWallet..." }
```

**recover (emergency drain — sells everything, sweeps sol)**
```
POST /phases/swarm/recover
{ "source_wallets": ["..."], "destination_wallet": "MainWallet..." }
```

---

## volume bot

**start**
```
POST /phases/volume/start
```
```json
{
  "token_mint": "TokenMint...",
  "wallet_addresses": ["VolumeWallet1...", "VolumeWallet2..."],
  "sol_per_trade": 0.001,
  "duration_minutes": 60,
  "intensity": "medium"
}
```
`intensity`: `"low"` | `"medium"` | `"high"`

returns `{ "success": true, "session_id": "uuid" }`

**stop**
```
POST /phases/volume/stop
{ "session_id": "uuid" }
```

---

## wallet ops

**transfer sol**
```
POST /wallets/transfer
{ "from_wallet": "...", "to_wallet": "...", "amount_sol": 1.0 }
```

**split sol (1 → many, max 50 targets)**
```
POST /wallets/split
{
  "source_wallet": "...",
  "targets": [
    { "address": "Wallet1...", "amount_sol": 0.1 },
    { "address": "Wallet2...", "amount_sol": 0.2 }
  ]
}
```

**vamp all (drain wallets — sells tokens, closes accounts, sweeps sol)**
```
POST /wallets/vamp-all
{ "source_wallets": ["Wallet1...", "Wallet2..."], "destination_wallet": "MainWallet..." }
```

**clean funds (privacy swap — sol→bnb→sol or sol→eth→sol, ~5 min)**

two routes available: `bnb` (BSC, default) or `eth` (Arbitrum). source and destination must match 1:1 — use fresh destination wallets.

get a quote first:
```
POST /wallets/clean-funds/quote
{ "amount_sol": 1.0, "route": "bnb" }
```

initiate:
```
POST /wallets/clean-funds
{ "source_wallets": ["Wallet1..."], "destination_wallets": ["FreshWallet1..."], "route": "bnb" }
```
`route`: `"bnb"` (default) | `"eth"` — xmr is not available.

check status:
```
GET /wallets/clean-funds/status
```

---

## sniping at launch

sniping is only available at launch time via `sniper_wallets` in the `/launch` payload — see the launch section above. standalone auto-snipe is not available.

---

## market data

**token info** (price, mcap, volume, holders, bonding curve %)
```
GET /token/{mint}
```

**ohlcv chart**
```
GET /market/chart/{mint}?limit=500&timeframe=5
```
timeframe is in minutes.

**holders**
```
GET /market/holders/{mint}?limit=20
```

**recent trades**
```
GET /market/trades/{mint}?limit=30
```

---

## referrals & stats

**your stats** (points, level, exp, trades, volume)
```
GET /auth/user-stats
```

**referral stats** (tier, l1/l2/l3 counts, earnings, claimable sol)
```
GET /user/referrals
```

**claim earnings** (pays to your payout wallet)
```
POST /user/referrals/claim
```

**leaderboard**
```
GET /user/leaderboard/points?limit=50
GET /user/leaderboard/referrals?limit=50
```

---

## fee preferences

```
GET /fees/preferences
POST /fees/preferences
```
```json
{
  "fee_mode": "manual",
  "priority_fee_max_sol": 0.001,
  "jito_tip_max_sol": 0.0005
}
```
`fee_mode`: `"auto"` | `"manual"`

---

## how to use this

**launching a token:**
```
reserve mint → upload image to ipfs → POST /launch → poll GET /launch/{id}
```

**coordinated buy:**
```
check balances → POST /phases/swarm/buy → GET /user/positions
```

**recovering funds:**
```
POST /wallets/vamp-all  (sells everything + sweeps sol)
or
POST /wallets/clean-funds  (privacy swap via bnb/eth, ~5 min)
```

---

## notes

- api keys start with `pb_` — don't log them, don't put them in prompts
- wallet private keys are encrypted server-side, the api never gives them back
- `reserve-mint` returns a **mint keypair** (the token's contract address keypair, not a wallet key), pass it to `/launch` as `reserved_mint_keypair` and discard after use
- sol amounts are in sol, not lamports
- slippage is in basis points — 500 = 5%
- sniping only works at launch time via `sniper_wallets` in `/launch` — no standalone auto-snipe
- clean funds routes: `bnb` (BSC) or `eth` (Arbitrum) — xmr is disabled
- the platform fee wallet is protected, you can't accidentally send to it

---

## config

`~/.openclaw/openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "gank": {
        "enabled": true,
        "apiKey": "pb_your_key_here"
      }
    }
  }
}
```

or just set `GANK_API_KEY` in env.

---

gank.dev · dm @pissdart on x or tg if something's broken
