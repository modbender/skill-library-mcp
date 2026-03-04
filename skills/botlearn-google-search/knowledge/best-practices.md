---
domain: google-search
topic: query-construction-and-quality
priority: high
ttl: 30d
---

# Google Search — Best Practices

## Query Construction Patterns

### 1. Intent Classification First
Before constructing a query, classify the search intent:
- **Navigational** — User wants a specific site → use `site:` or direct URL terms
- **Informational** — User wants to learn → use descriptive terms + authoritative source filters
- **Transactional** — User wants to do something → include action verbs and tool names
- **Investigative** — User wants to compare/analyze → use comparison terms + multiple sources

### 2. Keyword Selection
- Use **nouns and noun phrases** as primary search terms
- Prefer **specific technical terms** over generic descriptions
- Include **version numbers** for software-related queries (e.g., "React 18", "Python 3.12")
- Use the **terminology of the target domain** (e.g., "myocardial infarction" not "heart attack" for medical research)

### 3. Query Decomposition for Complex Topics
When a topic is broad or multi-faceted:
1. Break into 2-4 focused sub-queries
2. Each sub-query targets one aspect
3. Merge and deduplicate results
4. Cross-reference findings across sub-queries

Example: "What are the environmental and economic impacts of electric vehicles?"
- Sub-query 1: `electric vehicles environmental impact lifecycle emissions`
- Sub-query 2: `electric vehicles economic analysis cost ownership`
- Sub-query 3: `EV vs ICE environmental comparison study`

### 4. Iterative Refinement
- Start broad, then narrow based on initial results
- Add exclusions (`-term`) to filter noise discovered in initial results
- Switch to `site:` filters when you identify authoritative domains

## Result Quality Assessment

### Source Credibility Tiers

| Tier | Source Type | Trust Level | Examples |
|------|-----------|-------------|---------|
| T1 | Primary / Official | Highest | Government data, academic journals, official docs |
| T2 | Established Media | High | Reuters, AP, major newspapers, peer-reviewed blogs |
| T3 | Expert Community | Medium-High | Stack Overflow (high-rep), GitHub (popular repos), industry blogs |
| T4 | General Web | Medium | Wikipedia, Medium, personal blogs with citations |
| T5 | User-Generated | Low | Forums, social media, anonymous posts |

### Freshness Assessment
- Check publication date — prefer recent for technology, less critical for fundamentals
- Verify the content hasn't been superseded by newer information
- For software: match the version discussed to the user's version

### Deduplication Strategy
1. **URL-level** — Same URL from different queries → keep one
2. **Content-level** — Same article syndicated across sites → keep the primary source
3. **Fact-level** — Multiple sources stating the same fact → consolidate, cite best source

## Result Ranking Criteria

Rank results by weighted combination:
1. **Relevance** (40%) — How directly does it answer the query?
2. **Source Authority** (25%) — Credibility tier of the source
3. **Freshness** (20%) — How recent is the information?
4. **Depth** (15%) — How comprehensive is the coverage?
