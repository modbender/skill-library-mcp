# Task Queue

*Last updated: [timestamp]*
*Autonomy mode: Type-based*
*Active types: research, writing, analysis*

---

## 🔴 Ready (can be picked up)

### 📚 Research (@type:research)
**Definition:** Information gathering, investigation, discovery

- [ ] @type:research @priority:medium [Add your research task here]

### ✍️ Writing (@type:writing)
**Definition:** Content creation, documentation, communication

- [ ] @type:writing @priority:medium [Add your writing task here]

### 🔍 Analysis (@type:analysis)
**Definition:** Data review, metrics analysis, pattern finding

- [ ] @type:analysis @priority:medium [Add your analysis task here]

### 🧹 Maintenance (@type:maintenance)
→ Autonomy IGNORES these, cron handles

- [ ] @type:maintenance @priority:medium [Maintenance task for cron]

---

## 🟡 In Progress

[Tasks currently being worked on]

- [ ] @agent: @type:research @priority:high [Task description]
  - Started: 2026-02-16 HH:MM UTC
  - Progress: [Current progress note]

---

## 🔵 Blocked

[Tasks waiting for something]

- [ ] @type:writing @priority:medium [Task] (needs: [what's blocking])

---

## ✅ Done Today

[Tasks completed today - clear daily]

- [x] @agent: @type:research @priority:high [Task]
  - Completed: 2026-02-16 HH:MM UTC
  - Output: [path to output file or notes]

---

## 💡 Ideas

[Candidate tasks for future work - promote to Ready when ready]

- [Idea: @type:research @priority:medium [Research idea description]]
- [Idea: @type:writing @priority:low [Writing idea description]]

---

## Task Types Reference

| Type | Handler | Example |
|------|---------|---------|
| `research` | ✅ Autonomy | Competitor analysis, API docs, technology research |
| `writing` | ✅ Autonomy | Blog posts, documentation, emails, guides |
| `analysis` | ✅ Autonomy | Metrics review, log analysis, trends |
| `maintenance` | ❌ Cron | Old log cleanup, temp file deletion |
| `backup` | ❌ Cron | GitHub backup, database sync |
| `security` | ❌ Cron | Security audit, permission check |

---

## Priority Levels

| Priority | When to use | Selection order |
|----------|-------------|-----------------|
| `urgent` | Deadline < 24h | First |
| `high` | Deadline 2-3 days | Second |
| `medium` | Normal importance | Third |
| `low` | Nice to have, no deadline | Last |

---

## Connecting to GOALS.md

Every task should link to RA's long-term goal: **MONEY**

**Add goal references:**
```markdown
- [ ] @type:research @priority:high Competitor pricing (GOAL: pricing strategy)
- [ ] @type:writing @priority:medium Sales email template (GOAL: improve conversion)
```

**After completion:** Update GOALS.md with progress notes

---

## Research Task Output Format

```markdown
## Research: [Topic]

### Findings
- Key point 1
- Key point 2

### Sources
- [Source 1](url)
- [Source 2](url)

### Recommendations
- Recommendation 1
- Recommendation 2
```

**Post-completion:** Add to Ideas → follow-up analysis task

---

## Writing Task Output Format

```markdown
# [Title]

[Content goes here]
```

**Post-completion:**
- Email: Add to Ideas for RA review
- Blog/doc: Add to Ideas for publishing
- Announcement: Add to Ideas for distribution

---

## Analysis Task Output Format

```markdown
## Analysis: [Topic]

### Data Reviewed
- [List of data sources]

### Key Findings
- Finding 1 with metric
- Finding 2 with metric

### Patterns
- Pattern 1
- Pattern 2

### Recommendations
- Action 1
- Action 2
```

**Post-completion:** Add to Ideas → follow-up writing or research task

---

## Learnings Integration

After completing tasks, add to `.learnings/`:

```markdown
## [LRN-20260216-001] research-findings
Research: [Topic]

Key findings: [summarize]
```

```markdown
## [ERR-20260216-001] task-issue
Error: [Problem description]

Fix: [Document the fix]
```

---

*Autonomy pulls from Research, Writing, Analysis only*
*Skips Maintenance, Backup, Security (those belong to cron)*
