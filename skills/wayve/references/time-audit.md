# Phase 5: Time Audit — Where Does Your Time Go?

**Command:** `/wayve time audit`

## When This Applies
User explicitly says "audit my time", "where does my time go", "time tracking", "track my time."

## Your Approach
Curious and analytical. Frame it as discovery, not judgment. Inspired by the "Buy Back Your Time" framework — the goal is to identify what to delegate, automate, or eliminate so you can spend time on what matters most. Keep all messages short and concise.

## Where Data is Stored

All data is persisted via MCP tool calls → Wayve API → Azure SQL Database. Nothing is saved unless you call the tool.

| What | Tool call | Stored in |
|------|-----------|-----------|
| Audit config (name, dates, interval, active hours) | `wayve_manage_time_audit(action: "start")` | `wayve.time_audits` |
| Log entries (activity, energy, skill, bucket) | `wayve_manage_time_audit(action: "log_entry")` | `wayve.time_audit_entries` |
| Report (bucket summary, patterns, delegation) | `wayve_manage_time_audit(action: "report")` | Generated from entries |
| User preferences (timezone, active hours, config) | `wayve_manage_knowledge(action: "save_insight")` | Knowledge base |

**Available actions for `wayve_manage_time_audit`:**
- `start` — creates audit, returns `audit_id` (save this — you need it for every other call)
- `log_entry` — logs one entry (requires `audit_id`, `what_did_you_do`, `energy_level`)
- `report` — generates report from all entries (requires `audit_id`)

**There is no `list` or `get` action.** You cannot retrieve existing audits without the `audit_id`. Always save the `audit_id` from the `start` response — both in the cron job messages and via knowledge base.

## Flow

### Phase A: Introduce the Time Audit

Before asking anything, explain what the user is signing up for. Keep it brief:

> **What is a Time Audit?**
> For 7 days, I'll send you a quick check-in every 30 minutes during your waking hours. You reply with what you did, which life bucket it belongs to, and your energy level (1-5). Takes about 30 seconds per check-in.
>
> At the end of the week, you'll get a report showing where your time actually goes — compared to where you *want* it to go. You'll see energy patterns, discover what drains you, and identify what you could delegate, automate, or eliminate.
>
> **What to expect:**
> - 7 days of short check-ins via notifications
> - A daily summary each evening
> - A full analysis report at the end
>
> Want to get started?

Wait for confirmation before proceeding. If the user wants a shorter audit, that's fine — but always default to 7 days.

### Phase B: Onboarding — Set Up the Audit

Walk through each setting one at a time. Ask permission for each before moving on. Be brief — one question per message.

**Step 1: Sleep schedule**
Ask: "What time do you usually go to sleep and wake up? I'll make sure not to send check-ins during those hours."

Save sleep hours via `wayve_manage_settings` (action: `update_preferences`, `sleep_hours_per_day`) and use the times for `active_hours_start` / `active_hours_end`.

**Step 2: Check-in interval**
Ask: "Every 30 minutes works best for most people. Want to go with 30 min, or would you prefer every 15 or 60 minutes?"

Default: 30 minutes. Only change if the user explicitly asks.

**Step 3: Timezone**
Ask: "What's your timezone? (e.g., Europe/Amsterdam)"

Save via `wayve_manage_knowledge` (action: `save_insight`, category: `personal_context`, key: `timezone`).

**Step 4: Delivery channel**
Ask: "Where should I send the check-in notifications — Telegram, Slack, Discord, or somewhere else?"

**Step 5: Start date**
Ask: "Want to start today or tomorrow morning?"

Suggest starting tomorrow if it's already afternoon.

### Phase C: Execute — Create the Audit & Automations NOW

**CRITICAL: This is an execution phase, not a planning phase.** The user has confirmed all settings. You must now call the tools below in order. Do not summarize what you "will" do — do it. Each step = one tool call + one confirmation to the user.

**Step 1: Create the audit in Wayve**

Call NOW — this creates the audit record in the database (`wayve.time_audits`):
```
wayve_manage_time_audit(
  action: "start",
  name: "7-Day Time Audit — Month Year",
  start_date: "YYYY-MM-DD",
  end_date: "YYYY-MM-DD",
  interval_minutes: 30,
  active_hours_start: "HH:MM",
  active_hours_end: "HH:MM",
  channel: "telegram"
)
```
The response contains an `id` field — this is the `audit_id`. **You need this ID for every subsequent call.** Confirm: "Audit created ✓"

**Step 2: Save settings to knowledge base**

Call these immediately to persist user preferences (no need to ask permission — the user already provided the info):
```
wayve_manage_knowledge(action: "save_insight", category: "personal_context", key: "timezone", value: "USER_TIMEZONE")
wayve_manage_knowledge(action: "save_insight", category: "personal_context", key: "active_hours", value: "Mon-Thu HH:MM-HH:MM, Fri-Sun HH:MM-HH:MM")
wayve_manage_knowledge(action: "save_insight", category: "preferences", key: "time_audit_config", value: "audit_id: AUDIT_ID, interval: 30min, channel: telegram, duration: 7 days, start: YYYY-MM-DD, end: YYYY-MM-DD")
```
**Important:** Include the `audit_id` in the config so future sessions can find it. Confirm: "Settings saved ✓"

**Step 3: Create all automations**

Present these as a batch and ask permission once: "I'll set up 5 automations — check-ins, daily summary, auto-cleanup, final report invite, and a follow-up after a week. OK to create all of them?"

After the user says yes, create each one immediately using `cron.add`. Do NOT stop between crons to ask again.

**3a. Check-in cron** (recurring, every interval during active hours):
```json
{
  "name": "Wayve Time Audit Check-in",
  "schedule": { "kind": "cron", "expr": "*/30 ACTIVE_START-ACTIVE_END * * *", "tz": "USER_TIMEZONE" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send this check-in message to the user:\n\n⏱️ Time check!\n\nWhat have you been doing for the last 30 minutes?\nHow's your energy? (1=drained, 5=energized)\n\nQuick reply — e.g., \"emails, 2\" or \"gym, 5\"\n\n👉 https://gowayve.com/time-audit\n\nWhen the user replies, you MUST log their response immediately:\n1. Parse their reply — e.g., \"emails, 2\" means what_did_you_do: \"emails\", energy_level: 2\n2. Call wayve_get_planning_context to get the user's buckets, then match the activity to the right bucket\n3. Call wayve_manage_time_audit(action: \"log_entry\", audit_id: \"AUDIT_ID\", what_did_you_do: \"...\", energy_level: N, bucket_id: \"...\") to save the entry\n4. Confirm briefly: \"Logged: [activity] → [bucket], energy [N]/5 ✓\"\n\nDo NOT skip the wayve_manage_time_audit call. If you don't log it, the entry is lost."
  },
  "delivery": { "mode": "announce", "channel": "USER_CHANNEL", "to": "USER_CHANNEL_ID" }
}
```
**Important:** Replace `AUDIT_ID` with the actual audit ID from Step 2 before creating this cron.

Confirm: "Check-in cron ✓ — every 30 min during active hours"

**3b. Daily summary cron** (recurring, every evening):
```json
{
  "name": "Wayve Audit Daily Summary",
  "schedule": { "kind": "cron", "expr": "30 21 * * *", "tz": "USER_TIMEZONE" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "The user has an active time audit. Call wayve_manage_time_audit(action: 'report', audit_id: 'AUDIT_ID') to get current stats. Deliver a brief daily summary: how many entries were logged today, top buckets by time, average energy level, and any patterns noticed. Encourage them to keep going — 'X days left in the audit.' End with: 'View your audit: https://gowayve.com/time-audit'"
  },
  "delivery": { "mode": "announce", "channel": "USER_CHANNEL", "to": "USER_CHANNEL_ID" }
}
```
**Important:** Replace `AUDIT_ID` with the actual audit ID from Step 1 before creating this cron.

Confirm: "Daily summary ✓ — every evening at 21:30"

**3c. Auto-cleanup** (one-shot, at audit end):
```json
{
  "name": "Wayve Time Audit Cleanup",
  "schedule": { "kind": "at", "at": "AUDIT_END_DATE_T20:30:00+OFFSET" },
  "sessionTarget": "main",
  "deleteAfterRun": true,
  "payload": {
    "kind": "systemEvent",
    "text": "Time audit period ended. Delete the 'Wayve Time Audit Check-in' and 'Wayve Audit Daily Summary' cron jobs."
  }
}
```
Confirm: "Auto-cleanup ✓ — stops all audit notifications on [end date]"

**3d. Final report invite** (one-shot, morning after audit ends):
```json
{
  "name": "Wayve Time Audit Final Report",
  "schedule": { "kind": "at", "at": "AUDIT_END_DATE_T10:00:00+OFFSET" },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "The user's 7-day time audit just ended. Send them a warm congratulations — tracking for a full week takes commitment. Let them know you have their results ready and would love to walk through them together: where their time went, what energized vs. drained them, and what they might want to change. Include the link https://gowayve.com/time-audit and tell them to say 'show me my results' when they're ready. Keep it brief and inviting — 4-6 lines max."
  },
  "delivery": { "mode": "announce", "channel": "USER_CHANNEL", "to": "USER_CHANNEL_ID" }
}
```
Confirm: "Final report invite ✓ — sent morning of [end date + 1]"

**3e. Follow-up check-in** (one-shot, 7 days after audit ends):
```json
{
  "name": "Wayve Time Audit Follow-Up",
  "schedule": { "kind": "at", "at": "AUDIT_END_DATE_PLUS_7_DAYS_T10:00:00+OFFSET" },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "It's been a week since the user's time audit ended. Send a casual check-in: ask how things are going, whether they've noticed any shifts in how they spend their time. No pressure — even small changes count. Offer to look at this week together. Include links to https://gowayve.com/analytics and https://gowayve.com/week. Keep it warm and brief — 4-6 lines max."
  },
  "delivery": { "mode": "announce", "channel": "USER_CHANNEL", "to": "USER_CHANNEL_ID" }
}
```
Confirm: "Follow-up ✓ — check-in on [end date + 7]"

**Step 4: Verify everything is set up**

After creating all crons, verify and present a summary to the user:

1. Call `wayve_manage_time_audit(action: "report", audit_id: "AUDIT_ID")` to confirm the audit exists and is accessible
2. Present a complete summary:

> **All set! Here's what's live:**
>
> | What | Status | Schedule |
> |------|--------|----------|
> | Time audit | ✓ Active | [start] → [end] |
> | Check-in notifications | ✓ Active | Every 30 min, [active hours] |
> | Daily summary | ✓ Active | Every day at 21:30 |
> | Auto-cleanup | ✓ Scheduled | [end date] |
> | Final report invite | ✓ Scheduled | [end date + 1 morning] |
> | Follow-up | ✓ Scheduled | [end date + 7 morning] |
>
> **Your first check-in arrives [start date] at [active_hours_start].** Just reply with what you're doing and your energy level — e.g., "deep work, 4" or "gym, 5".
>
> 👉 Track your audit: https://gowayve.com/time-audit

If any step failed, tell the user which one and retry it. Do not move on until everything is confirmed working.

### Phase D: During the Audit — Log Entries

When the user responds to a check-in, keep it fast — 30 seconds per entry max. **Every response MUST be logged to the database via a tool call.**

1. Parse what they said — e.g., "emails, 2" → what_did_you_do: "emails", energy_level: 2
2. Call `wayve_get_planning_context` to get the user's buckets, then match the activity to the right bucket
3. Call `wayve_manage_time_audit` NOW to save the entry to `wayve.time_audit_entries`:
   ```
   wayve_manage_time_audit(
     action: "log_entry",
     audit_id: "AUDIT_ID",
     what_did_you_do: "emails",
     energy_level: 2,
     bucket_id: "matched-bucket-uuid",
     skill_level: 3,          // optional, 1-5
     note: "optional note"    // optional
   )
   ```
4. Reply with a short confirmation only — no commentary, no advice. E.g., "Logged: Emails → Work, energy 2/5 ✓"

**Quick-log shorthand**: If the user says "gym, 5" or "meeting with client, 3, low skill" — parse it and log without follow-ups. Still call the tool — no exceptions.

**If the tool call fails**, tell the user and retry. Do not silently skip logging.

### Phase E: Review Results

After the audit period ends (or when the user says "show me results"):

1. **Generate report** — call NOW:
   ```
   wayve_manage_time_audit(action: "report", audit_id: "AUDIT_ID")
   ```
   If you don't have the audit_id, retrieve it from knowledge: `wayve_manage_knowledge(action: "summary")` → look for `preferences` / `time_audit_config`.

   The report returns:
   - `total_entries` — how many check-ins were logged
   - `bucket_summary` — per bucket: entry_count, avg_energy, avg_skill
   - `time_patterns` — per time of day: entry_count, avg_energy
   - `delegation_candidates` — activities with high energy cost + low skill required

2. **Discuss bucket distribution**:
   - Where is time actually going vs. where they want it?
   - Compare against their Perfect Week template if one exists
   - Which buckets are getting starved?

3. **Highlight energy patterns**:
   - When do they have the most/least energy?
   - Which activities drain vs. energize them?

4. **Identify delegation candidates**:
   - Activities with high energy cost (4-5) but low skill required (1-2)
   - These are prime candidates for delegating, automating, or eliminating

5. **Deeper analysis** via `wayve_get_analytics` (action: `energy_skill_matrix`):
   - Activities grouped into quadrants: energizing+skilled, energizing+unskilled, draining+skilled, draining+unskilled
   - The draining+unskilled quadrant = "delegate immediately"

### Phase F: Action Plan (Audit-Transfer-Fill)

1. **Audit** — Done! Summarize the top 3 insights from the data
2. **Transfer** — For each delegation candidate, brainstorm a specific action:
   - **Delegate** to a person (assistant, colleague, family member)
   - **Automate** with tools or systems
   - **Eliminate** entirely — does it actually need to happen?
   - **Batch** — reduce context-switching by grouping similar activities
3. **Fill** — Reclaimed hours go to underserved buckets. Create specific activities:
   - Use `wayve_create_activity` to schedule what they want to do with freed-up time
   - Consider setting up recurrence with `wayve_manage_recurrence` for new habits

### Save Findings
Save key insights via `wayve_manage_knowledge` (action: `save_insight`):
- Category: `delegation_candidates` — specific activities to delegate
- Category: `energy_patterns` — when/what energizes or drains them
- Category: `bucket_balance` — actual vs. desired time per bucket

## End State
User understands their actual time allocation, has identified delegation candidates, and has concrete next steps. Insights saved for future planning sessions.

"Now you know where your time goes. Next week during Fresh Start, we can use these insights to plan with intention."

Direct them to the app:
- "View your time audit: https://gowayve.com/time-audit"
- "See your analytics: https://gowayve.com/analytics"
- "Plan your week with these insights: https://gowayve.com/week"
