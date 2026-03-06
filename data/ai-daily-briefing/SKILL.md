---
name: ai-daily-briefing
version: 1.0.0
description: "Start every day focused. Get a morning briefing with overdue tasks, today's priorities, calendar overview, and context from recent meetings. Works with ai-meeting-notes to-do list. No setup. Just say 'briefing'."
author: Jeff J Hunter
homepage: https://jeffjhunter.com
tags: [daily-briefing, morning-routine, productivity, todo, priorities, calendar, focus, daily-ops, task-management, planning]
---

# ☀️ AI Daily Briefing

**Start every day focused. Know exactly what matters.**

Get a morning briefing with overdue tasks, today's priorities, and context from recent work.

No setup. Just say "briefing".

---

## ⚠️ CRITICAL: BRIEFING FORMAT (READ FIRST)

**When the user asks for a briefing, you MUST respond with this EXACT format:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — [Day], [Month] [Date], [Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ OVERDUE ([X] items)
• Task 1 — was due [date]
• Task 2 — was due [date]

📅 TODAY'S PRIORITIES
1. [ ] Priority task 1 — [deadline/context]
2. [ ] Priority task 2 — [deadline/context]
3. [ ] Priority task 3 — [deadline/context]

📆 CALENDAR
• [Time] — [Event]
• [Time] — [Event]
• [Time] — [Event]

💡 CONTEXT (from recent meetings)
• [Key insight 1]
• [Key insight 2]
• [Key insight 3]

🎯 FOCUS FOR TODAY
[One sentence: What's the ONE thing that matters most today?]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### MANDATORY RULES

| Rule | Requirement |
|------|-------------|
| **ONE response** | Complete briefing in a single message |
| **Sections in order** | Overdue → Priorities → Calendar → Context → Focus |
| **Skip empty sections** | If no overdue items, skip that section |
| **Max 5 per section** | Keep it scannable (except calendar, show all) |
| **Focus statement** | Always end with ONE thing to focus on |

---

## Why This Exists

Every morning you face the same questions:
- What's overdue?
- What's due today?
- What meetings do I have?
- What's the context I need to remember?

Instead of checking 5 different places, get one briefing.

---

## What It Does

| Input | Output |
|-------|--------|
| "briefing" | ✅ Complete daily overview |
| "what's overdue?" | ✅ Overdue tasks only |
| "what's on my calendar?" | ✅ Today's schedule |
| "what should I focus on?" | ✅ Priority recommendation |
| "weekly preview" | ✅ Week-ahead view |

---

## Data Sources

The briefing pulls from these locations (if they exist):

### 1. To-Do List (from ai-meeting-notes)

**Location:** `todo.md` in workspace root

```markdown
# To-Do List

## ⚠️ Overdue
| # | Task | Owner | Due | Source |
|---|------|-------|-----|--------|
| 3 | Send proposal | @You | Jan 25 | client-call.md |

## 📅 Due Today
| # | Task | Owner | Source |
|---|------|-------|--------|
| 5 | Review budget | @You | team-sync.md |

## 📆 This Week
| # | Task | Owner | Due | Source |
|---|------|-------|-----|--------|
| 1 | Finalize report | @You | Fri | planning.md |
```

### 2. Meeting Notes

**Location:** `meeting-notes/` folder

- Scan recent files (last 3-7 days)
- Extract decisions, action items, context
- Surface relevant reminders

### 3. Calendar (if available)

- Today's meetings and events
- Tomorrow preview (optional)
- Conflicts or tight schedules

### 4. Memory/Context Files (if using ai-persona-os)

**Locations:**
- `MEMORY.md` — Permanent facts
- `memory/[today].md` — Session notes
- `USER.md` — User preferences

---

## Trigger Phrases

Any of these should trigger a briefing:

| Phrase | Action |
|--------|--------|
| "briefing" | Full daily briefing |
| "daily briefing" | Full daily briefing |
| "morning briefing" | Full daily briefing |
| "what's on my plate?" | Full daily briefing |
| "start my day" | Full daily briefing |
| "what do I need to know?" | Full daily briefing |
| "what's today look like?" | Full daily briefing |
| "give me the rundown" | Full daily briefing |

---

<ai_instructions>

## For the AI: How to Generate a Daily Briefing

When a user asks for a briefing, follow these steps.

### Step 0: Pre-Flight Check

Before generating the briefing, confirm:
- [ ] Will respond in ONE message
- [ ] Will use the exact format from the CRITICAL section
- [ ] Will include the Focus statement at the end

### Step 1: Gather Data Sources

Check for these files in order:

```
1. todo.md (to-do list from ai-meeting-notes)
2. meeting-notes/ folder (recent meeting notes)
3. MEMORY.md (if using ai-persona-os)
4. memory/[today].md (session notes)
5. Calendar integration (if available)
```

**If no data sources exist:**
```
No existing to-do list or meeting notes found.

Would you like me to:
• Create a to-do list? (just tell me your tasks)
• Process some meeting notes? (paste them here)
• Set up a simple priority list for today?
```

### Step 2: Extract Overdue Items

From `todo.md`, find items in the "⚠️ Overdue" section.

**Display format:**
```
⚠️ OVERDUE ([X] items)
• [Task] — was due [date]
• [Task] — was due [date]
```

**Rules:**
- Show max 5 items (if more: "+ [X] more overdue")
- Most urgent first
- Include original due date
- If none: Skip this section entirely

### Step 3: Extract Today's Priorities

Combine from multiple sources:

1. **From todo.md:**
   - "📅 Due Today" section
   - "📆 This Week" items due today

2. **From meeting-notes/:**
   - Action items assigned to user with today's deadline
   - Follow-ups due today

3. **From calendar:**
   - Important meetings to prep for
   - Deadlines

**Display format:**
```
📅 TODAY'S PRIORITIES
1. [ ] [Task] — [deadline/context]
2. [ ] [Task] — [deadline/context]
3. [ ] [Task] — [deadline/context]
```

**Rules:**
- Show max 5 items
- Numbered for easy reference
- Include checkbox format
- Prioritize by: urgency → importance → order mentioned

### Step 4: Calendar Overview

If calendar data is available:

**Display format:**
```
📆 CALENDAR
• [Time] — [Event]
• [Time] — [Event]
• [Time] — [Event]
```

**Rules:**
- Chronological order
- Show all events (don't truncate)
- Include time and event name
- If no calendar: Skip this section or note "No calendar connected"

### Step 5: Context from Recent Meetings

Scan `meeting-notes/` folder for files from last 3-7 days.

Extract:
- Key decisions made
- Important context to remember
- Upcoming deadlines mentioned
- People/relationships to follow up with

**Display format:**
```
💡 CONTEXT (from recent meetings)
• [Key insight 1]
• [Key insight 2]
• [Key insight 3]
```

**Rules:**
- Max 5 context items
- Only include relevant/actionable context
- Reference the meeting if helpful: "(from client-call)"
- If no recent meetings: Skip this section

### Step 6: Generate Focus Statement

Based on everything gathered, determine the ONE most important thing.

**Criteria for choosing focus:**
1. Overdue items with consequences
2. High-stakes meetings today
3. Deadlines that can't slip
4. Dependencies blocking others

**Display format:**
```
🎯 FOCUS FOR TODAY
[One clear sentence about the single most important thing]
```

**Examples:**
- "Get the Acme proposal sent — it's 2 days overdue and they're waiting."
- "Prep for the investor call at 2pm — everything else can wait."
- "Clear the 3 overdue tasks before starting anything new."
- "No fires today — use this for deep work on the Q2 plan."

### Step 7: Assemble the Briefing

Put it all together in the exact format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — [Day], [Month] [Date], [Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Overdue section — if any]

[Today's Priorities section]

[Calendar section — if available]

[Context section — if any]

[Focus statement — always]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 8: Handle Variations

**"What's overdue?"**
```
⚠️ OVERDUE ITEMS

1. [Task] — was due [date]
2. [Task] — was due [date]

[If none: "Nothing overdue! You're caught up."]
```

**"What's on my calendar?"**
```
📆 TODAY'S CALENDAR — [Date]

• [Time] — [Event]
• [Time] — [Event]

[Tomorrow preview if requested]
```

**"Weekly preview" / "What's this week look like?"**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 WEEKLY PREVIEW — Week of [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONDAY
• [Tasks/events]

TUESDAY
• [Tasks/events]

[etc.]

⚠️ WATCH OUT FOR
• [Key deadline or conflict]
• [Important meeting]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Edge Cases

**No data sources found:**
- Don't show empty briefing
- Offer to help set up todo list or process notes

**First time user:**
- Explain where data comes from
- Offer to create initial setup

**Weekend briefing:**
- Lighter format
- Focus on upcoming week prep
- Skip "today's priorities" if nothing scheduled

**End of day request:**
- Shift to "what's left today" + "tomorrow preview"
- Acknowledge time of day

### Tone

- **Crisp and actionable** — No fluff
- **Honest about priorities** — Don't sugarcoat overdue items
- **Encouraging but real** — "Busy day, but manageable"
- **Proactive** — Surface things before they're problems

</ai_instructions>

---

## Works Best With

| Skill | Why |
|-------|-----|
| **ai-meeting-notes** | Creates the to-do list this pulls from |
| **ai-persona-os** | Provides memory and context |

**Standalone:** Works without other skills — just won't have meeting context or persistent todo.

---

## Quick Start

**Day 1:**
```
You: "briefing"
AI: [Shows briefing based on available data, or offers to set up]
```

**After using ai-meeting-notes:**
```
You: "briefing"
AI: [Shows full briefing with overdue items, priorities, context]
```

---

## Customization

Want to customize your briefing? Tell me your preferences:

**Time preferences:**
- "I start work at 6am" → Earlier context
- "Show tomorrow's first meeting" → Tomorrow preview

**Section preferences:**
- "Always show weather" → Add weather
- "Skip calendar" → Omit calendar section
- "Include quotes" → Add motivational quote

**Priority preferences:**
- "Health tasks are always P1" → Boost health items
- "Family first" → Prioritize family commitments

---

## Example Briefing

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — Tuesday, February 3, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ OVERDUE (2 items)
• Send Acme proposal — was due Feb 1
• Review Week 2 training materials — was due Jan 31

📅 TODAY'S PRIORITIES
1. [ ] Anne follow-up call — 2pm today
2. [ ] Finalize Week 3 training content — EOD
3. [ ] Prep for Makati trip — flights need booking
4. [ ] Respond to Karlen re: workflow docs
5. [ ] Clear overdue Acme proposal

📆 CALENDAR
• 10:00 AM — Team standup (30 min)
• 2:00 PM — Anne follow-up call (1 hour)
• 4:30 PM — Workshop dry run (90 min)

💡 CONTEXT (from recent meetings)
• Anne partnership confirmed — ready to move forward (from anne-call)
• OpenClaw bot architecture changing to specialists (from pm-meeting)
• Makati trip deadline approaching — need flights by Friday

🎯 FOCUS FOR TODAY
Get the Acme proposal out first thing — it's 2 days overdue and blocking the deal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## About the Creator

**Jeff J Hunter** built this system to start every day with clarity instead of chaos.

He's trained thousands through the AI Persona Method and runs AI communities with 3.6M+ members.

**Want to turn AI into actual income?**

Most people burn API credits with nothing to show.
Jeff teaches you how to build AI systems that pay for themselves.

👉 **Join AI Money Group:** https://aimoneygroup.com
👉 **Connect with Jeff:** https://jeffjhunter.com

---

*Part of the AI Persona OS ecosystem — Build agents that work. And profit.*
