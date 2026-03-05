---
domain: twitter-intel
topic: twitter-api-engagement-metrics-kol-signals
priority: high
ttl: 30d
---

# Twitter Intelligence — API, Engagement Metrics & KOL Signals

## Twitter/X API v2 Endpoints

### Tweet Search
- **Recent Search** — `GET /2/tweets/search/recent` — Tweets from last 7 days
  - Query operators: `from:`, `to:`, `is:retweet`, `is:reply`, `is:quote`, `has:media`, `has:links`, `lang:`
  - Max results per request: 100 (paginate with `next_token`)
  - Rate limit: 450 requests / 15-min window (App-level), 180 (User-level)
- **Full-Archive Search** — `GET /2/tweets/search/all` — Complete tweet history (Academic/Pro access)
  - Same query operators as Recent Search
  - Rate limit: 300 requests / 15-min window
- **Filtered Stream** — `POST /2/tweets/search/stream/rules` + `GET /2/tweets/search/stream`
  - Real-time streaming with up to 25 concurrent rules (Basic), 1000 (Pro)
  - Supports all search operators as filter rules

### User & Account Data
- **User Lookup** — `GET /2/users/by/username/:username`
  - Fields: `id`, `name`, `username`, `created_at`, `description`, `public_metrics`, `verified`, `verified_type`
- **User Tweets Timeline** — `GET /2/users/:id/tweets` — Up to 3,200 most recent tweets
- **Followers/Following** — `GET /2/users/:id/followers`, `GET /2/users/:id/following`
  - Rate limit: 15 requests / 15-min window

### Engagement & Metrics
- **Tweet Metrics** (via `tweet.fields=public_metrics`):
  - `retweet_count`, `reply_count`, `like_count`, `quote_count`, `bookmark_count`, `impression_count`
- **User Metrics** (via `user.fields=public_metrics`):
  - `followers_count`, `following_count`, `tweet_count`, `listed_count`

### Trend Data
- **Trending Topics** — `GET /1.1/trends/place.json?id={WOEID}`
  - Returns top 50 trends for a location (WOEID-based)
  - Includes `tweet_volume` (last 24h) when available
  - Rate limit: 75 requests / 15-min window

## Search Query Operators

### Content Filters
- `"exact phrase"` — Match exact phrase in tweet text
- `keyword1 keyword2` — Both terms required (implicit AND)
- `keyword1 OR keyword2` — Match either term
- `-keyword` — Exclude tweets containing term
- `#hashtag` — Match hashtag
- `$TICKER` — Match cashtag (financial symbols)
- `url:"domain.com"` — Tweets containing links to domain

### Account Filters
- `from:username` — Tweets authored by account
- `to:username` — Tweets directed at account (replies/mentions)
- `@username` — Tweets mentioning account
- `retweets_of:username` — Retweets of account's tweets

### Tweet Type Filters
- `is:retweet` / `-is:retweet` — Include/exclude retweets
- `is:reply` / `-is:reply` — Include/exclude replies
- `is:quote` — Quote tweets only
- `is:verified` — From verified accounts only
- `has:media` — Tweets with images or video
- `has:links` — Tweets with URLs
- `has:hashtags` — Tweets with at least one hashtag

### Temporal & Engagement Filters
- `since:2024-01-01` / `until:2024-12-31` — Date range (YYYY-MM-DD)
- `min_retweets:100` — Minimum retweet threshold
- `min_faves:500` — Minimum like threshold
- `min_replies:50` — Minimum reply threshold
- `lang:en` — Language filter (ISO 639-1)

## KOL Identification Signals

### Authority Indicators
| Signal | Description | Weight |
|--------|------------|--------|
| Verified badge | Blue checkmark (paid) or gold/grey (org/gov) | Medium — verification is now pay-to-play; gold/grey is stronger |
| Follower-to-following ratio | High ratio (>10:1) suggests organic authority | High |
| Listed count | Number of lists the account appears on — indicates curation by others | High |
| Account age | Older accounts with consistent activity are more credible | Medium |
| Bio & affiliations | Institutional affiliation, professional credentials | High |

### Content Quality Indicators
| Signal | Description | Weight |
|--------|------------|--------|
| Original tweet ratio | Proportion of original tweets vs retweets — high ratio suggests thought leadership | High |
| Thread creation | Regularly publishes long-form threads — indicates deep analysis | Medium |
| Citation behavior | Links to primary sources, papers, data — indicates research rigor | High |
| Engagement quality | Reply-to-like ratio — high reply engagement suggests genuine discourse | Medium |
| Consistency | Posts on-topic regularly over months/years — not a flash account | High |

### KOL Classification Tiers

| Tier | Followers | Characteristics | Intelligence Value |
|------|-----------|----------------|-------------------|
| Mega-KOL | 1M+ | Broad reach, high noise, opinion-shaping | Trend confirmation, narrative direction |
| Macro-KOL | 100K-1M | Industry visibility, media crossover | Sector sentiment, emerging narratives |
| Mid-KOL | 10K-100K | Domain specialists, practitioner voices | Technical signals, insider perspective |
| Micro-KOL | 1K-10K | Niche experts, early adopters | Early signals, ground-truth validation |
| Nano-KOL | <1K | Hyper-specialized, often undervalued | Deep domain knowledge, contrarian signals |

## Engagement Metric Interpretation

### Healthy Engagement Ratios
- **Like-to-impression ratio**: 1-3% is typical; >5% indicates high resonance
- **Retweet-to-like ratio**: 0.1-0.3 is normal; >0.5 suggests strong shareability or controversy
- **Reply-to-like ratio**: 0.01-0.05 is normal; >0.1 indicates contentious content ("ratio'd")
- **Quote-to-retweet ratio**: >0.3 suggests the tweet is being challenged or annotated

### Anomalous Engagement Patterns
- **Spike without context**: Sudden engagement surge with no clear catalyst — possible bot amplification
- **Follower burst**: Account gains 10K+ followers in <24h without viral content — possible purchased followers
- **Uniform engagement timing**: Likes/retweets arriving at metronomic intervals — bot signature
- **Low-quality reply flood**: High reply count but replies are generic, single-emoji, or from low-follower accounts — astroturfing

## Bot Detection Heuristics

### Account-Level Signals
- Default profile image or AI-generated avatar
- Username contains long random number strings (e.g., `user83749201`)
- Account created in bulk pattern (similar creation dates, sequential naming)
- Bio is generic, copied, or empty; displays no domain expertise
- Following/follower ratio near 1:1 with high absolute numbers (follow-back bot)

### Behavior-Level Signals
- Tweets at inhuman frequency (>100 tweets/hour)
- Posts 24/7 with no sleep pattern
- Content is entirely retweets or templated replies
- Engages across unrelated topics with no coherent interest graph
- Replies within seconds of target tweet publication

### Network-Level Signals
- Cluster of accounts retweeting the same content within minutes
- Shared followers/following lists across multiple accounts
- Coordinated hashtag usage at the same timestamps
- Reply chains that form repetitive patterns (e.g., same phrase variations)
