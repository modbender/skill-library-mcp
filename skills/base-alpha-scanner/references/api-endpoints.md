# Base Alpha Scanner — API & Endpoint Reference

## DexScreener (no auth required)

| Endpoint | Use |
|----------|-----|
| `GET /latest/dex/search?q=<term>` | Search tokens by name/symbol |
| `GET /latest/dex/tokens/<addr>` | All pairs for a token address |
| `GET /latest/dex/pairs/base/<pair_addr>` | Single pair data |
| `GET /token-profiles/latest/v1` | Latest token profiles |
| `GET /token-boosts/top/v1` | Boosted tokens (paid promotions — low signal) |

Base URL: `https://api.dexscreener.com`

Key fields in pair response:
- `pairCreatedAt` — unix ms timestamp of pair creation
- `priceChange.h1 / h6 / h24` — % change
- `volume.h1 / h6 / h24` — USD volume
- `liquidity.usd` — pool liquidity
- `txns.h1.buys / sells` — transaction counts
- `marketCap` — circulating mcap
- `fdv` — fully diluted valuation
- `pairAddress` — pair contract (use for DexScreener URL)
- `baseToken.address` — token contract

## Basescan (free tier = rate limited)

Base URL: `https://api.basescan.org/api`

| Module | Action | Key Params |
|--------|--------|------------|
| token | tokenholderlist | contractaddress, page, offset |
| token | tokentx | contractaddress, address |
| account | txlist | address |
| stats | tokensupply | contractaddress |

Free tier: 5 req/sec, no API key needed but limited.
Paid key: `BASESCAN_API_KEY` env var for higher limits.

Holder chart direct URL: `https://basescan.org/token/tokenholderchart/<addr>`

## GMGN.ai

Base URL: `https://gmgn.ai/defi/quotation/v1`

GMGN often requires browser-like session cookies. Prefer using the browser tool
or directing ZHAO to https://gmgn.ai/base/token/<addr> for manual review.

Public endpoints (may work without auth):
- `GET /rank/base/swaps/1h?orderby=swaps&direction=desc` — top swappers
- `GET /token/base/<addr>` — token data
- `GET /wallet/base/<wallet_addr>` — wallet analysis

## Clanker

Clanker deploys tokens via Farcaster casts. API:
- `https://www.clanker.world/api/tokens?sort=desc&page=1&limit=30`
- `https://www.clanker.world/api/tokens?sort=trending&page=1&limit=30`

Key fields: `name`, `symbol`, `contract_address`, `pool_address`, `deployer`, `cast_hash`, `created_at`

Clanker token quality signals:
- Deployer FID with real Farcaster history
- Cast engagement (likes/recasts before launch)
- Narrative fit: AI agents, culture, memes with community
- No anonymous deployers with 0 social history

## Bankr.fun

Bankr is a Farcaster-native buy/sell frame. No clean public API.
Primary signal: Warpcast channel activity at `https://warpcast.com/~/channel/bankr`

High-signal Bankr plays:
- Power users (high follower count) buying via frame
- Multiple distinct wallets entering within first 30min
- Token has Farcaster cast with 50+ likes before Bankr integration

## VIRTUAL Protocol

Official API: `https://api.virtuals.io/api/virtuals`

Key params:
- `filters[status]=DEPLOYED` — live agents only
- `sort[0]=createdAt:desc` — newest first
- `sort[0]=marketCap:desc` — largest first

VIRTUAL token address (Base): `0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b`

Quality signals for VIRTUAL agents:
- Has actual agent capabilities (not just a token)
- Twitter/X account with real followers
- Listed on virtuals.io with complete profile
- Holder distribution not top-heavy (top 10 < 40% supply)

## Conviction Scoring (built into scan_base.py)

Score 0–100, higher = more interesting. Weights:
- Volume (1h): 25 pts max
- Liquidity health: 15 pts max
- Buy pressure ratio: 15 pts max
- Age (45min–3h sweet spot): 15 pts max
- Price momentum: 20 pts max
- Mcap sanity (<$5M): 5 pts max

**Alert thresholds (ZHAO's rules):**
- Score ≥ 70 + age 45min–3h + vol growth → second-wave alert candidate
- Score ≥ 60 + age < 45min + clean signals → early gem ping
- Score < 50 → filter out, don't bother ZHAO
