---
name: autonomy-type-based
version: 1.0.0
description: Type-based autonomous task queue system. Categorizes tasks by type (research, writing, analysis, maintenance) and lets autonomy work only on value-add tasks while cron handles maintenance. Use when you want autonomous work on specific task types, maximize token efficiency, and maintain clear separation of concerns between autonomous work and scheduled maintenance.
metadata:
  openclaw:
    emoji: "🏷️"
    category: productivity
---

# Type-Based Autonomy

Transform your agent from reactive to autonomous worker on **specific task types**.

---

## Concept

The agent pulls from `tasks/QUEUE.md` but **only works on tasks tagged with specific types**:

```
📚 Research  → ✅ Autonomy works on these
✍️ Writing   → ✅ Autonomy works on these
🔍 Analysis  → ✅ Autonomy works on these

🧹 Maintenance → ❌ Autonomy SKIPS these (cron handles)
💾 Backup      → ❌ Autonomy SKIPS these (cron handles)
```

Cron jobs handle backups, cleanup, security audits. Autonomy handles research, writing, analysis.

---

## How It Works

### 1. Task Queue Structure

Every task in `tasks/QUEUE.md` has a `@type:` label:

```markdown
## 🔴 Ready

### 📚 Research (@type:research)
- [ ] @priority:high @type:research Competitor pricing for X product
- [ ] @priority:medium @type:research Ollama model alternatives

### ✍️ Writing (@type:writing)
- [ ] @priority:medium @type:writing Blog post on memory systems
- [ ] @priority:low @type:writing Documentation update

### 🔍 Analysis (@type:analysis)
- [ ] @priority:medium @type:analysis Review weekly metrics
- [ ] @priority:low @type:analysis Analyze token patterns

### 🧹 Maintenance (@type:maintenance)
→ Autonomy IGNORES, cron handles
- [ ] @priority:medium @type:maintenance Old log cleanup
```

### 2. Heartbeat Flow

```
Heartbeat → Check urgent → No → Read QUEUE.md → Filter by @type → Pick task → Work → Update QUEUE → Log
```

**Filter logic:**
- Read all tasks in 🔴 Ready section
- **ONLY** pick tasks with `@type:research | @type:writing | @type:analysis`
- **SKIP** tasks with `@type:maintenance | @type:backup | @type:security`

### 3. Task Completion

```
1. Mark task as In Progress: @agent: @type:research [task description]
2. Work on it
3. Move to Done Today with completion notes
4. Log to memory/[today].md
5. Check GOALS.md and .learnings/ for follow-up tasks
```

---

## Task Types

### Research (@type:research)

**Definition:** Information gathering, investigation, discovery

**Examples:**
- Competitor analysis
- API documentation research
- Technology exploration
- Market research
- Best practices investigation

**Output format:**
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

**Add follow-up task to Ideas:**
```markdown
- [Idea: @type:analysis @priority:medium Analyze research findings for X]
```

---

### Writing (@type:writing)

**Definition:** Content creation, documentation, communication

**Examples:**
- Blog posts
- Documentation updates
- Email drafts
- Announcements
- Guides/tutorials

**Output format:**
```markdown
# [Title]

[Content]
```

**Post-completion:**
- If email: Add to Ideas for review by RA
- If blog/doc: Add to Ideas for publishing
- If announcement: Add to Ideas for distribution

---

### Analysis (@type:analysis)

**Definition:** Data review, metrics analysis, pattern finding

**Examples:**
- Weekly performance review
- Token usage analysis
- Log analysis
- Trend identification
- Metrics dashboard creation

**Output format:**
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

**Add follow-up tasks:**
```markdown
- [Idea: @type:writing @priority:medium Write analysis report]
- [Idea: @type:research @priority:low Investigate pattern X further]
```

---

### Maintenance (@type:maintenance)

**Definition:** System cleanup, organization, routine tasks

**Handler:** Cron (NOT autonomy)

**Examples:**
- Old log cleanup
- Temp file deletion
- File organization
- Archive old records

**Behavior:**
- Autonomy SKIPS these tasks
- Cron jobs handle them overnight
- Manual trigger if urgent, but usually not needed

---

### Backup (@type:backup)

**Definition:** Data backup, version control, sync

**Handler:** Cron (NOT autonomy)

**Examples:**
- GitHub backup
- Database backup
- Cloud sync

**Behavior:**
- Autonomy SKIPS these tasks
- Scheduled twice daily (00:00, 12:00 UTC)

---

### Security (@type:security)

**Definition:** Security checks, audits, vulnerability scans

**Handler:** Cron (NOT autonomy)

**Examples:**
- Security audit
- Permission check
- Credential review

**Behavior:**
- Autonomy SKIPS these tasks
- Monthly security audit cron (1st of month)

---

## Priority System

Priority affects task selection order:

| Priority | When to use | Selection |
|----------|-------------|-----------|
| `@priority:urgent` | Time-sensitive, deadline < 24h | Pick FIRST |
| `@priority:high` | Important, deadline 2-3 days | Pick SECOND |
| `priority:medium` | Normal importance | Pick THIRD |
| `priority:low` | Nice to have, no deadline | Pick LAST |

---

## GOALS.md Integration

Every task should support RA's long-term goal: **MONEY**

**When creating tasks:**
- Check `GOALS.md` for current objectives
- Link tasks to money-making activities
- Ask: "How does this help RA make money?"

**Examples:**

```markdown
### 📚 Research
- [ ] @priority:high @type:research Competitor pricing (GOAL: pricing strategy for new product)
- [ ] @priority:medium @type:research Market fit analysis (GOAL: validate product idea)
```

```markdown
### ✍️ Writing
- [ ] @priority:high @type:writing Sales email template (GOAL: improve conversion)
- [ ] @priority:medium @type:blog Marketing post (GOAL: drive traffic)
```

**Post-completion:**
- Update `GOALS.md` with progress notes if relevant
- Add to Ideas: follow-up tasks that advance goals

---

## .learnings/ Integration

When completing tasks, add findings to `.learnings/`:

**After research task:**
```markdown
## [LRN-20260216-001] research-findings
Research: Competitor pricing analysis

Key findings: [summarize]
```

**After analysis task:**
```markdown
## [LRN-20260216-002] analysis-insights
Analysis: Token usage patterns

Key insights: [summarize]
```

**After problem:**
```markdown
## [ERR-20260216-001] research-issue
Error: API rate limit during research

Fix: [document the fix]
```

---

## Queue Management

### Adding Tasks

**RA adds tasks directly to queue:**
```markdown
## 🔴 Ready
- [ ] @type:research @priority:high Analyze competitor X pricing
```

**The agent discovers tasks during work and adds to Ideas:**
```markdown
## 💡 Ideas
- [Idea: @type:research @priority:medium Investigate Ollama alternative models]
```

### Updating Tasks

**When starting:**
```markdown
## 🟡 In Progress
- [ ] @agent: @type:research @priority:high Competitor pricing analysis
  - Started: 2026-02-16 14:00 UTC
  - Progress: Gathering data
```

**When complete:**
```markdown
## ✅ Done Today
- [x] @agent: @type:research @priority:high Competitor pricing analysis
  - Completed: 2026-02-16 14:25 UTC
  - Output: tasks/outputs/competitor-pricing-analysis.md
```

**When blocked:**
```markdown
## 🔵 Blocked
- [ ] @type:writing @priority:medium Email draft (needs: RA review)
```

### Clearing Done Today

**Daily routine (during heartbeat or cron):**
- Move completed tasks from Done Today to `tasks/archive/` if you want to keep history
- Or simply delete if not needed
- Clear section with: `## ✅ Done Today` (empty)

---

## Token Budget

**Recommendation:** 4 sessions/day, ~3-8K tokens each = 12-32K/day

**Session strategy:**
| Time | Task Type | Tokens | Focus |
|------|-----------|--------|-------|
| 09:00 AM | Research | 8-10K | Deep investigation |
| 13:00 PM | Writing | 5-7K | Content creation |
| 17:00 PM | Analysis | 3-5K | Data review |
| 21:00 PM | Learning | 2-3K | Review learnings |

**When to stop:**
- If tokens remaining < 5K for the day
- If queue has no tasks of allowed types
- If RA is actively messaging (human priority)

---

## Coordination With Cron

Autonomy and cron work in parallel but on different task types:

| System | Task Types | Schedule |
|--------|-----------|----------|
| **Autonomy** | Research, Writing, Analysis | Any time (heartbeat-driven) |
| **Cron** | Backup, Maintenance, Security | Scheduled (midnight, noon, daily) |

**No conflicts** - they work on completely different things.

---

## When to Use This Skill

Use this skill when:
- You want autonomy focused on **value-add tasks** (research, writing, analysis)
- You want **maximum token efficiency**
- Tasks can be **clearly categorized by type**
- You want to **expand task types later** (add coding, testing as they come up)
- You want **clear separation** between autonomy and maintenance

---

## When NOT to Use This Skill

Do not use this skill when:
- You want continuous work on any task type → Use `autonomy-windowed` skill
- Task types are unclear or ambiguous → Use simpler queue
- You want the agent to handle maintenance tasks → Those belong to cron
- You want predictable work hours → Use `autonomy-windowed` for time-based control

---

## Quick Reference

**Task types for autonomy:** `@type:research` | `@type:writing` | `@type:analysis`

**Task types for cron:** `@type:maintenance` | `@type:backup` | `@type:security`

**Priority order:** `urgent` → `high` → `medium` → `low`

**Queue location:** `tasks/QUEUE.md`

---

*See templates/QUEUE.md for full template structure*
