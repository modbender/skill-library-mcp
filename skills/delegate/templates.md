# Spawn Templates

Copy-paste and fill in brackets.

## Research Task
```
TASK: Find [specific info] about [topic]. Return [N] sources.
MODEL: Small (Haiku/GPT-4o-mini)
CONTEXT: [constraints, e.g. "only sources from 2024"]
OUTPUT: Bullet list with URL for each finding
DONE: End message with "RESEARCH_COMPLETE"
```

## Code Implementation
```
TASK: Implement [feature] in [file path]
MODEL: Medium (Sonnet/GPT-4o)
CONTEXT: 
- Read [relevant files]
- Follow [coding standards]
OUTPUT: Modified files, tests passing
DONE: Commit with message "[feature] implemented"
```

## File Processing
```
TASK: [operation] on each file in [directory]
MODEL: Small
CONTEXT: [file type, expected format]
OUTPUT: Processed files in [output directory]
DONE: Report "X/Y files processed, Z failures"
```

## Analysis Task
```
TASK: Analyze [subject] for [purpose]
MODEL: Medium
CONTEXT: [data source, criteria]
OUTPUT: Structured report with [sections]
DONE: Write report to [path]
```

## Review Task
```
TASK: Review [artifact] against [criteria]
MODEL: Medium (or Large for architecture)
CONTEXT: [artifact path], [standards doc]
OUTPUT: List of issues with severity (critical/major/minor)
DONE: "REVIEW_COMPLETE: X critical, Y major, Z minor"
```
