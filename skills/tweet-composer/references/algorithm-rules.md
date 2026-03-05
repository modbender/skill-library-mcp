# X Algorithm Rules Engine

Rules derived from X's official open-source ranking algorithm (released February 2026).
This is from the **actual code**, not speculation.

## Architecture Overview

The "For You" feed pipeline:
1. **Thunder** fetches in-network posts (from accounts you follow) — sorted by recency
2. **Phoenix Retrieval** (two-tower ANN) fetches out-of-network posts — ML similarity search
3. **Phoenix Ranking** (Grok-based transformer) scores all candidates by predicting engagement
4. **Weighted Scorer** combines predictions into final score
5. **Author Diversity Scorer** penalizes repeated authors
6. **OON Scorer** adjusts out-of-network scores
7. **Filters** remove spam, duplicates, blocked authors, old posts

## The 19 Predicted Actions

Phoenix predicts these probabilities for every candidate tweet:

### Positive Actions (boost score)
| # | Action | Signal | Weight Estimate |
|---|--------|--------|----------------|
| 1 | `P(favorite)` | Like | Very High |
| 2 | `P(reply)` | Reply | Very High |
| 3 | `P(retweet)` | Repost | High |
| 4 | `P(quote)` | Quote tweet | High |
| 5 | `P(click)` | Expand tweet | Medium |
| 6 | `P(profile_click)` | Click author profile | Medium |
| 7 | `P(video_quality_view)` | Watch video (gated: only if video > min duration) | High |
| 8 | `P(photo_expand)` | Expand photo | Medium |
| 9 | `P(share)` | Share (generic) | High |
| 10 | `P(share_via_dm)` | Share via DM | High |
| 11 | `P(share_via_copy_link)` | Copy link | High |
| 12 | `P(dwell)` | Stopped scrolling (boolean) | Medium |
| 13 | `dwell_time` | How long they stopped (continuous, seconds) | Medium |
| 14 | `P(quoted_click)` | Click on quoted content | Low-Medium |
| 15 | `P(follow_author)` | Follow from tweet | Very High |

### Negative Actions (reduce score)
| # | Action | Signal | Weight Estimate |
|---|--------|--------|----------------|
| 16 | `P(not_interested)` | "Not interested" | Heavy Negative |
| 17 | `P(block_author)` | Block author | Heavy Negative |
| 18 | `P(mute_author)` | Mute author | Heavy Negative |
| 19 | `P(report)` | Report tweet | Heavy Negative |

**Note:** Exact weights are redacted in the open source release (`params` module excluded "for security reasons"). Weight estimates are based on structural analysis and industry knowledge.

## Score Formula

```
final_score = Σ(weight_i × P(action_i))
```

After combining:
- Score is normalized
- Negative offset applied to handle below-zero scores
- Then: AuthorDiversityScorer × OONScorer adjustments

## Author Diversity Scorer

Prevents feed domination by a single author:

```
For author's Nth post in a single feed:
multiplier = (1 - floor) × decay^N + floor

Example (estimated decay=0.5, floor=0.1):
1st post: 1.0 (full score)
2nd post: 0.55
3rd post: 0.325
4th post: 0.2125
```

**Implication:** Don't spam. Only your first tweet gets full score. Space tweets 4-6 hours apart.

## Out-of-Network Scorer

Posts from accounts you DON'T follow get multiplied by OON_WEIGHT_FACTOR (likely < 1.0).
But high-engagement out-of-network posts can still beat in-network ones.

**Implication for growth:** Your tweets need to be significantly better than average to appear in non-followers' feeds.

## Thunder: In-Network Post Selection

Thunder is the in-memory store for posts from accounts users follow:

- **Original posts** and **reply/retweet** posts have separate per-author limits
- **Reply chains:** Only first-level replies pass the filter. Deep reply-to-reply-to-reply gets filtered
- **Video posts** tracked separately — must have video > MIN_VIDEO_DURATION_MS and NOT be a reply
- **Retweets of the viewer's own posts** are explicitly removed

**Implications:**
- Don't rely on deep reply threads for visibility
- Video replies don't count as video posts
- Short video clips may not qualify for video boost

## Filters (Pre-Scoring)

Posts are removed before scoring if they match:
1. Duplicate tweet ID
2. Missing core data (no author, empty text)
3. Older than MAX_POST_AGE
4. Self-tweets (your own posts in your feed)
5. Duplicate retweets of same content
6. Premium content you haven't subscribed to
7. Previously seen (client sends bloom filter of impressions)
8. Previously served in current session
9. Muted keywords match
10. Author is blocked or muted

## Filters (Post-Selection)

After scoring and selection:
1. **VF Filter:** Safety check — spam, violence, deleted content removed
2. **DedupConversationFilter:** Only the highest-scored post per conversation branch survives

**Critical for threads:** The first tweet of your thread must be the strongest. If a reply in your thread scores higher, IT becomes the one shown, not your hook tweet.

## What the Model Sees

The transformer input for each candidate:
```
[User Embedding] [History_1...History_128] [Candidate_1...Candidate_32]
```

Per candidate:
- Post hash embedding (content representation)
- Author hash embedding
- Product surface (For You, Search, etc.)

Per history item (your recent engagement):
- Post hash embedding
- Author hash embedding
- What action you took (19-dim multi-hot, signed: +1 did it, -1 didn't)
- Product surface where you saw it

**Key insight:** The model knows your recent engagement patterns. If your followers interact with AI/crypto content and you post food content, the model predicts low engagement → low score.

## Candidate Isolation

Each candidate can only see:
- User embedding + engagement history
- Its own embedding

Candidates CANNOT see each other. Scores are independent and consistent.

**Implication:** Your tweet's score doesn't depend on what else is in the feed batch. Quality is absolute, not relative.

## What Changed from 2023

The old algorithm (twitter/the-algorithm, 2023) had explicit features:
- `has_image_flag`, `has_video_flag` → explicit weights
- `has_multiple_hashtags_flag` → explicit penalty
- `text_score` (entropy, readability) → explicit feature
- TweepCred (PageRank-like author score)
- SimClusters (145K community detection)
- Light Ranker (logistic regression) + Heavy Ranker (neural network)

The 2026 algorithm has **NONE of these**. Everything is learned by the Grok transformer from engagement data. But the learned behaviors align with what the old explicit features captured — images/video still boost engagement, hashtags still reduce it, quality content still wins.

## Practical Scoring Rules for Tweet Composition

### Maximize These Signals

| Rule | Why | Impact |
|------|-----|--------|
| Ask a question or prompt replies | Drives P(reply) — one of the highest-weighted actions | ⬆⬆⬆ |
| Attach native image/video | P(photo_expand) + P(video_quality_view) are separate predictions | ⬆⬆⬆ |
| Create shareable content | P(share) + P(share_via_dm) + P(share_via_copy_link) = 3 separate boosts | ⬆⬆⬆ |
| Write content that makes people pause | dwell_time is a continuous value with its own weight | ⬆⬆ |
| Quote tweet with added value | P(quote) has dedicated weight | ⬆⬆ |
| Make people click your profile | P(profile_click) has dedicated weight — "who is this?" effect | ⬆⬆ |
| Content that earns follows | P(follow_author) is predicted — likely very high weight | ⬆⬆⬆ |
| Video above minimum duration | VQV weight only applies above threshold | ⬆⬆ |

### Minimize These Signals

| Rule | Why | Impact |
|------|-----|--------|
| Don't post irrelevant content | P(not_interested) has negative weight | ⬇⬇⬇ |
| Don't be aggressive/toxic | P(block_author) + P(mute_author) + P(report) all negative | ⬇⬇⬇ |
| Don't spam tweets | AuthorDiversityScorer: 2nd post ~55%, 3rd ~33% score | ⬇⬇ |
| No links in tweet body | Model learns link tweets get less engagement | ⬇⬇ |
| No hashtags | Model learns hashtag tweets get less engagement | ⬇ |
| No short video clips | Below MIN_VIDEO_DURATION_MS = no VQV weight | ⬇ |

### Content Strategy

| Mix | Percentage | Why |
|-----|-----------|-----|
| Entertaining | 40% | Drives likes + shares + dwell |
| Educational | 30% | Drives saves + DM shares + follows |
| Inspirational | 20% | Drives profile clicks + follows |
| Promotional | 10% | Necessary but lower engagement |

### Posting Cadence

- **Max effective tweets/day:** 3-4 (AuthorDiversityScorer decay)
- **Spacing:** 4-6 hours between tweets minimum
- **Peak engagement window:** First 30 minutes (velocity determines viral potential)
- **Reply strategy:** 30 min/day replying to larger accounts in your niche (within 30 min of their post)
