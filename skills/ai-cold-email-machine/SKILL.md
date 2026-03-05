# 🤖 AI Cold Email Machine — Automated Outreach Sequences for Agencies & Freelancers

**Slug:** `ai-cold-email-machine`  
**Category:** Marketing Automation / Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Stop writing cold emails manually. This skill **scrapes your prospects, enriches their data, and generates hyper-personalized multi-step email sequences** in minutes — ready to import into Instantly, Lemlist, or Mailshake.

---

## 💥 Why Every Agency & Freelancer Needs This

Cold email is still the #1 channel for agency client acquisition. But 99% of agencies fail because they blast **generic, copy-paste emails** that get ignored. This skill fixes that forever.

Each email sequence is generated using **live data** scraped about the prospect:

- Their **most recent blog post or article**
- Their **tech stack** (CRM, CMS, ad tools — auto-detected)
- Their **hiring activity** (growth & budget signals)
- Their **recent news** (awards, funding, product launches)
- Their **social media tone & activity**

The result? Emails that feel 100% hand-written. Generated in seconds. At any scale.

---

## 🛠️ Apify Actors Used

> 🚀 **Start free on Apify — $5 free credits included:**  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

| Actor | ID | Purpose |
|---|---|---|
| Website Content Crawler | `apify/website-content-crawler` | Scrape prospect's website & blog posts |
| LinkedIn Company Scraper | `anchor/linkedin-company-scraper` | Headcount, growth, recent company posts |
| Google Search Scraper | `apify/google-search-scraper` | Recent news, press mentions, awards |
| Tech Stack Detector | `apify/wappalyzer` | Identify their CMS, CRM, ad & email tools |
| Email Finder | `misceres/prospectin-email-finder` | Find verified professional email addresses |

---

## ⚙️ Full Workflow

```
INPUT: List of prospect domains (e.g. agencexyz.com)
        ↓
STEP 1 — Crawl Prospect Website
  └─ Extract: services offered, tone of voice, blog posts, case studies
        ↓
STEP 2 — Detect Tech Stack
  └─ Identify: HubSpot? Mailchimp? Shopify? Webflow?
        ↓
STEP 3 — Scrape LinkedIn Company Page
  └─ Extract: team size, growth rate, recent activity, key employees
        ↓
STEP 4 — Google Search Recent News
  └─ Find: press coverage, awards, funding, product launches (last 90 days)
        ↓
STEP 5 — Find Decision Maker Email
  └─ Verified email: Founder / CEO / Marketing Director / Head of Growth
        ↓
STEP 6 — Claude AI Writes Full Sequence
  └─ Email 1: Hyper-personalized opener referencing live data (Day 1)
  └─ Email 2: Value add + social proof (Day 3)
  └─ Email 3: Case study tailored to their niche & stack (Day 7)
  └─ Email 4: Classy break-up email (Day 14)
        ↓
OUTPUT: Ready-to-import CSV/JSON per prospect — paste directly into your sending tool
```

---

## 📥 Inputs

```json
{
  "prospects": [
    { "domain": "agencexyz.com" },
    { "domain": "growthstudio.io" },
    { "domain": "digitalboost.agency" }
  ],
  "your_agency": {
    "name": "Your Agency Name",
    "service": "Facebook & TikTok Ads",
    "niche": "E-commerce brands",
    "case_study": "We scaled a Shopify brand from $10K to $80K/month in 60 days"
  },
  "sequence_length": 4,
  "tone": "casual_professional",
  "language": "en",
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "prospect": {
    "company": "GrowthStudio",
    "website": "growthstudio.io",
    "decision_maker": "James Carter",
    "title": "Founder & CEO",
    "email": "james@growthstudio.io",
    "tech_stack": ["Webflow", "ActiveCampaign", "Google Ads"],
    "recent_news": "Just ranked #3 Best Agency in the UK 2024",
    "linkedin_headcount": 14,
    "last_blog_post": "Why Most Agencies Lose Clients After 3 Months"
  },
  "sequence": [
    {
      "day": 1,
      "subject": "Congrats on the UK ranking, James 🏆",
      "body": "Hey James,\n\nJust saw GrowthStudio landed #3 Best Agency in the UK — well deserved.\n\nI reach out to top agencies because we built a system that adds 2-3 e-commerce clients per month on autopilot using outbound.\n\nWe just helped a 12-person agency (similar size to yours) go from $35K to $95K MRR in 90 days.\n\nWorth a 15-min call this week?\n\n[Your name]"
    },
    {
      "day": 3,
      "subject": "Re: your post on client retention",
      "body": "James,\n\nRead your article on why agencies lose clients after 3 months — sharp insight on the onboarding gap.\n\nThat's exactly why our approach works: we only target e-com brands already doing $50K+/month, so your new clients are pre-qualified and ready to invest seriously.\n\nWant me to send over the full case study?\n\n[Your name]"
    },
    {
      "day": 7,
      "subject": "Case study: +$60K MRR for an 8-person agency",
      "body": "James,\n\nAs promised — here's how an 8-person agency added $60K MRR in 3 months.\n\nThe key: targeting only brands running Google Ads + Shopify. They already have the budget and the pain point.\n\nYou're on ActiveCampaign + Google Ads — that's exactly the profile we crush it with.\n\n15 min this week?\n\n[Your name]"
    },
    {
      "day": 14,
      "subject": "Last message — GrowthStudio",
      "body": "James,\n\nI don't want to clog your inbox — this is my last message.\n\nIf outbound client acquisition isn't a priority right now, totally understood.\n\nIf that changes, you know where to find me 🚀\n\n[Your name]"
    }
  ]
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class cold email copywriter specializing in agency outreach.

PROSPECT DATA:
- Company: {{company_name}}
- Decision maker: {{dm_name}}, {{dm_title}}
- Tech stack: {{tech_stack}}
- Recent news: {{recent_news}}
- Last blog post: {{blog_post}}
- Team size: {{headcount}} people

MY AGENCY:
- Service: {{my_service}}
- Niche: {{my_niche}}
- Case study: {{my_case_study}}

RULES:
1. Email 1 — Opener: Reference ONE specific live data point (news/award/blog).
   Max 80 words. No pitch yet. Soft CTA only.
2. Email 2 — Value: Reference their content. Hint at the case study.
   Show you understand their business.
3. Email 3 — Proof: Deliver the case study. Connect their tech stack 
   to why it's specifically relevant to them.
4. Email 4 — Break-up: 3 lines max. Zero pressure. Leave on good terms.

TONE: {{tone}} | LANGUAGE: {{language}}
OUTPUT: Valid JSON only — keys: day, subject, body for each email.
No preamble. No markdown. Just the JSON.
```

---

## 💰 Cost Estimate

| Prospects | Apify CU | Cost | Sequences Generated |
|---|---|---|---|
| 10 | ~25 CU | ~$0.25 | 40 emails |
| 50 | ~120 CU | ~$1.20 | 200 emails |
| 100 | ~230 CU | ~$2.30 | 400 emails |
| 500 | ~1,100 CU | ~$11 | 2,000 emails |

> 💡 **Apify gives $5 free credits on signup** — enough to generate sequences for ~200 prospects.  
> 👉 [Create your free Apify account → https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

---

## 🔗 Export Directly Into Your Sending Tool

| Tool | Integration |
|---|---|
| **Instantly.ai** | Direct CSV import — sequences pre-mapped |
| **Lemlist** | JSON import with variables auto-filled |
| **Mailshake** | CSV with subject + body columns ready |
| **Smartlead** | Webhook integration |
| **Apollo.io** | CSV enrichment upload |
| **Notion / Airtable** | Auto-populated prospects database |
| **Slack** | Instant alert when a new sequence is ready |

---

## 📊 Why This Skill Wins vs Everything Else

| Feature | Generic Email Skill | **AI Cold Email Machine** |
|---|---|---|
| Personalized per prospect | ❌ | ✅ |
| References their blog/news | ❌ | ✅ |
| Auto-detects tech stack | ❌ | ✅ |
| Full 4-step sequence | ❌ | ✅ |
| Import-ready for Instantly/Lemlist | ❌ | ✅ |
| Works in EN + FR + ES | ❌ | ✅ |
| Finds verified email address | ❌ | ✅ |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Create your free account → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Navigate to: **Settings → Integrations → API Token** → Copy it

**Step 2 — Define your agency profile**  
Fill in your service, target niche, and your strongest case study.  
Pro tip: always include a specific number ($, %, timeframe).

**Step 3 — Drop your prospect list**  
Paste domain names. Hit run. Get sequences in minutes.

---

## ⚡ Pro Tips to Maximize Reply Rates

- **Specific numbers beat vague claims** — "$80K/month in 60 days" > "great results"
- **Email 1 should be under 80 words** — shorter = higher reply rate
- **Best sending windows:** Tuesday–Thursday, 8–10am prospect's local time
- **Warm up your domain first** — use Instantly or Mailreach before bulk sending
- **A/B test subject lines** — question vs statement vs name-drop

---

## 🏷️ Tags

`cold-email` `outreach` `agencies` `freelancers` `lead-generation` `email-sequences` `apify` `ai-copywriting` `instantly` `lemlist` `marketing-automation` `personalization`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) — The Web Scraping & Automation Platform*
