# Jarvis Research Workflow - Complete Process

## Overview

This document describes the complete workflow for Jarvis's paper research process, from user request to final delivery.

---

## 📋 Complete Workflow

```
User Request
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 1: Fetch Papers                                    │
│ Command: python3 scripts/fetch_papers.py --download --json │
│ Output: JSON with paper list + PDF paths               │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Review Papers (Jarvis Decision)                 │
│ - Examine paper list                                   │
│ - Select papers for sub-agent review                   │
│ - Typically: Top 5-6 by relevance score                │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Generate Sub-agent Tasks                        │
│ Command: python3 scripts/review_papers.py --papers '<json>' │
│ Output: JSON with tasks for each paper                 │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Spawn Sub-agents for Parallel Review            │
│ Command: clawdbot sessions spawn --task "<task>" --label "<name>" │
│ - Each paper gets its own sub-agent                    │
│ - Sub-agents read full paper via arXiv HTML            │
│ - Output: JSON with score, recommendation              │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Jarvis Review                                   │
│ - Collect all sub-agent reviews                        │
│ - Analyze scores and recommendations                   │
│ - Final selection: score >= 4 AND recommended == yes   │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Generate Briefing (Standard Format Required)   │
│ - For each selected paper:                             │
│   1. Fetch arXiv HTML page (for institutions)          │
│   2. Fetch arXiv HTML full text (for experiments)      │
│   3. Extract: institutions, Chinese abstract,          │
│      contributions, conclusions, experiments           │
│   4. Write: Title, Authors, Institutions, Abstract,    │
│      Contribution, Conclusion, Experiments, Notes      │
│ - Output: ~/jarvis-research/papers/briefing-YYYY-MM-DD.md │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│ Step 7: Deliver                                         │
│ Command: clawdbot message send --channel telegram --target <id> --message "<briefing>" │
└─────────────────────────────────────────────────────────┘
     ↓
Done
```

---

## Step Details

### Step 1: Fetch Papers

```bash
cd ~/skills/jarvis-research
python3 scripts/fetch_papers.py --download --json
```

**Expected Output:**
```json
{
  "papers": [
    {
      "id": "2601.19082",
      "title": "Paper Title",
      "summary": "Abstract...",
      "authors": ["Author1", "Author2"],
      "published": "2026-01-29",
      "url": "https://arxiv.org/abs/2601.19082",
      "pdf_url": "https://arxiv.org/pdf/2601.19082.pdf",
      "category": "cs.MA",
      "relevance_score": 5
    },
    ...
  ],
  "total": 15,
  "papers_dir": "/home/ubuntu/jarvis-research/papers"
}
```

### Step 2: Jarvis Review (Manual Decision)

Examine the papers and decide which to send for sub-agent review.

**Criteria:**
- Relevance score >= 3
- Based on title and summary
- Typically select top 5-6 papers

### Step 3: Generate Sub-agent Tasks

```bash
# Option A: Pipe from fetch
python3 scripts/fetch_papers.py --json | python3 scripts/review_papers.py --json

# Option B: Direct with selected papers
python3 scripts/review_papers.py --papers '<papers-json>' --json
```

**Expected Output:**
```json
{
  "papers": [...],
  "subagent_tasks": [
    {
      "paper_id": "2601.19082",
      "task": "请完整阅读这篇论文并给出评分：...",
      "label": "review-2601.19082"
    },
    ...
  ],
  "count": 5,
  "instructions": "使用 sessions_spawn 开子代理..."
}
```

### Step 4: Spawn Sub-agents (Parallel Review)

For each paper, spawn a **separate sub-agent** to read and review:

```bash
# Spawn sub-agent for paper 1
clawdbot sessions spawn \
  --task "请完整阅读这篇论文并给出评分：<task_from_step_3>" \
  --label "review-2601.19082"

# Spawn sub-agent for paper 2
clawdbot sessions spawn \
  --task "请完整阅读这篇论文并给出评分：<task_from_step_3>" \
  --label "review-2601.18631"

# ... repeat for all papers
```

**Sub-agent Task Requirements:**

Each sub-agent should:
1. Fetch paper content (choose one):
   - Option A: arXiv HTML page: `https://arxiv.org/html/<paper-id>`
   - Option B: Downloaded PDF: `python3 scripts/read_pdf.py ~/jarvis-research/papers/<paper-id>.pdf --sections --json`
2. Extract:
   - Authors (all)
   - Institutions (real ones, NOT author names)
   - Full abstract
   - Core contributions (2-4 points)
   - Main conclusions (2-4 points)
   - Experimental setup and key findings
3. Score: 1-5
4. Recommend: yes/no
5. Reply with **JSON format**:

```json
{
  "review": {
    "id": "2601.19082",
    "score": 5,
    "contribution": "一句话核心贡献",
    "conclusion": "一句话主要结论",
    "experiments": "实验设置和关键发现",
    "recommended": "yes"
  }
}
```

**Parallelism:**
- All sub-agents can run **in parallel** (default maxConcurrent: 8)
- Much faster than sequential reading
- Each sub-agent has its own context and token usage

### Step 5: Jarvis Review (Final Decision)

**Selection Criteria:**
- AI recommended: "yes"
- Score: >= 4

**Output:** List of papers to include in briefing

### Step 6: Generate Briefing (CRITICAL - Follow Standard Format)

For EACH selected paper:

1. **Fetch arXiv HTML page:**
   ```bash
   curl https://arxiv.org/abs/<paper-id>
   # Or use web_fetch
   web_fetch --url https://arxiv.org/abs/<paper-id> --extractMode text
   ```

2. **Extract information:**
   - Authors (all)
   - Institutions (real ones, NOT author names)
   - Abstract (English)

3. **Fetch HTML full text (for experiments):**
   ```bash
   curl https://arxiv.org/html/<paper-id>
   ```

4. **Write Chinese translation** of abstract

5. **Write briefing section** following **SKILL.md Standard Format**:

```markdown
## 📄 PAPER_TITLE

**标题:** Full title
**作者:** Author1, Author2, Author3...
**机构:** Real institution1; Real institution2...
**arXiv:** https://arxiv.org/abs/<id>
**PDF:** https://arxiv.org/pdf/<id>.pdf
**发布日期:** YYYY-MM-DD | **分类:** cs.XX

### 摘要
Chinese translation of full abstract (~200-400 characters).

### 核心贡献
1. Contribution 1
2. Contribution 2
3. Contribution 3

### 主要结论
1. Conclusion 1
2. Conclusion 2
3. Conclusion 3

### 实验结果
• Experiment setup
• Key findings

### Jarvis 笔记
- AI 评分: X/5
- 推荐度: ⭐⭐⭐⭐⭐
- 适合研究方向: Field1, Field2
- 重要性: One sentence
```

6. **Save to file:**
   ```bash
   ~/jarvis-research/papers/briefing-$(date +%Y-%m-%d).md
   ```

### Step 7: Deliver

```bash
clawdbot message send \
  --channel telegram \
  --target <user-id> \
  --message "$(cat ~/jarvis-research/papers/briefing-YYYY-MM-DD.md)"
```

---

## Quick Reference Commands

```bash
# Full workflow (manual)
cd ~/skills/jarvis-research

# Step 1: Fetch papers
python3 scripts/fetch_papers.py --download --json

# Step 2: Jarvis selects papers (manual)

# Step 3: Generate sub-agent tasks
python3 scripts/review_papers.py --papers '<json>' --json

# Step 4: Spawn sub-agents (parallel)
clawdbot sessions spawn --task "<task1>" --label "review-<id1>"
clawdbot sessions spawn --task "<task2>" --label "review-<id2>"
# ... repeat for all papers

# Step 5: Jarvis reviews results (manual)

# Step 6: Generate briefing (manual with web_fetch)

# Step 7: Deliver
clawdbot message send --channel telegram --target <id> --message "<content>"
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Missing institutions | Fetch arXiv HTML page, extract affiliations |
| Incomplete abstract | Fetch HTML full text, parse abstract section |
| Missing experiments | Fetch arXiv HTML full text (`/html/<id>`) |
| API failure | Use direct HTTP request with API key |
| JSON parsing error | Extract JSON from markdown code block |

---

## Files Generated

- **PDFs:** `~/jarvis-research/papers/<paper-id>.pdf`
- **Briefing:** `~/jarvis-research/papers/briefing-YYYY-MM-DD.md`

---

*Jarvis Research Workflow Documentation*
