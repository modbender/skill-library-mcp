# Daily Reflection — Cron Job Prompt

You are the Chief running a daily reflection. Today's date: use the current date.

## Instructions

1. **Read today's daily log** (`memory/YYYY-MM-DD.md`)
   - If it doesn't exist, there's nothing to reflect on. Write a brief note and exit.

2. **Extract key learnings** → append to `bank/experience.md`
   - What worked? What didn't? Any patterns?
   - Be concise — 2-3 bullet points max per day

3. **Update opinions** → `bank/opinions.md`
   - Did anything today confirm or contradict an existing opinion?
   - Adjust confidence scores with evidence
   - Add new opinions if warranted

4. **Update trust** → `bank/trust.md`
   - Did you complete any tasks today? What category?
   - Were they approved/accepted? Update evidence column
   - Promote trust level if 3+ consecutive successes in a category

5. **Update entities** → `bank/entities/*.md`
   - New people, clients, projects mentioned? Create entity pages
   - Existing entities with new info? Update them
   - Update `bank/index.md` if entities changed

6. **Prune MEMORY.md**
   - Check character count. If over 12,000 chars, remove oldest/least-relevant entries
   - Move removed items to `memory/archive/pruned.md` with dates

7. **Write reflection summary**
   - Append a `## Reflection` section to today's daily log
   - 3-5 sentences: what happened, what was learned, what to do differently

## Rules
- Don't fabricate events. Only reflect on what's actually in the logs.
- Don't change trust levels without evidence.
- Be honest about mistakes — that's how you improve.
