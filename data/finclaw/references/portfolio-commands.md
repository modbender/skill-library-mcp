# Portfolio Commands Quick Reference

## Natural Language → Script Mapping

| User Says | Action |
|-----------|--------|
| "add 10 AAPL at 150" | portfolio.py add --symbol AAPL --shares 10 --price 150 |
| "buy 0.5 BTC at 65000" | portfolio.py add --symbol BTC --shares 0.5 --price 65000 |
| "sell 5 AAPL at 175" | portfolio.py sell --symbol AAPL --shares 5 --price 175 |
| "remove AAPL from portfolio" | portfolio.py remove --symbol AAPL |
| "show my portfolio" | portfolio.py list |
| "portfolio summary" | portfolio.py summary |
| "alert me when BTC hits 70000" | alerts.py create --symbol BTC --condition above --target 70000 |
| "alert if AAPL drops below 140" | alerts.py create --symbol AAPL --condition below --target 140 |
| "show my alerts" | alerts.py list |
| "delete alert 3" | alerts.py delete --id 3 |

## Asset Type Detection

The system auto-detects asset type from the symbol:
- **US Stock**: `AAPL`, `MSFT`, `GOOGL` (default)
- **BIST**: `THYAO.IS`, `GARAN.IS` (`.IS` suffix)
- **Crypto**: `BTC`, `ETH`, `SOL` (known crypto symbols)
- **Forex**: `USD/TRY`, `EUR/USD` (slash-separated pair)

## Currency Mapping
- US stocks → USD
- BIST stocks → TRY
- Crypto → USDT
- Forex → target currency
