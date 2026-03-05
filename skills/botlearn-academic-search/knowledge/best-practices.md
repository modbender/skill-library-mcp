---
domain: academic-search
topic: query-construction-relevance-ranking-cross-referencing
priority: high
ttl: 30d
---

# Academic Search -- Best Practices

## Query Construction

### 1. Research Question Decomposition
Before searching, decompose the user's request into structured components:
- **Core topic** -- The primary subject (e.g., "federated learning")
- **Subtopic / aspect** -- Specific focus area (e.g., "privacy guarantees")
- **Methodology preference** -- Empirical, theoretical, survey (e.g., "benchmark evaluation")
- **Temporal scope** -- Date range for results (e.g., "2022 onwards")
- **Discipline** -- Target field(s) (e.g., computer science, biomedicine)

### 2. Academic Keyword Selection
Academic papers use different terminology than general web content:

| General Term | Academic Equivalent(s) |
|-------------|----------------------|
| AI chatbot | large language model, conversational agent, dialogue system |
| image recognition | visual recognition, image classification, object detection |
| data privacy | differential privacy, privacy-preserving, data protection |
| brain scan | neuroimaging, fMRI, MRI, EEG |
| drug discovery | pharmacological screening, molecular docking, compound identification |
| self-driving car | autonomous vehicle, automated driving, self-driving system |
| fake news | misinformation detection, claim verification, fact-checking |

**Key principle**: Use the terminology of the target research community. Check the "Keywords" section of known relevant papers to discover preferred terms.

### 3. Database-Specific Query Strategies

#### arXiv Strategy
- Use category codes to narrow scope: `cat:cs.LG` for ML, `cat:cs.CL` for NLP
- Search title (`ti:`) for high-precision results, abstract (`abs:`) for broader recall
- Use `ANDNOT` to exclude tangential categories
- Sort by `submittedDate` for latest work, `relevance` for best matches
- For emerging topics, prefer recency over relevance sorting

#### Semantic Scholar Strategy
- Use `fieldsOfStudy` parameter to filter by discipline
- Use `year` parameter with range syntax (`2022-2025`) to constrain dates
- Request `influentialCitationCount` to gauge true impact
- Use the `tldr` field for quick paper summaries when triaging large result sets
- Follow up with citation/reference graph for seminal paper discovery

#### Google Scholar Strategy (via google-search)
- Use `intitle:"keyword"` for title-focused search
- Use `author:"name"` to find specific researcher's work
- Use `source:"venue"` to restrict to specific journals/conferences
- Apply `as_ylo` and `as_yhi` URL parameters for date ranges
- Use `"exact phrase"` for specific technical terms or method names

### 4. Multi-Database Search Protocol
For comprehensive literature coverage:
1. **Start with Semantic Scholar** -- Best for structured metadata, citation graphs, and field-of-study filtering
2. **Supplement with arXiv** -- Catches very recent preprints not yet indexed elsewhere (especially CS, physics, math)
3. **Verify with Google Scholar** -- Broadest coverage; catches papers from smaller venues, theses, and technical reports
4. **Cross-reference results** -- Deduplicate using DOI or arXiv ID; merge metadata from the richest source

### 5. Query Expansion Techniques
When initial results are insufficient:
- **Synonym expansion**: Add OR clauses with alternative terms (e.g., `"graph neural network" OR "message passing network"`)
- **Citation snowballing**: Find one relevant paper, then search its references (backward) and citations (forward)
- **Author tracking**: Identify key authors from initial results, then search for their other recent papers
- **Venue scoping**: If a relevant paper was published at ICML, search specifically within ICML proceedings for related work
- **Related paper features**: Use Semantic Scholar's "recommended papers" or Google Scholar's "Related articles"

## Relevance Ranking

### Multi-Factor Ranking Framework
Rank papers by weighted combination of these factors:

| Factor | Weight | Assessment Criteria |
|--------|--------|-------------------|
| **Topical Relevance** | 35% | How directly does the paper address the user's specific question? Title/abstract keyword overlap, methodology match |
| **Methodological Rigor** | 20% | Appropriate methodology, sufficient baselines, statistical significance, reproducibility indicators |
| **Venue Quality** | 15% | Conference/journal ranking (A*/A for CS, Impact Factor for journals), peer-review status |
| **Recency** | 15% | Publication date relative to the field's pace; recent is better for fast-moving fields |
| **Impact** | 15% | Influential citation count, citation velocity, whether it introduced a widely-adopted technique |

### Scoring Procedure
For each paper, score 0-5 on each factor:
- **5** -- Excellent: directly relevant, top venue, rigorous method, high and growing citations
- **4** -- Strong: highly relevant with minor gaps in one dimension
- **3** -- Good: relevant but from a secondary venue or with moderate impact
- **2** -- Acceptable: tangentially relevant or older but still useful
- **1** -- Marginal: peripherally related or methodologically weak
- **0** -- Not relevant: off-topic, retracted, or fundamentally flawed

Compute weighted score: `(Relevance * 0.35) + (Rigor * 0.20) + (Venue * 0.15) + (Recency * 0.15) + (Impact * 0.15)`

### Special Ranking Adjustments
- **Survey papers**: Boost ranking when user requests "overview" or "literature review" -- surveys provide comprehensive coverage
- **Seminal papers**: Boost ranking for foundational papers even if older, when user is exploring a new field
- **Preprints**: Apply a -1 penalty to venue quality score unless the preprint is from a well-known research group or has high citation count
- **Open access**: Apply a +0.5 bonus when the user needs full-text access and the paper has a freely available PDF

## Cross-Referencing Strategies

### 1. Forward Citation Analysis
Starting from a known relevant paper, examine papers that cite it:
- Use Semantic Scholar `/paper/{id}/citations` endpoint
- Filter citations by year to find recent extensions
- Sort by `influentialCitationCount` to find the most impactful follow-up works
- Identify **citation clusters** -- groups of papers that cite the same source tend to be related

### 2. Backward Reference Analysis
Starting from a known relevant paper, examine its references:
- Use Semantic Scholar `/paper/{id}/references` endpoint
- Identify the **foundational papers** the author builds upon
- Look for methodological sources -- the papers describing the technique being used
- Find the dataset and benchmark papers for evaluation context

### 3. Bibliographic Coupling
Two papers that share many references are likely related:
- Compare reference lists of candidate papers
- Papers with 30%+ reference overlap are strong candidates for relevance
- Useful for finding papers the database search missed

### 4. Co-Citation Analysis
Two papers frequently cited together by other papers are related:
- If papers A and B both appear in the reference lists of many papers, they address related topics
- Use Semantic Scholar recommended papers feature as a proxy

### 5. Author Network Exploration
- Identify prolific authors in the initial result set
- Search for their other recent publications
- Check their co-authors for related work from collaborating labs
- Examine their Google Scholar profile for a comprehensive publication list

### 6. Deduplication Protocol
The same paper often appears across multiple databases:
1. **Match by DOI** -- Definitive identifier; if DOIs match, it is the same paper
2. **Match by arXiv ID** -- Maps arXiv preprints to their Semantic Scholar entries
3. **Match by title + first author + year** -- Fuzzy match for papers without DOI
4. **Merge metadata** -- Keep the record with the richest metadata (prefer Semantic Scholar for citations, arXiv for full text)
5. **Resolve version conflicts** -- A paper may have an arXiv v1 and a published version; prefer the published version but link to the arXiv open-access copy

## Output Formatting

### Per-Paper Entry
Each paper in the output should include:
```
[Rank]. Title
Authors: First Author et al. (Year)
Venue: Conference/Journal Name [Peer-reviewed / Preprint]
Citations: X total, Y influential | Citation velocity: Z/year
arXiv: XXXX.XXXXX | DOI: 10.XXXX/XXXXX
Open Access: [Yes - link] / [No - paywall]
Key Findings: 1-2 sentence summary of the main contribution
Relevance: Why this paper matters for the user's query
```

### Synthesis Section
After listing individual papers, provide:
- **Thematic grouping**: Cluster papers by approach or subtopic
- **Consensus findings**: What do multiple papers agree on?
- **Contradictions**: Where do papers disagree, and why?
- **Research gaps**: What questions remain unanswered?
- **Recommended reading order**: Suggest which papers to read first based on the user's background
