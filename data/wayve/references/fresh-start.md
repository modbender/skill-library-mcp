# Phase 3: Fresh Start — Monday Morning Planning

**Command:** `/wayve plan`

## When This Applies
User says "plan my week", "fresh start", "let's plan", or it's Monday context.

## Your Approach
Energizing and forward-looking. "What kind of week do you want?" This is about setting intentions, not building a rigid schedule.

## Flow

### 1. Fetch Context + Knowledge
Call `wayve_get_planning_context` AND `wayve_manage_knowledge` (action: `summary`) in parallel. Then pull specifics from `scheduling_preferences`, `energy_patterns`, and `weekly_patterns` categories — you'll use these for smarter scheduling.

Note from the planning context:
- **Last week's review**: what_worked, what_to_change, focus_bucket
- **Incomplete activities** from last week (carryovers)
- **Current buckets**: intentions, focus status, target hours
- **Perfect Week template**: ideal time distribution
- **Knowledge summary**: stored insights to reference

### 2. Handle Carryovers
Show incomplete activities from last week. For each, ask: **keep, drop, or reschedule?**

- **Keep** — `wayve_update_activity` to update `scheduled_date` to this week
- **Drop** — `wayve_delete_activity` if no longer relevant
- **Reschedule** — `wayve_update_activity` with new date/time

Don't guilt them about unfinished items. "These didn't happen last week — that's OK. Do any of them still feel important?"

### 3. Reference Last Week's Learnings
If a week review exists, surface the key insights:
- "Last week you said [what_worked] — let's keep that going"
- "You wanted to change [what_to_change] — how should we address that?"
- "Your focus bucket is [focus_bucket] — let's make sure it gets priority"

Also check `wayve_manage_knowledge` (action: `summary`) for stored patterns.

### 4. Choose a Focus Mode
Ask what kind of week they want. Offer these modes:

| Mode | Description | Bucket Strategy |
|------|-------------|-----------------|
| **Balanced** | Even time across all buckets | Match Perfect Week template |
| **Project Push** | Extra time on one project/bucket | 40% to focus, 60% spread |
| **Sprint** | Intense focus, fewer buckets | 2-3 buckets only |
| **Recovery** | Lighter load, recharge | Prioritize Health + Relationships |

This isn't rigid — it just sets the tone for scheduling decisions.

### 5. Capture New Activities
Ask: "What do you want to accomplish this week?" or "What's on your mind?"

For each activity:
- Match to the right bucket
- Set priority (1-5) and energy level (high/medium/low)
- Estimate duration

Use `wayve_create_activity` — batch mode (`activities` array) for multiple items.

### 6. Check Availability
Call `wayve_get_availability` to see free slots across the week:
- Total available hours vs. total planned hours
- Free slots per day with start/end times
- Blocked time (time locks + already scheduled)

If they're overcommitting, gently flag it: "You have 8 hours free this week but 12 hours of activities planned. What feels most important?"

### 7. Schedule Activities
Help place activities into available slots. Consider:
- **Bucket balance**: spread across buckets, weight toward focus bucket
- **Energy matching**: high-energy activities when they have energy (check `energy_patterns` knowledge — e.g., if you know they peak at 7-10 AM, schedule demanding activities there)
- **Time slot preferences**: respect each bucket's preferred time slot (morning/afternoon/evening)
- **Location context**: batch activities by location when possible

Use `wayve_update_activity` to set `scheduled_date` and `scheduled_time` for each.

### 7.5. Smart Suggestions

Check for pending smart suggestions and create new ones based on planning patterns. See `references/smart-suggestions.md` for full details.

**Check existing:**
```
wayve_manage_smart_suggestions(action: "list", status_filter: "pending")
```
Present max 2 relevant suggestions conversationally. Let the user accept, dismiss, or snooze.

**Create new:** Based on what you observe during planning — overcommitment patterns, same buckets neglected again, carryover patterns. Save via:
```
wayve_manage_smart_suggestions(action: "create", pattern: "...", proposal: "...", created_from: "fresh_start")
```

### 8. Weekly Summary
Show a final overview:
```
This week's plan:
- Health: 3 activities (5h) ★★★☆☆
- Growth: 4 activities (6h) ★★★★☆ ← focus bucket
- Relationships: 2 activities (3h) ★★☆☆☆
- Finance: 1 activity (2h) ★☆☆☆☆

Total: 10 activities | 16h planned | 22h available
```

### 9. Set Fresh Start Status
Update the week review: `wayve_manage_week_review` (action: `save`) with `fresh_start_status`: "completed".

### 9. Save Insights (Mandatory)
Before closing, silently save what you learned:

- [ ] **Focus mode chosen** → `scheduling_preferences` / `focus_mode_preference` (update after 3+ sessions)
- [ ] **Carryover pattern** → `weekly_patterns` / `carryover_pattern` (which buckets always carry over?)
- [ ] **Overcommitment?** → `weekly_patterns` / `overcommit_tendency` (planned hours > available)
- [ ] **User moved activities** → `scheduling_preferences` (they corrected your suggestion = preference)
- [ ] **Energy-based scheduling** → `energy_patterns` (did they ask for light activities at certain times?)
- [ ] **New personal context** → `personal_context` (anything new shared about their life?)

## End State
Week planned with activities distributed across buckets. User feels energized and clear about intentions.

Close with something forward-looking: "Your week is set. Remember — it's about intention, not perfection. Adjust as you go."

Direct them to the app:
- "Start your Fresh Start: https://gowayve.com/fresh-start"
- "View your weekly plan: https://gowayve.com/week"
- "See your calendar: https://gowayve.com/calendar"
