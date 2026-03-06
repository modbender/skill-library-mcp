---
name: 🎯 Google & Meta Ads Spy Tool — Steal Winning Ad Creatives From Any Competitor
description: "The #1 shortcut in paid advertising is this: don't guess what
  works — copy what's already proven. The problem? Manually spying on
  competitors takes hours, across multiple tools that each cost $100–..."
---

# 🎯 Google & Meta Ads Spy Tool — Steal Winning Ad Creatives From Any Competitor

**Slug:** `google-meta-ads-spy`  
**Category:** Paid Advertising / Competitive Intelligence  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input any competitor or niche. Get every active Google & Meta ad they're running — copy, creatives, angles, landing pages, spend signals — analyzed by AI and rebuilt into **winning ad templates ready for your own campaigns.**

---

## 💥 Why This Skill Will Dominate ClawHub

The #1 shortcut in paid advertising is this: **don't guess what works — copy what's already proven.** The problem? Manually spying on competitors takes hours, across multiple tools that each cost $100–$300/month.

This skill replaces them all. One run. Every competitor ad. Fully analyzed.

**Every media buyer, agency, brand, and e-commerce store is your target.** Paid ads is a $600B/year industry — everyone running ads needs this.

**What gets automated:**
- 🕵️ Scrape **all active ads** from any competitor on Meta & Google
- 📊 Detect **spend signals** — how long an ad has been running = proof it's profitable
- 🧠 Analyze **hooks, angles, CTAs, formats** that are performing best
- 🖼️ Extract **all creative assets** — images, video thumbnails, ad copy
- 🔗 Capture **landing page strategy** — what happens after the click
- ✍️ Claude AI **rewrites winning ads** adapted to your brand & offer
- 🎬 **InVideo AI produces video ad versions** of winning creatives
- 📋 Deliver a **battle-ready swipe file** for your next campaign

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Meta Ad Library Scraper | All active Facebook & Instagram ads per brand |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Ads Transparency Scraper | Active Google Search & Display ads |
| [Apify](https://www.apify.com?fpr=dx06p) — Website Content Crawler | Landing page copy, structure & CTA analysis |
| [Apify](https://www.apify.com?fpr=dx06p) — TikTok Ads Scraper | TikTok Creative Center top ads by niche |
| [InVideo AI](https://invideo.sjv.io/TBB) | Rebuild winning video ad concepts for your brand |
| Claude AI | Ad copy rewriting, angle analysis, campaign strategy |

---

## ⚙️ Full Workflow

```
INPUT: Competitor domains / brand names + your niche + your offer
        ↓
STEP 1 — Scrape All Active Competitor Ads
  └─ Meta Ad Library: every active Facebook & Instagram ad
  └─ Google Ads Transparency Center: Search + Display ads
  └─ TikTok Creative Center: top performing video ads in niche
        ↓
STEP 2 — Detect Spend & Performance Signals
  └─ Ad running 30+ days = proven winner (they're spending on it)
  └─ Ad running 90+ days = absolute winner (scale this angle)
  └─ Multiple ad variations of same angle = testing phase (watch this)
        ↓
STEP 3 — Deep Creative Analysis
  └─ Hook type: question / shock / story / testimonial / offer
  └─ Emotional trigger: fear / greed / curiosity / social proof
  └─ Format: static image / carousel / video / UGC style
  └─ CTA strategy: urgency / soft / direct / benefit-led
        ↓
STEP 4 — Landing Page Intelligence
  └─ Headline formula, offer structure, social proof type
  └─ CTA placement, urgency tactics, price anchoring
  └─ What they A/B test (detected via URL parameters)
        ↓
STEP 5 — Claude AI Rebuilds Winning Ads For Your Brand
  └─ Takes top 5 performing competitor ads
  └─ Rewrites each with your brand voice, offer & USP
  └─ Generates 3 angle variations per winning ad
        ↓
STEP 6 — InVideo AI Produces Video Versions
  └─ Top winning static ad angles turned into 15s & 30s video ads
  └─ Hook-first format optimized for Facebook, Instagram & TikTok
        ↓
OUTPUT: Full swipe file + rewritten ads + video creatives + campaign strategy
```

---

## 📥 Inputs

```json
{
  "competitors": [
    { "domain": "competitor1.com", "brand_name": "BrandOne" },
    { "domain": "competitor2.com", "brand_name": "BrandTwo" },
    { "domain": "competitor3.com", "brand_name": "BrandThree" }
  ],
  "your_brand": {
    "name": "YourBrand",
    "offer": "Online fitness coaching program — 12-week transformation",
    "usp": "No gym needed, 20 minutes/day, results in 30 days or money back",
    "target_audience": "Busy moms aged 30-45",
    "tone": "motivational, empathetic, real"
  },
  "platforms": ["meta", "google", "tiktok"],
  "min_days_running": 14,
  "max_ads_per_competitor": 50,
  "invideo_api_key": "YOUR_INVIDEO_API_KEY",
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "spy_summary": {
    "competitors_analyzed": 3,
    "total_ads_scraped": 147,
    "proven_winners_found": 23,
    "top_performing_angles": [
      "Before/After transformation story",
      "Social proof overload (numbers + testimonials)",
      "Objection-killer ('No gym? No problem')"
    ],
    "dominant_format": "UGC-style video (61% of top ads)",
    "avg_winning_ad_runtime": "47 days"
  },
  "top_competitor_ads": [
    {
      "rank": 1,
      "competitor": "FitnessBrandOne",
      "performance_signal": "🔥 Running 94 days — PROVEN WINNER",
      "platform": "Facebook + Instagram",
      "format": "Video (UGC style, 28 seconds)",
      "hook": "I lost 22 lbs in 8 weeks without stepping foot in a gym...",
      "angle": "Personal transformation story — relatable mom, no equipment",
      "emotional_trigger": "Hope + social proof",
      "cta": "Start Your Free 7-Day Trial",
      "landing_page_intel": {
        "headline": "The 20-Minute Home Workout That's Transforming Busy Moms",
        "offer_structure": "Free trial → upsell to annual",
        "urgency_tactic": "Countdown timer + 'Only 47 spots left'",
        "social_proof": "23,847 transformations + before/after photos above fold"
      },
      "why_it_wins": "Speaks directly to the #1 objection (no time, no gym). UGC format feels authentic. Free trial removes purchase risk entirely.",
      "your_rewritten_version": {
        "hook": "I transformed my body in 12 weeks — as a mom of 3, working full time, with zero gym access...",
        "body": "I tried everything. Early morning gym sessions I couldn't keep up. Diets that made me miserable. Then I found a 20-minute home program that actually fit my life.\n\n12 weeks later: down 19 lbs, more energy than I've had in years, and I've kept it off.\n\nYourBrand is giving busy moms a free 7-day trial right now — no gym, no equipment, just 20 minutes a day.",
        "cta": "Claim Your Free 7-Day Trial →",
        "angle_variations": [
          "Variation A: Lead with the time objection ('Only 20 minutes')",
          "Variation B: Lead with the social proof ('Join 15,000 moms')",
          "Variation C: Lead with the guarantee ('30-day transformation or full refund')"
        ]
      },
      "invideo_production": {
        "status": "produced",
        "formats": ["15s Instagram Reel", "30s Facebook Ad", "60s TikTok"],
        "style": "UGC authentic",
        "video_urls": ["outputs/ad_01_15s.mp4", "outputs/ad_01_30s.mp4", "outputs/ad_01_60s.mp4"]
      }
    }
  ],
  "niche_intelligence": {
    "top_hooks_in_niche": [
      "I lost X lbs in Y weeks without...",
      "Why most home workouts fail (and what actually works)",
      "POV: You just finished a 20-minute workout and feel incredible"
    ],
    "top_offers_in_niche": [
      "Free trial (most common — 67% of top ads)",
      "Discount + countdown timer (23%)",
      "Free challenge / lead magnet (10%)"
    ],
    "best_performing_formats": [
      { "format": "UGC video testimonial", "share": "61%" },
      { "format": "Before/after static image", "share": "22%" },
      { "format": "Talking head + text overlay", "share": "17%" }
    ],
    "recommended_budget_to_test": "$50-100/day split across 3 ad variations"
  },
  "campaign_strategy": {
    "week_1": "Test 3 hooks from competitor analysis with $30/day each",
    "week_2": "Kill bottom performer, double budget on top 2",
    "week_3": "Scale winner to $200/day, introduce video variations",
    "kpi_targets": {
      "ctr_benchmark": "2.5-4% (niche average from scraped data)",
      "cpc_benchmark": "$0.80-$1.40",
      "roas_target": "3x minimum before scaling"
    }
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class paid advertising strategist and direct response copywriter.

COMPETITOR AD DATA:
{{competitor_ads_data}}

LANDING PAGE INTELLIGENCE:
{{landing_pages_data}}

NICHE PERFORMANCE DATA:
{{niche_ad_benchmarks}}

MY BRAND:
- Name: {{brand_name}}
- Offer: {{offer}}
- USP: {{usp}}
- Target audience: {{target_audience}}
- Tone: {{tone}}

FOR EACH TOP COMPETITOR AD GENERATE:
1. Performance signal — how long running + what that signals
2. Deep breakdown: hook type, angle, emotional trigger, CTA strategy
3. Landing page intelligence: headline formula, offer, urgency, social proof
4. Why it wins — 2 sentences, brutally honest
5. Rewritten version for MY brand:
   - Same proven angle, adapted to my offer & audience
   - 3 hook variations (A/B/C test ready)
   - My CTA optimized for my offer type

ALSO GENERATE:
- Top 5 hooks dominating this niche
- Top 3 offer structures that convert best
- 4-week testing & scaling campaign strategy
- KPI benchmarks based on niche data

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Competitors | Apify CU | InVideo Cost | Total Cost |
|---|---|---|---|
| 3 competitors | ~50 CU (~$0.50) | ~$8 (3 videos) | ~$8.50 |
| 5 competitors | ~80 CU (~$0.80) | ~$15 (5 videos) | ~$15.80 |
| 10 competitors | ~155 CU (~$1.55) | ~$28 (10 videos) | ~$29.55 |
| Full niche audit (20) | ~300 CU (~$3) | ~$55 (20 videos) | ~$58 |

> 💡 **$5 free Apify credits on signup:**  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

> 🎬 **Produce your video ads with InVideo AI:**  
> 👉 [https://invideo.sjv.io/TBB](https://invideo.sjv.io/TBB)

---

## 🔗 Who Wins Big With This Skill

| User | How They Use It | Value |
|---|---|---|
| **Media Buyer** | Never launch a blind campaign again | Save $000s in wasted ad spend |
| **Marketing Agency** | Deliver competitor analysis as a paid service | $500–$2,000 per audit |
| **E-commerce Brand** | Copy proven ad angles before testing | 3x faster path to winning ads |
| **SaaS Company** | Spy on competitor acquisition strategy | Understand what converts in your market |
| **Dropshipper** | Find proven product ads before sourcing | Only source products with validated ads |
| **Freelance Copywriter** | Deliver competitor swipe files to clients | Add $500–$1,500 to any project |

---

## 📊 Why This Replaces $300+/Month Spy Tools

| Feature | AdSpy ($149/mo) | SocialPeta ($299/mo) | **This Skill** |
|---|---|---|---|
| Meta ads scraping | ✅ | ✅ | ✅ |
| Google ads scraping | ❌ | ✅ | ✅ |
| TikTok ads scraping | ❌ | ✅ | ✅ |
| Landing page analysis | ❌ | ❌ | ✅ |
| AI rewrites for your brand | ❌ | ❌ | ✅ |
| Video ad production | ❌ | ❌ | ✅ |
| Campaign strategy included | ❌ | ❌ | ✅ |
| Monthly cost | $149 | $299 | ~$8.50/run |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Sign up free → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your InVideo AI account**  
Sign up free → [https://invideo.sjv.io/TBB](https://invideo.sjv.io/TBB)  
Go to: **Settings → API → Copy your key**

**Step 3 — Input competitors & your brand**  
Competitor domains + your offer. Full spy report in under 10 minutes.

---

## ⚡ Pro Tips to Launch Winning Campaigns Faster

- **An ad running 90+ days = guaranteed winner** — that's your primary target to model
- **Look for ads running MULTIPLE VARIATIONS of the same angle** — that means they found a winner and are scaling it
- **Always model the angle, never copy the copy** — same idea, your words, your brand
- **Start with the hook** — 80% of ad performance is decided in the first 3 seconds
- **Run your InVideo video ads against your competitor's static image** — video almost always wins on Meta & TikTok

---

## 🏷️ Tags

`paid-ads` `facebook-ads` `google-ads` `tiktok-ads` `competitor-research` `ad-spy` `media-buying` `apify` `invideo` `creative-strategy` `performance-marketing` `swipe-file`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
