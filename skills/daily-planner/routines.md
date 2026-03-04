# Planning Routines

## Morning Briefing

Run at configured time (default: 7:30 for exec, 8:00 for others).

**Input sources:**
- Calendar events for today
- Open commitments from `commitments.md`
- Pending tasks from previous day
- Emails flagged as "needs decision" (if email access)

**Output format (max 5 bullets):**

```markdown
## Today — [Day], [Date]

🎯 **Top 3:**
1. [Most important outcome]
2. [Second priority]
3. [Third priority]

📅 **Fixed commitments:**
- 10:00 — Call with X (prep: review Q4 numbers)
- 14:00 — Team standup

⚠️ **Deadlines approaching:**
- Project Y proposal — due tomorrow 18:00

💡 **Quick wins available:**
- Reply to Z's email (draft ready)
```

**Rules:**
- Top 3 MUST fit on screen, no scrolling
- Fixed commitments show prep needed
- Deadlines only if <48h away
- Quick wins only if truly <10min

---

## Time-Blocking Process

When user asks "plan my day" or triggered automatically:

**Step 1: Identify constraints**
- Fixed meetings/appointments
- Hard deadlines today
- Energy windows from profile

**Step 2: Assign Top 3 to peak energy**
- Hardest task → best energy block
- Never split deep work <90min
- Always buffer 15min between blocks

**Step 3: Fill remaining time**
- Admin/email in low-energy slots
- Meetings in afternoon (if exec profile)
- Leave 20% unscheduled for unexpected

**Step 4: Validate**
- Total scheduled <80% of available time
- No back-to-back without buffer
- Deep work blocks protected

**Output format:**

```markdown
### Time-Blocked Schedule

**07:00 - 08:00** Morning routine (protected)

**08:00 - 10:00** Deep Work: [Priority 1]
- Focus: [Specific deliverable]
- No interruptions

**10:00 - 10:15** Buffer/transition

**10:15 - 11:00** [Meeting/Call]
- Context: [Who, what, prep needed]

**11:00 - 12:00** [Priority 2 or Admin block]

**12:00 - 13:00** Lunch (protected)

...
```

---

## Evening Review

Run at configured time (default: 21:00).

**Questions to answer:**
1. Did Top 3 get done? (celebrate or understand why not)
2. What commitments did I make today? (log them)
3. What's tomorrow's preview? (reduce morning anxiety)
4. Anything need prep tonight? (uniforms, documents, meals)

**Output format:**

```markdown
## End of Day — [Date]

### Done ✅
- [Completed item 1]
- [Completed item 2]

### Moved to tomorrow ➡️
- [Item that didn't happen + reason]

### New commitments logged
- Tell X about Y by Friday
- Send proposal to Z by Monday

### Tomorrow preview
- 3 meetings, 1 deadline
- Top priority: [Most important for tomorrow]

### Tonight prep
- Pack gym bag for morning workout
```

---

## Weekly Planning

Run Sunday evening or Monday morning (configurable).

**Review section:**
- What got done last week (celebrate wins)
- What kept getting pushed (pattern detection)
- Time audit: reactive vs proactive ratio

**Planning section:**
- Top 3 priorities for the week (not 10)
- Hard deadlines mapped to days
- Deep work blocks scheduled in advance
- Buffer day (usually Friday) for overflow

**Output format:**

```markdown
## Week of [Date Range]

### Last week
- ✅ Completed: [X items]
- ↩️ Pushed: [Y items] — pattern: [mostly admin/meetings/projects?]
- ⏱️ Time split: 60% proactive, 40% reactive

### This week's priorities
1. [Big outcome 1]
2. [Big outcome 2]
3. [Big outcome 3]

### Day-by-day overview
| Day | Focus | Deadlines | Meetings |
|-----|-------|-----------|----------|
| Mon | Deep work AM | - | 2 |
| Tue | Client calls | Proposal due | 4 |
| ... | ... | ... | ... |

### Protected time
- Tue/Thu mornings: deep work
- Friday PM: buffer for overflow
```

---

## On-Demand Routines

**"Am I overcommitted?"**
1. Count meetings this week
2. Count pending deliverables with deadlines
3. Calculate available hours vs required hours
4. Flag if >100% utilization
5. Suggest: what to cut, delegate, or push

**"Clear my afternoon"**
1. List what's scheduled
2. Identify what can move (not hard deadlines)
3. Suggest: "Move X to tomorrow, cancel/async Y"
4. After approval: reschedule and draft notifications

**"What did I promise this week?"**
1. Pull all commitments from `commitments.md`
2. Filter by deadline = this week
3. Show: who, what, when due
4. Flag: any at risk?
