#!/bin/bash
# fetch_tase_data.sh - Fetch TASE stock data via APIs
# Usage: ./fetch_tase_data.sh <ticker_or_etf> [data_type]
# Examples:
#   ./fetch_tase_data.sh ALRT
#   ./fetch_tase_data.sh ALRT price
#   ./fetch_tase_data.sh 510893

TICKER="${1:?Error: Ticker or ETF number required}"
DATA_TYPE="${2:-price}"

# Convert to ticker (simplified for compatibility)
# For Hebrew names, use Python script instead: python3 scripts/fetch_tase_data.py "בנק לאומי"
case "$TICKER" in
    510893) TICKER="TA25" ;;
    770001) TICKER="TA35" ;;
    *)      ;;
esac

# Normalize and add .TA suffix
TICKER=$(echo "$TICKER" | tr '[:lower:]' '[:upper:]')
if [[ ! "$TICKER" =~ \.TA$ ]] && [[ ! "$TICKER" =~ \.IL$ ]]; then
    TICKER="${TICKER}.TA"
fi

# Fetch from API (try in order)
fetch_data() {
    local ticker=$1
    
    # Try Finnhub if API key is set
    if [[ -n "$FINNHUB_API_KEY" ]]; then
        local result=$(curl -s "https://finnhub.io/api/v1/quote?symbol=${ticker}&token=${FINNHUB_API_KEY}")
        if echo "$result" | jq -e .c &>/dev/null; then
            echo "$result" | jq '{
                source: "Finnhub",
                ticker: "'$ticker'",
                price: .c,
                high: .h,
                low: .l,
                open: .o,
                volume: .v,
                currency: "ILS"
            }'
            return 0
        fi
    fi
    
    # Try Alpha Vantage (demo key)
    local result=$(curl -s "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${ticker}&apikey=demo")
    if echo "$result" | jq -e '.Global Quote."05. price"' &>/dev/null; then
        echo "$result" | jq '{
            source: "Alpha Vantage",
            ticker: "'$ticker'",
            price: (.["Global Quote"]["05. price"] | tonumber? // 0),
            change: (.["Global Quote"]["09. change"] | tonumber? // 0),
            timestamp: now | todate
        }'
        return 0
    fi
    
    # Fallback to mock
    echo "{
        \"source\": \"Template - Configure API\",
        \"ticker\": \"$ticker\",
        \"message\": \"Get free API key from finnhub.io and set FINNHUB_API_KEY=your_key\"
    }" | jq .
}

# Main logic
case "$DATA_TYPE" in
    price)
        fetch_data "$TICKER"
        ;;
    *)
        echo '{"error": "Use: fetch_tase_data.sh <ticker> price. For other types, use Python version."}' | jq .
        exit 1
        ;;
esac
