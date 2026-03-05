---
name: Daily News Digest
slug: daily-news-digest
version: 1.0.0
homepage: https://clawic.com/skills/daily-news-digest
description: Personalized news briefings from your chosen sources, delivered morning or evening, with voice option and smart filtering.
metadata: {"clawdbot":{"emoji":"📰","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

# Daily News Digest 📰

Your AI News Chief of Staff. Multi-source aggregation, intelligent prioritization, time-aware delivery, and deep-dive on demand. Never miss what matters, never drown in noise.

## Setup

On first use, read `setup.md` for integration guidelines. The setup process learns preferences through conversation.

## When to Use

User asks for news updates, daily briefings, current events, or scheduled news delivery. Handles source selection, topic filtering, format preferences, and automated scheduling.

## Architecture

Memory lives in `~/daily-news-digest/`. See `memory-template.md` for structure.

```
~/daily-news-digest/
├── memory.md           # Preferences + delivery schedule + learned interests
├── sources.md          # Configured sources + quality scores
├── archive/            # Past briefings for reference
│   └── YYYY-MM-DD.md   # Daily archives
└── cache/              # Temporary fetch cache (auto-cleaned)
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Source configuration | `sources.md` |
| Briefing formats | `formats.md` |
| Scheduling guide | `scheduling.md` |

## Core Rules

### 1. Multi-Source Aggregation
Fetch from multiple source types for comprehensive coverage:

| Source Type | Method | Best For |
|-------------|--------|----------|
| RSS feeds | Direct fetch | Established outlets, blogs |
| Web search | Brave Search API | Breaking news, trending |
| Public APIs | REST calls | Hacker News, Reddit public |

Combine sources to avoid single-point-of-failure. If one fails, others compensate.

### 2. Intelligent Deduplication
Same story appears across multiple outlets. Detect and merge:
- Headline similarity >70% = same story
- Keep version with most detail
- Note which outlets covered it (credibility signal)
- Never show duplicate stories in briefing

### 3. Priority Scoring
Rank stories by importance, not just recency:

| Signal | Weight | Rationale |
|--------|--------|-----------|
| User topic match | +40 | Personalization |
| Multi-outlet coverage | +25 | Importance indicator |
| Breaking/trending tag | +20 | Timeliness |
| Trusted source | +15 | Quality signal |
| Recency (last 6h) | +10 | Freshness |

### 4. Respect Preferences
Memory stores learned preferences. Always check before fetching:
- **Topics**: Include/exclude lists
- **Sources**: Preferred/blocked outlets
- **Geography**: Local emphasis level
- **Schedule**: Delivery times + frequency

Never override user preferences. If conflict, ask.

### 5. Format Adaptation
Deliver in user's preferred format:

| Format | When | Output |
|--------|------|--------|
| Brief | "quick update" | 3-5 headlines, 1 line each |
| Standard | default | 8-12 stories, 2-3 sentences each |
| Deep Dive | "full briefing" | All stories, full context |
| Audio | "voice/listen" | TTS via elevenlabs or system |
| Archive | "save this" | Markdown file in archive/ |

### 6. Time-Aware Delivery
Adapt tone and content based on time of day:

| Time | Mode | Behavior |
|------|------|----------|
| 6-11am | Morning | Energetic, forward-looking, "here's what's happening today" |
| 12-5pm | Midday | Neutral, focused on breaking/developing stories |
| 6-10pm | Evening | Reflective recap, "what you might have missed" |
| Weekend | Relaxed | Lighter content, skip urgent tone, more features/analysis |

### 7. Interactive Deep-Dive
End every briefing with: "Reply with any story number to dive deeper."

When user replies with a number:
1. Fetch full article content
2. Summarize with more context
3. Show related stories
4. Offer: "Want the full article link?"

### 8. Scheduled Delivery
Integrate with OpenClaw cron for automated briefings:

```
User: "Send me news every morning at 8am"
→ Create cron job with appropriate systemEvent
→ Briefing auto-delivers to configured channel
```

Track delivery history in memory. Don't duplicate if already sent.

### 9. Source Quality Tracking
Maintain quality scores per source in sources.md:
- Accuracy of headlines vs content
- Paywall frequency
- Ad density
- Update freshness
- User feedback signals

Deprioritize low-quality sources over time.

### 10. Graceful Degradation
Work with whatever is available. If a source fails:
- Log the failure
- Continue with other sources
- Never fail completely because one source is down
- Mention "X sources unavailable" only if significant

## Common Traps

- **Overwhelming the user** → Default to Standard format (8-12 stories), not everything
- **Stale news** → Always check story age, skip >24h unless explicitly requested
- **Paywall frustration** → Detect paywalls, warn user, offer alternative source
- **Missing local news** → Ask geography on first use, maintain local source list
- **Duplicate stories** → Always run dedup before presenting
- **Silent failures** → If source fetch fails, log and continue with others

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| RSS feed URLs | None (GET only) | Fetch headlines |
| Brave Search API | Query text | Trending/breaking news |
| Hacker News API | None (GET only) | Tech news |
| Reddit JSON API | None (GET only) | Public subreddit feeds |
| ElevenLabs TTS (optional) | Briefing text | Voice synthesis |

No other data is sent externally.

**Credential handling:** Brave Search and ElevenLabs credentials are managed by OpenClaw platform configuration. RSS, Hacker News, and Reddit public APIs require no authentication. Scheduled deliveries use OpenClaw's built-in channel integrations.

## Security & Privacy

**Data that leaves your machine:**
- Search queries sent to Brave API for news discovery
- Briefing text sent to TTS service (if voice enabled)

**Data that stays local:**
- All preferences in ~/daily-news-digest/
- Archive of past briefings
- Source quality scores
- No telemetry or analytics

**This skill does NOT:**
- Share reading habits with third parties
- Store credentials in plain text
- Access files outside ~/daily-news-digest/
- Modify itself or other skills

## Trust

By using this skill with voice features, briefing text is sent to ElevenLabs.
Only enable voice synthesis if you trust this service with your news content.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `news` — personalized news with learning
- `summarizer` — article summarization
- `podcast` — audio content discovery
- `schedule` — calendar and scheduling
- `digest` — general content digests

## Feedback

- If useful: `clawhub star daily-news-digest`
- Stay updated: `clawhub sync`
