name: toa-news
description: Real-time crypto news API with millisecond-level updates. Supports keyword search, coin filtering, and pagination. 6551-compatible format.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - curl
    emoji: "📡"
    tags:
      - crypto
      - news
      - trading
      - api
    os:
      - darwin
      - linux
      - win32
  version: 1.0.1
---

# ToA Crypto News Skill

Real-time crypto news API powered by Tree of Alpha WebSocket. Millisecond-level market updates with coin tagging and search.

**Base URL**: `https://web-production-666f44.up.railway.app`

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/news` | GET | Simple news fetch |
| `/news_search` | POST | Advanced search (6551-compatible) |

---

## 1. Health Check

```bash
curl -s "https://web-production-666f44.up.railway.app/health"

Returns: {"status": "ok"}


2. Get Latest News (Simple)

curl -s "https://web-production-666f44.up.railway.app/news?limit=10"

| Parameter | Type    | Default | Description         |
| --------- | ------- | ------- | ------------------- |
| limit     | integer | 10      | Max results (1-100) |


3. Advanced Search (Recommended)

POST /news_search — 6551-compatible format with filtering and pagination.

Get Latest News

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "page": 1}'

Search by Keyword

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"q": "bitcoin ETF", "limit": 10, "page": 1}'

Filter by Coin

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"coins": ["BTC", "ETH"], "limit": 10, "page": 1}'

Only News with Coins

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"hasCoin": true, "limit": 10, "page": 1}'

Search Parameters

| Parameter | Type     | Required | Description                                 |
| --------- | -------- | -------- | ------------------------------------------- |
| limit     | integer  | yes      | Max results per page (1-100)                |
| page      | integer  | yes      | Page number (1-based)                       |
| q         | string   | no       | Full-text keyword search                    |
| coins     | string[] | no       | Filter by coin symbols (e.g. ["BTC","ETH"]) |
| hasCoin   | boolean  | no       | Only return news with associated coins      |


Response Format

{
  "success": true,
  "total": 130,
  "page": 1,
  "limit": 10,
  "quota": "unlimited",
  "data": [
    {
      "id": "2027363213940293775",
      "text": "Yi He (@heyibinance)",
      "body": "Binance is actively exploring talent...",
      "newsType": "direct",
      "engineType": "news",
      "link": "https://twitter.com/heyibinance/status/...",
      "ts": 1772196031975,
      "receivedAt": "2026-02-27T12:40:32.615200+00:00",
      "coins": [
        {
          "symbol": "BNB",
          "market_type": "spot",
          "match": "title"
        }
      ],
      "aiRating": {
        "status": "pending",
        "score": null,
        "grade": null,
        "signal": null,
        "summary": null,
        "enSummary": null
      }
    }
  ]
}

Key Fields

| Field    | Description                           |
| -------- | ------------------------------------- |
| id       | Unique article ID                     |
| text     | Source name and handle                |
| body     | Full content text                     |
| coins    | Detected coins with exchange symbols  |
| link     | Original source URL                   |
| ts       | Unix timestamp (milliseconds)         |
| aiRating | AI analysis (pending = not yet rated) |


Common Workflows

Quick Market Overview

WISEBOT, [2026/2/27 21:31]
curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "page": 1}' | jq '.data[] | {text, body, coins}'

BTC News Only

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"coins": ["BTC"], "limit": 10, "page": 1}'

Search Binance News

curl -s -X POST "https://web-production-666f44.up.railway.app/news_search" \
  -H "Content-Type: application/json" \
  -d '{"q": "Binance", "limit": 10, "page": 1}'


Notes

• Data source: Tree of Alpha WebSocket (real-time)
• Update frequency: Millisecond-level
• Storage: Cloud PostgreSQL (persistent, 24/7)
• Rate limits: None currently
• AI Rating: Coming soon (score, grade, signal, summary)
