---
name: discord-shopping
description: Dedicated shopping deal finder optimized for Discord: wide search across new/used/refurbished vendors (Amazon, eBay, Best Buy, Walmart, Swappa, Back Market), top 3 results with prices/links, coupon code checks. Trigger exclusively on Discord keywords/phrases like &quot;shop&quot;, &quot;find me a deal&quot;, &quot;best price for [product]&quot;, &quot;cheap [product]&quot;, &quot;where to buy [product]&quot;. Use in Discord group/direct chats to quickly inform buying decisions.
---

# Discord Shopping Deals

## Overview
Rapid deal scouting across major vendors. Deliver top 3 current best deals (price, condition, link) + coupons. Discord-optimized output: bullets, suppressed link embeds, emojis for scannability.

## Triggers &amp; Context
- Keywords: shop, deal, buy, price check, cheapest, best [product]
- Discord-only: Use `message channel=discord` for replies. Respect group chat rules (value-add only).
- Parse product from context/query.

## Workflow
1. **Extract product**: Core item (e.g., &quot;AirPods Pro 2&quot;, &quot;RTX 4070&quot;). Refine ambiguous (ask if needed).

2. **Deal searches** (parallel web_search, count=10 each):
   | Query Template | Purpose |
   |----------------|---------|
   | &quot;[product] best deal&quot; | General deals |
   | &quot;cheapest [product] amazon ebay bestbuy walmart&quot; | Major retailers |
   | &quot;[product] used refurbished swappa backmarket&quot; | Used/refurb |
   | &quot;[product] slickdeals&quot; | Deal aggregators |
   | &quot;[product] coupon codes 2026&quot; | Promos |

3. **Aggregate &amp; Rank**:
   - Top 3: Lowest price first, then reputable/vendor, new&gt;refurb&gt;used.
   - Extract: Price, condition, vendor, direct link, notes (shipping, ratings).
   - Use web_fetch on top links for confirmation if snippets unclear.

4. **Discord Output**:
   ```
   🎯 Top 3 Deals for [product]:

   1️⃣ [Vendor]: $[price] [new/used/refurb] 
      &lt;[link]&gt; [notes]

   2️⃣ ...

   💸 Coupons: [code1@site] saves $[amount]
   ```
   - Suppress embeds: Wrap links in &lt;&gt;
   - React 👍 if good deals.

## Edge Cases
- No deals: &quot;No strong matches; alternatives: [suggest]&quot;
- High-price items: Flag &quot;Consider used/refurb&quot;
- Seasonal: Note dates/prices change.

## Tools Priority
- web_search (core)
- web_fetch (details)
- Avoid browser unless login/dynamic essential.

No bundled resources required.
