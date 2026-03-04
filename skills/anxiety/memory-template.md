# Memory Template - Anxiety (Tracker, Trigger Map, Coping Planner)

Create `~/anxiety/memory.md` with this structure:

```markdown
# Anxiety Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Active Mode
mode: track | reduce | recover
primary_goal:
secondary_goal:

## Baseline Snapshot
typical_trigger_windows:
common_body_signals:
peak_intensity_range:
usual_episode_duration:

## Trigger and Behavior Patterns
top_triggers:
avoidance_patterns:
safety_behaviors:
helpful_coping:

## Active Plan
plan_start:
this_week_focus:
next_check_in:
current_exposure_step:

## Escalation Preferences
urgent_contact_flow:
preferred_language_in_crisis:
professional_support_status:

## Notes
- Confirmed patterns
- Failed tactics to avoid repeating
- Open questions for therapy or medical follow-up

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Active support | Continue logging and plan refinement |
| `complete` | Stable control routine | Maintain with light check-ins |
| `paused` | User paused support | Keep context read-only until resumed |
| `never_ask` | No setup prompts wanted | Do not ask setup questions unless requested |

## File Templates

Create `~/anxiety/logs/events.md`:

```markdown
# Anxiety Event Log

## YYYY-MM-DD
- Event: HH:MM | context | trigger | body_signals | intensity_before_0_to_10 | behavior | intensity_after_0_to_10 | notes
- Event: HH:MM | context | trigger | body_signals | intensity_before_0_to_10 | behavior | intensity_after_0_to_10 | notes
```

Create `~/anxiety/logs/thought-records.md`:

```markdown
# Thought Records

## YYYY-MM-DD HH:MM
- Situation:
- Automatic thought:
- Emotion and intensity:
- Evidence for:
- Evidence against:
- Balanced alternative thought:
- Re-rated intensity:
```

Create `~/anxiety/plans/current.md`:

```markdown
# Current Anxiety Plan

## Mode
- track | reduce | recover

## Weekly Targets
- Target 1:
- Target 2:
- Review date:

## Coping Actions
- Low-intensity:
- Medium-intensity:
- High-intensity:

## Escalation Protocol
- Early warning:
- Immediate action:
- Follow-up within 24h:
```

Create `~/anxiety/triggers.md`:

```markdown
# Trigger Map

## Trigger
- Situation:
- Typical thought:
- Body response:
- Behavior:
- Response tested:
- Result:
- Next adjustment:
```

Create `~/anxiety/exposures.md`:

```markdown
# Exposure Ladder

## Goal
- Target situation:
- Why this matters:

## Steps
- Step | difficulty_0_to_10 | duration | completed_yes_no | notes
```

Create `~/anxiety/reviews/weekly.md`:

```markdown
# Weekly Anxiety Review

## Week Ending YYYY-MM-DD
- Episode frequency trend:
- Average intensity trend:
- Top trigger this week:
- Best coping response:
- Exposure progress:
- Next-week focus:
```

## Key Principles

- Keep entries short, timestamped, and behavior-focused.
- Separate observations from interpretations.
- Update `last` whenever mode, priorities, or escalation plan changes.
- Track only information needed for future support quality.
