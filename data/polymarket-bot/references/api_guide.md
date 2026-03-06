# API Guide for Polymarket Bot Skill

## Overview
This reference covers the Polymarket APIs used in the bot, including Gamma, CLOB, and Data APIs. These are essential for fetching market data, authentication, and trading.

## Gamma API (Public Read-Only)
- Base URL: https://gamma-api.polymarket.com
- Endpoints: Use `/markets?active=true&closed=false&limit=20` to list active markets.
- No authentication required for public data.

## CLOB API (Authenticated Trading)
- Base URL: https://clob.polymarket.com
- Requires EIP-712 signature for API keys.
- Use for placing orders; see scripts/auth_setup.py for implementation.

## Data API (User Analytics)
- Base URL: https://data-api.polymarket.com
- Endpoints: Fetch leaderboards and trades, e.g., /leaderboards for copy trading.

## Best Practices
- Handle private keys securely via environment variables.
- Add error handling for API failures and rate limits.