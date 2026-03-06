---
name: etoro-api
description: "eToro Public API — full trading, market data, social, and watchlist integration. Supports SSO, Bearer, and API key auth."
metadata: {"clawdbot":{"emoji":"📈","always":false,"requires":{"bins":["curl","python3"]}}}
---

# eToro Public API 📈

Full eToro Public API integration with trading execution, market data, social feed, and watchlists.

**API Docs:** https://etoro-6fc30280.mintlify.app/
**Base URL:** `https://public-api.etoro.com/api/v1`

## Authentication

Three auth modes (priority order):
1. **SSO Access Token** — `Authorization: Bearer <access_token>`
2. **SSO Auth Token** — `Authorization: <etoro_user_id>`
3. **API Keys** — `x-api-key` + `x-user-key` + `x-request-id` (UUID)

## Endpoints

### Portfolio & Account
| Tool | Method | Endpoint | Auth |
|------|--------|----------|------|
| `get_portfolio` | GET | `/trading/info/portfolio` (demo: `/trading/info/demo/portfolio`) | Personal |
| `get_trading_history` | GET | `/trading/info/real/history` (demo: `/trading/info/demo/history`) | Personal |

### Trading Execution
All trading endpoints support real/demo mode. Demo adds `/demo/` after `/execution/`.

| Tool | Method | Endpoint |
|------|--------|----------|
| `open_position_by_amount` | POST | `/trading/execution/market-open-orders/by-amount` |
| `open_position_by_units` | POST | `/trading/execution/market-open-orders/by-units` |
| `close_position` | POST | `/trading/execution/market-close-orders/{positionId}` |
| `place_limit_order` | POST | `/trading/execution/limit-orders` |
| `cancel_limit_order` | DELETE | `/trading/execution/limit-orders/{orderId}` |
| `cancel_open_order` | DELETE | `/trading/execution/market-open-orders/{orderId}` |
| `cancel_close_order` | DELETE | `/trading/execution/market-close-orders/{orderId}` |

### Market Data (Public)
| Tool | Method | Endpoint |
|------|--------|----------|
| `get_market_data` | GET | `/market-data/search?internalSymbolFull=AAPL` |
| `get_market_rates` | GET | `/market-data/rates?instrumentIds=1001,1002` |
| `get_price_history` | GET | `/market-data/instruments/{id}/candles?period=OneMonth` |
| `get_trading_info` | GET | `/trading/info/instrument/{id}` |
| `get_asset_classes` | GET | `/market-data/instrument-types` |
| `get_exchanges` | GET | `/market-data/exchanges` |
| `get_instrument_metadata` | GET | `/market-data/instruments?instrumentIds=1001,1002` |
| `get_closing_prices` | GET | `/market-data/closing-prices` |

### Social
| Tool | Method | Endpoint |
|------|--------|----------|
| `get_instrument_feed` | GET | `/feeds/instruments/{id}?limit=5` |
| `get_popular_investors` | GET | `/copy/popular-investors?limit=10` |
| `search_users` | GET | `/users/search?query=...` |
| `get_user_portfolio` | GET | `/users/{username}/portfolio` |
| `get_user_stats` | GET | `/users/{username}/stats` |
| `get_user_feed` | GET | `/feeds/users/{username}?limit=5` |
| `create_post` | POST | `/feeds/posts` |
| `create_comment` | POST | `/feeds/posts/{postId}/comments` |

### Watchlists
| Tool | Method | Endpoint |
|------|--------|----------|
| `get_watchlists` | GET | `/watchlists` |
| `get_curated_lists` | GET | `/watchlists/curated` |
| `create_watchlist` | POST | `/watchlists` |
| `add_to_watchlist` | POST | `/watchlists/{watchlistId}/items` |
| `remove_from_watchlist` | DELETE | `/watchlists/{watchlistId}/items/{instrumentId}` |

## Key Notes
- Instrument IDs are numeric (not tickers). Resolve via `/market-data/search?internalSymbolFull=AAPL`
- Trading tools default to `mode=real`. Only use demo if explicitly requested.
- All trading execution is logged with full request details before sending.
- Rate limit: 100 req/min
