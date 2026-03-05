---
domain: rss-manager
topic: feed-management-dedup-and-scoring
priority: high
ttl: 30d
---

# RSS Manager -- Best Practices

## Feed Collection & Polling

### 1. Respect Publisher Update Intervals

Before polling a feed, check for update frequency hints:
- **RSS `<ttl>`** -- Minutes the feed can be cached (e.g., `<ttl>60</ttl>` means poll no more than once per hour)
- **Atom `<sy:updatePeriod>` and `<sy:updateFrequency>`** -- e.g., `hourly` with frequency `1` means once per hour
- **HTTP `Cache-Control` / `Expires` headers** -- Standard cache directives
- **HTTP `ETag` / `Last-Modified` headers** -- Use conditional requests (`If-None-Match`, `If-Modified-Since`) to avoid re-downloading unchanged feeds

Default polling schedule when no hints are available:

| Feed Type | Suggested Interval | Rationale |
|-----------|-------------------|-----------|
| Breaking news | 15 minutes | High update frequency expected |
| Major news outlets | 30 minutes | Regular updates throughout the day |
| Blog / personal site | 2-4 hours | Updates less frequently |
| Weekly newsletter | 12-24 hours | Low frequency, conserve resources |
| Dormant / low-activity | 24 hours | Check daily, reclassify if activity increases |

### 2. Adaptive Polling

Track feed update patterns over time and adjust polling frequency:
- If a feed hasn't changed in 5 consecutive polls, double the interval (up to 24 hours max)
- If a feed has new content on every poll, halve the interval (down to the minimum allowed by TTL/headers)
- Track the average number of new items per poll to predict optimal timing
- Maintain a per-feed "reliability score" based on: uptime, valid XML rate, consistent timestamps

### 3. Error Handling

- **HTTP 301 (Moved Permanently)** -- Update the stored feed URL
- **HTTP 410 (Gone)** -- Mark feed as dead; alert the user; stop polling
- **HTTP 429 (Too Many Requests)** -- Back off using `Retry-After` header; double interval
- **XML parse failures** -- Attempt recovery with lenient parsing; if persistent (3+ failures), flag feed as unhealthy
- **Timeout** -- Set a 30-second timeout per feed; retry once after 60 seconds; mark as slow if persistent

## Deduplication Strategies

### Multi-Signal Deduplication Pipeline

Deduplication should use a layered approach, from cheapest to most expensive:

#### Layer 1: GUID / Entry ID Match (Exact)
- Compare `<guid>` (RSS) or `<id>` (Atom) values directly
- Cheapest and most reliable when present
- Caveat: Some feeds reuse GUIDs or change them on updates

#### Layer 2: URL Canonicalization Match (Exact)
- Canonicalize URLs (see knowledge/domain.md) and compare
- Catches the same article shared via different tracking URLs
- Handles `http` vs `https`, `www` vs non-www variants

#### Layer 3: Title Similarity (Fuzzy)
- Normalize titles: lowercase, strip punctuation, remove common prefixes ("Breaking:", "Update:", "ICYMI:")
- Use Jaccard similarity on word sets; threshold >= 0.85 indicates a likely duplicate
- For short titles (< 5 words), require higher threshold (>= 0.95) to avoid false positives
- Optionally use Levenshtein distance ratio as a secondary signal

#### Layer 4: Content Fingerprinting (Fuzzy)
- **SimHash**: Compute a 64-bit fingerprint of the article body (after HTML stripping and normalization). Articles with Hamming distance <= 3 are near-duplicates
- **MinHash with LSH (Locality-Sensitive Hashing)**: Compute k-shingle sets, generate MinHash signatures (128 hashes), use LSH bands (b=16, r=8) for candidate pair detection. Jaccard similarity >= 0.7 confirms near-duplicate
- **Sentence-level overlap**: Extract the first 3 non-trivial sentences (> 10 words each); if 2+ match another article, flag as near-duplicate

#### Layer 5: Entity & Fact Overlap (Semantic)
- Extract named entities (people, organizations, locations, dates) from both articles
- If entity overlap >= 80% and temporal proximity <= 24 hours, likely covering the same event
- Use this layer to merge "same story, different angle" articles into a cluster rather than discarding

### Dedup Decision Matrix

| Signal Combination | Action |
|-------------------|--------|
| GUID match | Exact duplicate -- merge, keep latest version |
| URL match (after canonicalization) | Exact duplicate -- merge, keep the one with more content |
| Title similarity >= 0.85 + URL domain differs | Near-duplicate from different sources -- cluster together |
| Content fingerprint match | Near-duplicate -- cluster together, note source diversity |
| Entity overlap >= 80% + within 24h | Same event coverage -- cluster, select most comprehensive as primary |
| Title similarity >= 0.85 + content fingerprint mismatch | Updated/revised article -- keep both, flag as revision |

## Importance Scoring

### Weighted Scoring Model

Score each article on a 0-100 scale using the following weighted dimensions:

| Dimension | Weight | Signal Sources |
|-----------|--------|---------------|
| Source Authority | 25% | Domain reputation tier (T1-T5), historical accuracy, feed health score |
| Recency | 20% | Publication age relative to poll time; decay function: `score = 100 * e^(-0.03 * hours_old)` |
| Cross-Source Corroboration | 20% | Number of independent sources covering the same story (from dedup clustering) |
| Topic Relevance | 20% | Cosine similarity between article TF-IDF vector and user interest profile vector |
| Content Depth | 15% | Word count (normalized), presence of data/citations, structured content (tables, lists) |

### Source Authority Tiers

| Tier | Description | Base Score | Examples |
|------|-------------|------------|---------|
| T1 | Wire services, official sources | 90-100 | Reuters, AP, government feeds, RFC publications |
| T2 | Major established outlets | 75-89 | NYT, BBC, Nature, IEEE Spectrum |
| T3 | Respected niche/industry sources | 60-74 | TechCrunch, Ars Technica, The Verge, domain-specific journals |
| T4 | Community & expert blogs | 40-59 | Popular personal blogs, Medium publications with editors, curated newsletters |
| T5 | Unverified / user-generated | 20-39 | Anonymous blogs, auto-generated feeds, low-quality aggregators |

### Recency Decay Function

Apply an exponential decay to the recency score so that newer articles score higher:

```
recency_score = 100 * e^(-lambda * hours_since_publication)

lambda = 0.03  (half-life ~ 23 hours)
```

| Age | Recency Score |
|-----|--------------|
| 0 hours | 100 |
| 6 hours | 84 |
| 12 hours | 70 |
| 24 hours | 49 |
| 48 hours | 24 |
| 72 hours | 12 |

Adjust lambda per user preference: set lambda lower (e.g., 0.01) for users who prefer weekly digests; higher (e.g., 0.05) for real-time monitoring.

### User Interest Profile

Maintain a vector of topic weights representing the user's interests:
- Initialize from explicit topic subscriptions and feed categories
- Update dynamically based on click-through behavior (articles the user reads vs skips)
- Decay stale interests: reduce weight by 10% per week for topics the user hasn't engaged with
- Use the interest profile vector to compute topic relevance scores via cosine similarity with article TF-IDF vectors

## Topic Clustering

### TF-IDF Vectorization

1. Preprocess text: lowercase, remove stop words, apply stemming or lemmatization
2. Compute TF-IDF vectors using the corpus of articles from the current digest window
3. Use only the title + first 200 words of the body for efficiency
4. Maintain a background IDF model updated weekly from all ingested articles

### Clustering Algorithm Selection

| Method | When to Use | Parameters |
|--------|------------|------------|
| DBSCAN | Default choice; handles variable cluster sizes and noise well | eps=0.4 (cosine distance), min_samples=2 |
| Agglomerative (Ward) | When you need a fixed number of topics (e.g., "give me 5 topics") | n_clusters=k, linkage=ward |
| Online K-Means | Streaming / real-time updates where articles arrive continuously | n_clusters=k (estimated from historical data) |

### Cluster Labeling

For each cluster, generate a human-readable topic label:
1. Extract the top 3 TF-IDF terms from the cluster centroid
2. Identify the most common named entity (person, org, or location) across cluster articles
3. Combine into a label: "[Named Entity]: [Top Terms]" (e.g., "OpenAI: language model GPT release")
4. If no clear named entity, use the top 3 terms as the label

### Representative Article Selection

From each cluster, select one "lead" article to represent the topic:
1. Pick the article closest to the cluster centroid (most representative)
2. Break ties by importance score (higher is better)
3. Break further ties by source authority tier (prefer T1/T2)
4. Include the lead article's summary in the digest; list other cluster articles as "Related"

## Digest Generation

### Digest Structure

```
# Daily Digest -- [Date]
## Top Stories (importance >= 70)
  [Topic Label 1]
    - Lead article summary (source, date, importance score)
    - Related: [n] more articles from [sources]
  [Topic Label 2]
    - ...

## Noteworthy (importance 40-69)
  [Topic clusters organized by category]

## Also Mentioned (importance < 40)
  [Brief one-line entries]

## Feed Health Report
  - [n] feeds polled, [n] successful, [n] errors
  - [n] new articles, [n] duplicates removed
  - Emerging topic: [topic gaining traction]
  - Declining topic: [topic losing traction]
```

### Digest Sizing

| Digest Type | Max Stories | Max Words per Summary | Delivery Window |
|-------------|-----------|---------------------|----------------|
| Morning brief | 10-15 | 50-75 | 06:00-08:00 local |
| Midday update | 5-10 | 30-50 | 11:30-13:00 local |
| Evening recap | 10-15 | 50-75 | 17:00-19:00 local |
| Weekly roundup | 20-30 | 100-150 | Saturday/Sunday morning |
