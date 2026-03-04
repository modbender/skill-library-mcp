---
domain: google-search
topic: anti-patterns
priority: medium
ttl: 30d
---

# Google Search — Anti-Patterns

## Query Construction Anti-Patterns

### 1. Overly Long Queries
- **Problem**: Queries with 10+ terms dilute relevance; Google ignores excess terms
- **Fix**: Focus on 3-7 high-signal keywords, use operators to add precision without verbosity

### 2. Natural Language Queries
- **Problem**: Searching "What is the best way to implement authentication in a React application?" treats every word equally
- **Fix**: Extract key terms: `React authentication implementation best practices`

### 3. Missing Context Terms
- **Problem**: Searching `merge` without context returns results about git, mail merge, corporate mergers, etc.
- **Fix**: Add domain context: `git merge conflict resolution` or `pandas merge dataframe`

### 4. Ignoring Operator Case Sensitivity
- **Problem**: `or` is treated as a regular word; only `OR` works as a Boolean operator
- **Fix**: Always use uppercase `OR`, and remember `-` must touch the excluded term (no space)

### 5. Single-Query Dependency
- **Problem**: Relying on one query for complex, multi-faceted topics
- **Fix**: Decompose into 2-4 targeted sub-queries, merge results

## Result Evaluation Anti-Patterns

### 6. First-Result Bias
- **Problem**: Treating the first search result as the authoritative answer
- **Fix**: Examine at least 3-5 results; first result may be SEO-optimized, not most accurate

### 7. Ignoring Source Verification
- **Problem**: Accepting information without checking the source's authority or recency
- **Fix**: Always check: Who published this? When? Are claims cited? Is the domain reputable?

### 8. Single-Source Dependency
- **Problem**: Using only one source to answer a question
- **Fix**: Cross-reference key facts across 2-3 independent sources; flag single-source claims

### 9. Ignoring Date Context
- **Problem**: Returning outdated information for rapidly evolving topics (frameworks, APIs, regulations)
- **Fix**: Use `after:` date filters; always note the publication date in results; flag if content may be outdated

### 10. Content Farm Inclusion
- **Problem**: Including results from low-quality aggregator sites that scrape and rewrite content
- **Fix**: Exclude known content farms with `-site:`; prefer domains with original analysis or primary data

## Output Anti-Patterns

### 11. Raw URL Dumping
- **Problem**: Returning a list of URLs without context, relevance scores, or summaries
- **Fix**: Each result should include: title, source, date, relevance note, and a 1-2 sentence summary

### 12. No Deduplication
- **Problem**: Returning the same information from multiple syndicated sources
- **Fix**: Deduplicate at content level, keep the primary/authoritative source
