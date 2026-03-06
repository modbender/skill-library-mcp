---
name: scholar-research
description: "Search, analyze, and summarize peer-reviewed academic papers from open access sources. Provides credibility scoring, visualization, timeline generation, and figure extraction for top papers."
---

# Scholar Research Skill

Search and analyze academic papers from open access sources with credibility scoring and detailed summaries.

## When to Use

- User wants to find papers on a specific topic
- User needs credibility assessment of papers
- User wants summarized research with methodology
- User wants to track field evolution over time
- User needs figures/tables extracted from top papers

## Data Sources (Free/Open Access)

The skill searches across these sources:
- **arXiv** - Pre-prints (Physics, Math, CS, q-bio, q-fin)
- **PubMed/PMC** - Biomedical & Life sciences
- **DOAJ** - Peer-reviewed OA journals (all disciplines)
- **OpenAlex** - 250M+ papers metadata
- **CORE** - Largest OA full-text aggregator
- **Semantic Scholar** - Limited free tier
- **Unpaywall** - Finds free versions of paywalled papers
- **CrossRef** - All DOI metadata
- **bioRxiv** - Biology pre-prints
- **medRxiv** - Medicine pre-prints
- **Zenodo** - EU research data/papers
- **HAL** - French OA repository
- **J-STAGE** - Japanese OA repository
- **SSRN** - Economics, Law pre-prints

## User-Added Sources

Users can add custom sources via config:
```json
{
  "custom_sources": [
    {"name": "My University", "url": "https://repo.my.edu", "api": "..."}
  ]
}
```

## Scoring System

### Default Weights (Total: 100 + 40 bonus)

**Paper Quality (100 points):**
| Factor | Weight | Description |
|--------|--------|-------------|
| citation_count | 15% | Times cited by other papers |
| publication_recency | 10% | Newer = more relevant |
| author_reputation | 12% | Combined h-index of authors |
| journal_impact | 12% | Impact factor, CiteScore |
| peer_review_status | 10% | Peer-reviewed vs pre-print |
| open_access | 8% | Free to read/download |
| retraction_status | 10% | Not retracted |
| author_network | 8% | Connected to established network |
| funder_acknowledgment | 5% | Clear funding sources |
| reproducibility | 5% | Code/data available |

**Bonus Points (up to +40):**
- Author Trust: +20 max
- Journal Reputation: +20 max

### Customizing Weights

Users can modify weights in config:
```json
{
  "scoring": {
    "citation_count": 25,
    "publication_recency": 5
  }
}
```

Or use preset profiles: "strict", "recent_only", "balanced"

## Output Format

### Top Papers (default: 5, user-configurable)
```
[1] Paper Title (Year)
    Score: 95/100 | Citations: 234
    📄 PDF | 📊 Figures | 🔬 SI
    
    Summary: [One paragraph]
    
    Methodology: [Detailed breakdown]
```

### Field Timeline
```
📈 FIELD TIMELINE (N papers)

2024: ████████████████████ 15 papers
       → Major: [Breakthrough 1]
       → Trend: [Trend 1]

2023: ████████████████ 12 papers
       → Major: [Breakthrough 2]
```

### Credibility Distribution
```
📊 Credibility Distribution

Score 90-100: ██ (5) ★ Top
Score 70-89:  ████████ (15)
Score 50-69:  ██████████████████ (25)
Score 30-49:  ██████████ (10)
Score 0-29:   ██ (2)

[████████████░░░░░░░░░] Average: 58/100
```

## Workflow

1. **Search**: Query across all enabled sources
2. **Fetch**: Download metadata + PDFs
3. **Score**: Calculate credibility scores
4. **Sort**: Rank by score + relevance
5. **Present**: Top N papers + timeline
6. **Extract**: Figures from top-scored papers (optional)

## Usage Examples

```
Find papers on: machine learning
Fields: computer science, AI
Top papers: 5
Extract figures: true

Find papers on: quantum computing
Fields: physics
Top papers: 10
Extract figures: false
```

## Dependencies

- Python 3.8+
- requests (API calls)
- beautifulsoup4 (parsing)
- pypdf2 (PDF extraction)
- opencv-python (figure detection)
- transformers (summarization)
- matplotlib (visualization)

## Configuration

See `config.json` for:
- API keys
- Source enable/disable
- Scoring weights
- Display preferences
- Custom sources

## Notes

- Always prioritize open access sources
- Cite sources in responses
- Warn about pre-print limitations
- Check retraction status when available
- Respect rate limits
