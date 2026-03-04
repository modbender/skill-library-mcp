# Skill: charts

## Purpose
Generate professional technical analysis charts with candlesticks, Fibonacci retracement, moving averages (SMA 20/50), RSI, and pattern detection. Uses the local `crypto_charts.py` module.

## When to Use
- Boss Man asks "show me the BTC chart" or "run TA on silver"
- You need visual charts for market analysis or reporting
- Morning protocol chart generation
- Any request for technical analysis with visuals

## Generate All Charts (Full Suite)
Generates charts for all 6 tracked assets: BTC, ETH, XRP, SUI, Gold, Silver.
**Warning:** Takes 2-3 minutes due to API rate limits between requests.
```bash
cd ~/clawd && python3 -c "
import json
from crypto_charts import generate_all_charts, cleanup_old_charts
cleanup_old_charts()
report = generate_all_charts(output_dir=os.path.expanduser('~/clawd/charts'))
print(json.dumps(report, indent=2, default=str))
" 2>&1
```

Charts saved to: `~/clawd/charts/chart_btc.png`, `chart_eth.png`, etc.

## Generate Single Chart
For a quick single-asset chart without waiting for the full suite:
```bash
cd ~/clawd && python3 -c "
import os, json
from crypto_charts import (
    fetch_yfinance, fetch_ohlc, fetch_market_data,
    calc_moving_averages, calc_rsi, calc_fibonacci,
    detect_patterns, generate_chart, COINS
)

coin_id = 'COIN_ID'  # bitcoin, ethereum, ripple, sui, gold, silver
info = COINS[coin_id]

# Fetch data (Yahoo Finance first, CoinGecko fallback)
df = fetch_yfinance(coin_id)
if df is None or len(df) < 10:
    df = fetch_ohlc(coin_id)
if df is None or len(df) < 10:
    df = fetch_market_data(coin_id)

if df is not None and len(df) >= 5:
    df = calc_moving_averages(df)
    df = calc_rsi(df)
    fib = calc_fibonacci(df)
    patterns = detect_patterns(df)

    chart_path = os.path.expanduser(f'~/clawd/charts/chart_{info[\"symbol\"].lower()}.png')
    generate_chart(coin_id, df, fib, chart_path)

    print(f'Chart: {chart_path}')
    print(f'Price: \${df[\"close\"].iloc[-1]:,.2f}')
    print(f'RSI: {df[\"rsi\"].iloc[-1]:.1f}')
    print('Patterns:')
    for p in patterns:
        print(f'  - {p}')
else:
    print('Not enough data to generate chart')
"
```

## Tracked Assets
| coin_id | Symbol | Chart Color | Data Source |
|---------|--------|------------|-------------|
| bitcoin | BTC | #F7931A | Yahoo Finance → CoinGecko |
| ethereum | ETH | #627EEA | Yahoo Finance → CoinGecko |
| ripple | XRP | #00AAE4 | Yahoo Finance → CoinGecko |
| sui | SUI | #6FBCF0 | Yahoo Finance → CoinGecko |
| gold | XAU | #FFD700 | Yahoo Finance |
| silver | XAG | #C0C0C0 | Yahoo Finance |

## What the Charts Include
- **Candlestick bars** (green up / red down) — 90 days of daily data
- **20 SMA** (blue) and **50 SMA** (gold) — trend and support/resistance
- **Fibonacci retracement levels** (0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%)
- **RSI subplot** (purple) — with overbought (70) and oversold (30) lines
- **Current price marker** — dot + horizontal line in the asset's accent color

## Pattern Detection (Automatic)
The module auto-detects and reports:
- SMA crossovers (Golden Cross / Death Cross)
- Head & Shoulders / Inverse H&S
- Fibonacci zone positioning
- Trend strength (7-day momentum)
- RSI condition (overbought/oversold/neutral)
- Price position within 90-day range

## Sending Charts via Telegram
After generating, send the chart image using Clawdbot's native `message` command:
```
message (Telegram, target="7887978276") [attach ~/clawd/charts/chart_btc.png]
```

## Rules
- Charts use 90 days of history — enough for meaningful TA
- Yahoo Finance is tried first (free, reliable), CoinGecko is fallback
- Rate limit: 8-second delays between coins, 20-second batch cooldowns
- Always run `cleanup_old_charts()` first to avoid disk buildup
- Chart images are ~150 DPI, dark theme (#0f172a background)
