---
name: content-ideas
description: Generate content ideas from multiple sources. Aggregates trends from RSS feeds, Reddit, Hacker News, X/Twitter, and web search. Outputs actionable content ideas with hooks, angles, and formats. Use when you need content inspiration, trend monitoring, or building a content calendar.
---

# Content Ideas Generator

Turn trends into content. Aggregate from multiple sources, filter by niche, output actionable ideas.

## How It Works

1. **Gather** — Pull from RSS, Reddit, HN, X, web search
2. **Filter** — Match to your niche and audience
3. **Analyze** — What's trending? What angle is missing?
4. **Output** — Actionable ideas with hooks and formats

## Quick Start

Ask your agent:

> "Generate 10 content ideas for this week. My niche is AI automation for small businesses."

The agent should:
1. Check configured sources (RSS feeds, subreddits, etc.)
2. Search for trending topics in your niche
3. Cross-reference what's getting engagement
4. Generate ideas with specific hooks and angles

## Configuration

Store in `content-ideas/config.json`:

```json
{
  "niche": "AI automation for small businesses",
  "audience": "non-technical founders, solopreneurs",
  "platforms": ["twitter", "linkedin", "blog"],
  
  "sources": {
    "rss": [
      "https://news.ycombinator.com/rss",
      "https://www.reddit.com/r/smallbusiness/.rss",
      "https://www.reddit.com/r/Entrepreneur/.rss"
    ],
    "subreddits": ["smallbusiness", "Entrepreneur", "SaaS", "artificial"],
    "twitter": {
      "accounts": ["@levelsio", "@marckohlbrugge", "@andrewchen"],
      "keywords": ["AI automation", "no-code", "solopreneur"]
    },
    "keywords": ["AI", "automation", "productivity", "small business", "startup"]
  },
  
  "filters": {
    "minEngagement": 100,
    "maxAgeDays": 7,
    "excludeKeywords": ["crypto", "NFT", "web3"]
  },
  
  "output": {
    "ideasPerRun": 10,
    "includeHooks": true,
    "includeFormats": true,
    "includeAngles": true
  }
}
```

## Output Format

```markdown
## Content Ideas - 2026-02-22

### Idea 1: [Title]
**Source:** r/smallbusiness trending post
**Why it's hot:** 500+ upvotes, addresses common pain point
**Your angle:** [How to spin for your audience]
**Hook options:**
- "Most small business owners waste 10 hours/week on this..."
- "I automated X and saved $2000/month. Here's how."
- "Stop doing [thing] manually. This is 2026."
**Formats:** Twitter thread, LinkedIn post, blog tutorial
**Engagement prediction:** High (solves clear pain point)

### Idea 2: [Title]
...
```

## Source Integration

### RSS Feeds (via rss-reader skill)
```bash
# Pre-configure feeds
node /root/clawd/skills/rss-reader/scripts/rss.js add "https://news.ycombinator.com/rss" --category tech
node /root/clawd/skills/rss-reader/scripts/rss.js add "https://www.reddit.com/r/Entrepreneur/.rss" --category business
```

### Reddit (public RSS)
Reddit exposes RSS for any subreddit:
- `https://www.reddit.com/r/{subreddit}/.rss` — new posts
- `https://www.reddit.com/r/{subreddit}/top/.rss?t=week` — top this week

### Hacker News
- Front page: `https://news.ycombinator.com/rss`
- Show HN: `https://hnrss.org/show`
- Ask HN: `https://hnrss.org/ask`
- By keyword: `https://hnrss.org/newest?q=AI+automation`

### X/Twitter (via bird or x-twitter skills)
Search trending topics and high-engagement posts in your niche.

### Web Search (via web_search tool)
Search for trending articles, news, and discussions.

## Workflow

### Daily Ideas (Cron)

Set up a daily cron to generate ideas:

```
Schedule: 07:00 daily
Task: Generate 5 content ideas based on overnight trends. Save to content-ideas/daily/YYYY-MM-DD.md
```

### Weekly Content Calendar

```
Schedule: Sunday 20:00
Task: Generate 15-20 content ideas for the week. Organize by platform and day. Save to content-ideas/weekly/YYYY-WW.md
```

### On-Demand Research

> "What's trending in [niche] right now? Give me 5 content ideas I can post today."

## Idea Categories

### Reactive (Trending Now)
- Breaking news response
- Hot take on viral post
- "Here's what everyone's missing about X"

### Evergreen (Always Relevant)  
- How-to tutorials
- Tool comparisons
- Beginner guides
- Common mistakes

### Personal (Your Experience)
- Behind-the-scenes
- Lessons learned
- Case studies
- Failures and wins

### Contrarian (Stand Out)
- Unpopular opinions
- Myth-busting
- "Why I don't do X"

## Hook Formulas

When generating ideas, include hooks:

1. **Problem-Agitate**: "Most [audience] waste [time/money] on [thing]..."
2. **Curiosity Gap**: "The one thing [successful people] do that nobody talks about..."
3. **Social Proof**: "How [person] went from [A] to [B] in [time]..."
4. **Contrarian**: "Unpopular opinion: [common belief] is wrong. Here's why..."
5. **How-To**: "How to [achieve result] in [timeframe] (step-by-step)"
6. **List**: "[Number] [things] every [audience] needs to know about [topic]"
7. **Story**: "I [did thing] and [result]. Here's what happened..."

## Integration with Brand Voice

When generating ideas, reference the brand voice profile:

```
1. Load brand-voice/profile.json
2. Match hooks to tone (casual vs professional)
3. Filter ideas by audience match
4. Adapt language to vocabulary preferences
```

## Tips

1. **Quality over quantity** — 5 good ideas beat 20 mediocre ones
2. **Cross-platform** — One idea can be a thread, post, AND article
3. **Timeliness matters** — Trending topics have a 24-48 hour window
4. **Your angle** — Don't just report trends, add unique perspective
5. **Save rejects** — Ideas that don't fit now might work later
6. **Track performance** — What ideas convert to engagement?
