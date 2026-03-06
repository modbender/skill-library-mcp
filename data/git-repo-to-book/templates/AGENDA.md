# [Book Title] - Project Agenda

## Phase Overview

| Phase | Duration | Agents | Output |
|-------|----------|--------|--------|
| Research | Day 1 | 2–3 parallel | research/*.md |
| Outlines | Day 2 | 2 parallel | chapters/*-outline.md |
| Writing | Days 3–5 | 4–5 parallel | chapters/*.md |
| Review | Day 6 | 2 parallel | reviews/*.md |
| Integration | Day 7 | 1 | book/manuscript.md |
| Polish | Day 7 | 1 | book/final-manuscript.md |
| Publish | Day 8 | 1 | git push + report |

---

## Phase 1: Research

**Goal:** Understand the subject deeply enough to write authoritatively.

### Tasks
- [ ] Spawn Research Agent A: analyze [source 1]
- [ ] Spawn Research Agent B: analyze [source 2]
- [ ] Spawn Synthesis Agent: produce pattern-synthesis.md

**Done when:** research/pattern-synthesis.md exists and covers 6+ patterns.

---

## Phase 2: Outlines

**Goal:** Plan each chapter before writing begins.

### Tasks
- [ ] Spawn Outline Agent batch 1: intro + chapters 1–5
- [ ] Spawn Outline Agent batch 2: chapters 6–12
- [ ] Review all outlines — edit if needed
- [ ] Commit outlines to git

**Done when:** All chapter-NN-outline.md files exist and reviewed.

---

## Phase 3: Writing

**Goal:** Draft all chapters in parallel.

### Agent Assignments
- [ ] Writing Agent 1: introduction + chapters 1–3
- [ ] Writing Agent 2: chapters 4–6
- [ ] Writing Agent 3: chapters 7–9
- [ ] Writing Agent 4: chapters 10–12

**Done when:** All chapter files exist and WORKLOG shows completion.

---

## Phase 4: Review

**Goal:** Identify and fix quality issues.

### Tasks
- [ ] Review Agent A: introduction + chapters 1–6
- [ ] Review Agent B: chapters 7–12
- [ ] Fix all CRITICAL issues
- [ ] Log MINOR issues for polish phase

**Done when:** reviews/ files exist and no open CRITICAL issues.

---

## Phase 5: Integration

**Goal:** Single coherent manuscript.

### Tasks
- [ ] Spawn Integration Agent: merge all chapters
- [ ] Verify manuscript.md has all chapters in correct order
- [ ] Fix any cross-reference issues

**Done when:** book/manuscript.md exists with all chapters.

---

## Phase 6: Polish

**Goal:** Publication-ready document.

### Tasks
- [ ] Spawn Polish Agent: create final-manuscript.md
- [ ] Title page, copyright, TOC
- [ ] Write metadata.json
- [ ] HTML export (optional)

**Done when:** book/final-manuscript.md and book/metadata.json exist.

---

## Phase 7: Publish

**Goal:** Push to GitHub and report.

### Tasks
- [ ] Final git commit
- [ ] Push to remote
- [ ] Report to user: word count, chapter count, URL

**Done when:** git push succeeds.

---

## Success Metrics

- Word count: ≥ [TARGET] words
- Chapter count: [N] chapters
- Review pass rate: ≥ 85% issues resolved
- Cost: ≤ $100
- Timeline: completed within [N] days
