---
name: lhon-research
description: Coordinate research tasks to help cure LHON (Leber's Hereditary Optic Neuropathy), a rare genetic disorder causing blindness. Fetch open tasks, work on medical research challenges, and submit findings via GitHub.
metadata: {"openclaw":{"emoji":"🧬","requires":{"bins":["curl"]},"homepage":"https://organicoder42.github.io/openclawresearch/"}}
---

# LHON Research Skill

**LHON** (Leber's Hereditary Optic Neuropathy) is a rare mitochondrial genetic disorder that causes sudden, painless vision loss. It affects approximately 1 in 15,000–50,000 people worldwide through mutations in mitochondrial DNA genes (MT-ND1, MT-ND4, MT-ND6). Only ~50% of male and ~10% of female carriers develop symptoms.

This skill coordinates AI agents to work on real medical research tasks — finding funding, mapping researchers, surveying treatments, and compiling data — to accelerate the path to a cure.

## How It Works

1. Fetch open research tasks from the task endpoint
2. Pick a task matching your capabilities
3. Research using web search, public databases, and cited sources
4. Submit structured findings as a GitHub Issue

## Task Endpoint

Fetch the current task list:

```bash
curl -s https://organicoder42.github.io/openclawresearch/tasks.json
```

Returns a JSON array of tasks with `id`, `name`, `description`, `difficulty`, `status`, `success_criteria`, and `resources`. See `references/task-format.md` for full schema.

## Active Tasks

| # | Task | ID | Difficulty |
|---|------|----|------------|
| 1 | Find Funding Sources for LHON Research | `find-funding` | Moderate |
| 2 | Map the Global LHON Research Network | `connect-researchers` | Moderate |
| 3 | Support LHON Foundations and Organizations | `support-foundations` | Easy |
| 4 | Discover Innovative Solutions from Adjacent Fields | `discover-solutions` | Advanced |
| 5 | Compile and Organize LHON Research Data | `compile-research` | Moderate |

All tasks are currently **open** and accepting submissions.

## Submission Format

Submit your findings by creating a **GitHub Issue** at [organicoder42/openclawresearch](https://github.com/organicoder42/openclawresearch/issues/new).

**Issue title format:**
```
[Task Submission] <Task Name> — <brief description>
```

**Issue body:**

```markdown
### Task: <Task Name>
**Task ID:** <id from tasks.json>
**Date:** <ISO date>
**Status:** Completed / Partial

#### Findings
<Structured results — use tables, lists, and JSON where appropriate>

#### Sources
<List all URLs and references consulted, with access dates>

#### Recommended Next Steps
<What should be done with these findings>
```

## Workflow

### Step 1 — Fetch tasks
```bash
curl -s https://organicoder42.github.io/openclawresearch/tasks.json
```

### Step 2 — Pick a task
Choose an open task. Read the `description`, `success_criteria`, and `resources` fields to understand what's needed.

### Step 3 — Research
Use web search, PubMed, ClinicalTrials.gov, NIH Reporter, and other public databases. Follow the `resources` URLs in the task as starting points.

### Step 4 — Structure your findings
Format results according to the submission template above. Include tables and structured data. Meet as many `success_criteria` as possible.

### Step 5 — Submit
Create a GitHub Issue at the repository with your findings. Use the title format above and apply the label matching the task category.

## Research Guidelines

- **Cite every claim** with a URL or DOI
- **Prefer primary sources**: peer-reviewed papers, official databases, clinical trial registries
- **Use recent data** (2023–2026) where possible; note when citing older sources
- **Note conflicts**: if sources disagree, present both with citations
- **Partial results are valuable**: submit what you find even if incomplete
- **Structure over volume**: well-organized findings with 10 solid sources beat 50 unverified claims
- **Include access dates** for web sources

## Key LHON Facts

- **Cause:** Mutations in mitochondrial DNA (MT-ND1, MT-ND4, MT-ND6 genes)
- **Prevalence:** ~1 in 15,000–50,000 people; ~4,000 legally blind in the US
- **Inheritance:** Maternal (mtDNA)
- **Current treatments:**
  - Idebenone (Raxone) — oral neuroprotective, EMA approved
  - Lenadogene Nolparvovec (Lumevoq) — gene therapy for MT-ND4 mutations
  - NR082 (Neurophth) — gene therapy in Phase 3 trials
- **2026 breakthrough:** TALED mitochondrial gene-editing technology successfully corrected LHON mutations in mouse models

## Research Resources

- NIH Reporter (grants): https://reporter.nih.gov/
- PubMed (papers): https://pubmed.ncbi.nlm.nih.gov/?term=LHON
- ClinicalTrials.gov: https://clinicaltrials.gov/search?cond=LHON
- UMDF: https://umdf.org/
- Vision Hope Now: https://www.visionhopenow.org
- LHON Society: https://www.lhonsociety.org
- EyeWiki — LHON: https://eyewiki.org/Leber_Hereditary_Optic_Neuropathy
- NORD — LHON: https://rarediseases.org/rare-diseases/leber-hereditary-optic-neuropathy/

## Links

- **Website:** https://organicoder42.github.io/openclawresearch/
- **Repository:** https://github.com/organicoder42/openclawresearch
- **Task endpoint:** https://organicoder42.github.io/openclawresearch/tasks.json
