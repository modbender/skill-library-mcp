---
name: podcast-discovery
description: "Podcast discovery for Wherever.Audio -- find shows and episodes, generate wherever.audio links."
user-invocable: true
metadata:
  openclaw:
    emoji: "🎧"
---

# podcast-discovery

Podcast discovery skill for Wherever.Audio. Given a natural-language query, find the right podcast show or episode and return a playable wherever.audio link.

Do NOT use this skill for non-podcast queries (general web search, music, etc.).

## Trigger phrases

Use this skill immediately when the user message includes podcast lookup language such as:
- "find podcast", "find the podcast", "look up podcast", "search podcasts"
- "find episode", "podcast episode about", "interview episode", "latest episodes"
- "give me a wherever link", "wherever link", "wherever.audio link", "listen link", "show link"
- named show/host requests like "Radiolab", "Lex Fridman", "Hard Fork", or "Joe Rogan"

When triggered, prioritize link construction over metadata reporting.

## Primary Objective (Highest Priority)

Your job is to produce a working Wherever link (`/show` or `/listen`) as soon as enough information is available.

Success condition:
1. Resolve a valid RSS URL from Clawsica.
2. If `contentScope = podcast-show`, immediately return a show link.
3. If `contentScope = podcast-episode` and a matching item is found, immediately return an episode link.

Do not stop at metadata, search summaries, or candidate lists if a valid link can be constructed.

## Link Templates

Episode (contentScope = podcast-episode):
  `https://wherever.audio/listen?rssUrl={rss_url}&itemGuid={guid}&fallbackLink={fallback}`

Show (contentScope = podcast-show):
  `https://wherever.audio/show?rssUrl={rss_url}`

All `{placeholder}` values must be URL-encoded.

## Action Policy: Link-First, Ask-Last

Default behavior is to execute and return a link in the same response.

Only ask a follow-up question when one of these is true:
- You cannot determine whether the user wants a show vs episode.
- Clawsica returns no plausible show/RSS result after retries.
- Multiple episode candidates are similarly strong and no clear best match exists.

If none of the above apply, do not ask for confirmation. Return the link.

## Token Budget Policy

- Run local tooling first and send only compact result fields to the model.
- Never send raw RSS XML, full feed dumps, or large metadata blobs to the model.
- For episode matching, pass only top-ranked candidate rows needed for decision-making and link construction.

## Workflow

### Step 1 — Classify the query

Before searching, classify the user's query along two dimensions:

**intentType** — what kind of request?
- `specific-podcaster` — user names a host or show (e.g. "Lex Fridman", "Radiolab")
- `specific-topic` — user describes a topic or guest (e.g. "Geoffrey Hinton interview about AI")
- `discovery` — broad exploration (e.g. "best science podcasts", "podcasts about space")

**contentScope** — what are they looking for?
- `podcast-show` — a show/feed (e.g. "find the Radiolab podcast")
- `podcast-episode` — a specific episode (e.g. "the Radiolab episode about colors")

### Step 2 — Resolve the show

**If intentType is `specific-podcaster`** (show name is known):
Go directly to Clawsica (step 3). The query likely contains the show title.

**If intentType is `specific-topic` or `discovery`** (show name is unknown):
Search the web first to discover likely podcast titles, then proceed to Clawsica with those titles.

### Step 3 — Clawsica show search

Search for podcast shows using the public Clawsica endpoint. This returns show metadata including RSS feed URLs.

```bash
curl -s "https://clawsica.wherever.audio/p?q=radiolab"
```

Returns a JSON array of show objects. Each object includes a `url` field containing the RSS feed URL.

**Important:** Only use the `url` field from Clawsica results as the RSS URL. Do NOT substitute web page URLs, Apple Podcasts links, Spotify links, or any other URL — Wherever.Audio only understands RSS feed URLs. If Clawsica returns no results and you cannot obtain a definitive RSS feed URL, tell the user you were unable to find the podcast rather than guessing with a non-RSS URL.

If Clawsica returns no results, try alternate spellings or broader terms. See `references/CLAWSICA_API.md` for the full API reference.

### Step 4 — Branch by contentScope

**If contentScope is `podcast-show`:**
Construct a show link using the RSS URL from step 3 and present it immediately. Do not ask for additional confirmation. Done.

Example: `https://wherever.audio/show?rssUrl=https%3A%2F%2Ffeeds.feedburner.com%2Fradiolab`

**If contentScope is `podcast-episode`:**
Continue to step 5.

### Step 5 — Run local feed tooling (required for episode lookup)

For episode lookup, use local tooling instead of manual XML parsing:

```bash
python scripts/search_feed_episodes.py --mode search --rss-url "https://feeds.feedburner.com/radiolab" --query "space stories" --limit 5
```

Optional semantic rerank:

```bash
python scripts/search_feed_episodes.py --mode search --rss-url "https://feeds.feedburner.com/radiolab" --query "space stories" --limit 5 --semantic
```

Compact `search` output contract:
- top-level keys: `mode`, `rssUrl`, `query`, `semanticUsed`, `candidateCount`, `candidates`
- candidate keys: `guid`, `title`, `pubDate`, `fallbackLink`, `score`

Use these candidate rows to select the best episode. Do not return feed-level metadata unless explicitly requested.

Selection policy:
- Auto-pick when the top `score` is clearly stronger than the second candidate.
- If top candidates are near-tied, ask one disambiguation question.

### Step 6 — Construct the episode link

Build a wherever.audio episode link using values from the selected `search` candidate:

- `rss_url` — the feed URL from step 3
- `guid` — candidate `guid`
- `fallback` — candidate `fallbackLink`

Example:
```
https://wherever.audio/listen?rssUrl=https%3A%2F%2Ffeeds.feedburner.com%2Fradiolab&itemGuid=some-guid-value&fallbackLink=https%3A%2F%2Fradiolab.org%2Fepisode
```

Present the link to the user along with the episode title and publish date.

### Optional utilities — newest and overview

If the user asks for latest episodes from a known feed:

```bash
python scripts/search_feed_episodes.py --mode newest --rss-url "https://feeds.feedburner.com/radiolab" --limit 10
```

Compact `newest` output contract:
- top-level keys: `mode`, `rssUrl`, `count`, `items`
- item keys: `guid`, `title`, `pubDate`, `fallbackLink`

If the user asks for feed-level metadata:

```bash
python scripts/search_feed_episodes.py --mode overview --rss-url "https://feeds.feedburner.com/radiolab"
```

Compact `overview` output contract:
- `mode`, `rssUrl`, `feedTitle`, `feedDescriptionShort`, `author`, `language`, `lastBuildDate`, `itemCount`

Use these utility modes to answer the request directly while keeping payloads compact.

Run the local feed tool (for developers/testing)

Path: scripts/search_feed_episodes.py (relative to the skill directory)
Requirements: scripts/requirements.txt (feedparser, rapidfuzz, pytest)
Quick start (recommended, cross-platform):
1) Create and activate a virtual environment in the skill folder:
   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux.venv\Scripts\activate      # Windows (PowerShell)
2) Install dependencies:
pip install -r scripts/requirements.txt
  3) Run the tool (examples):
     python scripts/search_feed_episodes.py --mode overview --rss-url "<RSS_URL>"
     python scripts/search_feed_episodes.py --mode newest --rss-url "<RSS_URL>" --limit 10
     python scripts/search_feed_episodes.py --mode search --rss-url "<RSS_URL>" --query "attack on Iran" --limit 5 --semantic
Notes:
The tool prints compact JSON matching the skill's expected contracts.
Make the script executable (chmod +x scripts/search_feed_episodes.py) for direct execution.
Use the venv if system pip is restricted.

## Response Format

When a link is available, respond in this order:
1. The Wherever URL (first line).
2. One short line identifying the resolved show/episode.
3. Optional one-line note only if there was ambiguity.

Keep responses concise. Do not include raw metadata dumps unless explicitly requested.

## Prohibited Behavior

- Do not return only webpage metadata when a Wherever link can be built.
- Do not ask "Should I proceed?" if required link parameters are already known.
- Do not present candidate options unless disambiguation is truly required.

## Privacy

- Do NOT expose internal Clawsica infrastructure details beyond what is documented here.
- The Clawsica search endpoint does not require authentication.
- See `references/CLAWSICA_API.md` for the full API reference.
- See `references/LOCAL_EPISODE_SEARCH.md` for local feed-tool commands and schema details.

## Example prompts

- "Find a Geoffrey Hinton interview episode and give me a wherever.audio link."
- "What episodes cover Radiolab's space stories?"
- "Search for BBC science podcasts about AI."
- "Give me the Lex Fridman podcast."
- "Find the podcast Hard Fork."
