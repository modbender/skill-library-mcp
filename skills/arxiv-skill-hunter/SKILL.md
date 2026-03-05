---
name: arxiv-skill-hunter
description: Patrol latest arXiv papers and auto-generate Node.js learned skills through hunter to extractor pipeline.
metadata:
  {"openclaw":{"requires":{"bins":["node"]}}}
---

# ArXiv Skill Hunter

## What it does

- Pulls latest papers from `arxiv-paper-reviews`
- Selects a candidate paper
- Writes `memory/evolution/pending_skill_task.json`
- Triggers `arxiv-skill-extractor` to generate a runnable Node.js skill

## Run

```bash
node skills/arxiv-skill-hunter/index.js
```

## Output

- Pending/extracted task state: `memory/evolution/pending_skill_task.json`
- Generated skills: `skills/arxiv-learned-*`
