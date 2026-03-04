---
domain: academic-search
topic: academic-database-apis-and-paper-structure
priority: high
ttl: 30d
---

# Academic Search -- Database APIs, Paper Structure & Citation Metrics

## arXiv API

### Overview
arXiv (arxiv.org) is an open-access repository for preprints in physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, systems science, and economics. All papers are freely accessible.

### API Endpoint
- **Base URL**: `http://export.arxiv.org/api/query`
- **Method**: GET
- **Rate Limit**: 1 request per 3 seconds (be respectful; no authentication required)

### Query Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `search_query` | Search terms with field prefixes | `ti:attention+AND+cat:cs.CL` |
| `id_list` | Comma-separated arXiv IDs | `2301.00001,2301.00002` |
| `start` | Offset for pagination | `0` |
| `max_results` | Number of results (max 30000) | `10` |
| `sortBy` | Sort field: `relevance`, `lastUpdatedDate`, `submittedDate` | `relevance` |
| `sortOrder` | `ascending` or `descending` | `descending` |

### Field Prefixes for search_query
- `ti:` -- Title
- `au:` -- Author
- `abs:` -- Abstract
- `co:` -- Comment
- `jr:` -- Journal reference
- `cat:` -- Subject category
- `all:` -- All fields

### Boolean Operators
- `AND` -- Both terms required
- `OR` -- Either term matches
- `ANDNOT` -- Exclude term
- Grouping with parentheses: `(ti:transformer OR ti:attention) AND cat:cs.CL`

### arXiv Category Codes (Common)
| Category | Description |
|----------|-------------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `cs.SE` | Software Engineering |
| `cs.CR` | Cryptography and Security |
| `stat.ML` | Machine Learning (Statistics) |
| `math.OC` | Optimization and Control |
| `q-bio.QM` | Quantitative Methods (Biology) |
| `econ.EM` | Econometrics |
| `physics.comp-ph` | Computational Physics |

### Response Format (Atom XML)
```xml
<entry>
  <id>http://arxiv.org/abs/2301.00001v1</id>
  <title>Paper Title</title>
  <summary>Abstract text...</summary>
  <author><name>Author Name</name></author>
  <published>2023-01-01T00:00:00Z</published>
  <updated>2023-01-15T00:00:00Z</updated>
  <arxiv:primary_category term="cs.CL"/>
  <category term="cs.AI"/>
  <link href="http://arxiv.org/pdf/2301.00001v1" title="pdf"/>
</entry>
```

### Example Queries
```
# Find recent transformer papers in NLP
search_query=ti:transformer+AND+cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=10

# Find papers by a specific author on attention mechanisms
search_query=au:vaswani+AND+ti:attention&sortBy=relevance&max_results=5

# Find reinforcement learning papers excluding robotics
search_query=all:reinforcement+learning+ANDNOT+cat:cs.RO&max_results=20
```

## Semantic Scholar API

### Overview
Semantic Scholar (semanticscholar.org) provides a comprehensive academic search engine with rich metadata, citation graphs, and AI-extracted features. Covers 200M+ papers across all fields.

### API Endpoints

#### Paper Search
- **URL**: `GET https://api.semanticscholar.org/graph/v1/paper/search`
- **Rate Limit**: 100 requests/5 minutes (unauthenticated); 1 request/second with API key

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Search terms | `attention mechanism transformers` |
| `fields` | Comma-separated fields to return | `title,authors,year,abstract,citationCount,venue` |
| `limit` | Results per page (max 100) | `10` |
| `offset` | Pagination offset | `0` |
| `year` | Publication year filter | `2023-` (2023 onwards), `2020-2023` |
| `fieldsOfStudy` | Discipline filter | `Computer Science` |
| `openAccessPdf` | Filter for open access | (presence means filter) |

#### Paper Details
- **URL**: `GET https://api.semanticscholar.org/graph/v1/paper/{paper_id}`
- **Paper ID formats**: Semantic Scholar ID, DOI (`DOI:10.xxx`), arXiv (`ARXIV:2301.00001`), PMID, ACL ID, Corpus ID

#### Citation Graph
- **Citations**: `GET https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations`
- **References**: `GET https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references`

| Parameter | Description |
|-----------|-------------|
| `fields` | Fields for each citing/referenced paper |
| `limit` | Number of citations/references (max 1000) |
| `offset` | Pagination offset |

#### Author Search
- **URL**: `GET https://api.semanticscholar.org/graph/v1/author/search`
- **URL**: `GET https://api.semanticscholar.org/graph/v1/author/{author_id}/papers`

### Available Fields
```
# Paper fields
title, abstract, year, venue, publicationDate, journal,
citationCount, referenceCount, influentialCitationCount,
fieldsOfStudy, s2FieldsOfStudy, authors, externalIds,
url, openAccessPdf, tldr, publicationTypes, citationStyles

# Author fields
name, affiliations, homepage, paperCount, citationCount, hIndex
```

### Example Queries
```
# Search for recent RAG papers
GET /graph/v1/paper/search?query=retrieval+augmented+generation&year=2023-&fields=title,authors,year,citationCount,abstract,venue&limit=10

# Get citation graph for a specific paper
GET /graph/v1/paper/ARXIV:2005.11401/citations?fields=title,year,citationCount&limit=50

# Find papers by field of study
GET /graph/v1/paper/search?query=protein+folding&fieldsOfStudy=Biology&fields=title,year,venue&limit=20
```

## Google Scholar (via google-search skill)

### Query Operators
Google Scholar inherits many standard Google Search operators with academic-specific behavior:
- `"exact phrase"` -- Exact match in title, abstract, or full text
- `author:"last name"` -- Filter by author name
- `intitle:"keyword"` -- Term must appear in paper title
- `source:"journal name"` -- Filter by publication venue
- Date range filter via Google Scholar UI or `after:YYYY` operator

### Google Scholar URL Construction
```
# Basic search
https://scholar.google.com/scholar?q=transformer+attention+mechanism

# With date range
https://scholar.google.com/scholar?q=transformer+attention&as_ylo=2023&as_yhi=2025

# Author search
https://scholar.google.com/scholar?q=author:"hinton"+deep+learning

# Specific journal
https://scholar.google.com/scholar?q=source:"nature"+gene+editing+CRISPR
```

### Advantages over Other Sources
- Broadest coverage: journals, conferences, theses, patents, preprints, books
- Includes citation counts and "Cited by" links
- "Related articles" feature for discovery
- Provides links to free PDF versions when available

### Limitations
- No official API (rely on google-search skill for scraping-safe queries)
- Rate-limited and may block automated access
- Citation counts may differ from Semantic Scholar
- Cannot filter by field of study programmatically

## Academic Paper Structure

### Standard Sections (IMRaD Format)
| Section | Purpose | Key Information to Extract |
|---------|---------|---------------------------|
| **Title** | Concise statement of the main finding or topic | Core topic, methodology hint |
| **Abstract** | 150-300 word summary of the entire paper | Problem, method, key result, conclusion |
| **Introduction** | Problem context, motivation, research gap | Research question, hypotheses, related work overview |
| **Related Work / Literature Review** | Positioning within existing research | Key prior work, how this paper differs |
| **Methodology** | How the research was conducted | Datasets, models, experimental setup, baselines |
| **Results** | Quantitative and qualitative findings | Tables, figures, statistical significance, metrics |
| **Discussion** | Interpretation of results | Implications, limitations, comparison with prior work |
| **Conclusion** | Summary and future directions | Main contributions, open questions |
| **References** | Cited works | Citation network, foundational papers |

### Paper Types
| Type | Description | Typical Structure |
|------|-------------|-------------------|
| **Empirical** | Reports original experimental results | Full IMRaD |
| **Survey / Review** | Comprehensive overview of a research area | Taxonomy + systematic analysis |
| **Theoretical** | Proves theorems or proposes frameworks | Definitions, propositions, proofs |
| **Systems** | Describes a software system or tool | Architecture, implementation, evaluation |
| **Position / Opinion** | Argues for a particular viewpoint | Argument structure with evidence |
| **Benchmark** | Introduces datasets or evaluation protocols | Dataset description, baseline results |

## Citation Metrics

### Paper-Level Metrics
| Metric | Description | Use Case |
|--------|-------------|----------|
| **Citation Count** | Total times cited by other papers | Rough impact indicator (use with caution) |
| **Influential Citation Count** | Citations where this paper is central to the citing work (Semantic Scholar) | Better quality indicator than raw count |
| **Citation Velocity** | Citations per year, especially in recent years | Identifies trending vs. declining relevance |
| **Field-Normalized Citation** | Citations relative to field average | Fair comparison across disciplines |

### Author-Level Metrics
| Metric | Description |
|--------|-------------|
| **h-index** | h papers with at least h citations each |
| **i10-index** | Number of papers with 10+ citations |
| **Total Citations** | Sum of all paper citations |

### Venue-Level Metrics
| Metric | Description |
|--------|-------------|
| **Impact Factor** | Average citations per paper in the last 2 years (journals) |
| **h5-index** | h-index for articles published in the last 5 complete years |
| **CORE Ranking** | Conference ranking: A* (top), A, B, C (australasian system) |
| **CSRankings** | Computer science venue rankings by research output |

### Well-Known Venues by Field

#### Computer Science -- AI/ML
| Venue | Type | Prestige |
|-------|------|----------|
| NeurIPS | Conference | Top-tier |
| ICML | Conference | Top-tier |
| ICLR | Conference | Top-tier |
| AAAI | Conference | Top-tier |
| CVPR / ICCV / ECCV | Conference | Top-tier (Vision) |
| ACL / EMNLP / NAACL | Conference | Top-tier (NLP) |
| JMLR | Journal | Top-tier |
| Nature Machine Intelligence | Journal | Top-tier |

#### Biomedical
| Venue | Type | Prestige |
|-------|------|----------|
| Nature | Journal | Top-tier |
| Science | Journal | Top-tier |
| Cell | Journal | Top-tier |
| PNAS | Journal | High |
| PLoS ONE | Journal | Open-access, broad |

#### General Science
| Venue | Type | Prestige |
|-------|------|----------|
| Nature / Science | Journal | Highest |
| IEEE Transactions (various) | Journal | High |
| ACM Computing Surveys | Journal | High (CS surveys) |

## Research Methodology Taxonomy

### Quantitative Methods
- **Controlled Experiment** -- Manipulates variables with control groups
- **Quasi-Experiment** -- Natural or existing group comparisons
- **Survey / Questionnaire** -- Large-scale data collection via structured instruments
- **Corpus Analysis** -- Statistical analysis of large text/data collections
- **Simulation** -- Computational modeling of systems
- **Benchmarking** -- Standardized evaluation on established datasets

### Qualitative Methods
- **Case Study** -- In-depth analysis of specific instances
- **Ethnography** -- Observational study within a community
- **Grounded Theory** -- Theory building from systematic data analysis
- **Content Analysis** -- Systematic categorization of textual content
- **Interview Study** -- Structured or semi-structured conversations

### Mixed Methods
- **Sequential Explanatory** -- Quantitative phase followed by qualitative
- **Sequential Exploratory** -- Qualitative phase followed by quantitative
- **Convergent Parallel** -- Both methods simultaneously, results merged

### Review Methods
- **Systematic Review** -- Rigorous, reproducible search and synthesis protocol
- **Meta-Analysis** -- Statistical aggregation of results across studies
- **Scoping Review** -- Broad mapping of a research area
- **Narrative Review** -- Expert-driven summary (less rigorous than systematic)
