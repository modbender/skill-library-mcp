# Forgetting Detection - Algorithm Reference

This document describes the heuristics used by Intent Guardian to distinguish between "forgotten" tasks and tasks that were deliberately abandoned or postponed.

## The Four States of a Suspended Task

When a user leaves a task, there are four possible reasons:

| State | Definition | Agent Action |
|-------|-----------|--------------|
| **Completed** | User finished the task naturally | Archive, no reminder |
| **Postponed** | User intentionally decided to do it later | Offer timed reminder, don't nag |
| **Abandoned** | User decided not to do it at all | Archive, no reminder |
| **Forgotten** | User was interrupted and lost track | **Remind proactively** |

## Detection Signals

### Strong "Forgotten" Signals

- Task was interrupted by an **external trigger** (notification, message, phone call)
- Task had **low completion** (was in the middle of typing, editing, coding)
- User entered **2+ unrelated contexts** after the interruption
- User shows **wandering behavior**: switching between apps every <30 seconds with no sustained focus
- Time since suspension exceeds threshold AND user has not returned

### Strong "Completed" Signals

- User was at a **natural stopping point** (sent the email, saved the file, closed the tab)
- The app associated with the task was **explicitly closed**
- The activity preceding the switch was a **terminal action** (submit, send, save, commit, deploy)

### Strong "Postponed" Signals

- User **verbally indicated** postponement ("I'll do this later", noted in a todo)
- User switched to a task with **known higher urgency** (calendar event starting, urgent message)
- The switch happened at a **natural break point** (end of a section, between subtasks)

### Strong "Abandoned" Signals

- User **closed or quit** the application without completing the task
- Significant time has passed (>2 hours) with no related activity
- The task was exploratory (browsing, researching) rather than goal-directed

## Personalized Thresholds

Over time, the focus_profile.json accumulates per-app and per-transition statistics:

```
forget_rate(app_from, app_to) = forgotten_count / total_transitions
```

If `forget_rate(VSCode, Slack) = 0.82`, the agent should be more aggressive about reminding when this specific transition occurs, even before the default threshold is reached.

Conversely, if `forget_rate(Chrome, VSCode) = 0.05`, the agent should assume the user knows what they're doing and be less intrusive.

## Confidence Scoring

Each detection should carry a confidence score:

```
confidence = base_score
  + 0.2 if external_trigger
  + 0.2 if low_completion_estimate
  + 0.1 * context_switches_since_suspension (max 0.3)
  + 0.1 if wandering_behavior_detected
  - 0.3 if natural_stopping_point
  - 0.2 if explicit_close
  - 0.1 if user_in_deep_focus_on_new_task
```

Only trigger a reminder when confidence > 0.6.

## Edge Cases

### Bathroom/Coffee Break
User leaves the desk entirely (no activity for 5+ minutes). This is NOT forgetting -- the user likely remembers what they were doing. However, if they return and start something completely different, re-evaluate.

### Meeting Interruption
User switches to Zoom/Teams for a meeting. After the meeting (30-90 min), they're very likely to have forgotten the pre-meeting task. Increase urgency.

### End of Day
If a task was suspended and the workday is ending, offer to create a note for tomorrow rather than a reminder now.
