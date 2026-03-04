# 🛡️ Brand Reputation Defender — Monitor, Respond & Protect Your Image 24/7

**Slug:** `brand-reputation-defender`  
**Category:** Brand Management / Online Reputation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Input any brand name. Get a **real-time reputation report** — every mention across Google, Reddit, Twitter/X, TikTok, Trustpilot, and news sites — sentiment-scored, crisis-flagged, and paired with AI-generated response drafts. Never get blindsided again.

---

## 💥 Why Every Brand, Agency & PR Pro Needs This Skill

One viral negative post can destroy years of brand building overnight. Most businesses have **zero system** to monitor what's being said about them online — until it's too late.

This skill is a **24/7 reputation radar**. It monitors everything, scores the sentiment, flags crises before they explode, and drafts the perfect response in seconds.

**Every brand, startup, agency, PR consultant, and public figure is your target.**

**What gets automated:**
- 🔍 Monitor **every mention** of any brand across 10+ platforms
- 😊 Score each mention: **Positive / Neutral / Negative / Crisis**
- 🚨 **Instant crisis alerts** when a negative mention goes viral
- ⭐ Track **review scores** across Google, Trustpilot, G2, Yelp, App Store
- 📰 Monitor **press & news coverage** in real time
- ✍️ Generate **AI response drafts** for every negative mention
- 📊 Deliver a **weekly reputation report** with score trends
- 🏆 Benchmark reputation **vs top 3 competitors**

---

## 🛠️ Apify Actors Used

| Actor | ID | Purpose |
|---|---|---|
| Google Search Scraper | `apify/google-search-scraper` | News, blog mentions, forum posts |
| Reddit Scraper | `apify/reddit-scraper` | Brand mentions in subreddits |
| Twitter/X Scraper | `apify/twitter-scraper` | Tweets, threads, viral mentions |
| TikTok Scraper | `apify/tiktok-scraper` | Video mentions & comment sentiment |
| Trustpilot Scraper | `apify/trustpilot-scraper` | Review scores & new reviews |
| Google Maps Scraper | `compass/crawler-google-places` | Google Business reviews |
| Google News Scraper | `apify/google-news-scraper` | Press coverage & media mentions |
| App Store Scraper | `apify/app-store-scraper` | App reviews (iOS & Android) |

---

## ⚙️ Full Workflow

```
INPUT: Brand name + competitors + alert keywords + monitoring frequency
        ↓
STEP 1 — Full Web Mention Scan
  └─ Google: news, blogs, forums, review sites
  └─ Reddit: brand mentions across all subreddits
  └─ Twitter/X: tweets, threads, quote-tweets
  └─ TikTok: videos mentioning the brand + comments
  └─ News sites: press coverage, journalist mentions
        ↓
STEP 2 — Review Platform Monitoring
  └─ Trustpilot, Google Reviews, G2, Yelp, App Store
  └─ New reviews since last scan
  └─ Average score trend (improving or declining?)
        ↓
STEP 3 — Sentiment Analysis Per Mention
  └─ 😍 Positive: praise, recommendations, UGC love
  └─ 😐 Neutral: factual mentions, news coverage
  └─ 😠 Negative: complaints, criticism, bad reviews
  └─ 🚨 Crisis: viral negative content, coordinated attacks
        ↓
STEP 4 — Crisis Detection & Scoring
  └─ Virality score: views + shares + engagement velocity
  └─ Reach estimate: how many people saw this?
  └─ Escalation risk: is this growing or contained?
        ↓
STEP 5 — Competitor Reputation Benchmark
  └─ Your score vs top 3 competitors on every platform
  └─ Their strengths & vulnerabilities detected
        ↓
STEP 6 — Claude AI Generates Response Drafts
  └─ Professional response to every negative review
  └─ Crisis statement template if needed
  └─ Thank you responses for top positive mentions
  └─ PR pitch angle based on positive coverage found
        ↓
OUTPUT: Full reputation report + crisis alerts + response drafts (JSON / PDF-ready)
```

---

## 📥 Inputs

```json
{
  "brand": {
    "name": "YourBrand",
    "domain": "yourbrand.com",
    "aliases": ["Your Brand", "YB", "@yourbrand"],
    "industry": "SaaS / Project Management",
    "tone_of_voice": "professional, empathetic, solution-focused"
  },
  "competitors": ["Competitor1", "Competitor2", "Competitor3"],
  "monitoring": {
    "platforms": ["google", "reddit", "twitter", "tiktok", "trustpilot", "google_reviews", "news"],
    "alert_keywords": ["scam", "fraud", "worst", "avoid", "lawsuit", "refund", "hack"],
    "frequency": "daily",
    "lookback_days": 7
  },
  "alerts": {
    "crisis_threshold_score": 70,
    "slack_webhook": "YOUR_SLACK_WEBHOOK",
    "email_alert": "alerts@yourbrand.com"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "report": {
    "brand": "YourBrand",
    "period": "March 1–7, 2025",
    "overall_reputation_score": 74,
    "score_trend": "📈 +6 points vs last week",
    "total_mentions": 847,
    "sentiment_breakdown": {
      "positive": "61% (517 mentions)",
      "neutral": "24% (203 mentions)",
      "negative": "13% (110 mentions)",
      "crisis": "2% (17 mentions) — 🚨 REQUIRES ATTENTION"
    }
  },
  "crisis_alerts": [
    {
      "severity": "🚨 HIGH",
      "platform": "Reddit",
      "url": "reddit.com/r/SaaS/comments/xyz",
      "title": "YourBrand deleted my account without warning and kept my money",
      "author": "u/frustrated_user_99",
      "upvotes": 847,
      "comments": 203,
      "reach_estimate": "~45,000 people",
      "virality_score": 89,
      "escalation_risk": "HIGH — growing 340 upvotes/hour",
      "detected_at": "2025-03-05 14:23 UTC",
      "ai_response_draft": {
        "public_reply": "Hi, we're really sorry to hear about your experience — this is absolutely not how we want any customer to feel. We've flagged your case as urgent and a member of our team will reach out to you directly within the next 2 hours to resolve this fully. Could you please DM us your account email so we can prioritize your case?",
        "internal_action": "Escalate to Customer Success VP immediately. Do NOT let this sit. Offer full refund + 3 months free as resolution.",
        "pr_statement": "We take all customer concerns seriously and are committed to making this right. We are in direct contact with the customer and will ensure a full resolution today."
      }
    }
  ],
  "review_summary": {
    "trustpilot": { "score": 4.1, "trend": "📉 -0.2 this week", "new_reviews": 23, "negative_new": 5 },
    "google_reviews": { "score": 4.4, "trend": "📈 stable", "new_reviews": 11, "negative_new": 1 },
    "g2": { "score": 4.6, "trend": "📈 +0.1", "new_reviews": 8, "negative_new": 0 }
  },
  "top_negative_mentions": [
    {
      "platform": "Twitter/X",
      "content": "Been waiting 5 days for a response from @yourbrand support. Absolutely shocking customer service.",
      "reach": "12,400 impressions",
      "sentiment_score": -78,
      "ai_response": "Hi [name], we sincerely apologize for the delay — this is unacceptable and not our standard. We've located your ticket and a senior support agent will contact you within the next 60 minutes. Thank you for your patience."
    }
  ],
  "top_positive_mentions": [
    {
      "platform": "TikTok",
      "content": "Switched to YourBrand 3 months ago and honestly can't believe I waited so long",
      "views": 284000,
      "sentiment_score": 94,
      "ai_response": "This made our whole team's day 🙌 So glad you made the switch — we'll keep working hard to deserve it! Mind if we share this?"
    }
  ],
  "competitor_benchmark": {
    "yourbrand_score": 74,
    "competitor1_score": 71,
    "competitor2_score": 68,
    "competitor3_score": 79,
    "insight": "You rank #2 of 4. Competitor3 leads on response time — they reply to reviews within 2 hours on average.",
    "opportunity": "Competitor2 has 47 unanswered negative reviews on Trustpilot this week — opportunity to attract their unhappy customers."
  },
  "weekly_recommendations": [
    "🚨 Address Reddit crisis post within 2 hours — escalation risk is HIGH",
    "⭐ Respond to 5 unanswered Trustpilot reviews today — impacts score directly",
    "📣 Amplify TikTok post (284K views) — request permission to share on your channels",
    "🏆 Competitor2 has 47 unanswered complaints — run a targeted campaign this week"
  ]
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class PR strategist and brand reputation manager.

MENTION DATA:
{{all_mentions_data}}

REVIEW DATA:
{{reviews_data}}

BRAND PROFILE:
- Name: {{brand_name}}
- Industry: {{industry}}
- Tone of voice: {{tone}}

FOR EACH NEGATIVE MENTION OR REVIEW GENERATE:
1. Sentiment score (-100 to +100)
2. Severity label: Crisis / Negative / Neutral / Positive
3. Reach estimate and escalation risk (for social posts)
4. Public response draft:
   - Acknowledge the issue with empathy
   - Take ownership without admitting legal liability
   - Offer a clear next step (DM, email, callback)
   - Max 3 sentences. Human tone, never corporate.
5. Internal action recommendation (what the team should actually do)

FOR CRISIS ALERTS (virality score 70+):
- Add a press statement template
- Suggest whether to respond publicly or take it private
- Estimate reputation damage if unaddressed for 24h / 48h / 72h

FOR TOP POSITIVE MENTIONS:
- Draft a genuine thank-you response
- Flag if worth amplifying (repost / share / UGC campaign)

WEEKLY REPORT:
- Overall reputation score (0-100)
- Score trend vs previous period
- Top 3 risks this week
- Top 3 opportunities this week
- Competitor vulnerability detected

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Monitoring | Apify CU | Cost | Mentions Scanned |
|---|---|---|---|
| 1 brand (weekly) | ~70 CU | ~$0.70 | ~1,000 mentions |
| 1 brand (daily) | ~70 CU/day | ~$21/month | ~30,000 mentions |
| 5 brands (daily) | ~350 CU/day | ~$105/month | ~150,000 mentions |
| Agency (20 brands) | ~1,400 CU/day | ~$420/month | ~600,000 mentions |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**

---

## 🔗 Who Makes Money With This Skill

| User | How They Use It | Revenue |
|---|---|---|
| **PR Agency** | Offer reputation monitoring as a monthly retainer | $500–$3,000/client/month |
| **Marketing Agency** | Bundle with social media management | +$500/month per client |
| **Brand Manager** | In-house daily monitoring for own brand | Protect $millions in brand value |
| **Startup Founder** | Monitor launch reactions in real time | Catch & fix crises before they scale |
| **Reputation Consultant** | Sell crisis management packages | $2,000–$10,000 per crisis handled |
| **Investor / VC** | Monitor portfolio company reputations | Early warning on brand risks |

---

## 📊 Why This Destroys Expensive Reputation Tools

| Feature | Mention ($99/mo) | Brand24 ($149/mo) | **This Skill** |
|---|---|---|---|
| Multi-platform monitoring | ✅ | ✅ | ✅ |
| Sentiment analysis | ✅ | ✅ | ✅ |
| Crisis alerts | ✅ | ✅ | ✅ |
| AI-generated response drafts | ❌ | ❌ | ✅ |
| Competitor vulnerability analysis | ❌ | ❌ | ✅ |
| PR statement templates | ❌ | ❌ | ✅ |
| Internal action recommendations | ❌ | ❌ | ✅ |
| Monthly cost (1 brand) | $99 | $149 | ~$21 |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Configure your brand profile**  
Brand name, aliases, competitors, crisis keywords, alert channel.

**Step 3 — Set your monitoring frequency & run**  
Daily for active brands. Weekly for smaller businesses. Crisis alerts fire instantly.

---

## ⚡ Pro Tips to Protect Your Reputation Like a Pro

- **Respond to every negative review within 24 hours** — review platforms reward responsiveness with better ranking
- **Never argue publicly** — acknowledge, empathize, take it to DMs. Always.
- **Set crisis keywords immediately** — "scam", "fraud", "lawsuit", "refund" should trigger instant alerts
- **Monitor competitor crises** — when they get hit, be ready to capture their unhappy customers
- **Amplify positive UGC** — when a customer posts something great, share it fast before momentum dies
- **Weekly score tracking beats daily panic** — trends matter more than single mentions

---

## 🏷️ Tags

`reputation-management` `brand-monitoring` `pr` `crisis-management` `sentiment-analysis` `apify` `reviews` `social-listening` `brand-protection` `trustpilot` `google-reviews` `agency`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + Claude AI*
