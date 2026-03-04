# RRA — Retrieve, Research, Analyze

API base: `https://www.pullthatupjamie.ai`

## Understanding Requests

Users make natural language requests. Decompose them into composable atoms:

| Atom | Signal Words | Action |
|---|---|---|
| **guest/org** | person's name, company name | Use People endpoint to find their episodes |
| **feed filter** | "from [show]", "on TFTC" | Use `feedIds` to restrict search |
| **episode filter** | "#716", "latest episode" | Find specific episode, search within it |
| **date filter** | "2026", "latest", "recent" | Use `minDate`/`maxDate` params or filter results |
| **count** | "8 clips", "top 5" | Target that many in final output |
| **topic** | "about mining", "energy FUD" | Primary semantic search query |
| **session** | "build a session", "share it" | Full workflow: search → curate → create session → return URL |
| **compare** | "X vs Y", "contrast" | Dual-angle search, contrasting clips |
| **ingest** | "add this podcast" | On-demand ingestion workflow (see Ingestion section) |
| **scan** | "what pods do you have" | Browse corpus feeds |
| **chain** | "ingest then search" | Sequential: complete first action, then proceed |

### Example Decompositions

| Request | Atoms | Strategy |
|---|---|---|
| "Clips from Jesse Shrader's latest TFTC appearance" | guest(Jesse Shrader) + feed(TFTC) + episode(latest) | People endpoint → find TFTC episode → search topics within it |
| "Build a session on energy FUD, 2026 only" | topic(energy FUD) + date(2026) + session | Multi-angle search with date filter → curate → session |
| "Compare what TFTC vs Simply Bitcoin say about mining" | compare + feed(TFTC, Simply Bitcoin) + topic(mining) | Search mining in each feed separately → contrast |
| "What does Amboss do?" | org(Amboss) | People endpoint with "Amboss" → find episodes → search topics |

---

## People & Organizations

Find episodes featuring a person, company, or affiliation. Works for guests, creators, AND organizations.

**Important:** The People endpoint tracks explicit guest **appearances** — people who were on the show. It does NOT find mentions or discussions about someone. For widely-discussed figures (e.g. Lyn Alden, Elon Musk, Satoshi), combine People (for direct appearances) with semantic search (for clips discussing their ideas).

### List People
```bash
curl -s "API_BASE/api/corpus/people"
```
Returns names, appearance counts, roles, and recent episodes. No auth required.

### Find Episodes by Person/Org
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name": "Jesse Shrader"}' \
  "API_BASE/api/corpus/people/episodes"
```
Works with person names ("Jesse Shrader") AND company/org names ("Amboss", "Bloomberg"). Returns episodes with guids, feedIds, dates, and roles.

**Recommended workflow for guest queries:** People endpoint → get their episodes → search within those episodes for specific topics. For broadly-discussed figures, also run semantic searches across the full corpus to catch clips where others discuss their ideas.

---

## Search Strategy: Choosing the Right Endpoint

Before searching, **triage the request type**. The API has three search layers — use the most specific one first:

| Request Type | Best Method | Endpoint(s) | Example |
|---|---|---|---|
| **Specific episode by title/number** | Episode title search | 1. `/corpus/feeds?search=<podcast>`<br>2. `/corpus/feeds/:feedId/episodes?search=<title>` | "Find NAG25: Berlin" |
| **Topic within known episode** | Chapter keywords | 1. Get episode guid<br>2. `/corpus/episodes/:guid/chapters`<br>3. Filter keywords client-side | "Privacy topics in NAG25" |
| **All episodes from feed** | List episodes | `/corpus/feeds/:feedId/episodes` (paginated) | "All Bitcoin Park episodes" |
| **Topic across corpus** | Semantic search | `/search-quotes` with optional filters | "What do podcasters say about tariffs?" |
| **Hybrid** (episode + topic) | Episode search → chapters → semantic fallback | Try title/chapters first, semantic if needed | "Zaprite episode discussing payments" |

### Why This Order Matters

- **Episode title search** is instant and exact (no token cost)
- **Chapters** give structured navigation within episodes — headlines, keywords, timestamps
- **Semantic search** is powerful but searches 1.9M paragraphs — slower, costs tokens

**When in doubt:** If a user mentions an episode title/number, try title search first. Only fall back to semantic if title search fails.

### Episode Title Search

Find episodes by name/number across the corpus:

```bash
# Step 1: Find the feed
curl -s "API_BASE/api/corpus/feeds?search=News+and+Guidance"
# Returns: feedId (e.g., 7648986)

# Step 2: Search episode titles within that feed
curl -s "API_BASE/api/corpus/feeds/7648986/episodes?search=Berlin&limit=20"
```

**No auth required** for corpus browsing. Returns:
- `title` — episode name
- `guid` — episode identifier (use for chapters and clip search)
- `publishedDate`, `duration`, `creator`, `imageUrl`

Search is fuzzy — "Berlin" matches "NAG25: Berlin, Germany".

### Chapter Search

Get structured topic navigation within an episode:

```bash
curl -s "API_BASE/api/corpus/episodes/EPISODE_GUID/chapters"
```

Returns chapters with:
- `headline` — chapter title
- `keywords` — array of topic tags (e.g., `["privacy tools", "Lightning Network"]`)
- `summary` — brief description
- `startTime`, `endTime`, `duration` — timestamps for clip generation
- `pineconeId` — use for semantic search or session items

**Use case:** "What privacy topics are in NAG25?" → get chapters → filter by keywords like "privacy", "encryption", "surveillance".

**Limitation:** No corpus-wide chapter search yet (only episode-level). To search chapters across all episodes, you'd need to iterate through episodes first.

---

## Retrieve: Semantic Search

When title/chapter search doesn't fit, use semantic search across all transcribed content:

```bash
curl -s -X POST \
  -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin Lightning Network scaling", "limit": 10}' \
  "API_BASE/api/search-quotes"
```

### Parameters
- `query` — semantic search string
- `limit` — number of results (default 10)
- `feedIds` — array of feed IDs to filter by specific podcasts
- `guid` — filter to a specific episode
- `minDate` / `maxDate` — date range filter
- `episodeName` — filter by episode title

### Response Fields
Each result contains:
- `shareLink` — unique clip ID (use as `pineconeId` for sessions)
- `quote` — transcript text
- `episode` — episode title
- `creator` — podcast name
- `audioUrl` — direct audio file link
- `date` — publish date
- `similarity.combined` — relevance score (0-1, aim for >0.84)
- `timeContext.start_time` / `end_time` — timestamp in seconds
- `shareUrl` — **deeplink to exact audio moment** (give these to users!)
- `listenLink` — original episode link
- `episodeImage` — artwork

### Multi-Angle Search Strategy

For thorough coverage, run 4-6 queries per topic from different angles:

1. **Broad topic** — "lightning network privacy"
2. **Comparative** — "why lightning is more private than on-chain"
3. **Technical** — "onion routing payment channels"
4. **Contrarian** — "lightning surveillance risks"
5. **Adjacent** — "ecash lightning combined privacy"

Deduplicate results by `shareLink` across all queries.

### Cost
~$0.002 per search. A full research session (6 queries × 10 results) costs ~$0.012.

---

## Research: Build Sessions

Research sessions are **interactive visual artifacts** — not text dumps. Users can:
- Play each audio clip inline
- Browse clips visually
- Click deeplinks to exact audio moments
- Share the session with anyone

**The session URL is your primary deliverable.** Supplement with a brief summary, but always lead with the link.

### Create a Session
```bash
curl -s -X POST \
  -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Compelling Session Title",
    "description": "🔥 Theme one\n⚡ Theme two\n💡 Theme three",
    "pineconeIds": ["clip_id_1", "clip_id_2"],
    "items": [
      {
        "pineconeId": "clip_id_1",
        "metadata": {
          "text": "quote text",
          "creator": "Podcast Name",
          "episodeTitle": "Episode Title",
          "audioUrl": "https://...",
          "episodeImage": "https://...",
          "listenLink": "https://...",
          "date": "2025-01-01",
          "start_time": 120.5,
          "end_time": 180.3,
          "shareUrl": "https://...",
          "shareLink": "clip_id_1"
        }
      }
    ]
  }' \
  "API_BASE/api/research-sessions?clientId=PAYMENT_HASH"
```

Returns `{"data": {"id": "SESSION_ID"}}` — note: `data.id`, not `id`.

**`clientId` is required.** Pass your `paymentHash` as `clientId` via query param, header, or body. Without it the API returns "Missing owner identifier".

### Session URL
```
https://www.pullthatupjamie.ai/app?researchSessionId=SESSION_ID
```
NOT `pullthatupjamie.ai/researchSession/ID` (that 404s).

### Critical: Always Include `items` with Full Metadata
The backend needs client-provided metadata. Without the `items` array, clips save with `metadata: null` and the session breaks.

### Curation Standards
- **10-12 clips per session** (18+ causes server hangs)
- **3 emoji bullet points** in description, one theme each
- **Compelling title** — specific, not generic
- **Most compelling clips first** — users scroll and bounce
- **Cap 2 clips per episode**, 3 per creator for diversity
- **Filter ad reads:** "brought to you by", "use code", sponsor URLs
- **Similarity > 0.83** preferred
- Clips must be substantive — no hot takes without depth, no casual banter

---

## Analyze: Run Analysis

```bash
curl -s -X POST \
  -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  "API_BASE/api/research-sessions/SESSION_ID/analyze"
```
Returns AI-generated analysis of the session content.

---

## Share Sessions

Generate a public share link with 3D visualization:

```bash
curl -s -X POST \
  -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Share Title",
    "visibility": "public"
  }' \
  "API_BASE/api/research-sessions/SESSION_ID/share?clientId=PAYMENT_HASH"
```

`nodes` array is **optional** — if omitted, the backend auto-generates a semantically meaningful 3D layout from stored embeddings (UMAP projection). Omit for best results. Only pass `nodes` if you need a custom layout.

Shared URL: `https://www.pullthatupjamie.ai/app?sharedSession=SHARE_ID`

---

## Corpus Exploration

### Browse Feeds (no auth required)
```bash
curl -s "API_BASE/api/corpus/feeds?page=1"
```
Paginated (50/page). **Always paginate** with `?page=N`. Response data under `data` key (not `feeds`).

### Corpus Stats
```bash
curl -s "API_BASE/api/corpus/stats"
```

### Feed Episodes
```bash
curl -s -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  "API_BASE/api/corpus/feeds/FEED_ID/episodes"
```

Use corpus exploration to answer:
- "What podcasts are available?" → paginate feeds
- "Is [show] indexed?" → search feeds by title
- "What's the latest episode?" → check feed episodes by date

---

## Ingestion: Add New Podcasts

If a podcast isn't in the corpus yet, ingest it on demand from any RSS feed. All endpoints proxied through the Jamie API for security.

### Step 1: Search for the Podcast
```bash
curl -s -X POST "https://www.pullthatupjamie.ai/api/rss/searchFeeds" \
  -H "Content-Type: application/json" \
  -d '{"podcastName": "Podcast Name"}'
```
Returns `data.feeds[]` with `id` (feedId), `title`, `url` (RSS URL).

### Step 2: Get Feed Episodes
```bash
curl -s -X POST "https://www.pullthatupjamie.ai/api/rss/getFeed" \
  -H "Content-Type: application/json" \
  -d '{
    "feedUrl": "https://feeds.example.com/feed.xml",
    "feedId": "12345",
    "limit": 50,
    "skipCleanGuid": true
  }'
```
Returns:
- `episodes.feedInfo` — feed metadata (feedGuid, feedTitle, etc.)
- `episodes.episodes[]` — array of episodes with `episodeGUID`, `itemTitle`, `publishedDate`, `enclosureUrl`

Extract `feedGuid` from `feedInfo.feedGuid`.

### Step 3: Confirm with User
**Always show the episode list and get approval before ingesting.** Never auto-submit. Present episode titles and dates for review.

### Step 4: Submit Ingestion
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: PREIMAGE:PAYMENT_HASH" \
  -d '{
    "message": "Ingest episodes for [Podcast Name]",
    "parameters": {},
    "episodes": [
      {"guid": "episode-guid", "feedGuid": "feed-guid", "feedId": 12345}
    ]
  }' \
  "https://www.pullthatupjamie.ai/api/on-demand/submitOnDemandRun"
```
- `parameters` must be `{}` (required but empty)
- Response: `jobId` at top level
- `guid` comes from `episodeGUID` field in getFeed response
- `feedGuid` comes from `feedInfo.feedGuid` field

### Step 5: Poll Status
```bash
curl -s "https://www.pullthatupjamie.ai/api/on-demand/getOnDemandJobStatus/JOB_ID" \
  -H "Authorization: PREIMAGE:PAYMENT_HASH"
```
Poll every 30-60 seconds. Status: `pending` → `complete` or `failed`. Typical: 8 episodes in ~1 minute.

---

## Known Feed IDs
| Feed | ID |
|---|---|
| TFTC | 226249 |
| Bitcoin Park | 5702105 |
| Thank God for Nostr | 6437926 |
| Stacker News Live | 4866432 |
| Stacker Sports Pod | 7050096 |
| No Agenda Show | 41504 |
| Convos On The Pedicab | 3498055 |

Browse `GET /api/corpus/feeds` for the full list.

---

## Footguns
- API base: `https://www.pullthatupjamie.ai` (must include `www.` — bare domain redirects and breaks API calls)
- `episodeCount` in feeds response caps at 1,000 per feed — not the true count for large feeds
- People/episodes responses have `feedTitle: null` — cross-reference `feedId` with corpus/feeds to get show names
- Session response: `data.id`, NOT `id`
- Feeds response: `data` key, NOT `feeds`
- Always include `items` array with metadata in session creation
- Share endpoint: `nodes` is optional (backend auto-layouts from embeddings if omitted)
- `shareLink` = `pineconeId` (interchangeable)
- RSS endpoints: Always use `/api/rss/*` (proxied through Jamie API for security)
- `submitOnDemandRun` needs `"parameters": {}` even if empty
- Always confirm episodes with user before ingesting
- If results look wrong, check the echoed `query` field in the response — it should match your input exactly
