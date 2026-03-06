# 🚀 Rankscale GEO Analytics for OpenClaw

![Version](https://img.shields.io/badge/version-v1.0.1-blue) ![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen) ![Platform](https://img.shields.io/badge/platform-OpenClaw-purple)

## The Best AI Rank Tracker & Generative Engine Optimization Tool

**Real-time visibility analytics across ChatGPT, Perplexity, Gemini, Claude, DeepSeek, Mistral, and more.**

Stop guessing where your brand shows up in AI answers. Rankscale GEO Analytics gives you deep, actionable visibility intelligence across all tracked AI engines — so you can optimize your content, protect your reputation, and dominate the AI-driven search landscape before your competitors even know it exists.

---

## ✨ Features at a Glance

- 📊 **Engine Strength Profile** — Visibility heatmap across tracked AI engines showing where you're strong and where you're invisible
- 🎯 **Content Gap Analysis** — Identify topics with low AI coverage and get concrete recommendations to fill those gaps
- 🛡️ **Reputation Score** — Brand health score (0–100) with full sentiment analysis across AI-generated responses
- 📈 **Engine Gainers & Losers** — Track visibility changes per engine over time to spot trends early
- ⚠️ **Sentiment Shift Alerts** — Detect emerging sentiment trends and surface risk keyword clusters before they escalate
- 🔗 **Citation Intelligence Hub** — Authority ranking, citation gap analysis, and PR opportunities where your brand should be cited but isn't
- 📋 **Default GEO Report** — Quick, comprehensive visibility overview to baseline your current standing

---

## 💡 Why This Skill?

### What is GEO?

**Generative Engine Optimization (GEO)** is the discipline of optimizing your brand, content, and digital presence so that AI-powered engines — like ChatGPT, Perplexity, Gemini, and Claude — surface you prominently and positively when users ask relevant questions. GEO is the next frontier beyond traditional SEO. As more users turn to AI for answers, your visibility in generated responses directly impacts brand discovery, trust, and revenue.

### Why Rankscale GEO Analytics?

- **Best-in-class GEO analytics** — Purpose-built for the AI era, not bolted onto legacy SEO tooling
- **Comprehensive engine coverage** — Track across all major AI engines:
  
  **GUI Engines (Live Browser):**
  - Google AI Overview
  - Google AI Mode
  - Google Gemini
  - ChatGPT
  - Perplexity
  - xAI Grok
  - Bing Copilot
  
  **API Engines:**
  - Perplexity Sonar / Sonar-Pro / Sonar-Reasoning-Pro
  - OpenAI GPT-5
  - Google Gemini 2.5 Flash, 3.0 Pro
  - Anthropic Claude 4.5 Haiku (3.5 Haiku deprecated)
  - DeepSeek V3
  - Mistral Large

- **Actionable insights, not just data** — Every report tells you what to do next, not just what's happening
- **Citation intelligence** — Discover the gold nuggets: where your brand *should* be cited but isn't, with direct PR opportunities
- **Brand reputation tracking** — Know your sentiment score before a crisis hits, not after
- **PR opportunity discovery** — Find gaps in your citation profile and turn them into press coverage

---

## 🏁 Getting Started

### Step 1 — Create Your Rankscale Account (PRO account required)

Head to [https://rankscale.ai/dashboard/signup](https://rankscale.ai/dashboard/signup) and create your account. Takes under 2 minutes.

> **⚠️ PRO account required.** Trial accounts do **not** have REST API access and cannot be used with this skill. You must be on a PRO plan (or higher) for API access to function.

### Step 2 — Set Up Your Brand in Dashboard

Before using this skill, **set up a brand and configure tracking in your Rankscale dashboard:**

1. Log in to [https://rankscale.ai/dashboard](https://rankscale.ai/dashboard)
2. Click **"Add Brand"** or select an existing brand
3. Configure tracking prompts:
   - Add search queries/keywords you want to track (e.g., your product name, use cases, solutions)
   - Select which AI engines you want to monitor (GUI, API, or both)
   - Set tracking frequency (daily, weekly, etc.)
4. Let the system run initial scans to populate baseline metrics (24–48 hours)
5. Once data is available, use the skill commands below

> **Why this matters:** The skill pulls visibility data from tracked searches. Without prompts configured, there's no data to analyze.

### Step 3 — Activate REST API Access

REST API access is required for this skill. Contact [support@rankscale.ai](mailto:support@rankscale.ai) to request API activation for your account. The team is fast and happy to help.

### Step 4 — Configure Credentials in OpenClaw Gateway

Add to your Gateway config:
```
RANKSCALE_API_KEY=rk_xxxxxxxx_<brandId>
RANKSCALE_BRAND_ID=<brandId>
```

> **Tip:** If your API key includes the brand ID (format: `rk_<hash>_<brandId>`), it will be extracted automatically.

### Step 5 — Ask Your Assistant!

Once configured, just talk to your AI assistant. Examples below.

---

## 🔍 What to Ask Your Assistant

The skill activates on natural language. Just ask:

### Default GEO Report
```
"Give me my Rankscale GEO overview for this week"
"Run a geo report"
"Show me my AI visibility"
```

**Returns:**
- GEO Score (0–100) with week-over-week change
- Citation rate vs. industry average
- Sentiment breakdown (Positive/Neutral/Negative)
- Top AI search terms where your brand appears
- Up to 5 prioritised insights (CRIT/WARN/INFO)

---

### Engine Strength Profile
```
"Which AI engines am I weakest on?"
"Show my engine strength profile"
"What's my visibility per AI engine?"
```

**Returns:**
```
ENGINE STRENGTH PROFILE — Brand: Acme Corp
────────────────────────────────────────
ChatGPT      ████████░░  82%  [+4 vs last week]
Perplexity   ███████░░░  74%  [+2 vs last week]
Gemini       ██████░░░░  61%  [stable]
Claude       █████░░░░░  53%  [-3 vs last week]
DeepSeek     ██░░░░░░░░  23%  [-8 vs last week] ⚠️
────────────────────────────────────────
STRONGEST:   ChatGPT (82%)
WEAKEST:     DeepSeek (23%) — priority focus
```

---

### Content Gap Analysis
```
"What topics should I be writing about?"
"Run a content gap analysis"
"Where am I losing to competitors in AI search?"
```

**Returns:**
```
CRITICAL GAPS (you missing entirely)
────────────────────────────────────
1. "best project management for remote teams"
   Cited: Notion, Asana, Monday.com
   Your share: 0%  |  Opportunity: 94/100

2. "project management pricing comparison"
   Cited: ClickUp, Trello, Asana
   Your share: 0%  |  Opportunity: 88/100

ACTION: Publish comparison + guide content
for gaps 1–3. Est. impact: +8–15 GEO pts.
```

---

### Reputation Score
```
"What's our brand reputation score?"
"Is our brand sentiment improving?"
"Show me our reputation across AI engines"
```

**Returns:**
```
Reputation Score: 78/100 (Good)
────────────────────────────────
Positive:    61%  ✅
Neutral:     26%
Negative:    13%  ⚠️

Sentiment Trend: Slightly positive (+2pts vs last week)
```

---

### Engine Gainers & Losers
```
"Which engines are we winning on?"
"Show engine movers"
"What's our visibility trend per engine?"
```

**Returns:**
```
⬆️  TRENDING UP
    ChatGPT       +4pts
    Perplexity    +2pts

⬇️  TRENDING DOWN
    DeepSeek      -8pts
    Gemini        -2pts
```

---

### Sentiment Shift Alerts
```
"Any sentiment risks I should know about?"
"Check for sentiment shift alerts"
"Are there emerging negative keywords?"
```

**Returns:**
```
⚠️ SENTIMENT SHIFT DETECTED (last 7 days)
Current score: 78/100 (down from 80)

Risk Keywords Emerging:
  → "slow support" (3 mentions, Perplexity)
  → "pricing concerns" (2 mentions, ChatGPT)

Recommendation: Address support perception
in content and FAQs.
```

---

### Citation Intelligence Hub
```
"Find PR opportunities for my brand"
"Show citation gaps"
"Where should I be cited but aren't?"
```

**Returns:**
```
🔗 CITATION INTELLIGENCE HUB
Your brand missing from 8 high-authority sources

Top PR Opportunities:
  → TechCrunch "Best CRM tools" (DA 94) — not cited
  → Forbes "Top SaaS 2025" (DA 96) — not cited
  → G2 comparison page (DA 91) — partially cited

Recommended outreach: 3 contacts identified
```

---

## 📚 Full Documentation

For complete trigger patterns and advanced options:

- [USAGE.md](./USAGE.md) — Complete list of all trigger patterns, flags, and detailed feature guide
- [SKILL.md](./SKILL.md) — Skill documentation and architecture overview

---

## 🤝 Support & Feedback

We're here for you. Seriously.

- **Email:** [support@rankscale.ai](mailto:support@rankscale.ai) — our team responds fast and loves helping users get the most out of GEO analytics
- **Dashboard:** [https://rankscale.ai/dashboard](https://rankscale.ai/dashboard) — manage your account, API keys, brands, and tracking configuration

Got a feature request? Found a bug? Just want to share what you built? Reach out — we genuinely want to hear from you.

---

## 🌐 About Rankscale

[Rankscale](https://rankscale.ai) is the leading platform for Generative Engine Optimization analytics. As AI-powered engines become the primary way people discover information, products, and brands, traditional SEO is no longer enough. Rankscale gives you the visibility data, reputation intelligence, and actionable insights you need to thrive in the AI-first world — tracking your brand presence across all major engines, surfacing citation gaps, monitoring sentiment shifts, and helping you build a stronger, more authoritative digital footprint where it counts most: inside the AI answers your customers are already reading.

---

## 📄 License & Contributing

This OpenClaw skill is provided as part of the Rankscale ecosystem.

- **License:** MIT — use it, fork it, build on it
- **Contributing:** PRs and improvements welcome. Open an issue or email [support@rankscale.ai](mailto:support@rankscale.ai) to discuss
- **Versioning:** Follows [Semantic Versioning](https://semver.org/) — current release is v1.0.1

---

*Built with ❤️ for the GEO-forward era. Track smarter. Rank better. Win the AI landscape.*
