---
name: TikTok Content Pipeline — OpenClaw Skill
description: Automated TikTok carousel content generation, publishing,
  scheduling, and analytics-driven optimization for any niche.
---

# TikTok Content Pipeline — OpenClaw Skill

Automated TikTok carousel content generation, publishing, scheduling, and analytics-driven optimization for any niche.

## Overview

This skill provides a complete content pipeline for TikTok accounts. It handles:
- **Content Generation** — AI-generated carousel slides with hooks, CTAs, and keyword overlays
- **Smart Scheduling** — Research-backed posting times with account-age-aware frequency
- **Publishing** — Post to TikTok via Postiz API (supports drafts, scheduled posts, multi-platform)
- **Analytics & Optimization** — Track performance, diagnose issues, auto-implement improvements

## Required Credentials

| Credential | Purpose | How to Obtain |
|---|---|---|
| **Postiz API Key** | Publishing & analytics via Postiz CLI | Sign up at postiz.com → Settings → API Keys |
| **TikTok Integration ID** | Links your TikTok account to Postiz | Postiz dashboard → Integrations → Add TikTok |

### Credential Storage (Important)

**Recommended:** Set `POSTIZ_API_KEY` as an environment variable (e.g. in `~/.zshrc` or `~/.bashrc`) rather than storing it in config files. The pipeline checks for this env var first.

**Alternative:** Store in `accounts/<your-account>/config.json` under `postiz.apiKey`. If using this approach, ensure the file is not committed to version control (add to `.gitignore`).

The Integration ID is account-specific and stored in per-account `config.json`.

### Security Notes

- This skill executes the `postiz` CLI via shell commands. All arguments are escaped to prevent injection.
- The skill writes files only within its own `accounts/` and `output/` directories.
- `auto-improve` mode can modify account configs and auto-post — test on a throwback account first.
- Run `npm audit` after installing dependencies to check for known vulnerabilities.

## Quick Setup

1. Set your Postiz API key: `export POSTIZ_API_KEY="your-key-here"`
2. Copy `config.example.json` to `accounts/<your-account>/config.json`
3. Fill in your TikTok integration ID
4. Create or adapt a template in `templates/` for your niche
5. Run: `node cli.js create <account> --template <template-name>`

See `SETUP.md` for the full setup guide.

---

## How to Use This Skill

### 1. Create a New Account

```bash
node cli.js create my-brand --template example-nostalgia
```

This copies the template into `accounts/my-brand/` and sets `createdAt` to now.

### 2. Configure the Account

Edit `accounts/my-brand/config.json`:

```json
{
  "account": { "name": "my-brand", "handle": "@mybrand", "niche": "your-niche", "createdAt": "2026-01-15T00:00:00Z" },
  "postiz": { "apiKey": "YOUR_KEY", "integrationId": "YOUR_TIKTOK_ID" },
  "posting": { "timezone": "Europe/London" }
}
```

Or use the CLI:
```bash
node cli.js config my-brand --handle @mybrand --integration-id YOUR_ID --api-key YOUR_KEY
```

### 3. Generate Content

```bash
node cli.js generate my-brand --type showcase
node cli.js generate my-brand --type showcase --post  # Generate and post as draft
```

The generator uses the template's `generator.js` to create carousel slides, applies hooks from config, adds keyword overlays for TikTok SEO, and outputs to `accounts/my-brand/output/`.

### 4. Check the Posting Schedule

```bash
node cli.js schedule my-brand          # This week's schedule
node cli.js schedule my-brand --next   # Next optimal posting slot
```

The scheduler automatically adjusts frequency based on account age:
- **Days 0-24**: Daily posting (building momentum)
- **Days 25-30**: Taper from 7 → 4 posts/week
- **Day 31+**: 3-4 posts/week on optimal days

### 5. Run Analytics

```bash
node cli.js analytics my-brand --days 7
node cli.js analytics my-brand --days 7 --auto-improve  # Auto-implement fixes
```

---

## Research-Backed Viral Mechanics

These findings are baked into the framework's scheduling, optimization, and content scoring:

### Algorithm Priority Signals
1. **Watch time & completion rate** — most critical signal. 80%+ completion = 5x reach.
2. **First 3-second hook** — determines whether content gets distributed at all.
3. **Shares** — strongest engagement signal for virality.
4. **Saves** — growing importance. 15%+ save-to-view = high-value content.
5. **Comment engagement** — quality conversations > generic comments.

### Posting Strategy
- **3-4 posts/week** is optimal for established accounts (NOT 3/day — that hurts reach)
- **Best days**: Wednesday, Tuesday, Thursday
- **Best times**: Tue 5pm, Wed 2-5pm, Thu 3-5pm
- **New accounts**: Post daily for first 30 days to build momentum
- **Max 1 post/day** for established accounts (2/day max for new accounts)

### Carousel Advantages
- **3x more saves** than standard video
- **40% longer dwell time** when users engage
- **Lower production barrier** — slides are easier to produce than video
- **5-7 slides optimal** for maintaining attention
- **First slide is everything** — must hook immediately

### Hook Patterns That Work
| Type | Example | Avg Engagement |
|------|---------|---------------|
| Contradiction | "Everyone thinks X, but actually..." | 9%+ |
| Challenge | "If you used X, you had no skill 😂" | 11%+ |
| Gatekeeping | "Only real ones remember..." | 8%+ |
| POV | "POV: You just discovered..." | 7%+ |
| Nostalgia | "Remember this? 🔥" | 6%+ |
| Question | "Would you do this? Yes or no 👇" | 8%+ |

### Content Scoring
The ViralOptimizer scores content before posting (0-100):
- **Hook quality** (40% weight) — length, power words, emoji, question format
- **Structure** (30% weight) — slide count, audio, format
- **Engagement potential** (30% weight) — CTA presence, opinion-split, hashtag count

Verdicts:
- 80+ = 🔥 HIGH VIRAL POTENTIAL — Post immediately
- 65+ = ✅ GOOD — Ready to post
- 50+ = ⚠️ DECENT — Consider optimizing
- 35+ = 🔧 NEEDS WORK — Apply suggestions
- <35 = ❌ LOW POTENTIAL — Rethink approach

---

## Diagnostic Matrix

When analyzing post performance, use this matrix to decide what to fix:

| Views | Engagement | Diagnosis | Action |
|-------|-----------|-----------|--------|
| High (>1000) | High (>5%) | **SCALE** | Create 3 variations of this content. Test same hook with different visuals. |
| High (>1000) | Low (<3%) | **FIX CTA** | Hook is working — add stronger call-to-action. Add opinion-split or challenge. |
| Low (<500) | High saves (>10%) | **FIX HOOK** | Content converts — needs better opening hook. Test trending audio. Stronger first-slide text. |
| Low (<500) | Low (<3%) | **FULL RESET** | Try radically different format. Research top creators in niche. Test different posting time. |

### Key Thresholds
| Metric | Target | Viral | Poor |
|--------|--------|-------|------|
| Completion rate | 80% | 90% | 40% |
| Save-to-view ratio | 15% | 25% | 3% |
| Share rate | 8% | 15% | 2% |
| Comment rate | 5% | 10% | 1% |
| Profile visit rate | 12% | 20% | 3% |
| Follower conversion | 8% | 15% | 2% |

---

## Creating a Custom Template

Templates define the content types, hooks, hashtags, and generation logic for a niche.

### Template Structure
```
templates/your-niche/
├── config.json      # Content types, hooks, hashtags, settings
├── generator.js     # Content generation logic (extends ContentGenerator)
└── README.md        # Template documentation
```

### config.json Required Fields
```json
{
  "account": { "template": "your-niche", "niche": "Your Niche" },
  "content": {
    "types": {
      "your-content-type": { "description": "...", "slides": 6 }
    },
    "hashtagSets": {
      "default": ["#yourniche", "#fyp"]
    }
  },
  "hooks": {
    "your-content-type": ["Hook text 1", "Hook with {placeholder} 2"]
  },
  "posting": { "timezone": "Europe/London" }
}
```

### generator.js Pattern
```javascript
const ContentGenerator = require('../../core/ContentGenerator');

class YourNicheGenerator extends ContentGenerator {
  getSupportedTypes() {
    return Object.keys(this.config.content.types);
  }

  async _generateContent(contentType, options, outputDir) {
    this._ensureOutputDir(outputDir);
    const hook = this.getSlide1Hook(contentType, options);
    // Generate slides using sharp/canvas/ImageMagick
    // Return { slides: [...paths], hook: hook.text, caption: '...' }
  }
}

module.exports = YourNicheGenerator;
```

---

## Architecture

```
tiktok-content-pipeline/
├── cli.js                    # Universal CLI
├── core/
│   ├── ContentGenerator.js   # Abstract base for content generation
│   ├── Publisher.js          # Postiz API integration
│   ├── PostingScheduler.js   # Smart scheduling engine
│   ├── ViralOptimizer.js     # Content scoring & optimization
│   └── AnalyticsEngine.js    # Performance tracking & insights
├── accounts/                 # Per-account configs & output (created at runtime)
└── templates/                # Niche templates
    └── example-nostalgia/    # Example template to fork
```

### Core Components

- **ContentGenerator** — Abstract base class. Subclass it per niche. Handles hooks, question hooks, keyword overlays, placeholder replacement.
- **Publisher** — Posts to TikTok (and other platforms) via Postiz CLI. Handles media upload, scheduling, draft mode, and post metadata saving.
- **PostingScheduler** — Account-age-aware scheduling. Knows optimal days/times from research. Supports weekly schedule generation and overdue detection.
- **ViralOptimizer** — Pre-post content scoring. Post-performance diagnostic matrix. Hook pattern library with engagement-weighted selection.
- **AnalyticsEngine** — Pulls metrics from Postiz API. Generates reports with alerts, opportunities, and auto-implementable actions.
