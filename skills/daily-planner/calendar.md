# Calendar Management

## Time Blocking Rules

**Block types:**

| Type | Min duration | Interruptions | Example |
|------|-------------|---------------|---------|
| Deep Work | 90 min | Zero | Strategy, creative, coding |
| Focus | 60 min | Emergency only | Writing, analysis |
| Meetings | 30-60 min | As scheduled | Calls, 1:1s |
| Admin | 30 min | Allowed | Email, messages |
| Buffer | 15 min | Open | Between blocks |

**Never do:**
- Deep work in <60min blocks (not enough ramp-up time)
- Back-to-back meetings without buffer
- Schedule >80% of available time

---

## Deep Work Protection

**Before blocking:**
1. Identify when user's energy peaks (config.md)
2. Check existing calendar for that window
3. If open: block automatically
4. If meeting: suggest moving the meeting

**During deep work:**
- All notifications paused (if agent has control)
- Auto-reply enabled: "In focused work. Responding in X hours."
- Only true emergencies interrupt (production down, family emergency)

**What qualifies as emergency:**
- System/production outage
- Family emergency contact calling
- Meeting with investor/CEO starting in 10min
- Everything else: wait for block to end

**Deep work target by profile:**
| Profile | Target per week | Block size |
|---------|-----------------|------------|
| Executive | 6-8 hours | 90 min blocks |
| Freelancer | 15-20 hours | 2-3 hour blocks |
| Founder | 10-15 hours | 2 hour blocks |
| Student | 20-25 hours (study) | 45 min pomodoros |

---

## Meeting Hygiene

**Before accepting any meeting:**
1. Does this need a meeting or can it be async (email/audio)?
2. Do I need to be there or can someone else represent?
3. Is the agenda clear?
4. Is 30 min enough (default to short)?

**Meeting prep (automatic):**
5 minutes before, agent provides:
- Who's attending + their context (last contact, pending items)
- Agenda or purpose
- What decision/outcome expected

**Meeting patterns to flag:**
- Same recurring meeting with no clear output
- >5 meetings in a day (meeting fatigue)
- Meetings scheduled during deep work blocks
- 60-min meetings that should be 30

**Post-meeting:**
- Log any commitments made
- Send summary if agreed to
- Schedule follow-up if needed

---

## Conflict Detection

**Immediate alerts for:**
- Double-booked time slots
- Meeting during blocked deep work
- Travel time not accounted for
- Multiple deadlines same day

**48-hour lookahead:**
Every evening, check next 48 hours for conflicts.
Alert format: "Tomorrow looks tight: 5 meetings, deadline for X, no buffer between 2-4pm."

**Resolution suggestions:**
- "Move your 11am call to Wednesday where you have a gap"
- "This deadline conflicts with your trip. Suggest completing today instead."
- "You're double-booked at 3pm. Which one is movable?"

---

## Calendar Consolidation

**For users with fragmented calendars:**

Many 30-min meetings scattered = context-switching hell.

**Detection:**
- >4 gaps <45min between meetings
- More than 6 context switches per day

**Suggestion:**
"Your Tuesday has 7 small gaps. Consider batching meetings to mornings and keeping afternoons clear. Want me to suggest a restructure?"

**Ideal day structure:**
```
AM: Deep work block (if not exec profile)
    or Strategic meetings (if exec)
11-12: Admin/email block
12-1: Lunch (protected)
PM: Meetings batched together
    or Deep work (if exec)
Late PM: Wrap-up, tomorrow prep
```

---

## Buffer Management

**Mandatory buffers:**
- 15 min between meetings (travel time, bio break, context shift)
- 30 min before important meetings (prep)
- 30 min after high-stakes calls (decompress, notes)

**No-meeting zones:**
- First hour of day (morning routine)
- Last hour of day (wrap-up)
- Friday PM (buffer for week overflow)

**Agent enforcement:**
If user tries to book meeting in no-meeting zone:
"That's during your protected morning time. Still want to schedule, or move to 10am?"
