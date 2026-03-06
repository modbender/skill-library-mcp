# Genviral Skill

An [OpenClaw](https://openclaw.ai) skill for the [Genviral](https://genviral.io) Partner API.

Generates slideshows, posts them across platforms, tracks what performs, and adjusts strategy based on real data. Every cycle makes the next one better.

## Supported Platforms

| Platform | Posting | Analytics | Notes |
|----------|---------|-----------|-------|
| **TikTok** | Yes | Yes | Slideshow carousels, videos. BYO or hosted accounts. |
| **Instagram** | Yes | Yes | Reels, stories, carousels, square/portrait/landscape posts. |
| **YouTube** | Yes | Yes | Shorts and standard video uploads. |
| **Facebook** | Yes | - | Posts, square posts, event covers. |
| **Pinterest** | Yes | - | Standard pins, square pins. |
| **LinkedIn** | Yes | - | Posts, square posts, company pages. |

Analytics (performance tracking, post metrics, account insights) is available for TikTok, Instagram, and YouTube.

## How It Works

The skill runs a closed loop:

1. **Generate** slideshows from a prompt + image pack (with deliberate image selection — no random picks)
2. **Review** every slide visually before anything gets posted (hard gate)
3. **Post** to connected accounts across any supported platform
4. **Track** performance through analytics endpoints
5. **Learn** what hooks, formats, and timing actually work
6. **Adapt** strategy weights, retire underperformers, double down on winners

## Quick Start

```bash
# Set your API key
export GENVIRAL_API_KEY="your_public_id.your_secret"

# See what accounts you have
./scripts/genviral.sh accounts

# Pull niche intelligence in one call
./scripts/genviral.sh trend-brief --keyword "indie hacker" --range 7d --limit 10

# List image packs
./scripts/genviral.sh list-packs

# Generate a slideshow (always pin images — see docs/api/packs.md)
./scripts/genviral.sh generate \
  --prompt "5 morning habits that changed my life" \
  --pack-id PACK_ID \
  --slides 5 \
  --slide-config-json '{"total_slides":5,"slide_types":["image_pack","image_pack","image_pack","image_pack","image_pack"],"pinned_images":{"0":"URL_0","1":"URL_1","2":"URL_2","3":"URL_3","4":"URL_4"}}'

# Render and post
./scripts/genviral.sh render --id SLIDESHOW_ID
./scripts/genviral.sh create-post \
  --caption "Caption with #hashtags" \
  --media-type slideshow \
  --media-urls "url1,url2,url3,url4,url5" \
  --accounts ACCOUNT_ID

# Check performance
./scripts/genviral.sh analytics-summary --range 30d
```

## Installation

Clone into your OpenClaw skills directory:

```bash
cd /path/to/your/workspace/agent/skills
git clone https://github.com/fdarkaou/genviral-skill.git genviral
```

Requires: `bash` 4+, `curl`, `jq`, and a [Genviral](https://genviral.io) account with Partner API access.

## What's Inside

```
genviral/
  SKILL.md                  # Kernel: agent entry point, routing table, non-negotiable rules
  README.md                 # This file
  setup.md                  # Conversational onboarding guide
  defaults.yaml             # API config and defaults (no secrets here)

  docs/
    api/
      accounts-files.md     # accounts, upload, list-files
      posts.md              # create-post, update-post, retry, list, get, delete
      slideshows.md         # generate, render, review, update, text styles, fonts
      packs.md              # pack CRUD + mandatory smart image selection workflow
      templates.md          # template CRUD, create-from-slideshow
      analytics.md          # analytics summary, posts, targets, refresh
      pipeline.md           # full content pipeline, performance loop, CTA testing
      errors.md             # error codes and troubleshooting

  workspace/                # Your instance data — never overwritten by updates
    content/
      scratchpad.md         # Working content plan and drafts
      calendar.json         # Upcoming planned posts
    context/
      product.md            # Product description, value props, target audience
      brand-voice.md        # Tone, style, do's and don'ts
      niche-research.md     # Platform research for the niche
    hooks/
      library.json          # Hook instances with performance data
      formulas.md           # Hook formula patterns and psychology
    performance/
      log.json              # Canonical post record (single source of truth)
      hook-tracker.json     # Hook and CTA tracking with metrics
      insights.md           # Agent learnings from performance data
      weekly-review.md      # Weekly review notes
      competitor-insights.md

  references/
    analytics-loop.md       # Full analytics feedback loop and weekly review process
    competitor-research.md  # How to research competitors

  scripts/
    genviral.sh             # 42+ commands wrapping every Partner API endpoint
    update-skill.sh         # Self-updater (keeps skill files current, never touches workspace/)

  prompts/
    slideshow.md            # Prompt templates for slideshow generation
    hooks.md                # Prompt templates for hook brainstorming
```

## Commands

| Category | Commands |
|----------|----------|
| **Accounts & Files** | `accounts`, `upload`, `list-files` |
| **Posts** | `create-post`, `update-post`, `retry-posts`, `list-posts`, `get-post`, `delete-posts` |
| **Slideshows** | `generate`, `render`, `review`, `update`, `regenerate-slide`, `duplicate`, `delete`, `list-slideshows` |
| **Packs** | `list-packs`, `get-pack`, `create-pack`, `update-pack`, `delete-pack`, `add-pack-image`, `delete-pack-image` |
| **Templates** | `list-templates`, `get-template`, `create-template`, `update-template`, `delete-template`, `create-template-from-slideshow` |
| **Analytics & Trends** | `analytics-summary`, `analytics-posts`, `analytics-targets`, `analytics-target-create`, `analytics-target-refresh`, `analytics-refresh`, `analytics-workspace-suggestions`, `trend-brief` |

```bash
./scripts/genviral.sh help  # full command list
```

## Auto-Updates

The skill can update itself without touching your data:

```bash
bash scripts/update-skill.sh           # check + apply if updates available
bash scripts/update-skill.sh --dry-run # preview only, no changes
bash scripts/update-skill.sh --force   # force re-apply even if already current
```

**Skill-owned (updated automatically):** `SKILL.md`, `scripts/`, `docs/` (all subdirs)

**User-owned (never touched):** `workspace/` — your product context, hooks, performance logs, and content data are always preserved.

## The Self-Improving Loop

The skill builds a feedback loop over time:

- **After every post:** log to `workspace/performance/log.json` + tag the hook in `hook-tracker.json`
- **At 48h and 7d:** pull analytics, fill in real metrics per post
- **Every Monday:** review last 7 days, categorize hooks (double down / keep rotating / testing / dropped), update strategy
- **Ongoing:** high performers get used more, dead angles get retired

After 4+ weeks the patterns become clear enough to make data-driven decisions about hooks, CTA types, and post timing.

## Links

- [Genviral](https://genviral.io)
- [Partner API docs](https://docs.genviral.io)
- [OpenClaw](https://openclaw.ai)

## License

MIT
