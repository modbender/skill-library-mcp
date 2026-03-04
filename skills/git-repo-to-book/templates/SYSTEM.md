# [Book Title] - System Definition

## Mission
[Describe the book's purpose, target audience, and key contribution in 2-3 sentences.]

## State Machine
**Current State:** PLANNING

**States:**
1. PLANNING → RESEARCH (when SYSTEM.md + AGENDA.md complete)
2. RESEARCH → WRITING (when pattern-synthesis.md exists)
3. WRITING → REVIEWING (when all chapter drafts exist)
4. REVIEWING → INTEGRATING (when quality reviews complete)
5. INTEGRATING → POLISHING (when manuscript.md merged)
6. POLISHING → PUBLISHING (when final-manuscript.md ready)
7. PUBLISHING → COMPLETE (when committed + pushed)

## Decision Rules

### Proceed to next state when:
- All tasks in current state marked DONE in AGENDA.md
- Quality gates passed (no CRITICAL issues in reviews/)
- Resources available (context window, API credits)

### Pause/retry when:
- Stuck on a task for >2 hours without progress
- Quality check fails 3 times on same content
- Cost exceeds $50/day

### Seek human input when:
- Major scope change needed
- Ethical concern or sensitive content detected
- Critical ambiguity that blocks writing

## Agent Roles

### Director (Main Session)
- Oversees entire project, reads WORKLOG.md to assess progress
- Spawns agents per phase, monitors quality gates
- Model: anthropic/claude-sonnet-4-6

### Research Agent (Isolated)
- Analyzes source material, identifies patterns
- Outputs structured findings to research/
- Model: openrouter/google/gemini-2.5-pro-preview

### Writing Agent (Isolated)
- Writes 3 chapters per agent instance
- References outlines and pattern-synthesis.md
- Model: anthropic/claude-sonnet-4-6

### Review Agent (Isolated)
- Checks chapters for quality, consistency, accuracy
- Outputs issue lists to reviews/
- Model: openrouter/deepseek/deepseek-v3.2

### Integration Agent (Isolated)
- Merges chapters into manuscript.md
- Fixes cross-references
- Model: anthropic/claude-sonnet-4-6

### Polish Agent (Isolated)
- Creates final-manuscript.md
- Adds TOC, title page, metadata
- Model: anthropic/claude-sonnet-4-6

## Chapters

| # | Title | Status |
|---|-------|--------|
| Intro | Introduction | PENDING |
| 1 | [Chapter Title] | PENDING |
| 2 | [Chapter Title] | PENDING |
| 3 | [Chapter Title] | PENDING |
| 4 | [Chapter Title] | PENDING |
| 5 | [Chapter Title] | PENDING |
| 6 | [Chapter Title] | PENDING |
| 7 | [Chapter Title] | PENDING |
| 8 | [Chapter Title] | PENDING |
| 9 | [Chapter Title] | PENDING |
| 10 | [Chapter Title] | PENDING |
| 11 | [Chapter Title] | PENDING |
| 12 | [Chapter Title] | PENDING |

## File System Protocol
- Read WORKLOG.md before starting any task
- Update WORKLOG.md after each milestone (append-only)
- Commit to git after completing each phase
- Never delete content — mark as DEPRECATED if superseded

## Success Criteria
- [ ] All chapters drafted (target: ~6,000–8,000 words each)
- [ ] Quality review: >85% of issues marked RESOLVED
- [ ] Final manuscript: single cohesive document
- [ ] HTML export: renders correctly
- [ ] Git committed and pushed

## Safety Rules
- Never include private user data, API keys, or PII
- Cite sources; flag unverifiable claims with [UNVERIFIED]
- Cost limit: $100 total project
- Backup: commit to git after every chapter

---
**Initialized:** [DATE]
**Target completion:** [DATE]
