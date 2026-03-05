---
name: arxiv-watcher
description: Search and summarize papers from ArXiv. Use when the user asks for the latest research, specific topics on ArXiv, or a daily summary of AI papers.
author: Claude (克劳德)
version: 2.0.0
---

# ArXiv Watcher Skill

This skill provides systematic ArXiv paper search with structured query strategies, duplicate handling, and comprehensive audit trail for academic research workflows.

## Capabilities

- **Structured Search Strategy**: Implements domain-specific search strategies based on research objectives
- **CS Category Filtering**: Searches only within arXiv CS (Computer Science) category
- **Time Range Enforcement**: Strictly adheres to specified date ranges
- **Duplicate Handling**: Automatically merges results from multiple queries and removes duplicates
- **Rate Limit Management**: Implements multi-round search strategies for large date ranges
- **Comprehensive Logging**: Maintains detailed records of all search activities and results

## Research Domain Configuration

### Music Generation Search Strategy
**Primary Objective**: Systematically map the methodological landscape, data/training resources, evaluation benchmarks, and SOTA trends in music generation over the past two years.

**Strong Relevance Keywords**:
- `music generation`
- `song generation` 
- `text-to-music`
- `text-to-song`
- `lyrics-to-music`
- `image-to-music`
- `video-to-music`
- `video-guided music generation`
- `text-to-midi`
- `symbolic music generation`
- `music synthesis`

**Weak Relevance Keywords** (require additional verification):
- `editing`
- `controllable generation`
- `instruction-following`

**Related Paper Types** (strong relevance if combined with music keywords):
- `survey`
- `benchmark` 
- `evaluation`
- `dataset`

## Search Implementation

### Query Construction
- **Base Query**: Combines strong relevance keywords with OR logic
- **Category Filter**: Restricts to `cat:cs.*` (Computer Science)
- **Date Filter**: Uses `submittedDate` range with strict bounds
- **Duplicate Prevention**: Tracks paper IDs across multiple queries

### Rate Limit Handling
For large date ranges (>6 months), implements multi-round strategy:
1. **Chunk by Quarter**: Split date range into quarterly segments
2. **Sequential Queries**: Execute queries sequentially with delay
3. **Merge Results**: Combine and deduplicate across all segments
4. **Progress Tracking**: Log completion status for each segment

### Result Processing
- **Deduplication**: Remove papers appearing in multiple query results
- **Metadata Extraction**: Extract title, authors, abstract, submission date, arXiv ID
- **Relevance Tagging**: Tag papers with primary keywords that matched
- **Structured Output**: Generate standardized paper list format

## Output Format

### Local File Storage
- **Search Log**: `research/{domain}/search_results/arxiv_search_log.md`
- **Paper List**: `research/{domain}/search_results/paper_list.json`
- **Directory Structure**: Automatically created if missing

### Search Log Structure
Each search session includes:
- **Session Header**: Date, domain, time range, search objective
- **Query Strategy**: Detailed keyword combinations and search parameters  
- **Execution Details**: Query chunks, rate limit handling, completion status
- **Results Summary**: Total papers found, duplicates removed, final count
- **Individual Results**: Structured list of all papers with metadata

### Paper List Format (JSON)
```json
{
  "search_metadata": {
    "domain": "music_generation",
    "time_range": {"start": "2024-06-01", "end": "2026-02-27"},
    "keywords": ["music generation", "song generation", ...],
    "total_papers": 187,
    "search_date": "2026-02-28"
  },
  "papers": [
    {
      "title": "Paper Title",
      "authors": ["Author1", "Author2"],
      "abstract": "Paper abstract...",
      "arxiv_id": "2602.xxxxx",
      "submission_date": "2026-02-23",
      "matched_keywords": ["music generation"],
      "category": "cs.SD",
      "url": "https://arxiv.org/abs/2602.xxxxx"
    }
  ]
}
```

## Usage Examples

```bash
# Search music generation papers for full date range
arxiv_watcher --domain "music_generation" --start_date "2024-06-01" --end_date "2026-02-27" --keywords "music generation,song generation"

# Search recent papers only  
arxiv_watcher --domain "music_generation" --days 15 --keywords "music generation,song generation"
```

## Files Created

- `research/{domain}/search_results/arxiv_search_log.md`
- `research/{domain}/search_results/paper_list.json`
- Directory structure automatically created if missing

## Audit Trail Requirements

All search activities must include:
- Complete query strategy documentation
- Execution progress tracking
- Duplicate handling records
- Final result validation