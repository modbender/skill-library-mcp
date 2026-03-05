# G-Prophet AI Skills Documentation

> Stock prediction and market analysis capabilities for AI agents

## Overview

G-Prophet is an AI-powered stock prediction platform that exposes its core capabilities through an external API for other AI agent systems. It supports global markets (China A-shares, US stocks, HK stocks, Crypto) and provides AI prediction, technical analysis, market sentiment, and deep analysis Skills.

## Basic Information

| Item | Description |
|------|-------------|
| API Base URL | `https://www.gprophet.com/api/external/v1` |
| Authentication | `X-API-Key` header |
| Key Format | `gp_sk_` prefix (e.g. `gp_sk_live_a1b2c3...`) |
| Response Format | JSON |
| Billing | Points-based, each call consumes corresponding points |

## Authentication

All requests must include an API Key in the HTTP header:

```
X-API-Key: gp_sk_live_your_api_key_here
```

API Keys can be created in the G-Prophet platform under "Settings → API Key Management".

## Unified Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2026-02-18T10:30:00Z",
    "processing_time_ms": 1250,
    "api_version": "v1"
  },
  "error": null
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "metadata": { ... },
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Stock symbol 'XXXXX' not found",
    "details": {}
  }
}
```

## Points Cost

| Skill | Endpoint | Points/Call |
|-------|----------|-------------|
| Stock Prediction | `POST /predictions/predict` | CN 10, HK 15, US 20, Crypto 20 |
| Algorithm Compare | `POST /predictions/compare` | Single prediction cost × number of algorithms |
| Quote | `GET /market-data/quote` | 5 |
| History | `GET /market-data/history` | 5 |
| Search | `GET /market-data/search` | 5 |
| Technical Analysis | `POST /technical/analyze` | 5 |
| Fear & Greed Index | `GET /sentiment/fear-greed` | 5 |
| Market Overview | `GET /sentiment/market-overview` | 5 |
| Deep Analysis | `POST /analysis/comprehensive` | 150 |
| Task Polling | `GET /analysis/task/{task_id}` | 0 (free) |

---

## Skill 1: Stock Price Prediction

Predict future stock/cryptocurrency price movements using AI algorithms. Supports G-Prophet2026V1, LSTM, Transformer, and more.

### POST /predictions/predict

**Request Body (JSON):**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | ✅ | - | Stock/crypto ticker (e.g. AAPL, 600519, BTCUSDT) |
| market | string | ✅ | - | Market code: `US`, `CN`, `HK`, `CRYPTO` |
| days | integer | No | 7 | Prediction days, range 1-30 |
| algorithm | string | No | auto | Algorithm: `auto`, `gprophet2026v1`, `lstm`, `transformer`, `random_forest`, `ensemble` |

**Example Request:**

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/predictions/predict" \
  -H "X-API-Key: gp_sk_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "market": "US", "days": 7, "algorithm": "auto"}'
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "market": "US",
    "current_price": 185.50,
    "predicted_price": 191.20,
    "change_percent": 3.07,
    "direction": "up",
    "confidence": 0.78,
    "prediction_days": 7,
    "algorithm_used": "gprophet2026v1",
    "data_quality": {
      "completeness": 1.0,
      "anomaly_count": 82,
      "missing_values": 0,
      "overall_score": 80
    },
    "points_consumed": 20
  }
}
```

### POST /predictions/compare

Multi-algorithm comparison prediction. Returns results from each algorithm and the best recommendation. Points cost = single prediction cost × number of algorithms.

**Request Body (JSON):**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | ✅ | - | Stock/crypto ticker |
| market | string | ✅ | - | Market code: `US`, `CN`, `HK`, `CRYPTO` |
| days | integer | No | 5 | Prediction days, range 1-30 |
| algorithms | string[] | No | ["gprophet2026v1","lstm","transformer","ensemble"] | Algorithm list, max 6 |

**Example Request:**

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/predictions/compare" \
  -H "X-API-Key: gp_sk_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA", "market": "US", "days": 5, "algorithms": ["gprophet2026v1", "lstm", "transformer"]}'
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "TSLA",
    "market": "US",
    "current_price": 245.00,
    "prediction_days": 5,
    "results": [
      {
        "algorithm": "gprophet2026v1",
        "predicted_price": 252.30,
        "change_percent": 2.98,
        "direction": "up",
        "confidence": 0.82,
        "success": true
      },
      {
        "algorithm": "lstm",
        "predicted_price": 248.10,
        "change_percent": 1.27,
        "direction": "up",
        "confidence": 0.71,
        "success": true
      }
    ],
    "best_algorithm": "gprophet2026v1",
    "consensus_direction": "up",
    "average_predicted_price": 250.20,
    "points_consumed": 60
  }
}
```

---

## Skill 2: Market Data

Get real-time quotes, historical OHLCV data, and search for stocks/crypto. Each call costs 5 points.

### GET /market-data/quote

Get real-time quote.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| symbol | string | ✅ | Stock/crypto ticker |
| market | string | ✅ | Market code: `US`, `CN`, `HK`, `CRYPTO` |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/quote?symbol=AAPL&market=US" \
  -H "X-API-Key: gp_sk_live_your_key"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "market": "US",
    "name": "Apple Inc.",
    "price": 185.50,
    "open": 183.90,
    "high": 186.80,
    "low": 183.20,
    "volume": 52340000,
    "previous_close": 183.20,
    "change": 2.30,
    "change_percent": 1.26,
    "points_consumed": 5
  }
}
```

### GET /market-data/history

Get historical OHLCV candlestick data.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | ✅ | - | Stock/crypto ticker |
| market | string | ✅ | - | Market code |
| period | string | No | 3m | Time range: `1w`, `1m`, `3m`, `6m`, `1y`, `2y` |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/history?symbol=AAPL&market=US&period=3m" \
  -H "X-API-Key: gp_sk_live_your_key"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "market": "US",
    "period": "3m",
    "data_points": 63,
    "history": [
      {
        "date": "2025-12-01",
        "open": 178.50,
        "high": 180.20,
        "low": 177.80,
        "close": 179.90,
        "volume": 48500000
      }
    ],
    "points_consumed": 5
  }
}
```

### GET /market-data/search

Search for stocks/crypto by keyword.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | ✅ | - | Search keyword |
| market | string | No | US | Market code |
| limit | integer | No | 10 | Result count, range 1-50 |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/market-data/search?keyword=apple&market=US&limit=5" \
  -H "X-API-Key: gp_sk_live_your_key"
```

---

## Skill 3: Technical Analysis

Calculate technical indicators and generate trading signals for a given stock. Each call costs 5 points.

### POST /technical/analyze

**Request Body (JSON):**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | ✅ | - | Stock/crypto ticker |
| market | string | ✅ | - | Market code: `US`, `CN`, `HK`, `CRYPTO` |
| indicators | string[] | No | ["rsi","macd","bollinger","kdj"] | Indicators: `rsi`, `macd`, `bollinger`, `kdj`, `sma`, `ema` |

**Example Request:**

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/technical/analyze" \
  -H "X-API-Key: gp_sk_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "market": "US", "indicators": ["rsi", "macd", "bollinger", "kdj"]}'
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "market": "US",
    "current_price": 185.50,
    "indicators": {
      "rsi_14": { "value": 55.3, "signal": "neutral" },
      "macd": { "macd": 1.25, "signal": 0.98, "histogram": 0.27, "signal_type": "bullish" },
      "bollinger": { "upper": 192.0, "middle": 185.0, "lower": 178.0, "position": 0.54 },
      "kdj": { "k": 65.2, "d": 58.7, "j": 78.2 }
    },
    "signals": [
      { "type": "bullish", "indicator": "MACD" },
      { "type": "neutral", "indicator": "RSI" }
    ],
    "overall_signal": "bullish",
    "signal_strength": 0.5,
    "points_consumed": 5
  }
}
```

---

## Skill 4: Market Sentiment

Get market sentiment data including Fear & Greed Index and market overview. Each call costs 5 points.

### GET /sentiment/fear-greed

Get the crypto market Fear & Greed Index.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | integer | No | 1 | History days, 1=current only, range 1-365 |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/sentiment/fear-greed?days=1" \
  -H "X-API-Key: gp_sk_live_your_key"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "value": 72,
    "classification": "greed",
    "previous_value": 68,
    "change": 4,
    "points_consumed": 5
  }
}
```

### GET /sentiment/market-overview

Get comprehensive market overview (breadth, hot sectors, major indices).

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| market | string | No | CN | Market code: `CN`, `US` |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/sentiment/market-overview?market=CN" \
  -H "X-API-Key: gp_sk_live_your_key"
```

---

## Skill 5: Deep Analysis (Async)

Multi-agent collaborative deep analysis evaluating stocks from 5 dimensions: technical, fundamental, capital flow, sentiment, and macro environment. Costs 150 points.

> ⚠️ **Async Mode**: Deep analysis typically takes 30-120 seconds, so this endpoint uses async mode.
> 1. `POST /analysis/comprehensive` → Returns `task_id` immediately
> 2. `GET /analysis/task/{task_id}` → Poll for status; get results when `status=completed`
>
> Recommended polling interval: 5 seconds. Max wait: 5 minutes.

### POST /analysis/comprehensive

Submit a deep analysis task. Returns task ID immediately.

**Request Body (JSON):**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| symbol | string | ✅ | - | Stock/crypto ticker |
| market | string | ✅ | - | Market code: `US`, `CN`, `HK`, `CRYPTO` |
| locale | string | No | zh-CN | Report language: `zh-CN`, `en-US` |

**Example Request:**

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/analysis/comprehensive" \
  -H "X-API-Key: gp_sk_live_your_key" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "market": "US", "locale": "en-US"}'
```

**Example Response (immediate):**

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "symbol": "AAPL",
    "market": "US",
    "status": "pending",
    "points_consumed": 150,
    "poll_url": "/api/external/v1/analysis/task/task_abc123def456",
    "message": "Analysis started. Poll the task URL every 5 seconds for results."
  }
}
```

### GET /analysis/task/{task_id}

Poll analysis task status and results.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | Task ID returned by POST /analysis/comprehensive |

**Example Request:**

```bash
curl "https://www.gprophet.com/api/external/v1/analysis/task/task_abc123def456" \
  -H "X-API-Key: gp_sk_live_your_key"
```

**Status Flow:** `pending` → `running` (progress 0-100) → `completed` / `failed`

**Example Response (in progress):**

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "running",
    "progress": 45,
    "message": "Analyzing fundamental data...",
    "result": null,
    "error": null
  }
}
```

**Example Response (completed):**

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "completed",
    "progress": 100,
    "message": "Analysis completed",
    "result": {
      "symbol": "AAPL",
      "asset_type": "stock_us",
      "analysis": {
        "overall_rating": "bullish",
        "confidence": 0.75,
        "agents": {
          "technical": {
            "rating": "bullish",
            "confidence": 0.80,
            "key_points": ["MACD golden cross", "Above 20-day MA"],
            "summary": "Technical outlook is bullish..."
          },
          "fundamental": {
            "rating": "neutral",
            "confidence": 0.65,
            "key_points": ["Reasonable PE", "Revenue growth slowing"],
            "summary": "Fundamentals are neutral..."
          },
          "capital_flow": {
            "rating": "bullish",
            "confidence": 0.70,
            "key_points": ["Net institutional inflow"],
            "summary": "Capital flow is positive..."
          },
          "sentiment": {
            "rating": "neutral",
            "confidence": 0.60,
            "key_points": ["Stable market sentiment"],
            "summary": "Sentiment is neutral..."
          },
          "macro": {
            "rating": "cautious",
            "confidence": 0.55,
            "key_points": ["Rate hike expectations", "Geopolitical risks"],
            "summary": "Macro environment is cautious..."
          }
        },
        "final_recommendation": "Short-term bullish, consider buying on dips, watch macro risks",
        "risk_level": "medium"
      }
    },
    "error": null
  }
}
```

**Example Response (failed):**

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "failed",
    "progress": 100,
    "message": "Analysis service timeout",
    "result": null,
    "error": "Analysis service timeout"
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| MISSING_API_KEY | 401 | Missing X-API-Key header |
| INVALID_KEY_FORMAT | 401 | Invalid API Key format (must start with gp_sk_) |
| INVALID_API_KEY | 401 | Invalid API Key |
| API_KEY_DISABLED | 403 | API Key has been disabled |
| API_KEY_EXPIRED | 403 | API Key has expired |
| INSUFFICIENT_SCOPE | 403 | API Key lacks permission for this Skill |
| INSUFFICIENT_POINTS | 402 | Insufficient points |
| POINTS_DEDUCTION_FAILED | 402 | Failed to deduct points |
| OWNER_NOT_FOUND | 403 | API Key owner account not found |
| INVALID_MARKET | 400 | Unsupported market code |
| SYMBOL_NOT_FOUND | 404 | Stock/crypto ticker not found |
| NO_DATA | 404 | Unable to retrieve data |
| TOO_MANY_ALGORITHMS | 400 | Too many algorithms (max 6) |
| PREDICTION_FAILED | 500 | Prediction service error |
| ANALYSIS_FAILED | 500 | Analysis service error |
| TASK_NOT_FOUND | 404 | Async task not found or expired |
| FORBIDDEN | 403 | Access denied (e.g. querying another user's task) |
| DATA_UNAVAILABLE | 503 | Data source temporarily unavailable |
| INTERNAL_ERROR | 500 | Internal service error |

---

## MCP Tools Definitions

MCP (Model Context Protocol) tool definitions for use with Claude, Kiro, and other MCP-compatible agents:

### gprophet_predict_stock

```json
{
  "name": "gprophet_predict_stock",
  "description": "Predict future stock/cryptocurrency price movements using G-Prophet AI. Supports multiple algorithms (G-Prophet2026V1, LSTM, Transformer, etc.) and global markets (China A-shares, US, HK, Crypto).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker, e.g. AAPL, 600519, BTCUSDT" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"], "description": "Market code" },
      "days": { "type": "integer", "minimum": 1, "maximum": 30, "default": 7, "description": "Prediction days" },
      "algorithm": { "type": "string", "enum": ["auto", "gprophet2026v1", "lstm", "transformer", "random_forest", "ensemble"], "default": "auto", "description": "Prediction algorithm" }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_compare_algorithms

```json
{
  "name": "gprophet_compare_algorithms",
  "description": "Compare multiple AI algorithms predicting the same stock simultaneously. Returns each algorithm's result and the best recommendation.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"] },
      "days": { "type": "integer", "minimum": 1, "maximum": 30, "default": 5 },
      "algorithms": { "type": "array", "items": { "type": "string", "enum": ["gprophet2026v1", "lstm", "transformer", "random_forest", "ensemble"] }, "description": "Algorithm list, max 6" }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_get_quote

```json
{
  "name": "gprophet_get_quote",
  "description": "Get real-time stock/cryptocurrency quote including price, change, volume.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"] }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_get_history

```json
{
  "name": "gprophet_get_history",
  "description": "Get historical OHLCV candlestick data for a stock/cryptocurrency.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"] },
      "period": { "type": "string", "enum": ["1w", "1m", "3m", "6m", "1y", "2y"], "default": "3m", "description": "Time range" }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_search_stocks

```json
{
  "name": "gprophet_search_stocks",
  "description": "Search for stocks/cryptocurrencies by keyword.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "keyword": { "type": "string", "description": "Search keyword" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"], "default": "US" },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
    },
    "required": ["keyword"]
  }
}
```

### gprophet_technical_analysis

```json
{
  "name": "gprophet_technical_analysis",
  "description": "Calculate technical indicators (RSI, MACD, Bollinger Bands, KDJ, etc.) and generate trading signals.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"] },
      "indicators": { "type": "array", "items": { "type": "string", "enum": ["rsi", "macd", "bollinger", "kdj", "sma", "ema"] }, "default": ["rsi", "macd", "bollinger", "kdj"], "description": "Technical indicators to calculate" }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_fear_greed_index

```json
{
  "name": "gprophet_fear_greed_index",
  "description": "Get the crypto market Fear & Greed Index reflecting market sentiment.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "days": { "type": "integer", "minimum": 1, "maximum": 365, "default": 1, "description": "History days, 1=current only" }
    }
  }
}
```

### gprophet_market_overview

```json
{
  "name": "gprophet_market_overview",
  "description": "Get comprehensive market overview including breadth, hot sectors, and major indices.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "market": { "type": "string", "enum": ["CN", "US"], "default": "CN", "description": "Market code" }
    }
  }
}
```

### gprophet_deep_analysis

```json
{
  "name": "gprophet_deep_analysis",
  "description": "Multi-agent collaborative deep analysis (async mode). Submits an analysis task and returns task_id immediately. Use gprophet_get_analysis_task to poll for results. Evaluates stocks from 5 dimensions: technical, fundamental, capital flow, sentiment, and macro environment. Costs 150 points.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "symbol": { "type": "string", "description": "Stock/crypto ticker" },
      "market": { "type": "string", "enum": ["US", "CN", "HK", "CRYPTO"] },
      "locale": { "type": "string", "enum": ["zh-CN", "en-US"], "default": "zh-CN", "description": "Report language" }
    },
    "required": ["symbol", "market"]
  }
}
```

### gprophet_get_analysis_task

```json
{
  "name": "gprophet_get_analysis_task",
  "description": "Poll deep analysis task status. When status is 'completed', the result field contains the full analysis. When status is 'failed', the error field contains the error message. Recommended polling interval: 5 seconds. Max wait: 5 minutes.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": { "type": "string", "description": "Task ID returned by gprophet_deep_analysis" }
    },
    "required": ["task_id"]
  }
}
```

---

## Integration Guide

### Typical Prediction Flow

```
1. Call gprophet_predict_stock to get prediction results (sync, typically 5-30 seconds)
2. Use data.direction and data.confidence to assess the trend
3. Optional: Call gprophet_technical_analysis for technical confirmation
```

### Typical Deep Analysis Flow

```
1. Call gprophet_deep_analysis to submit analysis task → get task_id
2. Poll gprophet_get_analysis_task every 5 seconds
3. When status = "completed", read the full report from result.analysis
4. When status = "failed", read the failure reason from error
```

### Agent Integration Tips

- **Search before predicting**: If unsure about a ticker, use `gprophet_search_stocks` to confirm first
- **Combine skills**: Prediction + Technical Analysis + Sentiment = more comprehensive judgment
- **Points management**: Deep analysis costs 150 points; use it selectively for key targets
- **Error handling**: Check the `success` field; on failure, refer to `error.code` for retry logic or user messaging

---

## Supported Market Codes

| Code | Market | Ticker Format | Example Tickers |
|------|--------|---------------|-----------------|
| CN | China A-shares | 6-digit number. 6xxxxx=Shanghai, 0/3xxxxx=Shenzhen | 600519, 000001, 300750 |
| US | US Stocks | Alphabetic ticker symbol | AAPL, TSLA, GOOGL, MSFT |
| HK | Hong Kong Stocks | Numeric code (no zero-padding needed) | 700, 9988, 1810, 3007 |
| CRYPTO | Cryptocurrency | Trading pair (ending in USDT) | BTCUSDT, ETHUSDT, SOLUSDT |

> ⚠️ **A-share Ticker Notes**:
> - A-share tickers are **6-digit numbers**; different prefixes indicate different exchanges/boards
> - `6xxxxx` = Shanghai Stock Exchange (Main Board / STAR Market)
> - `0xxxxx` = Shenzhen Stock Exchange (Main Board / SME Board)
> - `3xxxxx` = Shenzhen Stock Exchange (ChiNext / Growth Enterprise Market)
> - Make sure to pass the correct 6-digit code, e.g. `600986` (Zhewenhulan) and `000001` (Ping An Bank) are different stocks

## Supported Prediction Algorithms

| Algorithm | Description |
|-----------|-------------|
| auto | Automatically select the best algorithm |
| gprophet2026v1 | G-Prophet2026V1 proprietary model (recommended) |
| lstm | Long Short-Term Memory network |
| transformer | Transformer model |
| random_forest | Random Forest |
| ensemble | Ensemble learning (multi-algorithm fusion) |
