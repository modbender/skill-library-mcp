# Source Configuration — Daily News Digest

## Default Source Categories

### Tier 1: High Quality (Always Include)
| Source | Type | Topics | Notes |
|--------|------|--------|-------|
| Reuters | RSS | World, Business | Gold standard for accuracy |
| AP News | RSS | World, US | Wire service, fast |
| BBC | RSS | World, UK | Balanced international |
| NPR | RSS | US, Culture | Quality long-form |

### Tier 2: Tech & Business
| Source | Type | Topics | Notes |
|--------|------|--------|-------|
| Hacker News | Scrape | Tech, Startups | Community-curated |
| The Verge | RSS | Tech, Consumer | Good for product news |
| Ars Technica | RSS | Tech, Science | In-depth |
| TechCrunch | RSS | Startups, VC | Funding news |
| Bloomberg | RSS | Business, Finance | Paywalled sometimes |

### Tier 3: Specialized
| Source | Type | Topics | Notes |
|--------|------|--------|-------|
| The Guardian | RSS | World, Opinion | Left-leaning |
| WSJ | RSS | Business, Finance | Paywalled |
| NYT | RSS | General | Paywalled |
| Wired | RSS | Tech, Culture | Feature-heavy |

### Tier 4: Community Curated
| Source | Type | Topics | Notes |
|--------|------|--------|-------|
| Reddit r/worldnews | JSON API | World | Community-vetted |
| Reddit r/technology | JSON API | Tech | Discussion-heavy |
| Hacker News | Public API | Tech | Highly curated |

## Source Quality Scoring

Maintain in `~/daily-news-digest/sources.md`:

```markdown
## Source Quality Scores

| Source | Accuracy | Paywall | Freshness | Score |
|--------|----------|---------|-----------|-------|
| Reuters | 10 | 0 | 9 | 9.5 |
| BBC | 9 | 0 | 8 | 8.5 |
| TechCrunch | 8 | 2 | 9 | 8.0 |
| WSJ | 9 | 8 | 8 | 6.5 |
```

**Score formula:** (Accuracy * 0.4) + ((10 - Paywall) * 0.3) + (Freshness * 0.3)

Update scores based on:
- User feedback ("this source is always clickbait")
- Paywall encounters
- Article quality vs headline accuracy

## RSS Feed URLs

```
# Tier 1
Reuters World: https://feeds.reuters.com/reuters/topNews
AP News: https://rsshub.app/apnews/topics/apf-topnews
BBC World: http://feeds.bbci.co.uk/news/world/rss.xml
NPR News: https://feeds.npr.org/1001/rss.xml

# Tier 2 Tech
Hacker News Best: https://hnrss.org/best
The Verge: https://www.theverge.com/rss/index.xml
Ars Technica: https://feeds.arstechnica.com/arstechnica/index
TechCrunch: https://techcrunch.com/feed/

# Specialized
The Guardian: https://www.theguardian.com/world/rss
Wired: https://www.wired.com/feed/rss
```

## Adding Custom Sources

User can add sources via conversation:
- "Add Financial Times to my sources"
- "I want news from El País"
- "Remove Daily Mail from my feed"

Store custom sources in memory.md Sources section.

## Blocked Sources (Default)

These sources are low-quality by default:
- Daily Mail (accuracy issues)
- Buzzfeed News (defunct)
- Infowars (misinformation)

User can override blocks explicitly.

## Paywall Handling

When encountering paywall:
1. Note in source quality scores
2. Try to extract headline + first paragraph
3. If full article needed, suggest alternative source
4. Never claim to have content you can't access
