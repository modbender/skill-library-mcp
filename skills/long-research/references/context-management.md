# Context Management for Long Research Sessions

## The Problem
Research sessions generate massive amounts of data. A 15-min session can easily produce 50k+ tokens of tool output. Without management, context fills up and the session becomes useless.

## Rules

### 1. Write to file, summarize in context
- ALL raw findings → `research/[topic]-[date].md`
- Chat context gets only summaries and decision points
- Never paste raw web_fetch output into reasoning — extract, then discard

### 2. Monitor context usage
Check every 10 tool calls:
- Under 40%: proceed normally
- 40-60%: start being selective, write more to file, less in context
- Over 60%: write everything to file, rely on compaction to free space
- Over 80%: trigger compaction — summarize key findings in file checkpoint, continue research after compaction
- NEVER hard stop due to context. Compaction exists for this. A 4-hour session WILL compact multiple times — that's expected and fine.
- Checkpoints in the research file serve as recovery anchors after compaction.

### 3. Batch findings
Don't log one finding at a time to the file. Accumulate 3-5 findings, then write a batch. Reduces file I/O overhead.

### 4. Truncate tool output
- web_fetch: set maxChars to 5000-10000 for most pages
- web_search: results are already summarized, usually fine
- browser-use: extract specific elements, don't screenshot everything

### 5. Progressive summarization
Every 5-10 minutes, add a "checkpoint" to the research file:
```markdown
## Checkpoint [time]
**Key findings so far:** [3-5 bullets]
**Confidence:** [high/medium/low]
**Remaining angles:** [what to still investigate]
```
This serves as recovery point if context overflows or session dies.
