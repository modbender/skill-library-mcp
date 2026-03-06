---
name: arxiv-skill-extractor
description: Automates the process of extracting reusable skill code from arXiv papers. Use this skill to turn paper insights into actual OpenClaw skills.
---

# ArXiv Skill Extractor

This skill wraps `arxiv-paper-reviews` and provides an automated pipeline for:
1.  Fetching papers.
2.  Extracting key algorithms.
3.  Generating skill templates.

## Usage

### Extract Skill from a Paper

```javascript
const { extractSkill } = require("./skills/arxiv-skill-extractor/index.js");

async function run() {
  const result = await extractSkill("4711d67c242a5ecba2751e6b");
  console.log(result);
}

run();
```

### Automation

Run the default extraction loop (uses `local_task:arxiv_skill_learning` config):

```bash
# 自动读取 pending_skill_task.json 中的 paper_key
node skills/arxiv-skill-extractor/index.js

# 或直接指定 paper_key
node skills/arxiv-skill-extractor/index.js 4711d67c242a5ecba2751e6b
```

## Why?

We need to continuously learn from new research. Manual reading is slow. This skill bridges the gap between paper knowledge and executable code.
