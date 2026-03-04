---
strategy: academic-search
version: 1.0.0
steps: 5
---

# Academic Search Strategy

## Step 1: Keyword Extraction & Research Scoping
- Parse the user's request to identify: **core topic**, **subtopic/aspect**, **discipline**, **time scope**, **methodology preference**, and **desired output** (e.g., survey, empirical results, benchmarks)
- Classify the research intent:
  - **Exploratory** -- User is new to a topic and needs an overview → prioritize surveys and seminal papers
  - **Targeted** -- User knows the field and needs specific recent results → prioritize recent empirical work
  - **Comparative** -- User wants to compare approaches → prioritize benchmarks and ablation studies
  - **Bibliographic** -- User needs a specific paper or author's work → use identifier-based lookup
- Extract domain-specific keywords using the academic terminology mapping from knowledge/best-practices.md
- IF the query is ambiguous or spans multiple disciplines THEN ask one clarifying question: "Are you looking for [interpretation A] or [interpretation B]?"
- Determine the appropriate arXiv category codes from knowledge/domain.md for the topic
- Set temporal scope: default to last 3 years for fast-moving fields (CS, AI, biotech), last 5 years for established fields, no limit for foundational work

## Step 2: Database-Specific Query Construction
- Construct parallel queries for each target database:

### arXiv Query
- SELECT field prefixes based on desired precision:
  - `ti:` for high-precision title match on core terms
  - `abs:` for broader abstract search when title search yields < 5 results
  - `all:` only as a last resort for very niche topics
- APPLY category filters: `cat:cs.LG` or equivalent from knowledge/domain.md
- APPLY Boolean operators: `AND` for required terms, `OR` for synonyms, `ANDNOT` for exclusions
- SET `sortBy=submittedDate` for exploratory/recent queries, `sortBy=relevance` for targeted queries
- SET `max_results=15` to allow for filtering headroom
- EXAMPLE: `search_query=(ti:retrieval+augmented+generation+OR+ti:RAG)+AND+cat:cs.CL&sortBy=submittedDate&max_results=15`

### Semantic Scholar Query
- SET `query` with core terms (natural language works better here than on arXiv)
- SET `fields=title,authors,year,abstract,citationCount,influentialCitationCount,venue,openAccessPdf,tldr,externalIds,publicationTypes`
- SET `year` range based on temporal scope from Step 1
- SET `fieldsOfStudy` to the appropriate discipline
- SET `limit=15`
- EXAMPLE: `query=retrieval augmented generation hallucination&year=2023-&fieldsOfStudy=Computer Science&limit=15`

### Google Scholar Query (via google-search skill)
- Construct using google-search query operators: `intitle:"core term"`, `author:"name"`, `source:"venue"`
- Apply date filters via `as_ylo` and `as_yhi` parameters
- Use `site:scholar.google.com` prefix when routing through google-search skill
- Target 10 results

- VERIFY each query avoids anti-patterns from knowledge/anti-patterns.md:
  - Not a natural language sentence (Anti-Pattern #1)
  - Not overly broad (Anti-Pattern #3) or overly narrow (Anti-Pattern #4)
  - Uses field-appropriate terminology (Anti-Pattern #5)

## Step 3: Abstract Screening & Relevance Filtering
- Execute all database queries (arXiv, Semantic Scholar, Google Scholar) in parallel
- For each returned paper, perform rapid abstract screening:
  1. **Title scan** -- Does the title contain core topic terms? (5 seconds per paper)
  2. **Abstract relevance check** -- Does the abstract address the user's specific question? (15 seconds per paper)
  3. **Methodology match** -- IF the user specified a methodology preference THEN verify the paper uses that approach
  4. **Temporal check** -- Is the paper within the specified date range?
- Apply inclusion criteria (must meet ALL):
  - Directly addresses the core topic (not merely mentions it)
  - Is an actual academic paper (not a blog post, news article, or course material)
  - Has accessible metadata (title, authors, year at minimum)
- Apply exclusion criteria (reject if ANY):
  - Paper is retracted or has a published erratum that invalidates key findings
  - Paper is a duplicate of another result (apply deduplication protocol from knowledge/best-practices.md)
  - Paper is from a known predatory journal or publisher
- Deduplicate across databases:
  - Match by DOI first (definitive)
  - Match by arXiv ID second
  - Fuzzy match by title + first author + year for remaining
  - Merge metadata: keep the richest record, link to open-access version
- IF fewer than 5 papers pass screening THEN:
  - Expand query with synonym variants (knowledge/best-practices.md, Query Expansion Techniques)
  - Broaden date range by 2 years
  - Remove one category/field filter
  - Re-execute and re-screen

## Step 4: Cross-Reference & Citation Analysis
- For the top 3 papers from Step 3, perform citation graph analysis:

### Forward Citation Check (Who cites this paper?)
- Query Semantic Scholar `/paper/{id}/citations` with `limit=20`
- Filter citations by year (recent only) and relevance (title/abstract scan)
- IF a citing paper is more relevant than a lower-ranked result from Step 3 THEN promote it into the candidate set

### Backward Reference Check (What does this paper cite?)
- Query Semantic Scholar `/paper/{id}/references` with `limit=20`
- Identify foundational papers (high citation count) and methodological sources
- IF user intent is "Exploratory" THEN include the most-cited reference as a foundational reading recommendation

### Citation-Based Quality Signals
- Calculate citation velocity: `citationCount / (currentYear - publicationYear)`
- Note influential citation count vs. total citations (Semantic Scholar)
- Flag papers with unusually high self-citation ratios (> 30% self-citations)

- Apply multi-factor ranking from knowledge/best-practices.md:
  - Topical Relevance (35%)
  - Methodological Rigor (20%)
  - Venue Quality (15%)
  - Recency (15%)
  - Impact (15%)
- Sort candidates by weighted score, descending
- Select Top 5 papers

## Step 5: Synthesis & Structured Output
- For each of the Top 5 papers, produce a structured entry:
  ```
  [Rank]. Title
  Authors: First Author et al. (Year)
  Venue: Name [Peer-reviewed / Preprint / Workshop]
  Citations: X total, Y influential | Velocity: Z/year
  IDs: arXiv:XXXX.XXXXX | DOI:10.XXXX/XXXXX
  Open Access: [Yes - URL] / [No - suggest alternatives]
  Key Findings: 1-2 sentences on the main contribution
  Methodology: Brief description of the approach
  Relevance: Why this paper matters for the user's query
  ```
- Generate a synthesis section connecting the Top 5 papers:
  - **Thematic Clusters** -- Group papers by approach or subtopic (e.g., "Papers 1 and 3 propose attention-based methods, while 2 and 4 use retrieval-augmented approaches")
  - **Consensus** -- What findings are consistent across multiple papers?
  - **Divergence** -- Where do results or conclusions conflict, and what explains the differences?
  - **Research Gaps** -- What questions are not yet answered by the current literature?
  - **Suggested Reading Order** -- Recommend which paper to read first based on the user's apparent expertise level

- SELF-CHECK before presenting results:
  - Are all 5 papers real (retrieved from APIs, not fabricated)? (Anti-Pattern #14)
  - Is publication status clearly indicated for each paper? (Anti-Pattern #11)
  - Is bibliographic metadata complete? (Anti-Pattern #12)
  - Are at least 2 databases represented in the results?
  - Is there at least 1 open-access paper in the Top 5?
  - Does the synthesis connect papers rather than just listing them? (Anti-Pattern #13)
  - IF any check fails THEN loop back to the relevant step to fix the issue
