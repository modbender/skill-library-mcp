# Messari REST API Services Reference

Detailed breakdown of each service available through the Messari REST API.

**Base URL:** `https://api.messari.io`
**Auth Header:** `x-messari-api-key: <YOUR_API_KEY>`

---

## AI Service

Messari's AI completions endpoint, trained on 30TB+ of structured and unstructured crypto data.

**Data sources include:** market/price data, fundraising data, network metrics, Messari-exclusive
research reports, newsletters, podcasts, and curated third-party content (news, social posts).

**Use for:** open-ended crypto questions, synthesis across multiple data sources, market analysis,
protocol comparisons, narrative summaries.

**Requires:** Messari AI credits.

| Endpoint | Method | Description |
|---|---|---|
| `/ai/v1/chat/completions` | POST | Chat completion against Messari's crypto data warehouse |
| `/ai/openai/chat/completions` | POST | OpenAI-compatible chat completion endpoint |

**Key parameters (POST body):**
- `messages` — array of `{role, content}` message objects
- `stream` — boolean, enable streaming responses

---

## Signal Service

Real-time social intelligence and narrative tracking.

**Use for:** sentiment shifts, mindshare tracking, trending narratives, social-driven signals.

| Endpoint | Method | Description |
|---|---|---|
| `/signal/v1/assets` | GET | List assets with signal metrics |
| `/signal/v1/assets/{assetId}` | GET | Signal metrics for a specific asset |
| `/signal/v1/assets/{assetId}/timeseries` | GET | Historical signal timeseries for an asset |
| `/signal/v1/assets/gainers-losers` | GET | Top mindshare gainers and losers |

**Key query parameters:**
- `type` — signal type (e.g., `mindshare`)
- `limit` — number of results
- `start`, `end` — date range for timeseries (ISO 8601)

---

## Metrics Service

Comprehensive quantitative data across the crypto market.

**Coverage:** 34,000+ assets, 210+ exchanges, 175+ filterable metrics.

**Use for:** quantitative analysis, asset comparison, trend identification, portfolio-level data.

| Endpoint | Method | Description |
|---|---|---|
| `/metrics/v2/assets` | GET | List assets with market metrics |
| `/metrics/v2/assets/{assetId}` | GET | Detailed metrics for a specific asset |
| `/metrics/v2/assets/{assetId}/roi` | GET | ROI data for an asset |
| `/metrics/v2/assets/{assetId}/ath` | GET | All-time high data for an asset |
| `/metrics/v2/assets/{assetId}/timeseries` | GET | Historical metric timeseries for an asset |

**Key query parameters:**
- `assetSlugs` — comma-separated asset slugs (e.g., `bitcoin,ethereum`)
- `assetIds` — comma-separated asset IDs
- `metrics` — specific metrics to return
- `start`, `end` — date range for timeseries (ISO 8601)
- `interval` — timeseries interval (e.g., `1d`, `1w`)
- `limit`, `page` — pagination

---

## News Service

Real-time crypto news aggregation.

**Use for:** event-driven queries, breaking news, project updates, regulatory developments.

| Endpoint | Method | Description |
|---|---|---|
| `/news/v1/news/feed` | GET | Aggregated crypto news feed |
| `/news/v1/news/sources` | GET | List available news sources |

**Key query parameters:**
- `assetSlugs` — filter news by asset
- `limit`, `page` — pagination
- `sourceIds` — filter by specific news sources

---

## Research Service

Institutional-grade research from Messari's analyst team.

**Use for:** fundamental research, due diligence, sector analysis, protocol evaluations.

| Endpoint | Method | Description |
|---|---|---|
| `/research/v1/reports` | GET | List research reports |
| `/research/v1/reports/{reportId}` | GET | Get a specific report |
| `/research/v1/reports/tags` | GET | List available report tags |

**Key query parameters:**
- `tags` — filter by report tags
- `assetSlugs` — filter by related assets
- `limit`, `page` — pagination

---

## Stablecoins Service

Dedicated stablecoin analytics.

**Coverage:** 25+ stablecoins with per-chain breakdowns.

**Use for:** stablecoin supply analysis, chain-level flow tracking, market share shifts.

| Endpoint | Method | Description |
|---|---|---|
| `/stablecoins/v2/stablecoins` | GET | List stablecoins with metrics |
| `/stablecoins/v2/stablecoins/{stablecoinId}` | GET | Detailed metrics for a stablecoin |
| `/stablecoins/v2/stablecoins/{stablecoinId}/timeseries` | GET | Historical timeseries for a stablecoin |

**Key query parameters:**
- `metrics` — specific stablecoin metrics
- `chains` — filter by blockchain
- `start`, `end` — date range for timeseries (ISO 8601)
- `interval` — timeseries interval
- `limit`, `page` — pagination

---

## Exchanges Service

Crypto exchange market data.

**Use for:** exchange volume analysis, exchange-level metrics, cross-exchange comparisons.

| Endpoint | Method | Description |
|---|---|---|
| `/exchanges/v2/exchanges` | GET | List exchanges with metrics |
| `/exchanges/v2/exchanges/{exchangeId}` | GET | Detailed metrics for an exchange |
| `/exchanges/v2/exchanges/{exchangeId}/timeseries` | GET | Historical timeseries for an exchange |

**Key query parameters:**
- `exchangeSlugs` — comma-separated exchange slugs
- `metrics` — specific exchange metrics
- `start`, `end` — date range for timeseries (ISO 8601)
- `interval` — timeseries interval
- `limit`, `page` — pagination

---

## Networks Service

L1/L2 blockchain network metrics.

**Use for:** network activity analysis, chain comparisons, on-chain metrics.

| Endpoint | Method | Description |
|---|---|---|
| `/networks/v2/networks` | GET | List networks with metrics |
| `/networks/v2/networks/{networkId}` | GET | Detailed metrics for a network |
| `/networks/v2/networks/{networkId}/timeseries` | GET | Historical timeseries for a network |

**Key query parameters:**
- `networkSlugs` — comma-separated network slugs
- `metrics` — specific network metrics
- `start`, `end` — date range for timeseries (ISO 8601)
- `interval` — timeseries interval
- `limit`, `page` — pagination

---

## Protocols Service

DeFi protocol metrics across multiple categories.

**Use for:** DeFi analysis, protocol comparisons, TVL tracking, yield data.

| Endpoint | Method | Description |
|---|---|---|
| `/protocols/v2/protocols` | GET | List protocols with metrics |
| `/protocols/v2/protocols/{protocolId}` | GET | Detailed metrics for a protocol |
| `/protocols/v2/protocols/dex` | GET | DEX-specific protocol metrics |
| `/protocols/v2/protocols/lending` | GET | Lending protocol metrics |
| `/protocols/v2/protocols/interop` | GET | Interoperability/bridge protocol metrics |
| `/protocols/v2/protocols/liquid-staking` | GET | Liquid staking protocol metrics |

**Key query parameters:**
- `protocolSlugs` — comma-separated protocol slugs
- `metrics` — specific protocol metrics
- `limit`, `page` — pagination

---

## Token Unlocks Service

Token vesting schedules and unlock events.

**Use for:** tracking upcoming token unlocks, supply pressure analysis, vesting schedule lookup.

| Endpoint | Method | Description |
|---|---|---|
| `/token-unlocks/v1/assets` | GET | List assets with token unlock data |
| `/token-unlocks/v1/assets/{assetId}` | GET | Token unlock details for an asset |
| `/token-unlocks/v1/assets/{assetId}/events` | GET | Upcoming unlock events for an asset |
| `/token-unlocks/v1/assets/{assetId}/vesting` | GET | Full vesting schedule for an asset |

**Key query parameters:**
- `assetSlugs` — comma-separated asset slugs
- `start`, `end` — date range filter (ISO 8601)
- `limit`, `page` — pagination

---

## Fundraising Service

Crypto fundraising data including rounds, investors, and M&A activity.

**Use for:** tracking funding rounds, investor activity, project fundraising history, M&A deals.

| Endpoint | Method | Description |
|---|---|---|
| `/fundraising/v1/rounds` | GET | List fundraising rounds |
| `/fundraising/v1/organizations` | GET | List organizations involved in fundraising |
| `/fundraising/v1/projects` | GET | List projects that have raised funding |
| `/fundraising/v1/investors` | GET | List investors and their activity |
| `/fundraising/v1/funds` | GET | List investment funds |
| `/fundraising/v1/mergers-acquisitions` | GET | List M&A transactions |

**Key query parameters:**
- `assetSlugs` — filter by related asset
- `investorSlugs` — filter by investor
- `roundTypes` — filter by round type (e.g., `seed`, `series-a`)
- `start`, `end` — date range (ISO 8601)
- `limit`, `page` — pagination

---

## Intel Service

Governance events, protocol updates, and project milestones.

**Use for:** tracking governance proposals, protocol upgrades, key project events.

| Endpoint | Method | Description |
|---|---|---|
| `/intel/v1/events` | GET | List intel events |
| `/intel/v1/events/{eventId}` | GET | Details for a specific event |
| `/intel/v1/assets` | GET | List assets with intel event data |

**Key query parameters:**
- `assetSlugs` — filter by asset
- `eventTypes` — filter by event type
- `start`, `end` — date range (ISO 8601)
- `limit`, `page` — pagination

---

## Topics Service

Trending topic classification and timeseries.

**Use for:** identifying trending narratives, tracking topic momentum over time.

| Endpoint | Method | Description |
|---|---|---|
| `/topics/v1/classes` | GET | List topic classes/categories |
| `/topics/v1/current` | GET | Currently trending topics |
| `/topics/v1/timeseries` | GET | Daily topic trend timeseries |

**Key query parameters:**
- `classIds` — filter by topic class
- `start`, `end` — date range (ISO 8601)
- `limit` — number of results

---

## X-Users Service

Crypto X/Twitter user metrics and influence tracking.

**Use for:** tracking influential crypto accounts, social activity metrics, influence timeseries.

| Endpoint | Method | Description |
|---|---|---|
| `/signal/v1/x-users` | GET | List crypto X/Twitter users with metrics |
| `/signal/v1/x-users/{userId}` | GET | Metrics for a specific X user |
| `/signal/v1/x-users/{userId}/timeseries` | GET | Historical metrics for an X user |

**Key query parameters:**
- `limit`, `page` — pagination
- `start`, `end` — date range for timeseries (ISO 8601)
