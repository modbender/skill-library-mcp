# Quality Filter Skill

Academic paper quality filtering with rigorous scoring system and comprehensive audit trail.

## Directory Structure

```
quality_filter/
├── SKILL.md          # Skill definition and usage
├── README.md         # This file
└── scripts/          # Executable scripts (if any)
```

## Integration

This skill is designed to work within the broader music generation research workflow:

1. **Input**: Papers from arXiv search results
2. **Processing**: Applies systematic scoring based on relevance and quality
3. **Output**: Categorizes papers as passed/filtered with detailed rationale
4. **Audit Trail**: Maintains comprehensive log for manual recall

## Usage in Research Workflow

When processing papers from arXiv search:

```bash
# Example workflow integration
papers = arxiv_search("music generation", date_range)
filtered_papers = quality_filter(
    domain="music_generation",
    papers=papers,
    threshold=6
)
passed_papers = [p for p in filtered_papers if p.score >= 6]
```

## Quality Assurance

- All filtering decisions include complete score breakdown
- Filtered papers are preserved for manual recall
- Comprehensive audit trail maintained in append-mode log file
- Clear pass/fail rationale for each decision