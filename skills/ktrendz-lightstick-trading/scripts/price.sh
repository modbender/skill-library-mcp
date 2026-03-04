#!/bin/bash
# Get K-Trendz token price and signals

CONFIG_FILE="$HOME/.config/ktrendz/config.json"
BASE_URL="https://k-trendz.com/api/bot"

# Get API key from config or environment
if [ -n "$KTRENDZ_API_KEY" ]; then
    API_KEY="$KTRENDZ_API_KEY"
elif [ -f "$CONFIG_FILE" ]; then
    API_KEY=$(cat "$CONFIG_FILE" | grep -o '"api_key": *"[^"]*"' | sed 's/"api_key": *"//' | sed 's/"$//')
else
    echo "✗ Not configured. Run ./scripts/setup.sh first"
    exit 1
fi

# Get artist name from argument
ARTIST="${1:-}"
if [ -z "$ARTIST" ]; then
    echo "Usage: ./scripts/price.sh <artist_name>"
    echo ""
    echo "Available tokens:"
    echo "  RIIZE, IVE, BTS, Cortis, 'K-Trendz Supporters', 'All Day Project'"
    exit 1
fi

# Call API
RESPONSE=$(curl -s -X POST "$BASE_URL/token-price" \
    -H "Content-Type: application/json" \
    -H "x-bot-api-key: $API_KEY" \
    -d "{\"artist_name\": \"$ARTIST\"}")

# Check for success
if ! echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✗ API Error"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# Parse and display
echo ""
echo "🎤 $ARTIST Token Price"
echo "========================"
echo ""

# Extract values using Python for reliable JSON parsing
python3 << EOF
import json
import sys

data = json.loads('''$RESPONSE''')['data']

print(f"💰 Current Price: \${data['current_price_usdc']:.2f} USDC")
print(f"📈 Buy Cost:      \${data['buy_cost_usdc']:.2f} USDC")
print(f"📉 Sell Refund:   \${data['sell_refund_usdc']:.2f} USDC")
print(f"")

change = data.get('price_change_24h', '0')
if change and float(change) > 0:
    print(f"📊 24h Change:    +{change}% ✅")
elif change and float(change) < 0:
    print(f"📊 24h Change:    {change}% ⚠️")
else:
    print(f"📊 24h Change:    {change}%")

print(f"")
print(f"📈 Total Supply:    {data['total_supply']} tokens")
print(f"🔥 Trending Score:  {data['trending_score']}")
print(f"👥 Followers:       {data['follower_count']}")
print(f"👀 Views:           {data['view_count']}")

signals = data.get('external_signals', {})
if signals:
    print(f"")
    print(f"📰 News Signals:")
    print(f"   Articles (24h): {signals.get('article_count_24h', 0)}")
    print(f"   Has Recent News: {'✅ Yes' if signals.get('has_recent_news') else '❌ No'}")
    
    headlines = signals.get('headlines', [])
    if headlines:
        print(f"   Headlines:")
        for h in headlines[:3]:
            print(f"   • {h['title'][:60]}...")
EOF

echo ""
