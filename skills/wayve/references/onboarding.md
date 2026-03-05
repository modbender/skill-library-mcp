# Phase 1: Onboarding — First-Time Setup

**Command:** `/wayve setup`

## When This Applies
No buckets found in `wayve_get_planning_context`, or user says "set up", "I'm new to Wayve", "getting started."

## Your Approach
Exploratory and pressure-free. "We can always adjust later." Don't overwhelm — if the user seems done, let them stop and come back later. This is about intention, not perfection.

## Setup Flow

### Step 1: Life Buckets
Help the user create 4-6 life buckets — areas of life that matter to them.

**Suggested defaults:**
| Bucket | Color | Example Intention |
|--------|-------|-------------------|
| Health | #10B981 (green) | "Move my body and fuel it well" |
| Relationships | #EC4899 (magenta) | "Nurture the people who matter" |
| Growth | #8B5CF6 (purple) | "Keep learning and evolving" |
| Finance | #F59E0B (gold) | "Build security and abundance" |
| Adventure | #06B6D4 (cyan) | "Experience new things and have fun" |

Ask what resonates — let them rename, add, or remove. For each bucket:
1. **Name** and **color** (hex)
2. **Intention** — one sentence about why this area matters
3. **Target hours per week** — how much time they'd ideally spend (e.g., Health: 5h)
4. **Preferred time slot** — morning, afternoon, evening, or flexible

Use `wayve_manage_bucket` (action: `create`) for each.

### Step 2: Frequency Targets
For each bucket, suggest a weekly frequency target beyond just hours — e.g.:
- Health: "Exercise 3x/week, cook at home 4x/week"
- Relationships: "Date night 1x/week, call a friend 2x/week"

Use `wayve_manage_bucket_frequency` (action: `create`) for each target:
- `bucket_id` — the bucket UUID
- `frequency_type` — "weekly" (most common), "daily", or "monthly"
- `target_count` — how many times per period (e.g., 3 for "3x/week")

These become trackable via `wayve_get_frequency_progress`.

### Step 3: Time Locks
Ask about recurring commitments that block time every week:
- Work hours (e.g., Mon-Fri 9:00-17:00)
- Commute, gym class, school pickup, etc.

Use `wayve_manage_timelock` (action: `create`) for each. Key parameters:
- `name`, `start_time` (HH:MM), `end_time` (HH:MM)
- `days_of_week` — array of ints, 0=Sunday through 6=Saturday
- `recurrence_type` — usually "weekly"
- `bucket_id` — optional, link to a bucket if relevant (e.g., gym → Health)

### Step 4: First Activities
Help capture 3-5 activities for this week. Ask: "What are the most important things you want to do this week?"

For each activity, match to a bucket and suggest a time. Use `wayve_create_activity`:
- `title`, `bucket_id`, `scheduled_date` (YYYY-MM-DD), `scheduled_time` (HH:MM)
- `duration_minutes`, `priority` (1-5), `energy_required` (high/medium/low)

Use `wayve_get_availability` to find free slots before scheduling.

For multiple activities, use batch mode: pass an `activities` array (up to 100) instead of individual calls.

### Step 5: Perfect Week Design
Help design their ideal weekly time distribution across buckets. This is aspirational — the template they'll aim for each week.

Use `wayve_manage_focus_template` (action: `create`):
- `name`: e.g., "My Balanced Week"
- `is_perfect_week`: true
- `distribution`: `{ "bucket-uuid": hours, ... }` — hours per bucket
- `total_hours`: sum of all bucket hours

### Step 6: Calendar Preferences
Set their working hours via `wayve_manage_settings` (action: `update_preferences`):
- `calendar_start_hour` (e.g., 7)
- `calendar_end_hour` (e.g., 22)
- `max_hours_per_day` (e.g., 10)

### Step 7: Explain the Weekly Rhythm
Close by explaining the two rituals:
- **Wrap Up** (Sunday evening): Reflect on the week, celebrate wins, choose focus for next week
- **Fresh Start** (Monday morning): Handle carryovers, capture new activities, plan the week

"You don't have to do these every week to get value from Wayve — but when you do, they make a real difference."

## App Links
When guiding the user, include links to the relevant pages on `gowayve.com`:
- Buckets setup: https://gowayve.com/buckets
- Time locks: https://gowayve.com/time-locks
- Weekly planning: https://gowayve.com/week
- Calendar view: https://gowayve.com/calendar
- Perfect Week designer: https://gowayve.com/perfect-week
- Account settings: https://gowayve.com/account

## End State
User has buckets with intentions, basic time locks, a few activities scheduled, and understands the weekly rhythm. Save any preferences or context as knowledge via `wayve_manage_knowledge` (action: `save_insight`).

### Save Initial Knowledge (Mandatory)
During onboarding, save everything you learn about the user:

- [ ] Timezone → `personal_context` / `timezone`
- [ ] Preferred name → `personal_context` / `preferred_name`
- [ ] Work schedule → `personal_context` / `work_schedule`
- [ ] Family/life situation (if shared) → `personal_context` / `family_situation`
- [ ] Calendar preferences → `scheduling_preferences` / `morning_routine`, `evening_boundary`
- [ ] Communication style → `preferences` / `communication_style`
- [ ] Any stated scheduling preferences → `scheduling_preferences`

This is the foundation for all future personalization. The more you capture now, the smarter every future session will be.

Close by pointing them to their new dashboard: "You're all set! Check out your dashboard anytime at https://gowayve.com/dashboard"
