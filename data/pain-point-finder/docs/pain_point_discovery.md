# Pain Point Finder — Implementation Plan

## Context

A self-contained skill for ggbot that searches Reddit for complaints, frustrations, and unmet needs, then synthesizes findings into startup idea proposals.

**Data source**: PullPush API only (`https://api.pullpush.io`). No OpenAI web_search. No Reddit JSON API. Zero API keys required.

## What Changes

| File | Action |
|------|--------|
| `scripts/pain-points.mjs` | **Create** — Main script, 3 subcommands |
| `SKILL.md` | **Replace** — Agent-facing documentation with pain-point workflow |
| `_meta.json` | **Update** — Bump version, update displayName |
| `package.json` | **Update** — New description, bin entries |
| `references/SUBREDDITS.md` | **Create** — Curated subreddit seed lists by domain |
| `scripts/search.js` | **Delete** — Old OpenAI web_search script |

## PullPush API — Verified Capabilities

Tested live from this server on 2026-02-26:

| Capability | Detail |
|---|---|
| Base URL | `https://api.pullpush.io` |
| Post search | `/reddit/search/submission/?q=...&subreddit=...` |
| Comment search | `/reddit/search/comment/?q=...&subreddit=...` |
| Comments by post | `/reddit/search/comment/?link_id=<post_id_no_prefix>` |
| Max page size | `size=100` (hard cap) |
| Pagination | `before=<created_utc>` of last result → next page |
| Multi-subreddit | NOT supported — must query one subreddit at a time |
| Score filter | `score=%3E<N>` (URL-encoded `>N`) |
| Phrase search | `q=%22exact+phrase%22` (URL-encoded quotes) |
| Body search | `selftext=<terms>` searches post body |
| Sort | `sort=desc&sort_type=score` or `num_comments` or `created_utc` |
| Time range | `after=<unix_ts>&before=<unix_ts>` |
| Historical depth | Tested back to **2015**; archive goes to ~2005 |
| Boolean OR | NOT supported — run separate queries |
| Cloud IP blocking | **None** — works from datacenter IPs |
| Auth | None required |

## Rate Limiting & Backoff

PullPush is a free community service. We must be respectful.

### Self-imposed rate limiter (token bucket)

```
MIN_DELAY_MS  = 1000       # 1 request per second
MAX_PER_MIN   = 30         # hard cap: 30 requests per rolling minute
MAX_PER_RUN   = 300        # hard cap: 300 requests per invocation
```

Implementation: token bucket with timestamps. Before each request:
1. Check `requestsThisMinute < MAX_PER_MIN` — if exceeded, sleep until minute rolls
2. Check `requestsThisRun < MAX_PER_RUN` — if exceeded, stop and return partial results
3. Enforce minimum `MIN_DELAY_MS` between consecutive requests
4. Add jitter: `MIN_DELAY_MS + random(0, 200)ms`

### Exponential backoff on failure

```
Retry policy:
  HTTP 429 (rate limited) → wait 2s, 4s, 8s, 16s, 32s (max 5 retries)
  HTTP 5xx (server error) → wait 2s, 4s, 8s (max 3 retries)
  HTTP 403 (blocked)      → stop immediately, return partial results
  Timeout (>10s)          → retry once after 3s, then skip this query
  Network error           → retry with backoff, max 3 attempts
  Non-JSON response       → treat as server error, retry

After max retries exhausted for a query: skip it, continue with remaining queries.
Never crash the whole run for a single failed request.
```

## Architecture — 3 Phases + 3 Subcommands

### Pipeline Overview

```
INPUT: domain="project management", depth="deep"
                    │
    ┌───────────────┴───────────────┐
    │     Phase 1: DISCOVER         │
    │     Find relevant subreddits  │
    │  3-5 domain-scoped seed       │
    │  queries, global (no sub      │
    │  filter), collect subreddit   │
    │  frequency from results       │
    └───────────────┬───────────────┘
                    │ → r/projectmanagement, r/SaaS, r/smallbusiness...
    ┌───────────────┴───────────────┐
    │     Phase 2: SCAN             │
    │  Per subreddit × per query    │
    │  category = ~40-80 API calls  │
    │  Dedupe by post ID            │
    │  Score locally with           │
    │  painScore formula            │
    └───────────────┬───────────────┘
                    │ → 100-300 unique posts, scored & ranked
    ┌───────────────┴───────────────┐
    │     Phase 3: DEEP-DIVE        │
    │  Top N posts by painScore     │
    │  Fetch all comments per post  │
    │  Mine agreement signals       │
    │  Extract solution attempts    │
    │  Collect evidence quotes      │
    └───────────────┬───────────────┘
                    │ → Rich pain profiles with evidence
                    ▼
              JSON output to stdout
              (LLM synthesizes into proposals)
```

## Subcommand 1: `discover`

Finds the right subreddits for a given domain.

```bash
node {baseDir}/scripts/pain-points.mjs discover \
  --domain "project management" \
  --limit 10
```

**Flow:**

1. Generate domain-scoped seed queries from the user's domain string:
   - `"<domain>"` (exact phrase)
   - `"<domain> tool"` / `"<domain> software"` / `"<domain> app"`
   - `"<domain> alternative"`
2. For each seed query, search PullPush globally (no subreddit filter):
   - `/reddit/search/submission/?q=<seed>&size=100&score=%3E3`
3. Count subreddit frequency across all results
4. For each candidate subreddit (top 15 by frequency), run a validation query:
   - `/reddit/search/submission/?q=frustrated|terrible|alternative&subreddit=<sub>&size=10&score=%3E3`
   - If results > 0 → subreddit is pain-relevant
5. Rank validated subreddits by: `seedFrequency * 2 + painValidationCount`
6. Return top N

**Output:**
```json
{
  "ok": true,
  "data": {
    "domain": "project management",
    "subreddits": [
      { "name": "projectmanagement", "seedHits": 10, "painHits": 8, "score": 28 },
      { "name": "SaaS", "seedHits": 6, "painHits": 5, "score": 17 }
    ],
    "queries_used": 8,
    "api_calls": 23
  }
}
```

**API calls:** ~8-20 (seed queries + validation queries)

## Subcommand 2: `scan`

Broad pain-point search across subreddits.

```bash
node {baseDir}/scripts/pain-points.mjs scan \
  --subreddits "projectmanagement,SaaS,smallbusiness" \
  --domain "project management" \
  --days 90 \
  --minScore 5 \
  --minComments 3 \
  --limit 30 \
  --pages 2
```

**Flow:**

1. Build query set — 4 categories of pain signals:

   **FRUSTRATION** (what hurts):
   ```
   "frustrated with"  "fed up with"  "nightmare"  "terrible"
   "broken"  "unusable"  "worst"  "hate using"
   ```

   **DESIRE** (what's missing):
   ```
   "wish there was"  "looking for"  "alternative to"
   "switched from"  "better than"  "anything else"
   ```

   **COST** (pricing pain):
   ```
   "too expensive"  "price hike"  "overpriced"  "not worth"
   ```

   **DOMAIN-SPECIFIC** (generated from --domain):
   ```
   "<domain> sucks"  "<domain> frustrating"  "<domain> broken"
   ```

2. For each subreddit × each query:
   - `/reddit/search/submission/?q=<query>&subreddit=<sub>&size=100&score=%3E<minScore>&sort=desc&sort_type=num_comments`
   - If `--pages > 1`: paginate using `before=<last_created_utc>`
   - Apply time filter: `after=<now - days>&before=<now>`
3. Deduplicate by post `id`
4. Filter: `num_comments >= minComments`
5. Compute local painScore for each post:

   ```
   painScore =
       titleSignalCount * 2.0
     + bodySignalCount * 1.0
     + log2(num_comments + 1) * 0.5
     + log2(score + 1) * 0.3
     + (upvote_ratio > 0.90 ? 1.0 : 0)
     + flairBonus  (Rant/Complaint/Help/Vent → +1.0)
   ```

6. Sort by painScore desc, return top `--limit`

**Output:**
```json
{
  "ok": true,
  "data": {
    "posts": [
      {
        "id": "1inyk7o",
        "title": "Stripe's Payment Holds Are Ruining My Small Business",
        "subreddit": "smallbusiness",
        "url": "https://www.reddit.com/r/smallbusiness/comments/1inyk7o/...",
        "score": 265,
        "num_comments": 89,
        "upvote_ratio": 0.96,
        "created_utc": 1739386511,
        "selftext_excerpt": "Look, I've been running my business smoothly...",
        "painScore": 8.7,
        "painSignals": ["frustrated", "ruining"],
        "flair": "General"
      }
    ],
    "stats": {
      "queries_run": 48,
      "api_calls": 62,
      "raw_posts": 412,
      "after_dedup": 287,
      "after_filter": 30
    }
  }
}
```

**API calls:** ~40-80 (subreddits × queries × pages)

## Subcommand 3: `deep-dive`

Deep analysis of a single post or a batch of posts.

```bash
# Single post
node {baseDir}/scripts/pain-points.mjs deep-dive \
  --post "1inyk7o" \
  --maxComments 200

# Batch from scan output (pipe or file)
node {baseDir}/scripts/pain-points.mjs deep-dive \
  --from-scan scan_results.json \
  --top 10 \
  --maxComments 100
```

**Flow:**

1. For each post, fetch comments:
   - `/reddit/search/comment/?link_id=<post_id>&size=100`
   - Paginate with `before=` if `--maxComments > 100`
2. Score each comment for **agreement signals**:
   ```
   AGREEMENT: "same here" "me too" "can confirm" "exactly this"
              "+1" "this is why I" "I had the same" "happened to me"
              "I agree" "so true" "couldn't agree more"
   ```
3. Score each comment for **solution attempts**:
   ```
   SOLUTION: "I switched to" "I ended up using" "the workaround is"
             "I built my own" "I just use" "try using" "we moved to"
             "I found that" "what worked for me"
   ```
4. Extract:
   - `agreementCount` — how many commenters share the pain
   - `solutionAttempts[]` — what people have tried (tool names, workarounds)
   - `topQuotes[]` — highest-scored pain comments (evidence)
   - `mentionedTools[]` — products/services mentioned (competitive landscape)
   - `commentScoreDistribution` — how engagement is distributed

**Output:**
```json
{
  "ok": true,
  "data": {
    "post": {
      "id": "1inyk7o",
      "title": "Stripe's Payment Holds Are Ruining My Small Business",
      "painScore": 8.7
    },
    "analysis": {
      "totalComments": 89,
      "agreementCount": 23,
      "agreementRatio": 0.26,
      "topQuotes": [
        { "body": "Same here. Just had $4k held for 21 days...", "score": 77 }
      ],
      "solutionAttempts": [
        { "body": "I switched to Square and haven't looked back", "score": 45, "tool": "Square" }
      ],
      "mentionedTools": ["Square", "PayPal", "Helcim"],
      "validationStrength": "strong"
    }
  }
}
```

**Validation strength heuristic:**
```
strong:   agreementRatio > 0.20 AND agreementCount >= 10
moderate: agreementRatio > 0.10 AND agreementCount >= 5
weak:     agreementRatio > 0.05 OR  agreementCount >= 3
anecdotal: everything else
```

**API calls:** 1-3 per post (comment pagination)

## Pain Signal Keywords

Organized by category for matching in titles, selftext, and comments:

```javascript
const PAIN_SIGNALS = {
  frustration: [
    'frustrated', 'frustrating', 'annoying', 'annoyed',
    'fed up', 'sick of', 'tired of', 'giving up', 'nightmare',
    'terrible', 'awful', 'broken', 'buggy', 'unusable',
    'horrible', 'worst', 'garbage', 'trash', 'joke',
    'hate', 'ruining', 'killing', 'destroying',
  ],
  desire: [
    'wish there was', 'looking for', 'alternative to',
    'switched from', 'better than', 'anything else',
    'does anyone know', 'recommendations for',
    'is there a', 'need something',
  ],
  cost: [
    'too expensive', 'price hike', 'overpriced', 'not worth',
    'hidden fees', 'ripoff', 'rip off', 'gouging',
    'cost went up', 'raised prices',
  ],
  agreement: [
    'same here', 'me too', 'can confirm', 'exactly this',
    'this is why', 'i had the same', 'happened to me',
    'i agree', 'so true', 'couldn\'t agree more',
    'yep same', 'deal breaker for me too',
  ],
  solution: [
    'i switched to', 'i ended up using', 'the workaround is',
    'i built my own', 'i just use', 'try using',
    'we moved to', 'what worked for me', 'i found that',
  ],
};
```

## SKILL.md — Agent Workflow

The SKILL.md guides the LLM agent through a 4-phase research workflow:

1. **Discover**: Run `discover --domain "<user's domain>"` → get relevant subreddits
2. **Broad Scan**: Run `scan --subreddits <discovered> --domain "<domain>"` → get scored pain points
3. **Deep Analysis**: Run `deep-dive --from-scan <results> --top 10` → get agreement signals, themes, quotes
4. **Synthesis** (agent does this, not the script): Structure each finding as a startup proposal with:
   - Problem statement
   - Evidence (quotes + agreement ratio)
   - Who feels this (subreddit demographics)
   - Current solutions & why they fail (from solution attempts)
   - Opportunity gap
   - Idea sketch
   - Validation strength (strong/moderate/weak/anecdotal)

## Script Structure

Single file `scripts/pain-points.mjs`, structured as:

```
1. Constants & config
2. Rate limiter (token bucket)
3. HTTP client with backoff retry
4. PullPush API helpers
   - searchSubmissions(params)
   - searchComments(params)
   - paginateSubmissions(params, pages)
   - paginateComments(linkId, maxComments)
5. Pain scoring
   - computePainScore(post)
   - matchSignals(text, category)
   - analyzeComments(comments)
6. Subcommands
   - discover(args)
   - scan(args)
   - deepDive(args)
7. CLI arg parser & main
```

## Verification

1. `node scripts/pain-points.mjs discover --domain "project management" --limit 5`
2. `node scripts/pain-points.mjs scan --subreddits projectmanagement,SaaS --days 30 --limit 5`
3. `node scripts/pain-points.mjs deep-dive --post 1inyk7o`
4. Verify rate limiter: watch stderr for `[rate] sleeping Nms` messages
5. Verify backoff: temporarily use a bad URL, confirm retry logs
6. Verify partial results: kill PullPush mid-run, confirm graceful degradation
