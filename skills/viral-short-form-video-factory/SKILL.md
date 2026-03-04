# 📱 Viral Short-Form Video Factory — TikTok, Reels & Shorts at Scale With AI

**Slug:** `viral-short-form-video-factory`  
**Category:** Content Marketing / Video Automation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input your niche. Get **30 fully produced short-form videos** — TikTok, Instagram Reels & YouTube Shorts — researched from viral trends, scripted with proven hooks, produced with AI voiceover & visuals, and ready to post. Your content machine on autopilot.

---

## 💥 Why This Skill Will Be Your #1 Bestseller on ClawHub

Short-form video is the #1 distribution channel on earth right now. TikTok alone serves **1 billion users**. Instagram Reels reach **2 billion**. YouTube Shorts hit **70 billion views per day**.

Every brand, creator, agency, and business on the planet needs short-form content. Most post inconsistently — or not at all — because production is slow, expensive, and exhausting.

This skill produces **30 platform-ready videos in one run.** For any niche. In any language.

**What gets automated:**
- 📊 Scrape **top 100 viral short-form videos** across TikTok, Reels & Shorts in your niche
- 🧠 Reverse-engineer **exactly why they went viral** — hook, format, sound, pacing
- 🎯 Identify the **5 content formats** dominating your niche right now
- ✍️ Generate **30 complete scripts** with viral hooks + captions + hashtags
- 🎬 Produce **30 finished videos** with AI voiceover, visuals & captions
- 📅 Build a **30-day posting calendar** with optimal times per platform
- 📤 Export **platform-ready files** for TikTok, Instagram & YouTube Shorts

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — TikTok Scraper | Scrape viral TikToks by hashtag, niche, sound |
| [Apify](https://www.apify.com?fpr=dx06p) — Instagram Reels Scraper | Top Reels by engagement & niche |
| [Apify](https://www.apify.com?fpr=dx06p) — YouTube Shorts Scraper | Viral Shorts by views & retention signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Trends Scraper | Rising topics before they peak |
| [Apify](https://www.apify.com?fpr=dx06p) — Reddit Scraper | Raw audience pain points & questions |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce full 9:16 videos with voiceover, visuals & captions |
| Claude AI | Script writing, hook generation, caption & hashtag strategy |

---

## ⚙️ Full Workflow

```
INPUT: Your niche + target audience + brand tone + posting goals
        ↓
STEP 1 — Scrape Top 100 Viral Videos Across All 3 Platforms
  └─ TikTok: views, shares, comments, sound used, hashtags
  └─ Instagram Reels: reach, saves, shares, audio
  └─ YouTube Shorts: views, CTR, retention drop-off signals
        ↓
STEP 2 — Viral Pattern Analysis
  └─ Hook formula (first 2 seconds = make or break)
  └─ Video length sweet spot for this niche
  └─ Formats winning: POV / listicle / story / tutorial / trend hijack
  └─ Sounds & music driving the most reach
  └─ Comment patterns = what triggers engagement
        ↓
STEP 3 — Trend & Audience Research
  └─ Google Trends: topics rising in last 7 days
  └─ Reddit: raw questions & frustrations from your audience
  └─ TikTok trending sounds: what's boosting reach right now
        ↓
STEP 4 — 30-Video Content Calendar Built
  └─ Week 1: Trend-jacking videos (ride current momentum)
  └─ Week 2: Educational / value-packed videos (authority)
  └─ Week 3: Relatable / entertaining videos (shareability)
  └─ Week 4: Conversion-focused videos (CTA to offer)
        ↓
STEP 5 — Claude AI Writes All 30 Scripts
  └─ Hook (2 seconds — stops the scroll)
  └─ Body (punchy, no fluff, pattern interrupts)
  └─ CTA (comment bait / follow / click link in bio)
  └─ Caption (algorithm-optimized)
  └─ 5-10 hashtags per video (mix of niche + broad)
        ↓
STEP 6 — InVideo AI Produces All 30 Videos
  └─ 9:16 vertical format (TikTok / Reels / Shorts ready)
  └─ AI voiceover in chosen voice & language
  └─ Auto-matched B-roll visuals
  └─ Bold captions synced to voiceover
  └─ Background music at optimal volume
  └─ Export: MP4 1080p per platform
        ↓
OUTPUT: 30 produced videos + scripts + captions + hashtags + calendar
```

---

## 📥 Inputs

```json
{
  "brand": {
    "niche": "Personal Finance for Gen Z",
    "target_audience": "18-28 year olds learning to invest and save",
    "tone": "casual, real, no corporate BS",
    "goal": "grow following + drive traffic to newsletter",
    "posting_frequency": "daily"
  },
  "content": {
    "videos_count": 30,
    "avg_video_length_seconds": 45,
    "language": "en",
    "style": "faceless with AI voiceover"
  },
  "platforms": ["tiktok", "instagram_reels", "youtube_shorts"],
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "voice": "energetic_male_en",
    "visual_style": "modern_bold"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "niche_analysis": {
    "platform_breakdown": {
      "tiktok": { "avg_viral_views": "2.4M", "optimal_length": "30-45s", "best_post_time": "7PM EST" },
      "instagram_reels": { "avg_viral_views": "890K", "optimal_length": "15-30s", "best_post_time": "6PM EST" },
      "youtube_shorts": { "avg_viral_views": "1.1M", "optimal_length": "45-59s", "best_post_time": "3PM EST" }
    },
    "top_formats": [
      { "format": "Listicle ('5 things...')", "share": "34% of viral videos", "avg_shares": 12400 },
      { "format": "Myth-busting ('Stop doing X')", "share": "27% of viral videos", "avg_shares": 18700 },
      { "format": "POV / Story", "share": "21% of viral videos", "avg_shares": 9800 }
    ],
    "viral_hook_patterns": [
      "If you have $X, do this immediately...",
      "Nobody talks about this investing mistake...",
      "POV: You just discovered you can retire at 40..."
    ],
    "top_hashtags": ["#personalfinance", "#moneytok", "#investing101", "#genzmoney", "#financetips"]
  },
  "videos": [
    {
      "video": 1,
      "week": 1,
      "type": "Trend-jacking",
      "platform_primary": "TikTok",
      "title": "5 Money Rules They Don't Teach in School",
      "hook": "If nobody taught you these 5 money rules, you're already behind. Let's fix that right now.",
      "script": "Hook (0:00-0:03): 'If nobody taught you these 5 money rules, you're already behind.'\nRule 1 (0:03-0:10): 'Pay yourself first. 10% to savings before anything else. Non-negotiable.'\nRule 2 (0:10-0:18): 'Emergency fund is not optional. 3 months expenses. High-yield savings account.'\nRule 3 (0:18-0:26): 'Invest before you feel ready. Time in market beats timing the market. Every time.'\nRule 4 (0:26-0:34): 'Lifestyle inflation kills wealth. Got a raise? Invest the difference.'\nRule 5 (0:34-0:42): 'Your credit score is a financial weapon. A good score saves you $100K+ lifetime.'\nCTA (0:42-0:45): 'Follow for daily money tips school never taught you.'",
      "caption": "The 5 money rules school never taught you 💰 Save this! #personalfinance #moneytok #moneyadvice #genzfinance #investing101",
      "hashtags": ["#personalfinance", "#moneytok", "#moneyadvice", "#genzfinance", "#investing101"],
      "cta_type": "Follow bait",
      "invideo_production": {
        "status": "produced",
        "duration": "45s",
        "format": "9:16 vertical",
        "video_file": "outputs/video_01_money_rules.mp4"
      }
    },
    {
      "video": 2,
      "week": 1,
      "type": "Myth-busting",
      "platform_primary": "Instagram Reels",
      "title": "Stop Saving Money in a Regular Bank Account",
      "hook": "You're losing hundreds of dollars every year and you don't even know it.",
      "script": "Hook (0:00-0:03): 'You're losing hundreds of dollars every year and you don't even know it.'\nProblem (0:03-0:12): 'Your regular bank pays 0.01% interest. Inflation runs at 3%. You're going BACKWARDS.'\nSolution (0:12-0:22): 'High-yield savings accounts pay 4.5-5% right now. That's 500x your regular bank.'\nAction (0:22-0:28): '10 minutes to open. FDIC insured. Same money, same safety, 500x the return.'\nCTA (0:28-0:30): 'Comment HYSA and I'll send you the best options right now.'",
      "caption": "Stop letting your bank rob you 😤 Comment HYSA for my top picks 👇 #moneytok #personalfinance #savingmoney #highyieldsavings",
      "hashtags": ["#moneytok", "#personalfinance", "#savingmoney", "#highyieldsavings", "#financetips"],
      "cta_type": "Comment bait",
      "invideo_production": {
        "status": "produced",
        "duration": "30s",
        "format": "9:16 vertical",
        "video_file": "outputs/video_02_hysa.mp4"
      }
    }
  ],
  "posting_calendar": [
    { "day": 1, "platform": "TikTok", "video": 1, "post_time": "7:00 PM EST", "status": "ready" },
    { "day": 2, "platform": "Instagram Reels", "video": 2, "post_time": "6:00 PM EST", "status": "ready" },
    { "day": 3, "platform": "YouTube Shorts", "video": 3, "post_time": "3:00 PM EST", "status": "ready" }
  ],
  "growth_projections": {
    "month_1": "500-2,000 new followers (consistency phase)",
    "month_3": "5,000-15,000 followers (algorithm picks you up)",
    "month_6": "20,000-80,000 followers (compounding effect)"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class short-form video strategist and scriptwriter.

VIRAL VIDEO DATA FROM SCRAPING:
{{viral_videos_data}}

TRENDING TOPICS:
{{google_trends_data}}

AUDIENCE PAIN POINTS:
{{reddit_data}}

BRAND PROFILE:
- Niche: {{niche}}
- Audience: {{target_audience}}
- Tone: {{tone}}
- Goal: {{goal}}
- Video length: {{length}} seconds

FOR EACH OF THE 30 VIDEOS GENERATE:
1. Hook (first 2-3 seconds ONLY — must stop scroll instantly)
2. Full word-for-word script with timestamps
   Structure: Hook → Problem/Surprise → Value → CTA
   Zero fluff. Every word earns its place.
3. Caption (algorithm-optimized, includes hook + CTA)
4. 7-10 hashtags (mix: 3 niche + 3 broad + 1-2 trending)
5. CTA type: comment bait / follow bait / link in bio / save this

RULES:
- Hook must create IMMEDIATE curiosity, shock, or emotion
- Scripts must work WITHOUT visuals (voiceover-first)
- Every video must end with engagement bait
- Optimal pacing: 1 new idea every 8-10 seconds maximum

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Videos | Apify Cost | InVideo Cost | Total |
|---|---|---|---|
| 10 videos | ~$0.25 | ~$10 | ~$10.25 |
| 30 videos | ~$0.60 | ~$25 | ~$25.60 |
| 90 videos (3 clients) | ~$1.75 | ~$70 | ~$71.75 |
| 300 videos (10 clients) | ~$5.50 | ~$220 | ~$225.50 |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**

> 🎬 **Produce all your videos with [InVideo AI](https://invideo.sjv.io/TBB) — free plan available**

---

## 🔗 Revenue Opportunities With This Skill

| Use Case | Revenue |
|---|---|
| **Social media agency** | $1,500–$5,000/month per client for 30 videos |
| **Personal brand builder** | Grow to 100K followers → brand deals + courses |
| **Faceless content channel** | $2K–$20K/month via creator fund + affiliate links |
| **UGC creator service** | Sell 10-video packs to brands for $500–$2,000 |
| **E-commerce content** | Product video ads repurposed as organic content |

---

## 📊 Why This Is The Ultimate Content Skill

| Feature | Hiring a Video Editor | **Viral Short-Form Factory** |
|---|---|---|
| Cost per video | $50–$200 | ~$0.85 |
| Time per video | 2–4 hours | Under 2 minutes |
| Trend research included | ❌ | ✅ |
| Viral hook analysis | ❌ | ✅ |
| Scripts + captions + hashtags | ❌ | ✅ |
| All 3 platforms optimized | ❌ | ✅ |
| 30-day calendar included | ❌ | ✅ |
| Scale to 300 videos/month | ❌ | ✅ |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Define your niche & run**  
Brand profile + goals. 30 videos produced and ready to post in one run.

---

## ⚡ Pro Tips to Go Viral Faster

- **Post every single day for 30 days** — the algorithm rewards consistency above all
- **Your hook is 80% of the result** — rewrite it 5 times before producing
- **Comment bait CTAs 3x your reach** — "Comment X for Y" triggers the algorithm
- **Cross-post on all 3 platforms** — same video, 3x the distribution, zero extra work
- **Reply to every comment in the first 30 minutes** — early engagement = algorithm boost
- **Repost your best video every 30 days** — new audience, same proven content

---

## 🏷️ Tags

`tiktok` `instagram-reels` `youtube-shorts` `short-form-video` `content-automation` `invideo` `apify` `viral-content` `faceless-channel` `social-media` `content-calendar` `ai-video`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
