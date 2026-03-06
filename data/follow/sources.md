# Source Configuration

## Source File Template

Each followed entity gets a markdown file:

```markdown
# @naval

## Platforms
- Twitter: @naval
- Blog: nav.al
- Podcast appearances: search "naval ravikant podcast"

## Priority: high
## Check frequency: daily
## Alert tier: immediate for threads, daily for tweets

## Keywords (boost priority)
- startups, investing, philosophy, wealth, happiness

## Ignore
- retweets of news, political commentary

## Notes
Why following: foundational thinker on startups/wealth
```

---

## Source Types

### People
Track individuals across platforms:
- Social: Twitter/X, LinkedIn, Bluesky, Mastodon
- Content: YouTube, podcast appearances, blog/Substack
- Professional: GitHub commits, conference talks

### Topics
Track keywords/concepts across sources:
- Define 3-5 core keywords + synonyms
- Specify which sources to monitor
- Set relevance threshold

### Feeds
Track publications/channels:
- RSS feeds (blogs, news sites)
- YouTube channels
- Subreddits, HN frontpage
- Telegram channels

---

## Adding a Source

1. Determine type (person/topic/feed)
2. Create file in appropriate folder
3. Fill template with platforms, priority, alerts
4. Run initial backfill if needed
5. Add to `index.md` for quick reference

---

## Platform Access Methods

| Platform | Method | Reliability |
|----------|--------|-------------|
| Twitter/X | API (limited) or scraping | Medium |
| RSS/Blogs | Direct fetch | High |
| YouTube | yt-dlp or API | High |
| LinkedIn | Very limited, mostly manual | Low |
| GitHub | API (generous limits) | High |
| Substack | RSS feed per publication | High |
| HN/Reddit | API or RSS | High |
| Telegram | Join channel, forward or bot | Medium |

For detailed platform setup, see `platforms.md`.
