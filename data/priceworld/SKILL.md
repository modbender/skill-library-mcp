---
name: priceworld
description: Pricing intelligence across web hosting, email marketing, domain registrars, savings rates, and AI tools. Query real prices, compare providers by true cost (including renewal markup), find hidden fees, and check which banks silently cut APY. Use when users ask about software pricing, hosting costs, domain renewals, savings account rates, AI subscription comparisons, or budget recommendations.
---

# PriceWorld — Pricing Intelligence

Real-time verified pricing data across 5 categories. We track what you actually pay — not what the marketing page says.

**Website:** https://priceworld.com
**Data:** Independently verified monthly via direct checkout testing.

## Supported Categories

- ✅ **Web Hosting** (8 providers) — Hostinger, SiteGround, Bluehost, DreamHost, HostGator, WP Engine, A2 Hosting, InMotion Hosting
- ✅ **Email Marketing** (8 tools) — Mailchimp, Kit, Beehiiv, Buttondown, Brevo, ActiveCampaign, MailerLite, Klaviyo
- ✅ **Domain Registrars** (5 registrars) — Namecheap, GoDaddy, Porkbun, Cloudflare, Squarespace (Google Domains)
- ✅ **Savings Rates** (15 US banks) — SoFi, Bread Savings, Bask Bank, CIT Bank, Popular Direct, Barclays, Wealthfront, Amex HYSA, Discover, TAB Bank, Capital One 360, Marcus, Betterment, Ally, UFB Direct
- ✅ **AI Costs** (8 tools) — ChatGPT Plus, Claude Pro, Gemini Advanced, Perplexity Pro, GitHub Copilot, Midjourney, Cursor, v0

## Commands

### Lookup Pricing

Query current pricing for a specific provider:

```
priceworld:lookup <provider>
```

Examples:
- `priceworld:lookup hostinger` — hosting plans, promo vs renewal prices
- `priceworld:lookup beehiiv` — email marketing tiers by subscriber count
- `priceworld:lookup godaddy` — domain registration, renewal, hidden costs
- `priceworld:lookup sofi` — current APY, Rate Loyalty Score, decay events
- `priceworld:lookup chatgpt` — subscription price, usage limits

Returns: Plan tiers, pricing, renewal costs, hidden fees, score breakdown, last verified date.

### Compare Providers

Side-by-side comparison:

```
priceworld:compare <provider1> <provider2>
```

Examples:
- `priceworld:compare hostinger siteground`
- `priceworld:compare mailchimp kit`
- `priceworld:compare cloudflare godaddy`

Returns: Feature and pricing comparison table with true cost analysis.

### Find Cheapest

Find the best value option:

```
priceworld:cheapest <category> [--options]
```

Examples:
- `priceworld:cheapest hosting` — ranked by 3-year TCO
- `priceworld:cheapest email-marketing --subscribers=5000` — ranked by monthly cost at tier
- `priceworld:cheapest domains` — ranked by total .com cost over 3 years
- `priceworld:cheapest savings` — ranked by Rate Loyalty Score (not just today's APY)
- `priceworld:cheapest ai-costs` — ranked by monthly price

Returns: Ranked list by value for the category.

### Renewal Shock Check

Check how much more a provider charges after the promo period:

```
priceworld:renewal-check <provider>
```

Example: `priceworld:renewal-check siteground`

Returns: Promo price, renewal price, markup percentage, 3-year TCO.

### Regional Pricing

Check if a provider charges different prices by country:

```
priceworld:regional <provider>
```

Example: `priceworld:regional hostinger`

Returns: Prices across US, EU, UK, India, Brazil with USD comparison.

## Scoring System

Every provider gets a data-driven composite score (1.0–5.0):
- **4.5–5.0** Excellent Value
- **3.5–4.4** Good Value
- **2.5–3.4** Average
- **1.5–2.4** Below Average
- **1.0–1.4** Poor Value

Scores are derived from measurable data via published rubrics. No opinions, no pay-to-rank. Full methodology at https://priceworld.com/methodology/

## Key Metrics

- **Renewal Shock %** — How much more you pay after the promo ends
- **3-Year TCO** — Total cost of ownership including renewal pricing
- **Rate Loyalty Score** — How well a bank tracks Fed rate changes (savings)
- **Rate Gap** — Difference between bank APY and the Federal Funds Rate
- **Shrinkflation Events** — When AI tools reduce limits at the same price

## Data Freshness

- All pricing includes "last verified" dates
- Hosting/email/domain prices re-verified monthly
- Savings rates tracked weekly against EFFR
- AI tool limits checked weekly
- Sources: official vendor pricing pages + direct checkout testing

## Pricing Notes

- **Currency:** USD (regional pricing available for hosting)
- **Region:** US pricing default, 5 regions for hosting
- **Annual pricing:** Shown as monthly equivalent
- **Excludes:** Tax/VAT, promotional one-time discounts
- **Includes:** Mandatory add-ons, renewal pricing, WHOIS privacy costs

## Limitations

- Does not include enterprise/custom pricing tiers
- Savings data is US banks only (expansion planned)
- AI tool limits change frequently — always verify on vendor site
- Not affiliated with any listed provider

## Privacy & Security

- No personal information required
- **Do not paste API keys, invoices, or account screenshots**
- Queries processed by assistant runtime; no user queries stored

## Tool Aliases

- Kit = ConvertKit (rebranded 2024)
- A2 Hosting = hosting.com (rebranding in progress)
- Google Domains = Squarespace Domains (acquired 2023)

---

*PriceWorld — Track real prices, not marketing prices.*
