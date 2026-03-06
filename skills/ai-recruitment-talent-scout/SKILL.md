---
name: 👥 AI Recruitment & Talent Scout Engine
description: Recruitment agencies charge $15,000–$30,000 per hire. In-house HR
  teams spend 23 days on average to fill a single position. This skill does the
  same work in under 10 minutes.
---

# 👥 AI Recruitment & Talent Scout Engine

**Slug:** `ai-recruitment-talent-scout`  
**Category:** HR / Talent Acquisition  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Input a job role + criteria. Get a **ranked shortlist of pre-qualified candidates** — scraped from LinkedIn, GitHub, and job boards — with AI-scored profiles, personalized outreach messages, and full contact details. Hire faster than any recruiter alive.

---

## 💥 Why This Skill Is a Goldmine on ClawHub

Recruitment agencies charge **$15,000–$30,000 per hire**. In-house HR teams spend **23 days on average** to fill a single position. This skill does the same work in **under 10 minutes**.

Every startup, scale-up, agency, HR consultant, and freelance recruiter is your target. That's one of the largest B2B markets on earth.

**What gets automated:**
- 🔍 Scrape **hundreds of matching candidate profiles** from LinkedIn, GitHub & job boards
- 🎯 AI-score each candidate against your exact criteria (0–100 fit score)
- 📊 Enrich profiles with skills, experience, location, availability signals
- 📬 Generate **hyper-personalized outreach messages** per candidate
- 🏆 Deliver a **ranked shortlist** of your top 10 candidates ready to contact
- 💡 Detect **passive candidates** — people not actively looking but open to opportunities

---

## 🛠️ Apify Actors Used

| Actor | ID | Purpose |
|---|---|---|
| LinkedIn Profile Scraper | `dev_fusion/linkedin-profile-scraper` | Candidate profiles, experience, skills |
| LinkedIn Jobs Scraper | `curious_coder/linkedin-jobs-scraper` | Active job seekers & recent movers |
| GitHub Scraper | `apify/github-scraper` | Top developers by tech stack & activity |
| Indeed Scraper | `misceres/indeed-scraper` | Candidates actively looking for work |
| Hunter.io Email Finder | `misceres/prospectin-email-finder` | Verified professional email addresses |
| Google Search Scraper | `apify/google-search-scraper` | Personal websites, portfolios, press mentions |

---

## ⚙️ Full Workflow

```
INPUT: Job title + required skills + location + seniority + compensation range
        ↓
STEP 1 — Multi-Platform Candidate Sourcing
  └─ LinkedIn: profiles matching title + skills + location
  └─ GitHub: developers ranked by activity, stars, tech stack
  └─ Indeed: active job seekers with matching experience
        ↓
STEP 2 — Profile Enrichment
  └─ Current role, company, tenure, career trajectory
  └─ Skills detected, certifications, education
  └─ Availability signals (recent job change? open to work badge?)
        ↓
STEP 3 — AI Fit Scoring (0–100 per candidate)
  └─ Skills match vs requirements
  └─ Career trajectory (growing or stagnating?)
  └─ Seniority level alignment
  └─ Location & remote compatibility
  └─ Culture fit signals (company types, industries worked in)
        ↓
STEP 4 — Contact Details Extraction
  └─ Professional email (verified)
  └─ LinkedIn URL, GitHub, portfolio, personal site
        ↓
STEP 5 — Claude AI Generates Personalized Outreach
  └─ LinkedIn DM: short, specific, human — referencing their actual work
  └─ Email: 5-line max, compelling hook, clear opportunity
  └─ Follow-up message: for non-responders at Day 5
        ↓
OUTPUT: Ranked shortlist of top 10 candidates + full profiles + outreach messages
        (JSON / CSV / Notion-ready)
```

---

## 📥 Inputs

```json
{
  "job": {
    "title": "Senior Full-Stack Engineer",
    "required_skills": ["React", "Node.js", "PostgreSQL", "AWS"],
    "nice_to_have": ["TypeScript", "Docker", "GraphQL"],
    "seniority": "senior",
    "location": "London or Remote (EU timezone)",
    "remote": true,
    "compensation": "$90,000 - $130,000"
  },
  "company": {
    "name": "YourStartup",
    "stage": "Series A",
    "industry": "FinTech",
    "culture_keywords": ["fast-paced", "product-led", "no bureaucracy"]
  },
  "sourcing": {
    "platforms": ["linkedin", "github", "indeed"],
    "max_candidates": 100,
    "exclude_companies": ["Google", "Meta", "Amazon"],
    "min_experience_years": 4
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "search_summary": {
    "role": "Senior Full-Stack Engineer",
    "candidates_sourced": 94,
    "candidates_scored": 94,
    "shortlist_count": 10,
    "avg_fit_score": 81,
    "run_time_minutes": 7
  },
  "shortlist": [
    {
      "rank": 1,
      "fit_score": 96,
      "fit_label": "🔥 Exceptional Match",
      "name": "Alex Morgan",
      "current_role": "Full-Stack Engineer @ Revolut",
      "experience_years": 6,
      "location": "London, UK",
      "skills_matched": ["React", "Node.js", "PostgreSQL", "AWS", "TypeScript", "Docker"],
      "skills_missing": [],
      "availability_signal": "Liked 3 startup job posts in last 14 days — likely open to move",
      "github": {
        "url": "github.com/alexmorgan",
        "stars": 847,
        "top_repos": ["react-dashboard-kit", "node-auth-boilerplate"],
        "last_commit": "2 days ago",
        "activity_level": "🟢 Very Active"
      },
      "contact": {
        "linkedin": "linkedin.com/in/alex-morgan-dev",
        "email": "alex.morgan@gmail.com",
        "portfolio": "alexmorgan.dev"
      },
      "why_they_win": "6 years full-stack, currently at a FinTech scale-up (directly relevant), all required skills matched, highly active on GitHub with quality open-source work, showing passive job-seeking signals.",
      "outreach": {
        "linkedin_dm": "Hey Alex — saw your work on react-dashboard-kit, really clean architecture. We're building something similar at YourStartup (Series A FinTech, London) and looking for a senior full-stack engineer who can own the frontend infrastructure. Would love to share what we're working on — worth a quick chat?",
        "email_subject": "Senior Full-Stack role @ YourStartup — saw your GitHub work",
        "email_body": "Hi Alex,\n\nYour react-dashboard-kit repo caught my eye — exactly the kind of clean, scalable React work we need at YourStartup.\n\nWe're a Series A FinTech in London building [one-line pitch]. Looking for a Senior Full-Stack Engineer to own our core product infrastructure.\n\nStack: React, Node.js, PostgreSQL, AWS — your exact wheelhouse.\n\nComp: $90K-$130K + equity. Remote-friendly (EU timezone).\n\nWorth 20 minutes to hear more?\n\n[Your name]",
        "followup_day5": "Hey Alex — just circling back on this. Happy to share more details on what we're building if useful. No pressure either way!"
      }
    },
    {
      "rank": 2,
      "fit_score": 91,
      "fit_label": "🔥 Excellent Match",
      "name": "Sarah Chen",
      "current_role": "Full-Stack Developer @ Monzo",
      "experience_years": 5,
      "location": "Remote (UK-based)",
      "skills_matched": ["React", "Node.js", "PostgreSQL", "AWS", "TypeScript"],
      "skills_missing": ["Docker"],
      "availability_signal": "Updated LinkedIn profile 8 days ago — strong signal",
      "contact": {
        "linkedin": "linkedin.com/in/sarah-chen-fullstack",
        "email": "sarah.chen.dev@gmail.com"
      },
      "why_they_win": "5 years at two top UK FinTechs, recently updated her profile (strong availability signal), missing only Docker which is nice-to-have only."
    }
  ],
  "talent_market_insights": {
    "avg_time_to_hire_this_role": "34 days (market average)",
    "candidate_supply": "Medium — 94 matches found, market not oversaturated",
    "avg_compensation_market": "$85,000 - $125,000 (your offer is competitive)",
    "top_companies_to_poach_from": ["Revolut", "Monzo", "Wise", "Starling Bank"],
    "best_outreach_day": "Tuesday or Wednesday morning",
    "response_rate_benchmark": "18-24% for cold LinkedIn DMs in this role"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class technical recruiter and talent acquisition specialist.

CANDIDATE DATA FROM SCRAPING:
{{candidates_raw_data}}

JOB REQUIREMENTS:
- Title: {{job_title}}
- Required skills: {{required_skills}}
- Nice to have: {{nice_to_have}}
- Seniority: {{seniority}}
- Location: {{location}}
- Compensation: {{compensation}}

COMPANY PROFILE:
- Name: {{company_name}}
- Stage: {{company_stage}}
- Industry: {{industry}}
- Culture: {{culture_keywords}}

FOR EACH CANDIDATE GENERATE:
1. Fit score (0–100) based on: skills match (40%), experience (25%),
   career trajectory (20%), availability signals (15%)
2. Fit label: Exceptional (90+) / Excellent (80+) / Good (65+) / Weak (<65)
3. Skills matched vs missing
4. Availability signal (any passive job-seeking behavior detected)
5. Why they win — 2-sentence honest assessment
6. Outreach package:
   - LinkedIn DM (max 80 words, reference something specific about their work)
   - Email (subject + 5-line body max, mention their exact skills + your stack)
   - Day 5 follow-up (2 lines, zero pressure)

ALSO GENERATE:
- Talent market insights: supply level, avg compensation, best companies to source from
- Recommended outreach timing

RANK by fit score. Return top 10 only.
OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Searches | Apify CU | Cost | Candidates Sourced |
|---|---|---|---|
| 1 role | ~55 CU | ~$0.55 | 100 candidates |
| 5 roles | ~270 CU | ~$2.70 | 500 candidates |
| 20 roles | ~1,080 CU | ~$10.80 | 2,000 candidates |
| 100 roles | ~5,400 CU | ~$54 | 10,000 candidates |

> 💡 **$5 free Apify credits on signup** = your first 9 full recruitment searches completely free.  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

---

## 🔗 Who Makes a Fortune With This Skill

| User | Use Case | Revenue Potential |
|---|---|---|
| **Recruitment Agency** | Automate candidate sourcing for clients | $15K–$30K per placement |
| **HR Freelancer** | Offer sourcing-as-a-service at $500–$2K/role | $10K–$30K/month |
| **Startup Founder** | Hire without paying a recruiter | Save $20K per hire |
| **HR Consultant** | Bundle into talent strategy package | $5K–$15K per engagement |
| **Headhunter** | Source passive candidates 10x faster | 3x more placements/month |
| **VC-backed Startup** | Rapid team scaling post-funding | Hire 10 people in 30 days |

---

## 📊 Why This Destroys LinkedIn Recruiter ($9,000/year)

| Feature | LinkedIn Recruiter | **AI Talent Scout Engine** |
|---|---|---|
| Search LinkedIn profiles | ✅ | ✅ |
| Search GitHub for developers | ❌ | ✅ |
| Search Indeed job seekers | ❌ | ✅ |
| AI fit scoring (0–100) | ❌ | ✅ |
| Personalized outreach per candidate | ❌ | ✅ |
| Availability signal detection | ❌ | ✅ |
| Talent market insights | ❌ | ✅ |
| Annual cost | $9,000/year | ~$0.55/search |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Sign up free → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Go to: **Settings → Integrations → API Token**

**Step 2 — Define your ideal candidate**  
Job title, must-have skills, location, seniority, compensation range.

**Step 3 — Run & get your shortlist**  
Top 10 ranked candidates with outreach messages ready in under 10 minutes.

---

## ⚡ Pro Tips to Hire Faster & Better

- **Target candidates at your #2 competitor** — they know the industry, proven skills, motivated to move
- **GitHub activity = best signal for developers** — daily commits beat any resume claim
- **Profile updated in last 30 days = strong availability signal** — prioritize these first
- **Send outreach Tuesday–Thursday morning** — 40% higher response rates than Monday/Friday
- **Always reference something specific** — mention their repo, their company, their last post — generic DMs get ignored
- **Follow up exactly once at Day 5** — no more, no less

---

## 🏷️ Tags

`recruitment` `talent-acquisition` `hr` `sourcing` `linkedin` `github` `headhunting` `apify` `ai-recruiting` `passive-candidates` `startup-hiring` `talent-scout`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + Claude AI*
