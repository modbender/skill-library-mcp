---
name: "Skill: Get Kalshi Live Games"
description: Fetch currently live Kalshi sports markets using the browser.
---

# Skill: Get Kalshi Live Games

## Purpose
Fetch currently live Kalshi sports markets using the browser.

## Tool Policy
- MUST use the browser tool
- MUST NOT use web_search or web_fetch for live market data

## Steps
1. Start browser if not running.
2. Open https://kalshi.com
3. Navigate to live sports markets.
4. Extract up to 5 currently running games.
5. Return only:
   - Game name
   - Probability

