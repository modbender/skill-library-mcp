# 🛍️ Amazon & Etsy Bestseller Product Research Engine

**Slug:** `amazon-etsy-product-research`  
**Category:** E-Commerce / Product Research  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Input any niche. Get a **complete product research report** — bestsellers, pricing gaps, review weaknesses, search trends, profit margins & untapped opportunities — in minutes. Find your next winning product before your competitors do.

---

## 💥 Why This Skill Will Explode on ClawHub

Every dropshipper, Amazon FBA seller, Etsy creator, and e-commerce founder spends **20-40 hours/week** manually researching products. That's the most painful, repetitive, high-stakes task in their business.

This skill cuts that to **5 minutes**. With better data than anything they'd find manually.

**What gets researched automatically:**
- 🏆 Top 50 bestselling products in any niche (Amazon + Etsy combined)
- 💰 Real pricing data — average, min, max, optimal price point
- ⭐ Review gap analysis — what customers LOVE and HATE about existing products
- 📈 Search trend momentum — rising vs declining demand
- 🏭 Supplier intelligence — estimated production cost & profit margin
- 🔍 Keyword goldmine — top search terms driving sales
- 🚀 Untapped opportunity score — low competition, high demand niches
- 📦 Listing optimization tips — titles, tags, descriptions that rank

---

## 🛠️ Apify Actors Used

| Actor | ID | Purpose |
|---|---|---|
| Amazon Product Scraper | `junglee/amazon-product-scraper` | Bestsellers, pricing, reviews, BSR rank |
| Amazon Reviews Scraper | `junglee/amazon-reviews-scraper` | Deep review sentiment analysis |
| Etsy Scraper | `emastra/etsy-scraper` | Top Etsy listings, sales estimates, tags |
| Google Trends Scraper | `emastra/google-trends-scraper` | Demand momentum & seasonal patterns |
| Google Search Scraper | `apify/google-search-scraper` | Market size, competitor brands, news |

---

## ⚙️ Full Workflow

```
INPUT: Niche keyword + marketplace (Amazon / Etsy / Both) + budget range
        ↓
STEP 1 — Scrape Top 50 Bestsellers in the Niche
  └─ Amazon BSR rank, Etsy sales count, pricing, review volume
        ↓
STEP 2 — Deep Review Mining (1,000+ reviews analyzed)
  └─ What do buyers LOVE? What do they HATE?
  └─ Most mentioned complaints = your product improvement opportunity
        ↓
STEP 3 — Pricing Intelligence
  └─ Average price, price clustering, optimal entry price point
  └─ Identify underpriced gaps and premium opportunities
        ↓
STEP 4 — Google Trends Analysis
  └─ Is demand rising or declining?
  └─ Seasonal peaks, emerging micro-trends
        ↓
STEP 5 — Keyword & SEO Analysis
  └─ Top search terms, long-tail opportunities, low-competition keywords
        ↓
STEP 6 — Profit Margin Estimation
  └─ Estimated COGS based on product type & complexity
  └─ Realistic margin after platform fees, shipping, ads
        ↓
STEP 7 — Claude AI Generates Full Opportunity Report
  └─ Top 10 product opportunities ranked by score
  └─ Review gap = your product angle
  └─ Exact listing strategy to outrank existing sellers
        ↓
OUTPUT: Ranked product list + full opportunity report (JSON / Markdown / CSV)
```

---

## 📥 Inputs

```json
{
  "niche": "minimalist home decor",
  "marketplace": "both",
  "price_range": {
    "min": 15,
    "max": 80
  },
  "target_margin": 40,
  "exclude_brands": ["IKEA", "Amazon Basics"],
  "research_depth": {
    "max_products": 50,
    "reviews_per_product": 100,
    "lookback_days": 90
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "niche": "minimalist home decor",
  "market_overview": {
    "total_products_analyzed": 50,
    "average_price": "$34.50",
    "average_reviews": 847,
    "market_trend": "📈 Rising +23% YoY",
    "competition_level": "🟡 Medium",
    "best_entry_price_point": "$24.99 - $39.99"
  },
  "top_opportunities": [
    {
      "rank": 1,
      "opportunity_score": 94,
      "product_idea": "Minimalist Wooden Desk Organizer with Hidden Wireless Charger",
      "why_it_wins": "Top 3 complaints in 800+ reviews of existing organizers: 'no cable management', 'takes up too much space', 'no charging'. Zero products currently solve all 3.",
      "estimated_price": "$39.99",
      "estimated_cogs": "$11.00",
      "estimated_margin": "62%",
      "monthly_search_volume": "28,400",
      "top_competitors": 4,
      "review_gap": {
        "buyers_love": ["clean design", "sturdy wood", "good size"],
        "buyers_hate": ["no wireless charging", "cables everywhere", "too bulky"],
        "your_angle": "Same minimalist aesthetic + built-in wireless charging pad + cable routing"
      },
      "listing_strategy": {
        "title": "Minimalist Wooden Desk Organizer with Wireless Charger — Cable-Free Workspace Storage for Home Office",
        "top_keywords": ["desk organizer", "wireless charging desk organizer", "minimalist office accessories", "wooden desk storage"],
        "price_to_win": "$37.99 (undercut leader by $4 while adding features)"
      }
    },
    {
      "rank": 2,
      "opportunity_score": 87,
      "product_idea": "Expandable Minimalist Spice Rack — Bamboo, No Assembly",
      "why_it_wins": "Best seller has 2,400 reviews. #1 complaint (340 reviews): 'took 45 min to assemble, instructions terrible'. Opportunity: same product, tool-free snap assembly.",
      "estimated_price": "$28.99",
      "estimated_cogs": "$7.50",
      "estimated_margin": "58%",
      "monthly_search_volume": "41,200",
      "top_competitors": 6,
      "review_gap": {
        "buyers_love": ["looks great", "holds a lot", "bamboo quality"],
        "buyers_hate": ["horrible assembly", "screws stripped", "instructions useless"],
        "your_angle": "Snap-fit bamboo construction — zero tools, 60 seconds to set up"
      }
    }
  ],
  "keyword_goldmine": [
    { "keyword": "minimalist desk organizer", "volume": 28400, "competition": "medium", "trend": "rising" },
    { "keyword": "aesthetic home office accessories", "volume": 18700, "competition": "low", "trend": "rising +41%" },
    { "keyword": "bamboo desk storage", "volume": 12300, "competition": "low", "trend": "stable" }
  ],
  "seasonal_insights": {
    "peak_months": ["October", "November", "January"],
    "advice": "Launch by September to catch Q4 gifting season — this niche sees 3x volume in November"
  },
  "sourcing_intelligence": {
    "recommended_platforms": ["Alibaba", "1688.com", "AliExpress"],
    "estimated_moq": "50-200 units for custom branding",
    "avg_sample_cost": "$15-30",
    "production_lead_time": "15-25 days"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class Amazon FBA and Etsy product research expert.

SCRAPED MARKETPLACE DATA:
- Bestsellers: {{bestsellers_data}}
- Review analysis: {{reviews_data}}
- Pricing data: {{pricing_data}}
- Google Trends: {{trends_data}}
- Keyword data: {{keyword_data}}

RESEARCH PARAMETERS:
- Niche: {{niche}}
- Target price range: {{price_range}}
- Target margin: {{target_margin}}%

GENERATE:
1. Market overview — average price, competition level, trend direction
2. Top 10 product opportunities ranked by opportunity score (0-100)
   For each opportunity include:
   - Why it wins (review gap + market gap)
   - Estimated price, COGS, and margin
   - Exact buyer complaints that become your product USP
   - Listing strategy: optimized title + top 5 keywords + recommended price
3. Keyword goldmine — top 10 search terms with volume, competition & trend
4. Seasonal insights — when to launch and peak months
5. Sourcing intelligence — where to source, MOQ, lead time estimates

SCORING CRITERIA (weight each):
- Review gap score (30%) — how many complaints can you fix?
- Demand trend (25%) — is search volume rising?
- Competition density (25%) — how many strong sellers dominate?
- Margin potential (20%) — can you hit the target margin?

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Research Runs | Apify CU | Cost | Niches Researched |
|---|---|---|---|
| 1 niche | ~45 CU | ~$0.45 | 1 full report |
| 5 niches | ~220 CU | ~$2.20 | 5 full reports |
| 20 niches | ~880 CU | ~$8.80 | 20 full reports |
| 100 niches | ~4,300 CU | ~$43 | 100 full reports |

> 💡 **$5 free Apify credits on signup** = your first 10 niche reports completely free.  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

---

## 🔗 Who Makes Money With This Skill

| User | How They Use It | Revenue Potential |
|---|---|---|
| **Amazon FBA Seller** | Find next winning product before competitors | $5K-$50K/month per product |
| **Etsy Creator** | Identify trending niches with low competition | $2K-$15K/month passive |
| **Dropshipper** | Validate products before buying inventory | Avoid $000s in bad stock |
| **Product Research Agency** | Sell reports to clients at $200-$500 each | $5K-$20K/month service |
| **E-com Consultant** | Bundle into strategy package | $2K-$10K per engagement |
| **Private Label Brand** | Source & brand winning products | Build 6-7 figure brand |

---

## 📊 Why This Beats Every Existing Research Tool

| Feature | Helium10 ($99/mo) | Jungle Scout ($69/mo) | **This Skill** |
|---|---|---|---|
| Amazon data | ✅ | ✅ | ✅ |
| Etsy data | ❌ | ❌ | ✅ |
| Review gap analysis | ❌ | ❌ | ✅ |
| AI-generated product angle | ❌ | ❌ | ✅ |
| Listing strategy included | ❌ | ❌ | ✅ |
| Monthly subscription | $99/mo | $69/mo | ~$0.45/run |
| Works for any niche instantly | ✅ | ✅ | ✅ |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Sign up free → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Go to: **Settings → Integrations → API Token**

**Step 2 — Define your niche & parameters**  
Keyword, marketplace, price range, target margin. The more specific, the better.

**Step 3 — Run & get your report**  
Full opportunity report with ranked products in under 5 minutes.

---

## ⚡ Pro Tips to Find Winning Products Faster

- **Focus on products with 500+ reviews AND a 3.8-4.2★ rating** — enough demand, enough complaints to improve on
- **The best opportunity is always in the reviews** — sort by 1-3 stars and read 50 complaints
- **Target the #2 or #3 bestseller, not #1** — easier to dethrone, same demand
- **Launch in October for Q4** — home decor, gifts & organizers 3x in November
- **Start with Etsy to validate** — lower ad costs, faster feedback loop than Amazon

---

## 🏷️ Tags

`amazon` `etsy` `product-research` `ecommerce` `dropshipping` `fba` `private-label` `apify` `bestseller` `market-research` `product-validation` `keyword-research`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + Claude AI*
