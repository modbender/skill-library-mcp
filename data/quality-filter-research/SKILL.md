---
name: quality_filter
description: Academic paper quality filtering agent with rigorous scoring system and comprehensive audit trail. Filters papers based on relevance and quality criteria for research workflows.
author: Claude (克劳德)
version: 1.0.0
---

# Quality Filter Skill

This skill provides systematic quality filtering for academic papers with a rigorous scoring system and complete audit trail for research workflows.

## Capabilities

- **Relevance Scoring**: Evaluates paper relevance based on title and abstract keywords
- **Quality Assessment**: Assesses technical quality and experimental rigor
- **Comprehensive Logging**: Maintains detailed records of all filtering decisions
- **Manual Recall Support**: Preserves filtered papers for potential human review
- **Local File Storage**: Saves all results to organized directory structure

## Filtering Criteria

### Relevance Scoring (Max 3 points)
- **Strong Match** (+3): Title contains "music" or "song" keywords
- **Medium Match** (+2): Title contains "audio" + "generation" 
- **Weak Match** (+1): Title has weak but related keywords
- **Negative Scoring**: Abstract verification can subtract points (-1 to -3)

### Quality Assessment (Max 3 points)
- **High Quality** (+3): Complete experiments, multiple baselines, strong results
- **Medium Quality** (+2): Experiments present but limited baseline comparison  
- **Low Quality** (+1): Limited technical contribution or incomplete evaluation

### Pass Threshold
- **Minimum Score**: 6/10 points required to pass filtering
- **Strong Relevance Override**: Papers with clear "music/song generation" focus may pass with lower scores

## Workflow Integration

This skill integrates with the broader research workflow:

1. **Input**: Raw paper list from arXiv search
2. **Processing**: Applies scoring system to each paper
3. **Output**: Categorizes papers as "passed" or "filtered"
4. **Audit Trail**: Maintains complete record for manual recall

## Output Format

### Local File Storage
- **Main Log**: `research/{domain}/quality_filtering/quality_filtering_log.md`
- **Append Mode**: All results appended to single comprehensive file
- **Directory Structure**: Automatically created if missing

### Log Structure
Each filtering session includes:
- **Session Header**: Date, domain, search parameters
- **Scoring Standards**: Detailed criteria used
- **Individual Paper Results**: Title, authors, score breakdown, decision
- **Summary Statistics**: Pass/fail counts, score distribution
- **Manual Recall Section**: List of filtered papers available for human review

## Usage Examples

```bash
# Filter music generation papers
quality_filter --domain "music_generation" --papers "[paper_list]" --date "2026-02-28"

# Filter with custom threshold
quality_filter --domain "speech_audio" --threshold 5 --papers "[paper_list]"
```

## Files Created

- `research/{domain}/quality_filtering/quality_filtering_log.md` (append mode)
- Directory structure automatically created if missing

## Audit Trail Requirements

All filtering decisions must include:
- Complete score breakdown (relevance + quality components)
- Clear pass/fail rationale
- Preservation of filtered papers for manual recall
- Timestamp and session context