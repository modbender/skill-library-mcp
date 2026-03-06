---
name: intent-guardian
version: 1.0.0
description: Watches your desktop activity, maintains a real-time task stack, detects when you forget what you were doing after interruptions, and gently reminds you. Your always-on focus companion.
author: huiling-one2x
tags: [productivity, focus, memory, awareness, context-switch]
tools: [shell, filesystem, memory, chat]
trigger: "intent guardian|task stack|what was I doing|focus guard|track my tasks"
config:
  poll_interval_seconds: 5
  interruption_threshold_minutes: 5
  reminder_cooldown_minutes: 3
  max_stack_depth: 20
  screen_capture_enabled: false
  screen_capture_interval_seconds: 30
  vision_model: ""
  activitywatch_enabled: true
  activitywatch_url: "http://localhost:5600"
  notification_channel: "system"
  working_hours_start: "09:00"
  working_hours_end: "18:00"
  excluded_apps: ["Finder", "SystemPreferences", "loginwindow"]
---

# Intent Guardian

**Never lose your train of thought again.**

Intent Guardian continuously monitors your desktop activity, builds a real-time understanding of what you're working on, and detects when you've been derailed by an interruption and forgotten your original task. When that happens, it nudges you back on track.

## The Problem

Knowledge workers are interrupted every 3 minutes on average. After an interruption, it takes ~23 minutes to return to the original task -- and often, you never return at all. Not because the task isn't important, but because you simply *forgot*.

Intent Guardian solves this by maintaining a **task stack** -- a living model of what you're doing, what you were doing, and what got interrupted -- so you don't have to.

## When to Use

- You are a multi-tasker who frequently context-switches between apps and tasks
- You often finish replying to a message and think "wait, what was I doing?"
- You want an AI companion that understands your work rhythm, not just your commands
- You want to build long-term awareness of your own focus patterns

## Core Capabilities

### 1. Real-Time Activity Sensing

Polls the active window title and application name to build a continuous activity stream.

**macOS:**
```bash
bash command:"scripts/sense_activity.sh"
```

**With ActivityWatch (richer data):**
```bash
bash command:"scripts/sense_activitywatch.sh"
```

**With Screen Capture (optional, requires vision model):**
```bash
bash command:"scripts/sense_screen.sh"
```

### 2. Task Stack Maintenance

The agent maintains a task stack in `memory/skills/intent-guardian/task_stack.json`:

```json
{
  "stack": [
    {
      "id": "task_001",
      "intent": "Writing product requirements doc, section 3",
      "app": "Google Docs",
      "window_title": "Product Requirements v2 - Google Docs",
      "started_at": "2026-02-26T14:28:00",
      "status": "suspended",
      "suspended_at": "2026-02-26T14:31:00",
      "suspended_by": "Slack notification from Li Si",
      "completion_estimate": 0.6
    },
    {
      "id": "task_002",
      "intent": "Replying to Li Si about the API bug",
      "app": "Slack",
      "window_title": "Slack - #engineering",
      "started_at": "2026-02-26T14:31:00",
      "status": "completed",
      "completed_at": "2026-02-26T14:35:00"
    },
    {
      "id": "task_003",
      "intent": "Looking up React useEffect cleanup pattern",
      "app": "Chrome",
      "window_title": "Stack Overflow - React useEffect cleanup",
      "started_at": "2026-02-26T14:35:00",
      "status": "active"
    }
  ],
  "current_focus": "task_003",
  "forgotten_candidates": ["task_001"]
}
```

### 3. Interruption & Forgetting Detection

The agent analyzes the task stack to detect potential forgetting:

**Signals that suggest forgetting:**
- A suspended task has not been resumed for longer than `interruption_threshold_minutes`
- The user has moved through 2+ unrelated contexts since the suspension
- The user shows "wandering" behavior: rapid app-switching without sustained focus
- The suspended task had low completion estimate (was in the middle of something)

**Signals that suggest deliberate abandonment (do NOT remind):**
- The user explicitly closed the application associated with the task
- The task was at a natural completion point (e.g., finished sending an email)
- The user started a clearly intentional new deep-work session

### 4. Gentle Reminders

When forgetting is detected, the agent sends a non-intrusive reminder:

**Simple reminder:**
> "You were working on the product requirements doc (section 3) about 25 minutes ago, before the Slack interruption. Want to go back to it?"

**Smart reminder (with context carried forward):**
> "You left the product requirements doc to look up the useEffect cleanup pattern for Li Si's bug. The answer is: return a cleanup function in useEffect. Ready to bring this back to the doc?"

The second form is more powerful -- it doesn't just remind you what you forgot, it **completes the reason you left**, so you can return to your main task with the answer in hand.

### 5. Long-Term Pattern Learning

Over time, the agent builds a focus profile in `memory/skills/intent-guardian/focus_profile.json`:

```json
{
  "user_id": "default",
  "updated_at": "2026-02-26",
  "patterns": {
    "avg_focus_duration_minutes": 12,
    "interruption_sources": {
      "Slack": { "count": 45, "forget_rate": 0.78 },
      "Mail": { "count": 22, "forget_rate": 0.18 },
      "Chrome": { "count": 31, "forget_rate": 0.42 }
    },
    "peak_focus_hours": ["09:00-11:00", "14:00-16:00"],
    "high_risk_transitions": [
      { "from": "VSCode", "to": "Slack", "forget_rate": 0.82 },
      { "from": "Google Docs", "to": "Chrome", "forget_rate": 0.55 }
    ],
    "reminder_effectiveness": {
      "accepted": 34,
      "dismissed": 8,
      "ignored": 5
    }
  }
}
```

This profile is used to personalize detection thresholds and reminder timing.

## Architecture

```
 Your Desktop
      |
      v
 [Sensing Layer]  ---- scripts/sense_activity.sh (window title, every N sec)
      |                 scripts/sense_activitywatch.sh (ActivityWatch API)
      |                 scripts/sense_screen.sh (optional screenshot + vision)
      v
 [Activity Log]   ---- memory/skills/intent-guardian/activity_log.jsonl
      |
      v
 [Understanding]  ---- LLM analyzes activity stream on each Heartbeat:
      |                 - Segments activities into logical tasks
      |                 - Infers intent for each task
      |                 - Detects interruptions and context switches
      v
 [Task Stack]     ---- memory/skills/intent-guardian/task_stack.json
      |
      v
 [Detection]      ---- Compares stack state against forgetting heuristics
      |                 Consults focus_profile.json for personalized thresholds
      v
 [Reminder]       ---- Sends reminder via configured notification channel
      |                 Logs user response for feedback loop
      v
 [Learning]       ---- Updates focus_profile.json with new patterns
```

## Heartbeat Integration

Add to your `HEARTBEAT.md`:

```markdown
## Intent Guardian Check
Every heartbeat, run the intent guardian cycle:
1. Read latest activity from memory/skills/intent-guardian/activity_log.jsonl
2. Update task_stack.json with new activities
3. Check for forgotten tasks (suspended > threshold, not resumed)
4. If forgotten task detected, send reminder
5. Log any reminder responses to focus_profile.json
```

## Cron Integration

Add a daily focus report:

```bash
openclaw cron add --name "intent-guardian-daily" --schedule "0 18 * * *" \
  --prompt "Generate my daily focus report using intent-guardian data"
```

## Setup

### Minimal Setup (macOS, no dependencies)

1. Install the skill:
```bash
npx playbooks add skill openclaw/skills --skill intent-guardian
```

2. The skill uses native macOS commands (`osascript`) to get the active window.
No additional software required.

3. Add the Heartbeat integration above to your `HEARTBEAT.md`.

### Enhanced Setup (with ActivityWatch)

1. Install [ActivityWatch](https://activitywatch.net/) for richer window-level tracking.
2. Set `activitywatch_enabled: true` in skill config.
3. ActivityWatch provides detailed per-window timelines including URLs and document titles.

### Full Setup (with Screen Capture)

1. Set `screen_capture_enabled: true` and configure `vision_model`.
2. Requires a vision-capable model (Claude, Gemini, Qwen3-VL).
3. Screenshots are captured locally, analyzed locally or via API, and **never stored permanently**.

## Privacy & Security

- **All data stays local.** Activity logs, task stacks, and focus profiles are stored as local files in your OpenClaw memory directory.
- **No raw screenshots are persisted.** If screen capture is enabled, frames are analyzed and immediately discarded. Only the semantic summary is kept.
- **Excluded apps are respected.** Configure `excluded_apps` to prevent tracking specific applications.
- **Working hours enforced.** Sensing only runs during configured `working_hours_start` to `working_hours_end`.
- **You own the data.** All files are human-readable JSON/JSONL. Review, edit, or delete at any time.

## Configuration Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `poll_interval_seconds` | int | 5 | How often to check the active window |
| `interruption_threshold_minutes` | int | 5 | Minutes before a suspended task is flagged as potentially forgotten |
| `reminder_cooldown_minutes` | int | 3 | Minimum time between reminders to avoid nagging |
| `max_stack_depth` | int | 20 | Maximum tasks to track in the stack |
| `screen_capture_enabled` | bool | false | Enable periodic screenshot analysis |
| `screen_capture_interval_seconds` | int | 30 | Interval for screenshots (if enabled) |
| `vision_model` | string | "" | Model for screenshot analysis (e.g., "gemini", "claude") |
| `activitywatch_enabled` | bool | true | Use ActivityWatch for richer activity data |
| `activitywatch_url` | string | "http://localhost:5600" | ActivityWatch server URL |
| `notification_channel` | string | "system" | Where to send reminders ("system", "telegram", "slack", etc.) |
| `working_hours_start` | string | "09:00" | Start of active tracking window |
| `working_hours_end` | string | "18:00" | End of active tracking window |
| `excluded_apps` | list | ["Finder", "SystemPreferences", "loginwindow"] | Apps to ignore |

## Example Interactions

**User:** "What was I doing before I got sidetracked?"
**Agent reads task_stack.json, responds:**
> "Before the Slack interruption at 14:31, you were writing section 3 of the product requirements doc in Google Docs. You were about 60% through. Want to jump back?"

**User:** "Show me my task stack"
**Agent responds with current stack visualization:**
> ```
> Task Stack (3 items):
> [ACTIVE]     Looking up React useEffect cleanup (Chrome) - 17 min
> [COMPLETED]  Replying to Li Si about API bug (Slack) - 4 min
> [SUSPENDED]  Writing product requirements doc, section 3 (Google Docs) - 25 min ago  !!
> ```

**User:** "How's my focus today?"
**Agent reads activity log and focus profile:**
> "Today you've had 6 deep work sessions averaging 18 minutes each. You were interrupted 11 times, mostly by Slack (7 times). You forgot to return to your original task 4 times -- I caught 3 of those. Your peak focus was 09:30-10:45."

**Proactive (via Heartbeat):**
> "Heads up -- you've been away from the quarterly report (Excel) for 40 minutes since that phone call. It's due tomorrow. Want to wrap up the current task and go back to it?"

## Integration with Other Skills

Intent Guardian works well alongside these existing skills:

| Skill | Integration |
|-------|-------------|
| `personal-analytics` | Feed focus_profile data into analytics for richer weekly reports |
| `daily-review` | Include task completion stats and interruption counts in daily reviews |
| `deepwork-tracker` | Auto-start deepwork timer when sustained focus is detected |
| `screen-monitor` | Use screen_analyze for richer context when vision model is configured |
| `rememberall` | Convert suspended tasks into time-based reminders as fallback |
| `get-focus-mode` | Suppress reminders when macOS Focus mode is active |

## Roadmap

- [ ] Cross-device sync (remind on phone about tasks left on laptop)
- [ ] Team mode (with consent: "Zhang San is waiting for your review, 2 days now")
- [ ] Proactive task delegation ("I can draft that email reply while you focus on the doc")
- [ ] Calendar-aware urgency ("The quarterly report meeting is in 2 hours, and you're only 60% done")
- [ ] Intent hierarchy (L1-L4 goal tracking, not just immediate tasks)

## License

MIT
