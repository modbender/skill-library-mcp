---
domain: rss-manager
topic: anti-patterns
priority: medium
ttl: 30d
---

# RSS Manager -- Anti-Patterns

## Feed Parsing Anti-Patterns

### 1. Assuming Well-Formed XML
- **Problem**: Treating all feeds as valid XML and failing hard on the first parse error. In practice, 5-15% of feeds in the wild contain malformed XML: unescaped ampersands, invalid characters, unclosed tags, or mixed encoding declarations
- **Fix**: Use a lenient XML parser with fallback strategies. On parse failure: (1) attempt HTML-tolerant parsing, (2) try fixing common issues (unescaped `&`, invalid UTF-8 bytes), (3) attempt regex-based extraction as last resort. Log parse errors per feed for health monitoring

### 2. Ignoring Namespace Prefixes
- **Problem**: Hardcoding namespace prefixes like `content:encoded` instead of resolving by namespace URI. Feed A might use `content:encoded` while Feed B uses `c:encoded` -- both map to the same namespace URI but a prefix-based parser breaks on Feed B
- **Fix**: Resolve all elements by their full namespace URI (`http://purl.org/rss/1.0/modules/content/`), not the prefix string. Use a namespace-aware XML parser

### 3. Trusting Feed-Declared Encoding
- **Problem**: Accepting the XML declaration's encoding attribute (`encoding="UTF-8"`) without verification. Many feeds declare UTF-8 but actually serve Windows-1252 or ISO-8859-1, causing mojibake in non-ASCII characters
- **Fix**: Detect actual encoding using BOM detection and byte-pattern analysis. If detected encoding conflicts with declared encoding, trust the detection. Always validate that decoded text is valid Unicode before processing

### 4. Ignoring Content Type Negotiation
- **Problem**: Not sending proper `Accept` headers when requesting feeds, or not checking the response `Content-Type`. Some servers return HTML error pages or redirects with `text/html` instead of the expected feed XML
- **Fix**: Send `Accept: application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9` header. Verify response `Content-Type` before parsing. If HTML is returned, attempt feed auto-discovery from the HTML page

## Deduplication Anti-Patterns

### 5. URL-Only Deduplication
- **Problem**: Deduplicating solely by comparing URLs. This misses: (1) the same article with different tracking parameters, (2) the same article syndicated to multiple domains, (3) updated articles with new URLs, and (4) AMP vs canonical URL variants
- **Fix**: Use the multi-signal deduplication pipeline from knowledge/best-practices.md. URL matching should be one layer (after canonicalization), not the only layer. Always combine with title similarity and content fingerprinting

### 6. Title-Only Deduplication
- **Problem**: Deduplicating solely by title match. Short titles like "Q3 Earnings Report" or "Weekly Update" produce massive false positive matches across unrelated feeds. Conversely, slightly reworded titles ("Company X Acquires Y" vs "Y Acquired by Company X") produce false negatives
- **Fix**: Never use title matching alone. Combine with at least one content-level signal (fingerprint or entity overlap). For titles under 5 words, require additional confirmation signals. Use fuzzy matching with appropriate thresholds per title length

### 7. Aggressive Deduplication Without Clustering
- **Problem**: Discarding all but one article when duplicates are detected, losing valuable diverse perspectives. If Reuters, BBC, and a domain expert all cover the same event, the domain expert's unique analysis gets discarded
- **Fix**: Cluster related articles rather than deleting duplicates. Select the most comprehensive article as the "lead" but preserve other sources as "Related" entries. The digest should show source diversity, not suppress it

### 8. Ignoring Article Updates
- **Problem**: Treating an article with a matching GUID but updated content as a duplicate and ignoring the update. Many feeds legitimately update articles: correcting errors, adding developments, or appending editor notes
- **Fix**: When a GUID matches but content has changed (detected via content hash), treat it as an article revision. Keep the latest version but note "Updated" in the digest. Track revision history for articles that update frequently

## Importance Scoring Anti-Patterns

### 9. Recency-Only Ranking
- **Problem**: Ranking articles purely by publication date, treating all newer articles as more important. This surfaces low-quality recent content above high-quality older content and is easily gamed by feeds that backdate or repeatedly update timestamps
- **Fix**: Use the multi-dimensional scoring model from knowledge/best-practices.md. Recency should be one factor (20% weight), balanced against source authority, cross-source corroboration, topic relevance, and content depth

### 10. Equal Source Weighting
- **Problem**: Treating all feed sources as equally authoritative. A random blog post and a Reuters wire report about the same event get the same importance score, leading to unreliable content surfacing in top stories
- **Fix**: Maintain per-source authority tiers (T1-T5) and apply authority weight to importance scoring. Initialize tiers from known source lists and refine based on historical signal quality, factual accuracy, and user feedback

### 11. Ignoring Cross-Source Corroboration
- **Problem**: Scoring articles independently without considering how many other sources cover the same story. A single blog post about an event gets the same importance as a story covered by 15 major outlets
- **Fix**: After deduplication clustering, use the cluster size as a corroboration signal. Stories covered by multiple independent sources are more likely to be genuinely important. Weight: cluster_size * source_diversity_factor

### 12. Static Interest Profiles
- **Problem**: Using a fixed user interest profile that never adapts. The user's interests shift over time, but the digest keeps surfacing topics they no longer care about while missing emerging interests
- **Fix**: Implement interest profile decay (reduce weight for unengaged topics by 10%/week) and reinforcement (boost topics the user clicks through on). Allow explicit user feedback ("more like this" / "less like this") to directly adjust weights

## Digest Generation Anti-Patterns

### 13. Information Overload Digests
- **Problem**: Including every article from every feed in the digest, producing an overwhelming wall of text. Users receiving 200+ item digests stop reading them entirely, defeating the purpose of aggregation
- **Fix**: Apply strict digest sizing limits from knowledge/best-practices.md. Morning briefs: 10-15 top stories with 50-75 word summaries. Use importance scoring to ruthlessly prioritize. Surface detail on demand ("Show me more about this topic") rather than by default

### 14. Flat List Presentation
- **Problem**: Presenting digest items as a flat chronological list with no organization. Users must scan the entire list to find topics they care about, and related articles about the same event appear scattered throughout
- **Fix**: Organize digests by topic clusters. Group related articles under topic headings. Within each topic, order by importance score. Provide a table of contents at the top with topic labels and article counts

### 15. Missing Source Attribution
- **Problem**: Summarizing articles without attributing the original source. Users cannot verify information, assess credibility, or navigate to the full article. Aggregation without attribution also raises ethical and legal concerns
- **Fix**: Every digest item must include: source name, publication date, direct URL to the original article, and source authority tier. When clustering, list all contributing sources

### 16. Stale Digest Windows
- **Problem**: Using a fixed 24-hour digest window regardless of user behavior or news cycle. Breaking news gets delayed until the next scheduled digest, while slow news days produce padding with low-quality content
- **Fix**: Support multiple digest cadences (morning brief, midday update, evening recap). Implement "breaking news" threshold: if an article scores above 90 importance and is from a T1 source, consider immediate notification outside the regular digest schedule

## Feed Health Anti-Patterns

### 17. Silent Feed Failures
- **Problem**: Continuing to poll feeds that consistently fail (404, 500, parse errors) without alerting the user. The user believes they are monitoring a source that has actually been dead for weeks
- **Fix**: Track per-feed error rate over a rolling window. After 3 consecutive failures or >50% failure rate over 7 days, mark the feed as unhealthy and alert the user. Suggest alternatives if available (e.g., the feed may have moved to a new URL)

### 18. No Feed Diversity Monitoring
- **Problem**: Not tracking the topical diversity of subscribed feeds. The user may subscribe to 20 feeds that all cover the same narrow topic, creating an echo chamber with massive duplication and no breadth
- **Fix**: Periodically analyze the topic distribution across all subscribed feeds. Report: "80% of your feeds cover AI/ML; consider adding feeds for [underrepresented topics based on stated interests]." Show a diversity dashboard with topic coverage breakdown

### 19. Ignoring Feed Freshness Decay
- **Problem**: Continuing to poll feeds at the same rate even when they haven't published new content in weeks or months. This wastes resources and clutters the feed list with dormant sources
- **Fix**: Implement adaptive polling (see knowledge/best-practices.md). After 14+ days of no new content, reduce polling to once daily. After 30+ days, reduce to weekly. After 90+ days, prompt the user: "This feed appears inactive. Keep monitoring or unsubscribe?"
