---
name: arxiv-skill-learning
description: Orchestrates the continuous learning of new skills from arXiv papers. Use this to trigger a learning cycle, which fetches papers, extracts code/skills, and solidifies them.
---

# ArXiv Skill Learning

## Usage

```javascript
const learner = require('./index');
const result = await learner.main();
```

## Workflow

1.  **Patrol**: Checks arXiv for relevant new papers (Agent, LLM, Tool Use).
2.  **Extract**: Uses `arxiv-skill-extractor` to generate skill code.
3.  **Test**: Runs generated tests.
4.  **Solidify**: Commits the new skill to the workspace.

## Configuration

- Target Categories: cs.AI, cs.CL, cs.LG, cs.SE
- Schedule: Hourly
