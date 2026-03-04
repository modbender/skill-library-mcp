# Commitment Tracking

## What Gets Tracked

Every promise or commitment made in conversation:

**Trigger phrases:**
- "I'll send you..."
- "Let me get back to you..."
- "I'll check on that..."
- "I promised to..."
- "Can you remind me to..."
- "I need to tell X about Y"

**Extracted data:**
| Field | Example |
|-------|---------|
| What | Send proposal |
| To whom | Client X |
| By when | Friday 5pm |
| Context | Follow-up to meeting |

---

## Storage Format

In `~/planner/commitments`:

```markdown
## Open Commitments

### Due This Week

- [ ] **Send proposal to Client X** — Due: Fri 17:00
  - Context: Follow-up to Tuesday meeting
  - Status: Draft started

- [ ] **Reply to investor email** — Due: Thu EOD
  - Context: Questions about metrics
  - Status: Need to pull data first

### Due Next Week

- [ ] **Review contractor's work** — Due: Mon 15th
  - Context: Website redesign phase 1
  - Status: Waiting for their delivery

### No Deadline (but promised)

- [ ] **Coffee with Maria** — Promised: 2 weeks ago
  - Context: Networking, she reached out
  - Action: Propose specific dates

---

## Completed (last 7 days)

- [x] ~~Send onboarding docs to new hire~~ — Done: Wed
- [x] ~~Call back the accountant~~ — Done: Tue
```

---

## Reminder System

**Automatic reminders:**

| Time before deadline | Action |
|---------------------|--------|
| 1 week | Include in weekly planning |
| 48 hours | Add to daily briefing |
| 24 hours | Explicit reminder: "Tomorrow: X due" |
| 2 hours | Final alert: "X due in 2h, is it ready?" |
| Overdue | Flag daily until resolved |

**Overdue handling:**
Don't nag constantly. Daily morning briefing includes:
"Overdue: 2 items. [Show them]. Update status or mark done?"

---

## Follow-up Tracking

For things waiting on others:

**Trigger phrases:**
- "I'm waiting for X to..."
- "Ball's in their court"
- "They said they'd get back to me"
- "Sent, waiting for response"

**Follow-up rules:**
- After 72h with no response: "Want me to draft a follow-up?"
- After 1 week: "X hasn't replied. Priority: high/low?"
- Passive mode: just track, don't prompt (for low-priority)

**Storage in commitments file:**

```markdown
### Waiting On Others

- [ ] **Response from Client Y on proposal** — Sent: Mon
  - Follow-up if no reply by: Thu
  - Status: ⏳ waiting
```

---

## Commitment Patterns

Track over time to identify issues:

**Metrics to monitor:**
- How many commitments made per week
- What % completed on time
- What topics keep getting pushed (pattern)
- Who you make most commitments to

**Weekly insight:**
"You made 12 commitments last week, completed 8. The 4 pushed were all admin tasks. Consider batching admin or delegating."

**Overcommitment alert:**
If open commitments > historical average + 50%:
"You have 15 open commitments. Your average is 10. This week might be unrealistic."

---

## Integration with Daily Planning

**Morning briefing includes:**
- Commitments due today (must complete)
- Commitments due tomorrow (last chance to prep)
- Overdue items (need attention)

**Evening review includes:**
- New commitments made today (confirm logged)
- Tomorrow's commitments (preview)

**Weekly planning includes:**
- All commitments for the week
- Conflict detection with calendar
- Suggest: which to do when
