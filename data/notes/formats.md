# Note Formats — Notes

## Meeting Notes

```markdown
---
date: YYYY-MM-DD
type: meeting
title: [Meeting Title]
tags: [topic1, topic2]
attendees: [name1, name2, name3]
duration: XX min
---

# Meeting: [Title] — YYYY-MM-DD

**Time:** HH:MM - HH:MM | **Duration:** XX min
**Facilitator:** [Name]
**Attendees:** Name1, Name2, Name3

## 🎯 Meeting Goal
[One sentence — what was this meeting supposed to achieve?]

## 📝 Key Discussion Points
- Point 1
- Point 2
- Point 3

## ✅ Decisions Made
- [DECISION] **Topic:** Decision text — *Owner:* @name | *Effective:* date
- [DECISION] **Topic:** Decision text — *Owner:* @name | *Effective:* date

## ⚡ Action Items
| # | Task | Owner | Due | Status |
|---|------|-------|-----|--------|
| 1 | [Task description] | @name | YYYY-MM-DD | ⬜ |
| 2 | [Task description] | @name | YYYY-MM-DD | ⬜ |

## ❓ Open Questions
- Question 1 — *Needs input from:* @name
- Question 2 — *Needs input from:* @name

## 🅿️ Parking Lot
- Topic deferred to future discussion

## 📊 Meeting Effectiveness: [X/10]
□ Clear agenda beforehand
□ Started/ended on time
□ Decisions were made
□ Actions have owners + deadlines
□ Could NOT have been an email

## 📎 Related Notes
- [[YYYY-MM-DD_previous-meeting]]
```

---

## Decision Log Entry

```markdown
---
date: YYYY-MM-DD
type: decision
title: [Decision Title]
tags: [domain, impact-area]
status: active | superseded
---

# [DECISION] Title — YYYY-MM-DD

## Context
Why was this decision needed? What problem does it solve?

## Options Considered

### Option A: [Name]
- ✅ Pro 1
- ✅ Pro 2
- ❌ Con 1

### Option B: [Name]
- ✅ Pro 1
- ❌ Con 1
- ❌ Con 2

### Option C: [Name]
- ✅ Pro 1
- ✅ Pro 2
- ❌ Con 1

## Decision
**Chosen:** Option [X]

## Rationale
Why this option was selected over alternatives.

## Implementation
- **Owner:** @name
- **Effective Date:** YYYY-MM-DD
- **Review Date:** YYYY-MM-DD (optional)

## Dependencies
- Depends on: [[related-decision]]
- Blocks: [[future-decision]]

## Reversal
- [REVERSES] [[previous-decision]] — if this supersedes a prior decision
```

---

## Brainstorm Notes

```markdown
---
date: YYYY-MM-DD
type: brainstorm
title: [Topic]
tags: [domain, project]
participants: [name1, name2]
---

# Brainstorm: [Topic] — YYYY-MM-DD

**Participants:** Name1, Name2, Name3
**Duration:** XX min
**Goal:** [What are we trying to generate ideas for?]

## 💡 Raw Ideas
1. Idea one
2. Idea two
3. Idea three
4. Idea four
5. Idea five
[No filtering during capture — quantity over quality]

## 🎯 Clusters
Group related ideas:

### Cluster A: [Theme]
- Idea 1
- Idea 4

### Cluster B: [Theme]
- Idea 2
- Idea 3

### Cluster C: [Theme]
- Idea 5

## ⭐ Top 3 to Explore
1. **[Idea]** — Why: [rationale]
2. **[Idea]** — Why: [rationale]
3. **[Idea]** — Why: [rationale]

## ⚡ Next Steps
| Action | Owner | Due |
|--------|-------|-----|
| Research idea 1 | @name | YYYY-MM-DD |
| Prototype idea 2 | @name | YYYY-MM-DD |
```

---

## Daily Journal

```markdown
---
date: YYYY-MM-DD
type: journal
mood: [emoji]
energy: [1-10]
---

# Daily Note — YYYY-MM-DD

## 🌅 Morning Intention
What do I want to accomplish today?

## ✅ Completed
- [x] Task 1
- [x] Task 2

## 🚧 In Progress
- [ ] Task 3 — blocked by X

## 💡 Insights
- Learning or realization

## 🙏 Gratitude
- Something I'm grateful for

## 📝 Notes
Free-form thoughts, ideas, observations.

## 🎯 Tomorrow
Top 3 priorities for tomorrow:
1. Priority 1
2. Priority 2
3. Priority 3
```

---

## Project Update

```markdown
---
date: YYYY-MM-DD
type: project-update
project: [Project Name]
tags: [project-slug]
status: on-track | at-risk | blocked
---

# Project Update: [Name] — YYYY-MM-DD

**Status:** 🟢 On Track | 🟡 At Risk | 🔴 Blocked
**Progress:** [X]% complete
**Next Milestone:** [Milestone] — Due: YYYY-MM-DD

## ✅ Completed This Period
- Accomplishment 1
- Accomplishment 2

## 🚧 In Progress
- [ ] Task 1 (XX% done)
- [ ] Task 2 (XX% done)

## 🚨 Blockers
- Blocker 1 — *Waiting on:* @name
- Blocker 2 — *Needs:* [resource/decision]

## ⚠️ Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | High/Med/Low | High/Med/Low | Plan |

## 📊 Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Metric 1 | X | Y | 🟢/🟡/🔴 |

## ⚡ Next Actions
| Action | Owner | Due |
|--------|-------|-----|
| Action 1 | @name | YYYY-MM-DD |
```

---

## Quick Note (Minimal Format)

For rapid capture when full structure isn't needed:

```markdown
---
date: YYYY-MM-DD HH:MM
type: quick
tags: [tag1, tag2]
---

# Quick Note — YYYY-MM-DD HH:MM

[Content]

**Actions:** (if any)
- [ ] @owner: task — due: date
```

---

## 1-on-1 Meeting

```markdown
---
date: YYYY-MM-DD
type: 1on1
with: [Person Name]
tags: [1on1, person-name]
---

# 1-on-1: [Person Name] — YYYY-MM-DD

## 🔄 Since Last Time
- Status of previous action items

## 📋 Their Topics
- Topic they want to discuss

## 📋 My Topics
- Topic I want to discuss

## 💬 Discussion Notes
[Free-form notes from conversation]

## ⚡ Action Items
| Task | Owner | Due |
|------|-------|-----|
| Task 1 | @them | date |
| Task 2 | @me | date |

## 📅 Next 1-on-1
Date: YYYY-MM-DD
```
