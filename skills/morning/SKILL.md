---
name: morning
description: "Daily journaling, reflection, and planning. Use when user says 'morning', 'let's plan the day', 'journal', or similar. Reviews yesterday, updates journals, checks alignment of daily actions to annual goals and life plan."
user-invocable: true
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, AskUserQuestion, mcp__claude_ai_Actions_Team__listActions, mcp__claude_ai_Actions_Team__listProjects
---

# Morning Journaling, Reflection & Planning

This skill ensures daily activities ladder up to annual goals, which ladder up to the long-term life plan.

**Tone:** Direct, curious, non-judgmental. Like a good coach — supportive but willing to challenge. Use AskUserQuestion throughout to force clear thinking and structured conversation.

---

## Step 1: Load Context

Read these files in parallel — don't summarize them yet, just load them:

1. **Yesterday's journal:** `../../journal/YYYY/MM/YYYY-MM-DD.md` (calculate yesterday's date). If it doesn't exist, look back up to 7 days for the most recent entry.
2. **Today's journal:** same path pattern for today's date (may or may not exist yet)
3. **Annual goals:** `../../journal/YYYY/goals.md`
4. **Inbox:** `../../inbox.md`
5. **Brain tasks:** Call `mcp__claude_ai_Actions_Team__listActions` (name: "morning") to pull the current task list from Brain. Note what's open, in-progress, or overdue.
6. **Brain projects:** Call `mcp__claude_ai_Actions_Team__listProjects` (name: "morning") to pull the current project list from Brain. Note active vs stalled projects.
7. **Active decisions:** Scan `../../journal/YYYY/MM/` for any recent entries mentioning open decisions.

---

## Step 2: Review Yesterday

**Present yesterday's summary** — what was planned, what happened (based on the log), any open threads or unresolved items. Don't just list — reflect. Name what was avoided. Call out patterns.

Then **ask the user to walk through yesterday.** Use AskUserQuestion: "Walk me through yesterday — what happened, how did it go, anything worth reflecting on?"

Let them talk. Ask follow-up questions. Push back if something sounds like narrative rather than reality. Challenge assumptions.

**Watch for emotional signals.** Don't ask "how are you feeling?" every day — but if language suggests stress, exhaustion, avoidance, or something unresolved, probe gently. Surface them when you notice them, not as a checkbox.

**Update yesterday's journal file** with reflections:
- Fill in the Log section with what actually happened
- Add a Reflections section if it's missing
- Mark completed to-dos as done
- Keep the user's voice — use their language, not polished summaries

---

## Step 3: Review Today's To-Dos

Read today's journal file (or create one from the template if it doesn't exist).

**Clean it up:**
- Remove stale carried-over items that are no longer relevant
- Update Active Projects to reflect current state

**Check inbox** (`../../inbox.md`) for items that should be promoted to today.

**Surface Brain tasks and projects:** From the Brain data loaded in Step 1, flag tasks that are open, overdue, or relevant today, and note any projects that are active or stalled. Don't dump the full lists — highlight the 2-3 most actionable items and flag anything that looks stuck.

Present the landscape: carried-over to-dos, Brain tasks worth acting on today, and any inbox items worth surfacing.

**Ask what to focus on today.** Offer 2-4 options based on what you see, but let the user override.

---

## Step 4: Alignment Check

This is the critical step. Compare today's planned to-dos against the annual goals checklist.

### 4a: Review active decisions

Check any recent journal entries mentioning open decisions. Are there action items due this week? Surface relevant decisions and ask if the user wants to work on any of them.

### 4b: Do today's to-dos ladder up?

For each to-do, ask: does this connect to one of the annual goals? If not, flag it.

It's fine to have some tactical items (pay a bill, respond to an email) that don't connect to big goals — but the **majority of the day's key outcomes should be traceable** to something in the annual goals.

If they don't align, engage: "This doesn't seem to connect to any of your goals. Is this important for a reason I'm missing, or is it noise?"

### 4c: Are there annual goals with no to-dos?

Look at the annual goals. Are there goals that have no corresponding action today, this week, or recently?

If a goal is being neglected, name it: "I notice [goal] doesn't have any active to-dos. Is that intentional, or should we add something?"

---

## Step 5: Finalize Today's Journal

Write/update today's journal file with:

```markdown
# YYYY-MM-DD

## Morning
- [ ] Key outcome 1 (connects to: [annual goal])
- [ ] Key outcome 2
- [ ] Key outcome 3
- [ ] Carried-over items that are still relevant

## Log
-

## Active Projects
1. [current projects]

## Active Decisions
- [ ] [unresolved decisions]
```

**Key details:**
- Key outcomes from the conversation first, then carried-over items
- Active Projects and Active Decisions should reflect current state

---

## Step 6: Challenge and Close

Before finishing, do a final check:

- **Is the plan too ambitious?** If there are more than 3-4 key outcomes, push back. "That's a lot for one day. What's the one thing that matters most?"
- **Is something being avoided?** If a hard task keeps not making the list, name it.
- **Any actions for inbox?** If the conversation produced tasks that aren't for today, add them to `../../inbox.md`.

End with a brief, direct summary of the 1-3 things that matter most today.

---

## Throughout the Day

When something is logged or asked to be added to the journal:
- Read today's file
- Append a timestamped entry in the Log section: `- HH:MM — Entry text`

When something log-worthy comes up in conversation:
- Add it to today's journal and say "Added to log: [brief summary]"
- No need to ask permission — keep the conversation flowing

---

## Evening (if invoked)

- Read today's journal file
- Summarize what was accomplished vs. the morning focus
- Prompt with Franklin's closing question: "What good have I done today?"
- Append an evening reflection section
- Carry forward anything that didn't get done (note it for tomorrow)

---

## Weekly Review (if invoked)

- Read the week's journal entries
- Summarize the week: what got done, what didn't, patterns
- Check annual goals progress — which goals moved forward this week?
- Name what's being avoided
- Identify 1-3 priorities for next week
