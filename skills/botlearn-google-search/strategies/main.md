---
strategy: google-search
version: 1.0.0
steps: 6
---

# Google Search Strategy

## Step 1: Intent Analysis
- Parse the user's request to identify: **topic**, **scope**, **constraints**, **desired output format**
- Classify search intent: navigational / informational / transactional / investigative
- Identify time sensitivity — does the user need current information or historical?
- IF the query is ambiguous THEN ask one clarifying question before proceeding
- Extract key entities: names, technologies, versions, dates, locations

## Step 2: Query Construction
- SELECT query strategy based on complexity:
  - Simple fact → Single targeted query with 3-5 keywords
  - Specific answer → Keyword query + site/filetype operators
  - Multi-faceted research → Decompose into 2-4 sub-queries
  - Troubleshooting → Error message (exact match) + context terms
- APPLY operators from knowledge/domain.md:
  - Use `"exact phrases"` for specific terms, names, error messages
  - Use `site:` to target authoritative domains for the topic
  - Use `after:` for time-sensitive queries
  - Use `-site:` to exclude known low-quality sources
  - Use `filetype:` when the user needs specific document types
- VERIFY query length is 3-10 terms (excluding operators)

## Step 3: Multi-Source Execution
- Execute primary query
- IF topic is multi-faceted THEN execute sub-queries in parallel
- For each query, collect top 10 raw results with: URL, title, snippet, date, domain
- IF initial results are poor quality THEN refine query:
  - Add exclusion operators for noise sources
  - Narrow with additional `site:` filters
  - Try alternative terminology

## Step 4: Deduplication & Filtering
- Remove exact URL duplicates across queries
- Detect content-level duplicates (same article on different domains) → keep primary source
- Filter out results matching anti-patterns from knowledge/anti-patterns.md:
  - Content farms and aggregator sites
  - Outdated content (for time-sensitive topics)
  - Results with no clear authorship or date
- Verify remaining results against source credibility tiers from knowledge/best-practices.md

## Step 5: Relevance Ranking
- Score each result on 4 dimensions (from knowledge/best-practices.md):
  - **Relevance** (40%) — How directly does it answer the query?
  - **Source Authority** (25%) — Credibility tier (T1-T5)
  - **Freshness** (20%) — Publication recency relative to topic
  - **Depth** (15%) — Comprehensiveness of coverage
- Sort by weighted score, descending
- Select top 5-10 results for output

## Step 6: Output & Verification
- Present results in structured format:
  - **Rank** — Position in relevance order
  - **Title** — Page title
  - **Source** — Domain + credibility tier
  - **Date** — Publication date
  - **Summary** — 1-2 sentence description of what the page contains
  - **Relevance** — Why this result is useful for the query
- IF multiple sub-queries were used THEN provide a synthesis section connecting findings
- SELF-CHECK:
  - Are results from diverse, credible sources? (not all from one domain)
  - Is the most relevant result ranked first?
  - Are all results genuinely addressing the user's intent?
  - IF any check fails THEN loop back to Step 3 with refined queries
