# Financial Skill (YFinance-AI)

Scope: 56+ financial data tools via Yahoo Finance. Stock prices, fundamentals, earnings, dividends, options, crypto, forex, commodities, news, and more.

Author: lucas0 | Version: 3.0.4 | License: MIT

How to use (human-friendly):
- Get a stock price: say "price of AAPL" or "stock price for MSFT". The system will auto-route to this skill and return the current price and key metrics.
- Other data: ask for a specific tool, e.g., "earnings for TWTR", "dividends for KO", or "history for GOOGL". The skill supports 56+ functions (see references).

Auto-routing (AI-friendly):
- This skill is discovered and wired via skill.json. Requests matching price/stock/quote/ticker trigger this skill automatically. If unavailable, a graceful fallback is provided.

First-run tips:
- Ensure the OpenClaw environment has the finance venv and the dependencies from requirements.txt installed.
- Fresh installs should auto-route a price query without prompting.

Example:
- User: price of AAPL
- System: current price and key metrics for AAPL are returned.

Internal notes: This document focuses on human readability and AI comprehension; the actual routing is defined in skill.json.
