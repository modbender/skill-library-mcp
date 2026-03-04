---
strategy: rss-manager
version: 1.0.0
steps: 6
---

# RSS Manager Strategy

## Step 1: Source Monitoring & Feed Ingestion

- Enumerate all subscribed feed URLs from the user's feed list
- For each feed, execute a conditional HTTP GET request:
  - Include `If-None-Match` (ETag) and `If-Modified-Since` headers from the previous poll
  - Set `Accept: application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9`
  - Set a 30-second timeout per feed
- Process HTTP responses:
  - IF **304 Not Modified** THEN skip parsing, record successful poll, move to next feed
  - IF **301 Moved Permanently** THEN update the stored feed URL and process the redirect target
  - IF **410 Gone** THEN mark the feed as dead, alert the user, and remove from active polling
  - IF **429 Too Many Requests** THEN read `Retry-After` header, schedule retry, and double the polling interval for this feed
  - IF **4xx/5xx error** THEN log the failure, increment the feed's error counter, and apply the error handling rules from knowledge/best-practices.md
  - IF **200 OK** THEN proceed to parsing
- Detect the feed format (RSS 2.0, RSS 1.0/RDF, or Atom 1.0) from the root XML element
- Parse the feed using namespace-aware XML parsing, following encoding detection priority from knowledge/domain.md
- IF XML parsing fails THEN attempt lenient recovery: (1) fix common XML issues (unescaped `&`, invalid bytes), (2) retry with HTML-tolerant parser, (3) flag feed as unhealthy if recovery fails
- Store the response `ETag` and `Last-Modified` headers for the next conditional request
- Update the feed's health metrics: success/failure count, average response time, last successful poll timestamp
- Apply adaptive polling: adjust the next poll interval based on historical update frequency (see knowledge/best-practices.md)

## Step 2: Content Extraction & Normalization

- For each new item/entry in the parsed feed, extract metadata using the priority order from knowledge/domain.md:
  - **Title**: `<title>` -> first line of description; strip HTML tags, decode entities, trim whitespace
  - **URL**: `<link>` -> `<guid isPermaLink="true">` -> `<id>` (Atom); canonicalize per knowledge/domain.md URL rules
  - **Author**: `<dc:creator>` -> `<author><name>` -> `<author>` (email) -> `<managingEditor>`; extract name only
  - **Date**: `<dc:date>` -> `<published>` -> `<updated>` -> `<pubDate>`; parse all format variants to ISO 8601 UTC
  - **Body**: `<content:encoded>` -> `<content>` (Atom) -> `<description>` -> `<summary>`; sanitize HTML (strip `<script>`, `<iframe>`, event handlers)
  - **Categories**: all `<category>` elements + `<dc:subject>`; normalize casing, map known synonyms
  - **Media**: `<enclosure>` -> `<media:content>` -> `<media:thumbnail>` -> embedded `<img>` in body; extract URL, MIME type, dimensions
  - **GUID**: `<guid>` -> `<id>` -> canonicalized URL; use as the primary deduplication key
- IF title is missing AND body is missing THEN skip this item, log as malformed, increment feed's malformed-item counter
- IF date is missing or unparseable THEN use the current poll timestamp and flag the item with `dateUncertain: true`
- Extract plain text from HTML body for downstream NLP processing (deduplication, scoring, clustering)
- Compute word count and reading time estimate (`words / 238` for average reading speed)
- IF body content is truncated (< 100 words and ends with "..." or "[...]") THEN flag as `partialContent: true`

## Step 3: Deduplication

- Apply the multi-signal deduplication pipeline in order (cheapest to most expensive), following knowledge/best-practices.md:
- **Layer 1 -- GUID Match**: Compare each new item's GUID against the existing article database
  - IF exact GUID match found THEN check if content hash has changed:
    - IF content hash unchanged THEN mark as exact duplicate, skip
    - IF content hash changed THEN mark as article revision, update stored content, flag as "Updated"
- **Layer 2 -- URL Match**: Compare canonicalized URLs against the database
  - IF exact URL match found (after canonicalization) THEN merge, keeping the version with more content
- **Layer 3 -- Title Similarity**: For items that passed Layers 1-2:
  - Normalize titles: lowercase, strip punctuation, remove common prefixes ("Breaking:", "Update:", "ICYMI:", "JUST IN:")
  - Compute Jaccard similarity on word sets against all articles from the past 72 hours
  - IF title length >= 5 words AND Jaccard similarity >= 0.85 THEN flag as near-duplicate candidate
  - IF title length < 5 words AND Jaccard similarity >= 0.95 THEN flag as near-duplicate candidate
- **Layer 4 -- Content Fingerprinting**: For near-duplicate candidates from Layer 3:
  - Compute SimHash (64-bit) of the plain text body
  - IF Hamming distance <= 3 against any existing article THEN confirm as near-duplicate
  - ALTERNATIVELY: compute MinHash signatures (128 hashes) and use LSH (b=16, r=8) for candidate detection; confirm if Jaccard similarity >= 0.7
- **Layer 5 -- Entity Overlap**: For articles that are similar but not confirmed duplicates:
  - Extract named entities (people, organizations, locations) from both articles
  - IF entity overlap >= 80% AND publication dates within 24 hours THEN classify as "same event, different coverage"
- Assign dedup disposition to each article:
  - `unique` -- No match found, add to the article database
  - `exact_duplicate` -- Identical content, skip entirely
  - `revision` -- Updated version of an existing article, replace stored version
  - `near_duplicate` -- Substantially similar, cluster with the original
  - `same_event` -- Different coverage of the same event, cluster together

## Step 4: Importance Scoring

- For each article with disposition `unique`, `revision`, or `same_event`, compute a composite importance score (0-100):
- **Source Authority (25%)**:
  - Look up the feed's authority tier (T1-T5) from the source registry (see knowledge/best-practices.md)
  - Map tier to base score: T1=95, T2=80, T3=65, T4=50, T5=30
  - Adjust by feed health score: multiply by `(successful_polls / total_polls)` over the last 30 days
- **Recency (20%)**:
  - Compute hours since publication: `hours_old = (now - pubDate) / 3600`
  - Apply decay: `recency_score = 100 * e^(-0.03 * hours_old)`
  - IF `dateUncertain: true` THEN apply a 20% penalty to the recency score
- **Cross-Source Corroboration (20%)**:
  - Count the number of unique feeds that produced articles in the same dedup cluster
  - Compute: `corroboration_score = min(100, cluster_source_count * 25)`
  - Apply source diversity bonus: if cluster sources span 3+ authority tiers, add 10 points (capped at 100)
- **Topic Relevance (20%)**:
  - Compute TF-IDF vector of the article (title + first 200 words)
  - Compute cosine similarity against the user's interest profile vector
  - Scale to 0-100: `relevance_score = cosine_similarity * 100`
  - IF no user interest profile exists THEN default to 50 (neutral)
- **Content Depth (15%)**:
  - Evaluate content signals:
    - Word count: 0-200 words = 20pts, 200-500 = 50pts, 500-1000 = 75pts, 1000+ = 100pts
    - Contains data (numbers, statistics, percentages): +15pts
    - Contains structured content (tables, lists >= 3 items): +10pts
    - Has citations or external references (links to sources): +10pts
  - Cap at 100
  - IF `partialContent: true` THEN cap at 40 (cannot assess depth of truncated content)
- **Final score**: `importance = 0.25*authority + 0.20*recency + 0.20*corroboration + 0.20*relevance + 0.15*depth`
- SELF-CHECK: IF the highest scoring article is from a T5 source THEN review corroboration and relevance scores for anomalies

## Step 5: Topic Clustering

- Collect all articles from the current digest window (default: past 24 hours) that scored above the minimum threshold (default: importance >= 15)
- Prepare text features:
  - For each article, concatenate: title (weighted 2x) + first 200 words of plain text body
  - Preprocess: lowercase, remove stop words, apply stemming (Porter stemmer or equivalent)
  - Compute TF-IDF vectors using the current digest window as the corpus
- Apply DBSCAN clustering:
  - Distance metric: cosine distance (`1 - cosine_similarity`)
  - Parameters: `eps=0.4`, `min_samples=2`
  - Articles that do not cluster (noise points) are treated as standalone topics
- IF the user requests a fixed number of topics THEN use Agglomerative Clustering with `n_clusters=k` and Ward linkage instead of DBSCAN
- For each cluster, generate a topic label:
  1. Compute the cluster centroid (mean TF-IDF vector)
  2. Extract the top 3 terms by TF-IDF weight from the centroid
  3. Identify the most frequent named entity (person, org, or location) across cluster articles
  4. Compose label: IF named entity found THEN "[Entity]: [top terms]" ELSE "[Top 3 Terms]"
- Select a representative "lead" article for each cluster:
  1. Pick the article with the highest cosine similarity to the cluster centroid
  2. IF tie THEN prefer the article with the higher importance score
  3. IF still tied THEN prefer the article from the higher authority tier source
- Detect trend signals:
  - **Emerging topic**: Cluster that did not exist in the previous digest window but has 3+ articles now
  - **Growing topic**: Cluster whose article count increased by 50%+ compared to the previous window
  - **Declining topic**: Cluster whose article count decreased by 50%+ compared to the previous window
  - Tag clusters with trend indicators: `[EMERGING]`, `[TRENDING]`, `[FADING]`

## Step 6: Digest Assembly & Output

- Determine the digest type based on context:
  - IF user requested a specific digest type THEN use that format
  - IF scheduled delivery THEN use the time-appropriate format (morning brief, midday update, evening recap, weekly roundup)
  - DEFAULT: morning brief format
- Sort topic clusters by the maximum importance score of any article in the cluster (descending)
- Assemble the digest following the structure from knowledge/best-practices.md:
  - **Header**: Digest type, date range, total article count, duplicate count removed
  - **Top Stories** (importance >= 70): Full topic clusters with lead article summary (50-75 words), source attribution, importance score, trend indicator, and related article count
  - **Noteworthy** (importance 40-69): Condensed topic entries with one-line summaries and source/date
  - **Also Mentioned** (importance 15-39): Single-line entries with title, source, and link only
  - **Feed Health Report**: Feeds polled, success rate, error count, unhealthy feeds flagged, emerging/declining topics
- Apply digest sizing limits:
  - Morning brief / evening recap: max 15 top stories, 10 noteworthy, 10 also mentioned
  - Midday update: max 10 top stories, 5 noteworthy, 5 also mentioned
  - Weekly roundup: max 30 top stories, 15 noteworthy, 15 also mentioned
- For each digest item, include:
  - Topic label (with trend indicator if applicable)
  - Lead article: title, source name, source authority tier, publication date, URL, importance score
  - Summary: 50-75 words capturing the key facts and significance
  - Related articles: count and source names (e.g., "4 more from Reuters, BBC, TechCrunch, Ars Technica")
- SELF-CHECK before output:
  - Are all sources properly attributed with names and URLs?
  - Do top stories genuinely represent the most important developments?
  - Is the digest within sizing limits?
  - Are topic labels clear and informative?
  - Are trend indicators accurate (compare against previous digest)?
  - IF any check fails THEN adjust: re-rank, re-label, or trim as needed
