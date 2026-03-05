---
domain: academic-search
topic: anti-patterns
priority: medium
ttl: 30d
---

# Academic Search -- Anti-Patterns

## Query Construction Anti-Patterns

### 1. Natural Language Search Queries
- **Problem**: Submitting conversational queries like "What are the best methods for detecting fake images?" to academic APIs. Academic databases perform poorly on natural language; they expect keyword-based queries.
- **Fix**: Extract core concepts and use database-specific syntax. Transform to: `ti:deepfake+detection+AND+cat:cs.CV` (arXiv) or `query=deepfake detection generative adversarial&fieldsOfStudy=Computer Science` (Semantic Scholar).

### 2. Single-Database Dependency
- **Problem**: Searching only arXiv and missing published journal papers, or searching only Google Scholar and missing very recent preprints uploaded in the last 48 hours.
- **Fix**: Always query at least 2 databases. Use arXiv for the freshest preprints, Semantic Scholar for structured metadata and citation graphs, and Google Scholar for the broadest coverage including theses and technical reports.

### 3. Overly Broad Queries
- **Problem**: Searching for "machine learning" without topic, method, or application constraints returns millions of irrelevant results.
- **Fix**: Add specificity through subtopic terms, category filters, date ranges, and venue constraints. "machine learning" becomes `"graph neural network" protein structure prediction 2023-` with `fieldsOfStudy=Computer Science,Biology`.

### 4. Overly Narrow Queries
- **Problem**: Using hyper-specific technical jargon that returns 0 results because the exact phrasing does not match paper titles or abstracts. For example, searching `"multi-head cross-attention with rotary position embeddings"` may miss papers that use slightly different terminology.
- **Fix**: Start specific, then progressively broaden. Use OR clauses with synonymous terms. Check if zero results means the topic is genuinely niche or your terminology is misaligned with the literature.

### 5. Ignoring Field-Specific Terminology
- **Problem**: Using CS terminology when searching for biomedical papers, or vice versa. Different fields use different terms for the same concepts (e.g., "feature" in ML vs. "biomarker" in medicine).
- **Fix**: Consult the keywords section of one known relevant paper to identify field-appropriate terminology. Use Semantic Scholar's `fieldsOfStudy` filter to disambiguate.

## Ranking & Selection Anti-Patterns

### 6. Citation Count Bias
- **Problem**: Ranking papers primarily by citation count. This biases toward older papers (more time to accumulate citations), popular fields (more researchers citing each other), and anglophone research (English papers cited more globally). A 2024 paper with 15 citations may be more impactful for the user than a 2018 paper with 500.
- **Fix**: Use **citation velocity** (citations per year) and **influential citation count** (Semantic Scholar) instead of raw citation count. Weight recency appropriately for fast-moving fields. A paper with 15 influential citations in 1 year may outrank one with 500 total citations over 6 years.

### 7. Ignoring Methodology Quality
- **Problem**: Selecting papers based solely on claimed results without evaluating the methodology. Papers may report impressive numbers from flawed experimental setups, cherry-picked baselines, or non-standard evaluation metrics.
- **Fix**: Check for: (a) comparison against established baselines, (b) use of standard benchmark datasets, (c) statistical significance reporting, (d) ablation studies, (e) reproducibility indicators (code/data availability). Apply the methodology rigor factor from the ranking framework in best-practices.md.

### 8. Recency Bias
- **Problem**: Automatically preferring the newest papers and dismissing foundational work. Users may miss seminal papers that define the field's core concepts, or survey papers that provide essential context.
- **Fix**: Include at least one foundational or survey paper when the user is exploring a new topic. Explicitly distinguish between "latest results" and "essential background." A 2017 paper that introduced a paradigm (e.g., "Attention Is All You Need") is critical context even if the user asked for recent work.

### 9. Venue Snobbery
- **Problem**: Dismissing papers from workshops, smaller conferences, or preprints solely based on venue prestige. Groundbreaking work sometimes appears first in workshops or on arXiv before being published at a top venue.
- **Fix**: Assess the paper on its own merits (methodology, results, clarity) rather than venue alone. Note the venue tier but do not automatically exclude lower-tier publications. Flag preprints as "not yet peer-reviewed" rather than excluding them.

### 10. Popularity Echo Chamber
- **Problem**: Returning only the most-cited papers leads to an echo chamber where the same 5-10 well-known papers appear for every query in a field, missing diverse perspectives and newer approaches.
- **Fix**: Deliberately include at least 1-2 papers from different research groups, geographic regions, or methodological traditions. Use Semantic Scholar's "recommended papers" feature to discover less obvious but relevant work.

## Result Presentation Anti-Patterns

### 11. Missing Publication Status
- **Problem**: Presenting arXiv preprints alongside peer-reviewed journal articles without distinguishing between them. Users may assume all results have undergone peer review.
- **Fix**: Always indicate publication status: `[Preprint]`, `[Peer-reviewed - Conference]`, `[Peer-reviewed - Journal]`, `[Workshop paper]`, `[Thesis]`. This is a hard requirement (see skill.md Constraints).

### 12. Incomplete Bibliographic Metadata
- **Problem**: Returning paper titles and URLs without authors, year, venue, or identifiers. Users cannot properly cite, find, or assess the papers.
- **Fix**: Every paper must include: authors (at least first author + "et al."), year, venue/journal, and at least one persistent identifier (DOI, arXiv ID, or Semantic Scholar Corpus ID).

### 13. Abstract Dump Without Synthesis
- **Problem**: Copy-pasting raw abstracts for each paper without summarizing the key finding or explaining why it is relevant to the user's specific query.
- **Fix**: Extract 1-2 sentences of key findings relevant to the user's question. Provide a synthesis section that connects papers thematically, identifies consensus and contradictions, and suggests a reading order.

### 14. Fabricating Paper Details
- **Problem**: Generating plausible-sounding but non-existent paper titles, authors, or findings to fill gaps in search results. This is a critical failure mode for LLM-based agents.
- **Fix**: Only return papers actually retrieved from database API responses. If the search returns fewer than 5 relevant results, report that honestly rather than padding with fabricated entries. Include the database query used so the user can verify.

### 15. Ignoring Open Access Status
- **Problem**: Returning papers behind paywalls without checking for open-access alternatives. Users without institutional access cannot read the papers.
- **Fix**: For each paper, check: (a) arXiv preprint version, (b) Semantic Scholar `openAccessPdf` field, (c) author's personal website or institutional repository. Flag papers with no open-access version available and suggest the user check their institutional library access.

## Workflow Anti-Patterns

### 16. No Iteration on Poor Results
- **Problem**: Returning the first set of results without assessing quality. If the top results are irrelevant or insufficient, the skill should refine and retry.
- **Fix**: After initial results, perform a quality check: Are at least 3 of the top 5 directly relevant? If not, refine the query using synonym expansion, alternative category codes, or broader/narrower scope. Iterate up to 2 times before presenting final results.

### 17. Ignoring the Citation Graph
- **Problem**: Treating each paper as an isolated entity rather than exploiting the citation network for discovery. Citation snowballing (forward and backward) is one of the most powerful techniques in academic search.
- **Fix**: For the top 1-2 most relevant initial results, always check their citations (forward) and references (backward) using the Semantic Scholar API. This often surfaces highly relevant papers that keyword search alone would miss.

### 18. Conflating Preprint Versions
- **Problem**: Returning both the arXiv preprint and the published version of the same paper as separate results, inflating the result count with duplicates.
- **Fix**: Follow the deduplication protocol from best-practices.md. Match by DOI/arXiv ID, then by title+author+year. Keep the published version as the primary entry but include the arXiv link for open access.
