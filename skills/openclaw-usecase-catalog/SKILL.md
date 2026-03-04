---
name: usecase-catalog
description: "Comprehensive catalog of what people are doing with OpenClaw. Covers 15+ categories with real examples, sources, and inspiration. Use when asked about OpenClaw use cases, what others are building, project ideas, or 'what can OpenClaw do'. Triggers on: use cases, ideas, inspiration, what people do, showcase, examples."
---

# OpenClaw Use Cases Catalog

A curated reference of real-world OpenClaw use cases gathered from Twitter/X, Reddit, blogs, GitHub, and community showcases. Updated 2026-02-04.

## How to Use

When My Lord asks about use cases or wants inspiration:

1. Reference the catalog below and `findings/` directory for past discoveries
2. Search the web for fresh examples (Twitter/X, Reddit, Discord, blogs)
3. Save new findings to `findings/YYYY-MM-DD.md` with structured format
4. Git commit and push to `{github_org}/openclaw-skill-usecases`

### Saving Findings (Bilingual)

After each invocation that discovers new use cases, append to (or create) `findings/YYYY-MM-DD.md`.
**All findings MUST be bilingual** — write both Chinese and English in the same entry. Chinese first, then English. This makes it easier for My Lord to read in his native language while keeping English for reference and searchability.

```markdown
# Findings / 发现 - YYYY-MM-DD

## HH:MM PST

### [中文标题] / [English Title] — [Category/类别]
- **来源/Source**: [URL or @handle]
- **平台/Platform**: [WhatsApp/Telegram/Discord/etc.]
- **描述/Description**:
  - 🇨🇳 中文描述
  - 🇺🇸 English description
- **亮点/Why interesting**:
  - 🇨🇳 中文说明为什么有趣
  - 🇺🇸 English explanation of why it's notable
```

Then commit and push:
```bash
cd /path/to/skills/openclaw-usecases
git add findings/ && git commit -m "findings: YYYY-MM-DD" && git push
```

---

## 1. Messaging & Communication Automation

- **Inbox Zero**: Scan emails, archive spam, summarize high-priority items into daily morning briefings. Auto-create Gmail filters. (@andrewjiang: "Helped me clean up hundreds of emails. Inbox 0. Then setup a weekly cron job. All on WhatsApp.")
- **iMessage/SMS Monitoring**: Scan text threads every 15 min, detect promises ("I'll review this tomorrow"), auto-create calendar holds. (@brandon.wang)
- **Group Chat Summarization**: Daily summaries of high-volume WhatsApp/Signal groups (100+ msgs/day). Pick out interesting topics, skip noise.
- **Auto-Reply Drafting**: Draft email/message responses for review before sending.

## 2. Calendar & Scheduling

- **Morning Briefings**: 8pm nightly summary of next day's calendar -- meetings, prep notes, commute times. (@benemredoganer: "Daily calendar briefs, creates tasks in Basecamp via voice, preps me for meetings.")
- **Smart Conflict Detection**: When texting plans, auto-create "hold" events on calendar to prevent double-booking.
- **Dentist/Doctor Booking**: Log into portal, find slots matching calendar availability + location proximity, confirm before booking. (@brandon.wang)
- **Cross-Calendar Intersection**: Check both partners' calendars to find mutual free evenings for dinner reservations.

## 3. Remote Coding & Development

- **Phone-Based Development**: Build and deploy code projects from WhatsApp/Telegram while on the go. (@christinetyip)
- **Site Rebuilds from Bed**: Full website migration (Notion to Astro, 18 posts, DNS to Cloudflare) via Telegram while watching Netflix. (@davekiss)
- **Auto-Deployment**: "Deploy the latest commit to staging" -- runs git commands, SSH scripts, handles the pipeline.
- **Code Refactoring**: Scan directories, identify messy code, propose refactored versions.
- **Server Monitoring**: Periodic htop/disk checks, alert via Telegram when under load.
- **GitHub Workflow**: Manage Issues, PRs, CI runs, auto-assign/label/close via webhooks.

## 4. Price Monitoring & Shopping

- **Complex Price Alerts**: 30+ simultaneous alerts on hotels, Airbnbs, products. Supports reasoning criteria like "pullout bed OK if not in same room as another bed." Reviews listing photos to verify. (@brandon.wang)
- **Hotel/Airbnb Tracking**: Check prices every few hours, notify on changes. Can evaluate subjective criteria (room vibe, renovation quality).
- **Package Tracking**: USPS/FedEx tracking numbers, daily progress updates, flags stuck-in-transit items.
- **Grocery Price Comparison**: Compare prices on Amazon via browser automation, suggest best options.

## 5. Smart Home & IoT

- **Home Assistant Integration**: Full-home smart control via natural language. (@WolframRvnwlf: "OpenClaw truly is next level... my sassy AI assistant Amy is finally running persistently on my Home Assistant box.")
- **Air Purifier / Device Control**: Discover and control Winix, Philips Hue, Elgato devices. (@antonplex)
- **Scene Automation**: Away/Home/Sleep modes -- lights, AC, security based on WiFi proximity and sleep data.
- **Complete Life Integration**: Emails + Home Assistant + homelab SSH + todo lists + shopping list, all via single Telegram chat. (@acevail_)

## 6. Restaurant & Booking

- **Resy/OpenTable Automation**: Log in (including 2FA from texts), browse availability page by page, intersect with your + partner's calendar, suggest options. (@brandon.wang)
- **Form Filling**: Fill out vendor forms, questionnaires. Workshopes answers back and forth, unchecks marketing emails automatically.
- **Flight Check-in**: Auto check-in for flights, generate packing lists based on destination weather.

## 7. Health & Fitness Tracking

- **Fitness Coach**: Analyze Garmin/Apple Health data. "You only slept 5 hours last night; maybe skip heavy cardio today."
- **Medical Lab Analysis**: Feed blood test PDFs for plain-English explanations.
- **Wearable Data Dashboard**: Steps, sleep quality, heart rate summaries on demand.

## 8. Household & Life Management

- **Freezer Inventory**: Take photos of freezer contents, AI parses items/quantities, updates Notion list, removes stocked items from grocery list. (@brandon.wang)
- **Grocery List from Recipes**: Screenshot a recipe, ingredients auto-organized into Apple Reminders. Dedupes and combines ("2 carrots becomes 3").
- **Todo Creation with Context**: Photo of running shoes at REI -> todo with brand, model, size, product URL auto-found.
- **Travel Planning**: Search flights, generate packing lists based on weather, book accommodations.

## 9. Digital Agency / Business

- **One-Person Agency**: AI "Chief of Staff" coordinating all ops -- SEO client monitoring, email triage, content creation, Shopify management, overnight PRs for morning review. (@openclaw.com.au)
- **Project Management**: Connect code, Linear, WhatsApp history, and Obsidian for seamless PM workflow. (@crossiBuilds)
- **Content Creation Pipeline**: Blog posts, meta descriptions, reports, social media content.
- **24/7 Accountability Partner**: Daily reminders, GitHub tracking, weekly accountability nudges for goals. (@tobi_bsf)

## 10. AI Phone & Voice

- **Phone Call Assistant**: Make and receive phone calls on your behalf. (@steipete)
- **Voice-to-Text Processing**: Transcribe voice messages, act on content.
- **Voice-Controlled Tasks**: Create tasks in Basecamp via voice commands.

## 11. Full-Stack Productivity Hub

- **Single Chat Command Center**: Control Gmail, Calendar, WordPress, Hetzner servers from Telegram. (@Abhay08: "controlling Gmail, Calendar, WordPress, Hetzner from Telegram like a boss.")
- **Perfect Memory Assistant**: Remembers everything across all conversations, learns preferences over time. (@darrwalk)
- **Workflow Self-Documentation**: Auto-writes human-readable workflow descriptions to Notion with version control diffs. (@brandon.wang)

## 12. Self-Creating Skills & Integrations

- **On-Demand Skill Creation**: "I wanted to automate Todoist and OpenClaw created a skill for it on its own, all within Telegram." (@iamsubhrajyoti)
- **ClawHub Ecosystem**: 3,000+ community skills on clawhub.ai. 1,715+ curated in awesome-openclaw-skills repo.
- **Category Breakdown**: Web/Frontend (46), Coding Agents (55), Git/GitHub (34), DevOps/Cloud (144), Browser Automation (69), Image/Video (41), Apple Apps (32), Search/Research (148), CLI Utilities (88), Marketing/Sales (94), Productivity (93), AI/LLMs (159), Notes/PKM (61), Smart Home (50), Communication (58), Speech (44), Health/Fitness (35), Shopping (33), Calendar (28), PDF/Documents (35), Security (21), Gaming (7).

## 13. Content & Media

- **WeChat公众号 Article Illustration**: Auto-generate scrapbook-style infographics for articles using GPT-4o or GLM-Image. (Our own suwin-illustrator skill)
- **YouTube Transcription**: yt-dlp + Whisper API for video transcription and note-taking.
- **News Aggregation**: Aggregate 8+ sources (Hacker News, GitHub Trending, Product Hunt). Daily tech briefings.
- **Podcast Summarization**: Extract transcripts and key points from audio content.
- **Remotion Video**: Programmatic video creation with React + Remotion framework.

## 14. AI-Powered Research

- **Deep Research**: Multi-source web research, synthesized reports.
- **Academic Paper Analysis**: Parse PDFs, explain findings, compare methodologies.
- **Competitive Intelligence**: Monitor competitor websites, pricing changes, product updates.

## 15. Security & Privacy

- **Local-First Architecture**: All data stored locally, keys never sent to third parties.
- **Docker Isolation**: Sandboxed execution prevents system damage.
- **Human-in-the-Loop**: Sensitive commands require explicit approval.
- **Dedicated Account Strategy**: Use burner accounts for integrations to limit blast radius.

---

## Sources

| Source | URL |
|--------|-----|
| Official Showcase | getclawdbot.com/showcase |
| OpenClaw Wiki | openclawwiki.org/blog/openclaw_clawdbot-usage-use-cases |
| Medium (10 Use Cases) | medium.com/@balazskocsis/10-clawdbot-use-cases |
| Brandon Wang Deep Dive | brandon.wang/2026/clawdbot |
| Awesome Skills (1715+) | github.com/VoltAgent/awesome-openclaw-skills |
| Extension Ecosystem | help.apiyi.com/en/openclaw-extensions-ecosystem-guide-en |
| Digital Agency Case | openclaw.com.au/use-cases |
| r/openclaw | reddit.com/r/openclaw |
| r/OpenClawCentral | reddit.com/r/OpenClawCentral |
| ClawHub Registry | clawhub.ai/skills |

## Stats (Feb 2026)

- GitHub Stars: 135K+
- ClawHub Skills: 3,000+ published, 1,715+ curated
- Messaging Platforms: 12 (WhatsApp, Telegram, Discord, Slack, iMessage, Signal, Google Chat, Teams, Matrix, BlueBubbles, Zalo, WebChat)
- Discord Community: 8,900+ members
- Subreddits: 5+ (r/openclaw, r/OpenClawCentral, r/openclawpirates, r/myclaw, r/OpenClawDevs)
