#!/bin/bash
# NOFX API Helper Script
# Usage: ./nofx-api.sh <endpoint> [params]

set -e

# Configuration
CONFIG_FILE="${NOFX_CONFIG:-$HOME/clawd/skills/nofx/config.json}"
BASE_URL="https://nofxos.ai"

# Load API key from config
if [ -f "$CONFIG_FILE" ]; then
    API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE" 2>/dev/null)
fi

# Override with environment variable if set
API_KEY="${NOFX_API_KEY:-$API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: API key not found. Set NOFX_API_KEY or configure config.json" >&2
    exit 1
fi

# Endpoints
endpoint="$1"
shift || true

case "$endpoint" in
    # AI Signals
    ai500)
        curl -s "$BASE_URL/api/ai500/list?auth=$API_KEY"
        ;;
    ai500-stats)
        curl -s "$BASE_URL/api/ai500/stats?auth=$API_KEY"
        ;;
    ai500-coin)
        symbol="${1:-BTC}"
        curl -s "$BASE_URL/api/ai500/$symbol?auth=$API_KEY"
        ;;
    ai300)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/ai300/list?auth=$API_KEY&limit=$limit"
        ;;
    ai300-stats)
        curl -s "$BASE_URL/api/ai300/stats?auth=$API_KEY"
        ;;
    
    # Fund Flow
    flow-in)
        limit="${1:-10}"
        duration="${2:-1h}"
        type="${3:-institution}"
        curl -s "$BASE_URL/api/netflow/top-ranking?auth=$API_KEY&limit=$limit&duration=$duration&type=$type"
        ;;
    flow-out)
        limit="${1:-10}"
        duration="${2:-1h}"
        type="${3:-institution}"
        curl -s "$BASE_URL/api/netflow/low-ranking?auth=$API_KEY&limit=$limit&duration=$duration&type=$type"
        ;;
    
    # Open Interest
    oi-up)
        limit="${1:-10}"
        duration="${2:-1h}"
        curl -s "$BASE_URL/api/oi/top-ranking?auth=$API_KEY&limit=$limit&duration=$duration"
        ;;
    oi-down)
        limit="${1:-10}"
        duration="${2:-1h}"
        curl -s "$BASE_URL/api/oi/low-ranking?auth=$API_KEY&limit=$limit&duration=$duration"
        ;;
    oi-cap)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/oi-cap/ranking?auth=$API_KEY&limit=$limit"
        ;;
    
    # Price
    price)
        duration="${1:-1h}"
        curl -s "$BASE_URL/api/price/ranking?auth=$API_KEY&duration=$duration"
        ;;
    
    # Funding Rate
    funding-high)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/funding-rate/top?auth=$API_KEY&limit=$limit"
        ;;
    funding-low)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/funding-rate/low?auth=$API_KEY&limit=$limit"
        ;;
    funding)
        symbol="${1:-BTC}"
        curl -s "$BASE_URL/api/funding-rate/$symbol?auth=$API_KEY"
        ;;
    
    # Long-Short Ratio
    long-short)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/long-short/list?auth=$API_KEY&limit=$limit"
        ;;
    long-short-coin)
        symbol="${1:-BTC}"
        curl -s "$BASE_URL/api/long-short/$symbol?auth=$API_KEY"
        ;;
    
    # Heatmap
    heatmap)
        limit="${1:-10}"
        trade="${2:-future}"
        curl -s "$BASE_URL/api/heatmap/list?auth=$API_KEY&limit=$limit&trade=$trade"
        ;;
    heatmap-future)
        symbol="${1:-BTC}"
        curl -s "$BASE_URL/api/heatmap/future/$symbol?auth=$API_KEY"
        ;;
    heatmap-spot)
        symbol="${1:-BTC}"
        curl -s "$BASE_URL/api/heatmap/spot/$symbol?auth=$API_KEY"
        ;;
    
    # Single Coin
    coin)
        symbol="${1:-BTC}"
        include="${2:-all}"
        curl -s "$BASE_URL/api/coin/$symbol?auth=$API_KEY&include=$include"
        ;;
    
    # Upbit
    upbit-hot)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/upbit/hot?auth=$API_KEY&limit=$limit"
        ;;
    upbit-flow-in)
        limit="${1:-10}"
        duration="${2:-1h}"
        curl -s "$BASE_URL/api/upbit/netflow/top-ranking?auth=$API_KEY&limit=$limit&duration=$duration"
        ;;
    upbit-flow-out)
        limit="${1:-10}"
        duration="${2:-1h}"
        curl -s "$BASE_URL/api/upbit/netflow/low-ranking?auth=$API_KEY&limit=$limit&duration=$duration"
        ;;
    
    # Query Ranking
    query-rank)
        limit="${1:-10}"
        curl -s "$BASE_URL/api/query-rank/list?auth=$API_KEY&limit=$limit"
        ;;
    
    # Help
    help|--help|-h)
        cat << EOF
NOFX API Helper

Usage: ./nofx-api.sh <endpoint> [params]

Endpoints:
  AI Signals:
    ai500                     AI500 high potential coins
    ai500-stats               AI500 statistics
    ai500-coin <symbol>       Single coin AI analysis
    ai300 [limit]             AI300 quantitative signals
    ai300-stats               AI300 statistics

  Fund Flow:
    flow-in [limit] [duration] [type]    Inflow ranking
    flow-out [limit] [duration] [type]   Outflow ranking

  Open Interest:
    oi-up [limit] [duration]   OI increase ranking
    oi-down [limit] [duration] OI decrease ranking
    oi-cap [limit]             OI market cap ranking

  Price:
    price [duration]           Price gainers/losers

  Funding Rate:
    funding-high [limit]       High funding rate (crowded longs)
    funding-low [limit]        Low funding rate (crowded shorts)
    funding <symbol>           Single coin funding rate

  Long-Short:
    long-short [limit]         Long-short ratio anomalies
    long-short-coin <symbol>   Single coin long-short history

  Heatmap:
    heatmap [limit] [trade]    Order book heatmap list
    heatmap-future <symbol>    Future order book heatmap
    heatmap-spot <symbol>      Spot order book heatmap

  Single Coin:
    coin <symbol> [include]    Comprehensive coin data

  Upbit:
    upbit-hot [limit]          Upbit hot coins
    upbit-flow-in [limit] [duration]   Upbit inflow
    upbit-flow-out [limit] [duration]  Upbit outflow

  Other:
    query-rank [limit]         Query ranking

Parameters:
  limit: Number of results (default: 10)
  duration: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 24h, 2d, 3d, 5d, 7d
  type: institution, personal
  trade: future, spot
  include: all, price, netflow, oi, ai500

Environment:
  NOFX_API_KEY: API key (overrides config)
  NOFX_CONFIG: Config file path (default: ~/clawd/skills/nofx/config.json)
EOF
        ;;
    
    *)
        echo "Unknown endpoint: $endpoint" >&2
        echo "Run './nofx-api.sh help' for usage" >&2
        exit 1
        ;;
esac
