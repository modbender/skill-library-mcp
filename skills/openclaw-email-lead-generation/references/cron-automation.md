# Cron Automation — Reference

*Detailed protocols for the automated pipeline management jobs.*

---

## Overview

Tier 3 sets up 4 cron jobs via `openclaw cron add`. Each job triggers the agent with a specific prompt. The agent then follows the protocol defined here.

**Prerequisites:**
- Tier 1 (Pipeline Tracker) must be set up
- Tier 2 (Outreach Engine) must be set up for midday sends
- `openclaw` CLI must be available
- `cron.enabled: true` in config

---

## Cron Schedule Summary

| Job | Default Time | Frequency | Purpose |
|-----|-------------|-----------|---------|
| `leadgen-morning` | 9:00 AM | Daily | Reply scan, status updates, morning briefing |
| `leadgen-midday` | 12:00 PM | Daily | Send scheduled follow-ups |
| `leadgen-evening` | 5:00 PM | Daily | Daily metrics, next-day prep |
| `leadgen-weekly` | 8:00 AM Monday | Weekly | Weekly performance report |

---

## Morning Check — Detailed Protocol

**Trigger:** `leadgen-morning` cron at 9:00 AM

**Step 1: Reply Detection**

If email method is `smtp` or `browser`:
- Check inbox for new messages since last check
- Filter by: messages from addresses matching any active lead's email
- For each matched reply:
  - Read the reply content
  - Match to lead by email address
  - Analyze sentiment (see Sentiment Analysis below)
  - Update lead record: set `replied: true`, `reply_content`, `reply_date`, `sentiment`
  - If lead is in an active sequence → set `sequence.paused = true`
  - Update lead status based on sentiment rules

If email method is `manual`:
- Skip automatic reply detection
- Include in briefing: "📬 Check your inbox for replies and tell me about any responses."

**Step 2: Stale Lead Detection**

```bash
# Find leads with next_action_date in the past
today=$(date +%Y-%m-%d)
for f in ~/workspace/leadgen/leads/active/*.json; do
  next_date=$(grep -o '"next_action_date": "[^"]*"' "$f" | cut -d'"' -f4)
  if [[ "$next_date" < "$today" ]] && [[ -n "$next_date" ]]; then
    lead_name=$(grep -o '"name": "[^"]*"' "$f" | head -1 | cut -d'"' -f4)
    echo "OVERDUE: $lead_name — due $next_date"
  fi
done
```

**Step 3: Generate Briefing**

Compile all findings into the morning briefing format (see main SKILL.md for format).

**Step 4: Draft Responses**

For each reply with actionable sentiment:
- **Interested:** Draft a response with booking link or next step
- **Question:** Draft an answer based on business context from config
- **Objection:** Draft a rebuttal aligned with the user's voice

Save drafts to `~/workspace/leadgen/drafts/` for user review.

---

## Midday Send — Detailed Protocol

**Trigger:** `leadgen-midday` cron at 12:00 PM

**Step 1: Find Due Follow-ups**

```bash
today=$(date +%Y-%m-%d)
for f in ~/workspace/leadgen/leads/active/*.json; do
  # Check: sequence active, not paused, next_action_date is today or past
  active=$(grep -o '"active": [a-z]*' "$f" | head -1 | awk '{print $2}')
  paused=$(grep -o '"paused": [a-z]*' "$f" | head -1 | awk '{print $2}')
  next_date=$(grep -o '"next_action_date": "[^"]*"' "$f" | cut -d'"' -f4)
  
  if [[ "$active" == "true" ]] && [[ "$paused" != "true" ]] && [[ "$next_date" <= "$today" ]]; then
    echo "DUE: $f"
  fi
done
```

**Step 2: Check Conditions**

For each due lead:
- Read the sequence definition to find the current step
- Check the step condition:
  - `always` → proceed
  - `if_no_reply` → check if any reply exists since last send. If reply exists → skip, pause sequence.

**Step 3: Rate Limit Check**

Before sending:
1. Count emails sent today (scan all active lead files for sends with today's date)
2. If at `daily_email_max` → stop, report: "Daily limit reached. [X] follow-ups deferred to tomorrow."
3. If approaching `hourly_email_max` → space sends with `min_minutes_between_emails` gaps

**Step 4: Generate and Queue**

For each eligible send:
1. Read the template for the current sequence step
2. Replace placeholders with lead data
3. Queue the draft

**Step 5: Present Queue**

If email method is `manual` or `browser`:
- Show all drafts in a batch for review
- User can approve all, approve individually, or skip

If email method is `smtp` with auto-send:
- Send automatically
- Log each send
- Report summary

**Step 6: Update Records**

After each send:
1. Add email to lead's `email_history`
2. Advance `sequence.current_step`
3. Calculate next `next_action_date` from sequence delays
4. If final step → set `sequence.completed = true`
5. Update `lead.updated` timestamp

---

## Evening Summary — Detailed Protocol

**Trigger:** `leadgen-evening` cron at 5:00 PM

**Step 1: Collect Today's Activity**

Scan all active lead files for activity today:
- Emails sent (email_history entries with today's date)
- Replies received (reply_date = today)
- Leads added (created = today)
- Status changes (compare current status to any logged changes)

**Step 2: Calculate Metrics**

```
Emails sent today: [count]
Replies received: [count]
Reply rate (today): [replies / sent * 100]%
Leads added: [count]
Status changes: [list of lead → new_status]
```

**Step 3: Prepare Tomorrow**

- Count follow-ups due tomorrow
- Count overdue actions
- Count pending drafts in `~/workspace/leadgen/drafts/`

**Step 4: Generate Summary**

Use the Evening Summary format from main SKILL.md.

**Step 5: Save Report**

Write to `~/workspace/leadgen/reports/daily/[YYYY-MM-DD].md`

---

## Weekly Report — Detailed Protocol

**Trigger:** `leadgen-weekly` cron on Mondays at 8:00 AM

**Step 1: Aggregate Weekly Data**

Read daily reports from the past 7 days in `~/workspace/leadgen/reports/daily/`.
If daily reports are missing, scan lead files directly.

**Step 2: Calculate Metrics**

- Total emails sent this week
- Total replies received
- Reply rate
- Calls booked
- New leads added
- Leads closed (won + lost)
- Pipeline movement (how many leads changed status)

**Step 3: Template Performance**

For each template:
- Count sends
- Count replies
- Calculate reply rate
- Rank by effectiveness

**Step 4: Compare to Last Week**

Read last week's report from `~/workspace/leadgen/reports/weekly/`.
Calculate ↑/↓ trends for each metric.

**Step 5: Identify Issues**

- Stalled leads: active leads with no activity in 7+ days
- Dying sequences: leads past final step with no reply
- Underperforming templates: reply rate below 3%

**Step 6: Generate Recommendations**

Based on data:
- If reply rate < 5% → "Consider refreshing templates with Template Forge"
- If many stalled leads → "X leads have gone cold. Review or archive?"
- If one template outperforms → "Template X has [Y]% reply rate — consider making it your primary"
- If pipeline is top-heavy (many new, few qualified) → "Bottleneck at [stage]. Focus on moving leads forward."

**Step 7: Save Report**

Write to `~/workspace/leadgen/reports/weekly/[YYYY-MM-DD].md`

---

## Customizing Cron Times

User can change cron times by saying "change morning check to 8am" or editing config directly.

Agent updates via:
```bash
openclaw cron update "leadgen-morning" --schedule "0 8 * * *"
```

Or if `openclaw cron update` isn't available:
```bash
openclaw cron remove "leadgen-morning"
openclaw cron add "leadgen-morning" --schedule "0 8 * * *" --prompt "[same prompt]"
```

---

## Disabling Cron

"Pause autopilot" or "disable cron":
1. Remove all leadgen cron jobs: `openclaw cron remove "leadgen-morning"` (repeat for each)
2. Update config: set `cron.enabled: false`
3. Confirm: "Autopilot paused. Your leads are safe — sequences are paused, no emails will send. Say 'setup tier 3' to re-enable."

---

*Autopilot — Your agent works the pipeline while you sleep.* ⚡
