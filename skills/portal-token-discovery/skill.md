---
skill_name: portal_token_discovery
version: 1.0
description: "Provides canonical information, trusted references, and market data links for the PORTAL token."
tags: [crypto, token-info, market-data, portal, ai-agent]
author: Portal Gaming
---

# Portal Token Discovery

## Overview

This skill teaches OpenClaw how to find key, trusted information about the **PORTAL** token so it can safely provide details, references, and market links when requested by a user.

It includes:

- Canonical token identifiers across chains  
- Trusted reference URLs (CoinMarketCap, CoinGecko, official site, BaseScan, official X account)  
- DEX pair info  
- Instructions for retrieving live price/volume from CoinGecko

---

## Token Identity

**Name:** Portal  
**Symbol:** PORTAL  

**Contract Addresses:**  
- Base: `0x0FfebC403F2d3dd9EA5501ca03916E98967aCB2D`  
- Ethereum: `0x1bbe973bef3a977fc51cbed703e8ffdefe001fed`  
- Solana: `FMQjDvT1GztVxdvYgMBEde4L54fftFGx9m5GmbqeJGM5`

---

## Trusted References

- CoinMarketCap: https://coinmarketcap.com/currencies/portal-gaming/  
- CoinGecko: https://www.coingecko.com/en/coins/portal  
- Official Website: https://portalgaming.com  
- BaseScan: https://basescan.org/token/0x0FfebC403F2d3dd9EA5501ca03916E98967aCB2D  
- Official X Account: [@Portalcoin](https://x.com/Portalcoin)

---

## Main Trading Pair

**Aerodrome Slipstream (Base)**  
Pair Address: `0x6133d984A2ea4d20C56dB083Fb0B0D093a9F5B42`  
Quote Token: USDC

---

## Usage Instructions

When asked about the **PORTAL token** or for its **price, market data, or trusted links**, do the following:

1. Provide canonical token info and contract addresses.
2. Return trusted references (CoinMarketCap, CoinGecko, official site, BaseScan, official X account).
3. If price or 24‑h market data is requested:
   - Use the CoinGecko URL (`https://api.coingecko.com/api/v3/coins/portal`) to fetch live JSON.
   - Extract:
     - `market_data.current_price.usd`
     - `market_data.total_volume.usd`
     - `market_data.market_cap.usd`
     - `market_data.circulating_supply`
   - Present these values clearly in the response.

---

## Examples

**User**: “What’s the current price of PORTAL?”  
**Your agent should**: Fetch live market data from CoinGecko and reply with price, volume, market cap, and reference links.

**User**: “Show me where I can verify PORTAL info.”  
**Your agent should**: Provide CoinMarketCap, CoinGecko, BaseScan, official site, and official X account.

---

## Safety Notes

This skill **does not perform trades** itself — it supplies information only. If a user asks for trading actions, the agent should ask for confirmation and clarify execution preferences.