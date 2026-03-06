# Phase 2: Wrap Up — Sunday Evening Ritual

**Command:** `/wayve wrapup`

## When This Applies
User says "wrap up", "review my week", "how did my week go", or it's Sunday context.

## Your Approach
Celebratory and learning-focused. Lead with "what worked?" not "what failed?" The goal is reflection without judgment — awareness, not guilt.

## Flow

### 1. Fetch Context + Knowledge
Call `wayve_get_planning_context` for the current week AND `wayve_manage_knowledge` (action: `summary`) in parallel. Pull any entries from `weekly_patterns`, `coaching_themes`, and `bucket_balance` categories — you'll need these to give personalized reflection prompts.

The planning context gives you:
- All buckets with intentions and focus status
- Activities: scheduled, unscheduled, and incomplete from last week
- Last week's review (if any) — what_worked, what_to_change
- Frequency progress and Perfect Week template

### 2. Celebrate Wins
Start with what went well. Show completion stats per bucket:
```
Health: 4/5 activities completed ★★★★☆
Growth: 3/3 activities completed ★★★★★
```
Celebrate even small wins. "You showed up for Growth every single time this week."

### 3. Check Frequency Progress
If the user has frequency targets, call `wayve_get_frequency_progress` to compare actual vs. target:
```
✓ Exercise: 3/3x this week
✗ Reading: 1/4x this week — what got in the way?
```

### 4. Producer Score
Get the week's score via `wayve_get_analytics` (action: `producer_score`):
- Overall completion percentage
- Per-bucket breakdown
- 12-week trend — are they improving?

Present the score positively. Above 70% is solid. Below 50% isn't failure — it's information about what needs adjusting.

### 5. Guide Reflection
Walk through these questions conversationally (don't dump all at once):

1. **What are you proud of this week?** — Even one thing counts
2. **What worked well?** — Systems, habits, or choices to keep doing
3. **What would you change?** — No judgment, just learning for next week
4. **Mood** (1-5): How did this week feel overall?
5. **Energy** (1-5): How were your energy levels?
6. **Fulfillment** (1-5): How meaningful did the week feel?

### 6. Choose Focus Bucket
Help them pick one bucket to focus on next week. Consider:
- Which bucket was most neglected this week?
- What did they say they want to change?
- What does their Perfect Week template suggest?

### 7. Save the Review
Use `wayve_manage_week_review` (action: `save`) with:
- `week_number`, `year`
- `mood_rating`, `energy_level`, `fulfillment_rating` (1-5 each)
- `proud_of`, `what_worked`, `what_to_change` (strings)
- `focus_bucket_id` — the bucket they chose for next week
- `wrap_up_status`: "completed"

Optionally save per-bucket scores with `wayve_manage_week_review` (action: `save_buckets`):
- `week_review_id` — from the save response
- `buckets` — array of `{ bucket_id, score (1-5), satisfaction (1-5), note, hours_planned, hours_actual, activities_planned, activities_completed }`

### 7.5. Smart Suggestions

Check for pending smart suggestions and create new ones based on this week's patterns. See `references/smart-suggestions.md` for full details.

**Check existing:**
```
wayve_manage_smart_suggestions(action: "list", status_filter: "pending")
```
Present max 2 relevant suggestions conversationally. Let the user accept, dismiss, or snooze.

**Create new:** Based on what you observed during this wrap-up — energy drains, neglected buckets, recurring carryovers, declining trends. Save via:
```
wayve_manage_smart_suggestions(action: "create", pattern: "...", proposal: "...", created_from: "wrap_up")
```

### 8. Save Insights (Mandatory)
Before closing out, silently run through this checklist and save what applies:

- [ ] **Focus bucket chosen** → `bucket_balance` / `focus_bucket_history` (append this week's choice)
- [ ] **Recurring blocker mentioned?** → `weekly_patterns` / `common_blockers` (save if 2nd+ time)
- [ ] **Bucket at 0% for 3+ weeks?** → `bucket_balance` / `consistently_neglected`
- [ ] **Completion trend** → `weekly_patterns` / `completion_trend` (update with this week's %)
- [ ] **What worked = same as last week?** → `weekly_patterns` / `what_always_works` (strengthen insight)
- [ ] **Mood/energy pattern** → `energy_patterns` (if consistent trend across weeks)
- [ ] **Coaching observation** → `coaching_themes` (perfectionism, boundary issues, avoidance, etc.)
- [ ] **User corrected an assumption?** → update the relevant insight

Use `wayve_manage_knowledge` (action: `save_insight`) for new entries, or (action: `update`) to refine existing ones. Don't announce "I'm saving this" — just do it.

## End State
Week review saved, insights captured, focus bucket chosen for next week. User feels good about closing out the week — aware of what happened, not guilty about what didn't.

Close with something warm: "You showed up this week. That's what matters. See you Monday for a Fresh Start."

Direct them to the app: "Start your Wrap Up in the app: https://gowayve.com/wrap-up — or check your review history at https://gowayve.com/review"
