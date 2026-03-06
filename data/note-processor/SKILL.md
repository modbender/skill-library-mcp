---
name: note-processor
description: "Summarize and analyze research notes created by
  research-assistant. Features: generate summaries, extract keywords, search
  within topics, list all topics. Works with research_db.json format. Perfect
  for finding patterns, reviewing research progress, and extracting insights
  from accumulated notes without re-reading everything."
---


# Note Processor

Analyze and summarize research notes to extract insights quickly.

## Quick Start

```bash
note_processor.py summarize <topic>
note_processor.py keywords <topic>
note_processor.py extract <topic> <keyword>
note_processor.py list
```

**Examples:**
```bash
# Get a summary of a research topic
note_processor.py summarize income-experiments

# Extract top keywords from notes
note_processor.py keywords security-incident

# Search for specific information
note_processor.py extract income-experiments skill

# List all research topics with stats
note_processor.py list
```

## Features

- **Summaries** - Overview of topic with statistics, tags, key points
- **Keywords** - Extract most common words (filters stop words)
- **Search** - Find notes containing specific keywords
- **List** - See all research topics with basic stats
- **Integration** - Works with research-assistant's database format

## When to Use

### After Research Sessions
```bash
# Summarize what you learned
note_processor.py summarize new-research-topic

# Extract key themes
note_processor.py keywords new-research-topic
```

### Before Writing Reports
```bash
# Find specific information
note_processor.py extract income-experiments monetization

# Get overview for introductions
note_processor.py summarize income-experiments
```

### Reviewing Progress
```bash
# See all topics and their sizes
note_processor.py list

# Check what you've been working on
note_processor.py keywords income-experiments
```

## Command Details

### summarize <topic>
Shows:
- Note count and word count
- Creation and last update dates
- Top 5 tags
- Key points (sentences with important words)
- 3 most recent notes

**Output example:**
```
📊 Summary: income-experiments
------------------------------------------------------------
Notes: 4
Words: 63
Created: 2026-02-07
Last update: 2026-02-07

🏷️  Top Tags:
   content: 2
   automation: 2
   experiment: 2

💡 Key Points:
   1. First experiment: create and publish skills...
   2. Second experiment: content automation pipeline...
```

### keywords <topic>
Shows:
- Total unique keywords
- Top 20 keywords with frequency
- Filters common stop words (that, this, with, from, etc.)

**Output example:**
```
🔤 Keywords: income-experiments
------------------------------------------------------------
Total unique keywords: 38

Top 20 Keywords:
  1. experiment           ( 4x)
  2. skill                ( 3x)
  3. clawhub              ( 2x)
  4. content              ( 2x)
```

### extract <topic> <keyword>
Shows:
- All notes containing the keyword
- Keyword highlighted in uppercase
- Timestamps and tags
- Preview of matched content

**Output example:**
```
🔍 Search Results: 'skill' in income-experiments
------------------------------------------------------------
Found 4 match(es)

1. [2026-02-07 19:09:51]
   Tags: ideas, autonomous
   First experiment: create and publish **SKILL**s to ClawHub...
```

### list
Shows:
- All research topics
- Note count and word count
- Last update date
- Preview of most recent note

**Output example:**
```
📚 Research Topics (5)
------------------------------------------------------------

income-experiments
   Notes: 4 | Words: 63 | Updated: 2026-02-07
   Latest: Experiment 2 STARTING: Content automation...

security-incident
   Notes: 1 | Words: 45 | Updated: 2026-02-07
   Latest: Day 1: Security vulnerability found...
```

## Integration with research-assistant

note-processor works with the same database as research-assistant (`research_db.json`).

### Typical Workflow
```bash
# 1. Add research notes
research_organizer.py add "new-topic" "Research finding here" "tag1" "tag2"

# 2. Add more notes over time
research_organizer.py add "new-topic" "Another finding" "tag3"

# 3. Summarize when done
note_processor.py summarize new-topic

# 4. Find specific information
note_processor.py extract new-topic keyword

# 5. See all topics
note_processor.py list
```

### Using Both Together
```bash
# Research phase
research_organizer.py add "experiment" "Test result 1" "testing"
research_organizer.py add "experiment" "Test result 2" "testing"
research_organizer.py add "experiment" "Conclusion: worked!" "results"

# Analysis phase
note_processor.py summarize experiment
note_processor.py keywords experiment

# Writing phase
note_processor.py extract experiment conclusion
# Now write report based on extracted notes
```

## Key Point Detection

The `summarize` command detects key points by finding sentences with important words:
- important, key, critical, essential
- must, should, note, remember
- warning, priority, critical

This helps surface actionable insights from your research.

## Keyword Extraction

The `keywords` command:
- Filters words shorter than 4 characters
- Removes common stop words
- Counts frequency across all notes
- Shows top 20 keywords

**Stop words filtered:**
that, this, with, from, have, been, will, what, when, where, which, their, there, would, could, should, about, these, those, other, into, through

## Use Cases

### Before Writing a Report
```bash
# Get overview
note_processor.py summarize research-topic

# Find specific data points
note_processor.py extract research-topic metrics

# Extract themes
note_processor.py keywords research-topic
```

### Reviewing Research Progress
```bash
# See what you've been working on
note_processor.py list

# Check a specific topic's progress
note_processor.py summarize current-project

# Find patterns
note_processor.py keywords current-project
```

### Finding Specific Information
```bash
# Search across a topic
note_processor.py extract income-experiments monetization

# Find references to specific tools
note_processor.py extract security-incident path-validation

# Locate conclusions
note_processor.py extract experiment conclusion
```

## Best Practices

1. **Use summaries** - Get overview before diving into details
2. **Search first** - Use extract before reading all notes
3. **Check keywords** - Find themes you might have missed
4. **List regularly** - Review all topics to see gaps
5. **Tag consistently** - Makes keywords more meaningful

## Data Location

Database: `~/.openclaw/workspace/research_db.json`
Format: Compatible with research-assistant skill

## Limitations

- **Simple keyword extraction** - Frequency-based, not semantic
- **No NLP** - Basic text processing (no ML/AI)
- **Stop word list** - English-focused, customize for other languages
- **Key point detection** - Pattern-based, not understanding-based

## Tips

### For Better Keywords
- Use consistent terminology in your notes
- Avoid abbreviations or synonyms for the same concept
- Tag notes with important terms
- Review keywords to see if important terms appear

### For Better Summaries
- Write complete sentences in notes
- Include important words (key, critical, must, etc.)
- Tag notes with themes
- Regularly summarize to track progress

### For Better Search
- Use specific keywords in extract
- Search for related terms (synonyms)
- Check tags in results
- Use summaries to find the right topic

## Troubleshooting

### "Topic not found"
```
Topic 'x' not found.
```
**Solution:** Check topic name spelling. Use `note_processor.py list` to see all topics.

### "No matches found"
```
No matches for 'keyword' in topic 'x'
```
**Solution:** Try different keywords, check spelling, use `note_processor.py keywords` to find related terms.

### Poor keyword results
```
Top Keywords are mostly common words
```
**Solution:** 
- Use more specific terms in your notes
- Tag notes with important terms
- The stop word filter can be customized in the code

## Examples by Use Case

### Project Review
```bash
# What have I been working on?
note_processor.py list

# Tell me about this project
note_processor.py summarize project-x

# What are the main themes?
note_processor.py keywords project-x
```

### Writing Documentation
```bash
# Find specific details
note_processor.py extract security-incident vulnerability

# Get overview for introduction
note_processor.py summarize security-incident

# What's important?
note_processor.py keywords security-incident
```

### Preparing a Report
```bash
# Find all relevant information
note_processor.py extract income-experiments monetization

# Get summary
note_processor.py summarize income-experiments

# Extract key points
note_processor.py summarize income-experiments
# Key points are in the output
```

## Integration with Other Skills

### With research-assistant
- research-assistant: add notes
- note-processor: analyze notes
- Use together: add → analyze → write report

### With task-runner
```bash
# Add task to summarize research
task_runner.py add "Summarize experiment results" "documentation"

# When complete
note_processor.py summarize experiment

# Mark done
task_runner.py complete 1
```

### With file skills
```bash
# Extract research notes
note_processor.py extract research-topic important

# Export for sharing
research_organizer.py export research-topic ~/shared/summary.md

# Or export summary output to file
note_processor.py summarize research-topic > ~/shared/summary.txt
```

## Zero-Cost Advantage

This skill requires:
- ✅ Python 3 (included)
- ✅ No API keys
- ✅ No external dependencies
- ✅ No paid services
- ✅ Works with research-assistant (free)

Perfect for autonomous research workflows with no additional costs.
