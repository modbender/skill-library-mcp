# ArXiv Watcher Skill

Systematic ArXiv paper search with structured query strategies and comprehensive audit trail.

## Directory Structure

```
arxiv-watcher/
├── SKILL.md          # Skill definition and usage
├── README.md         # This file
└── scripts/          # Search scripts and utilities
    └── search_arxiv.sh
```

## Integration

This skill is designed to work within the broader music generation research workflow:

1. **Input**: Research domain, time range, keywords
2. **Processing**: Implements structured search strategy with rate limit handling
3. **Output**: Generates deduplicated paper list with metadata
4. **Audit Trail**: Maintains comprehensive search log

## Usage in Research Workflow

When initiating a new research domain:

```bash
# Example workflow integration
papers = arxiv_watcher(
    domain="music_generation",
    start_date="2024-06-01", 
    end_date="2026-02-27",
    keywords=["music generation", "song generation"]
)
# Output: paper_list.json + arxiv_search_log.md
```

## Quality Assurance

- All searches restricted to CS category only
- Strict time range enforcement using submittedDate
- Automatic duplicate detection and removal
- Multi-round search strategy for large date ranges
- Comprehensive audit trail for reproducibility