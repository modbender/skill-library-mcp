# NOFX API Response Examples

## AI500 List

```json
{
  "success": true,
  "data": {
    "coins": [
      {
        "pair": "POWERUSDT",
        "score": 87.385,
        "start_time": 1770683700,
        "start_price": 0.25585,
        "last_score": 81.21,
        "max_score": 88.66,
        "max_price": 0.41825,
        "increase_percent": 63.47
      }
    ],
    "count": 3
  }
}
```

## AI300 List

```json
{
  "success": true,
  "data": {
    "coins": [
      {
        "rank": 1,
        "symbol": "ASTER",
        "future_flow": 3341335.19,
        "spot_flow": 525990.18,
        "level": "S"
      },
      {
        "rank": 2,
        "symbol": "BCH",
        "future_flow": 964889.28,
        "spot_flow": 6132.01,
        "level": "A"
      }
    ],
    "count": 10
  }
}
```

## Netflow Ranking

```json
{
  "success": true,
  "data": {
    "count": 10,
    "limit": 10,
    "netflows": [
      {
        "amount": 132692732.74,
        "price": 1950.41,
        "rank": 1,
        "symbol": "ETHUSDT"
      }
    ],
    "rank_type": "top",
    "time_range": "1h",
    "trade": "future",
    "type": "institution"
  }
}
```

## OI Ranking

```json
{
  "success": true,
  "data": {
    "count": 10,
    "exchange": "binance",
    "positions": [
      {
        "current_oi": 1773693.274,
        "net_long": -855488.22,
        "net_short": 647034.16,
        "oi_delta": 11245.82,
        "oi_delta_percent": 0.63,
        "oi_delta_value": 81088700.36,
        "price_delta_percent": 1.74,
        "rank": 1,
        "symbol": "ETHUSDT"
      }
    ],
    "rank_type": "top",
    "time_range": "1h"
  }
}
```

## Price Ranking

```json
{
  "success": true,
  "data": {
    "data": {
      "1h": {
        "top": [
          {
            "pair": "YALAUSDT",
            "symbol": "YALA",
            "price_delta": 0.299,
            "price": 0.01445,
            "future_flow": 10419171.3,
            "spot_flow": 0,
            "oi": 542674993,
            "oi_delta": -144774990,
            "oi_delta_value": -284890.88
          }
        ]
      }
    }
  }
}
```

## Funding Rate

```json
{
  "success": true,
  "data": {
    "count": 10,
    "desc": "Positive funding rate ranking (crowded longs)",
    "rank_type": "top",
    "rates": [
      {
        "rank": 1,
        "symbol": "1000000BOB",
        "funding_rate": 0.160772,
        "mark_price": 0.01228,
        "index_price": 0.01211714,
        "next_funding_time": 1770840000000
      }
    ]
  }
}
```

## Long-Short List

```json
{
  "success": true,
  "data": {
    "coins": [
      {
        "rank": 1,
        "symbol": "POWER",
        "score": 87.385,
        "start_time": 1770683700,
        "start_price": 0.25585,
        "current_price": 0.37214,
        "price_change_pct": 45.45,
        "max_price": 0.41825,
        "max_score": 88.66
      }
    ]
  }
}
```

## OI Market Cap Ranking

```json
{
  "success": true,
  "data": {
    "count": 10,
    "exchange": "binance",
    "rankings": [
      {
        "rank": 1,
        "symbol": "BTC",
        "oi": 81014.876,
        "oi_value": 5427696936.96,
        "price": 66996.3,
        "net_long": -46092.98,
        "net_short": 37709.32
      }
    ]
  }
}
```

## Heatmap

```json
{
  "success": true,
  "data": {
    "count": 10,
    "heatmaps": [
      {
        "rank": 1,
        "symbol": "ETH",
        "bid_volume": 48294621.13,
        "ask_volume": 59703654.08,
        "delta": -11409032.95
      }
    ],
    "trade": "future"
  }
}
```

## Single Coin Data

```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "price": 67106.6,
    "price_change": {
      "1h": 0.015,
      "4h": 0.023,
      "24h": 0.045
    },
    "netflow": {
      "institution": {
        "1h": 26510000,
        "4h": 85000000
      },
      "personal": {
        "1h": -5000000
      }
    },
    "oi": {
      "binance": {
        "oi": 81000,
        "oi_delta_percent": 0.5,
        "oi_delta_value": 37000000
      }
    },
    "ai500": {
      "score": 72.5,
      "is_active": true
    }
  }
}
```
