# 🏠 Real Estate Lead Machine — Scrape & Contact Property Sellers Before Anyone Else

**Slug:** `real-estate-lead-machine`  
**Category:** Real Estate / Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Input a target location. Get a **ranked list of motivated property sellers** — scraped from Zillow, Rightmove, and major portals — with owner contact details, market analysis, opportunity scores, and AI-generated outreach messages. Be first. Win the deal.

---

## 💥 Why Every Real Estate Pro Will Want This Skill

Real estate is a race. The agent or investor who contacts a motivated seller **first wins the deal**. Most pros spend hours manually browsing listings, copy-pasting into spreadsheets, then writing the same email 50 times.

This skill makes you the fastest player in every market you target.

**What gets automated:**
- 🏡 Scrape **fresh listings daily** from major property portals
- ⏰ Detect **motivated sellers** — price reductions, long days-on-market, distressed signals
- 👤 Find **owner & agent contact details** — name, email, phone
- 📊 Enrich each property with **market comps & estimated value**
- 🎯 AI **opportunity score (0–100)** per property
- 📬 Generate **personalized outreach** — email + SMS + follow-up sequence
- 🗺️ Deliver leads ranked by motivation level — Hot / Warm / New

---

## 🛠️ Apify Actors Used

| Actor | ID | Purpose |
|---|---|---|
| Zillow Scraper | `maxcopell/zillow-scraper` | US listings — price, days on market, details |
| Rightmove Scraper | `dhrumil/rightmove-scraper` | UK property listings & seller data |
| LeBonCoin Scraper | `misceres/leboncoin-scraper` | French FSBO listings |
| Google Maps Scraper | `compass/crawler-google-places` | Estate agents, landlords, property managers |
| Google Search Scraper | `apify/google-search-scraper` | Owner details, public records, contact info |

---

## ⚙️ Full Workflow

```
INPUT: Target location + property type + price range + seller signals
        ↓
STEP 1 — Scrape Fresh Listings (Daily Run)
  └─ New listings posted in last 24–72 hours
  └─ Price reductions → motivated seller signal #1
  └─ Long days-on-market → motivated seller signal #2
        ↓
STEP 2 — Detect Motivated Seller Signals
  └─ 🔴 HOT: Price dropped 2+ times + 60+ days on market
  └─ 🟡 WARM: Price dropped once + 30+ days on market
  └─ 🟢 NEW: Fresh listing under 48 hours old
        ↓
STEP 3 — Property Data Enrichment
  └─ Sqft, bedrooms, year built, last sale price
  └─ Estimated current market value via comps
  └─ Neighborhood stats — avg price/sqft, avg days-on-market
        ↓
STEP 4 — Owner & Agent Contact Extraction
  └─ Agent name, phone, email (from listing)
  └─ FSBO — direct seller contact where available
  └─ Cross-reference Google for additional contact details
        ↓
STEP 5 — AI Opportunity Scoring (0–100)
  └─ Motivated signals + price vs market + location desirability
        ↓
STEP 6 — Claude AI Generates Personalized Outreach
  └─ Email referencing exact property + seller situation
  └─ SMS-length message for direct contact
  └─ Day 3 + Day 7 follow-up sequence
        ↓
OUTPUT: Ranked lead list + property data + outreach messages (CSV / JSON)
```

---

## 📥 Inputs

```json
{
  "target_zones": ["London Zone 2-4", "Manchester City Centre"],
  "property_type": ["flat", "terraced house"],
  "price_range": { "min": 150000, "max": 450000 },
  "motivated_signals": {
    "min_days_on_market": 30,
    "price_reduction": true,
    "fsbo_priority": true
  },
  "buyer_profile": {
    "type": "investor",
    "strategy": "buy-to-let",
    "completion_time": "4-6 weeks",
    "is_cash_buyer": true
  },
  "max_leads": 50,
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "search_summary": {
    "location": "London Zone 2-4",
    "properties_scraped": 284,
    "hot_leads": 8,
    "warm_leads": 23,
    "new_listings": 41,
    "run_date": "2025-03-01"
  },
  "top_leads": [
    {
      "rank": 1,
      "opportunity_score": 94,
      "signal": "🔴 HOT — Price reduced 3x, 87 days on market",
      "property": {
        "address": "14 Elmwood Gardens, London E3 4NR",
        "type": "2-bed flat",
        "listing_price": "£285,000",
        "original_price": "£325,000",
        "price_reduction": "-£40,000 (-12.3%)",
        "days_on_market": 87,
        "sqft": 720,
        "portal_url": "rightmove.co.uk/property/123456"
      },
      "market_analysis": {
        "estimated_market_value": "£295,000",
        "vs_listing": "Priced 3.4% BELOW market",
        "area_avg_days_on_market": 32,
        "verdict": "87 days vs 32-day area average = strong motivation signal"
      },
      "seller_contact": {
        "agent": "Morrison & Fox Estate Agents",
        "agent_phone": "+44 20 7946 0321",
        "agent_email": "sales@morrisonfox.co.uk"
      },
      "outreach": {
        "email_subject": "14 Elmwood Gardens — cash buyer, quick completion possible",
        "email_body": "Dear Morrison & Fox team,\n\nI'm a cash buyer actively looking in E3 and came across 14 Elmwood Gardens. I'd be interested in viewing and potentially moving quickly if the seller is open to a competitive offer.\n\nI can complete in 4–6 weeks without a chain.\n\nWould the seller consider a viewing this week?\n\nBest regards,\n[Your name]",
        "sms_message": "Hi, cash buyer interested in 14 Elmwood Gardens. Can move fast, no chain. Worth a chat? [Your name]",
        "followup_day3": "Just following up re: Elmwood Gardens — still very interested if the seller would like to discuss.",
        "followup_day7": "Final follow-up on 14 Elmwood Gardens. Happy to arrange a call at your convenience."
      }
    }
  ],
  "market_snapshot": {
    "avg_days_on_market": "32 days (London E3)",
    "price_trend_90d": "📉 -2.3% — buyer's market, motivated sellers increasing",
    "best_opportunity_streets": ["Elmwood Gardens", "Victoria Park Road", "Approach Road"]
  }
}
```

---

## 🧠 Claude AI Outreach Prompt

```
You are an expert real estate investor and negotiator.

PROPERTY DATA:
- Address: {{address}}
- Listing price: {{price}} (original: {{original_price}})
- Days on market: {{days_on_market}} (area avg: {{area_avg_dom}})
- Price reductions: {{price_reductions}}x
- Market value estimate: {{market_value}}
- Seller type: {{seller_type}}

BUYER PROFILE:
- Type: {{buyer_type}}
- Cash buyer: {{is_cash_buyer}}
- Can complete in: {{completion_time}}

GENERATE:
1. Email to agent/seller — professional, specific, references the exact 
   property and your ability to move fast. Max 100 words. Clear CTA.
2. SMS (max 160 chars) for direct seller contact
3. Day 3 follow-up (2 lines, different angle)
4. Day 7 final follow-up (1 line, keeps door open)

TONE: Professional, credible, cash-buyer confidence.
Never mention you know they're desperate.
OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Leads | Apify CU | Cost | Properties Analyzed |
|---|---|---|---|
| 50 leads | ~60 CU | ~$0.60 | ~300 properties |
| 200 leads | ~220 CU | ~$2.20 | ~1,000 properties |
| 500 leads | ~540 CU | ~$5.40 | ~2,500 properties |
| Daily auto-run | ~60 CU/day | ~$18/month | Fresh leads every morning |

> 💡 **$5 free Apify credits on signup** = your first 250 properties analyzed for free.  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

---

## 🔗 Who Makes Money With This Skill

| User | How They Use It | Revenue Potential |
|---|---|---|
| **Property Investor** | Find motivated sellers before competitors | Deals at 10–15% below market |
| **Estate Agent** | Generate off-market leads for buyers | £3K–£15K commission per deal |
| **Real Estate Wholesaler** | Build motivated seller lists at scale | £5K–$20K per assigned contract |
| **Mortgage Broker** | Target homeowners likely to refinance | £500–£2K per referral |
| **Property Sourcer** | Sell sourced deals to investors at a fee | £2K–£5K per deal sourced |

---

## 📊 Why This Beats Manual Research

| Feature | Manual Research | **Real Estate Lead Machine** |
|---|---|---|
| Time to find 50 leads | 8–12 hours | Under 5 minutes |
| Motivated seller detection | Guesswork | Automated signal scoring |
| Market value comparison | Manual comps | Auto-generated |
| Contact details found | Sometimes | Always attempted |
| Outreach messages | Write from scratch | AI-generated per property |
| Daily refresh | Never happens | Fully automated |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Sign up free → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Go to: **Settings → Integrations → API Token**

**Step 2 — Define your target zone & buyer profile**  
Location, property type, price range, investment strategy.

**Step 3 — Run daily for fresh motivated leads every morning**  
Set it on a schedule — wake up to a ranked list of leads every day.

---

## ⚡ Pro Tips to Close More Deals

- **Contact HOT leads within 2 hours** — speed is your #1 advantage
- **Always mention chain-free & fast completion** — that's what motivated sellers want to hear
- **Run the scraper daily at 6AM** — new listings drop overnight, be first to reach out
- **Focus on FSBO (For Sale By Owner)** — no agent = no competition, direct seller contact
- **Price reductions 3x+ = desperation signal** — these sellers will negotiate hard

---

## 🏷️ Tags

`real-estate` `property` `lead-generation` `motivated-sellers` `zillow` `rightmove` `apify` `investor` `estate-agent` `off-market` `property-sourcing` `outreach`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + Claude AI*
