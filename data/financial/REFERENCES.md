# Financial Skill References (machine-friendly)

- Intent: get_stock_price_intent
- Triggers: price, stock price, stock, quote, ticker
- Parameters: ticker (string, e.g., AAPL)
- Action: shell_command
  - Command: python3 -u /home/openclaw/.openclaw/workspace/skills/financial/scripts/yfinance_ai.py --ticker {ticker} --action price
- Activation: auto_route = true, fallback = true
- Notes: All functions are wired through the manifest and auto-route on supported queries.
