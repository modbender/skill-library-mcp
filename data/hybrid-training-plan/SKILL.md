---
name: hybrid-training-plan
description: View and manage a Hybrid Training Plan — check today's workout, log strength sets and runs, mark days complete or skip, view exercise 1RMs and session history. Use when the user asks about their training, wants to log a workout, or needs to interact with hybridtrainingplan.app.
compatibility: Requires curl and jq. Set HYBRID_API_KEY and optionally HYBRID_API_URL.
metadata: {"openclaw":{"requires":{"bins":["curl","jq"],"env":["HYBRID_API_KEY"]},"primaryEnv":"HYBRID_API_KEY"}}
---

# Hybrid Training Plan Skill

Interact with the user's training plan at hybridtrainingplan.app via natural language.

## Setup

1. Generate an API key at **hybridtrainingplan.app/account** → Agent Skills → New key
2. Add to your Claude environment (`.claude/.env` or shell profile):

```bash
export HYBRID_API_KEY="htp_your_key_here"
export HYBRID_API_URL="https://api.hybridtrainingplan.app"   # optional, this is the default
```

The helper script is at `scripts/htp.sh` relative to this skill. Run `chmod +x scripts/htp.sh` once to make it executable.

## Common operations

### Check today's dashboard
```bash
scripts/htp.sh dashboard
```
Returns the current plan ID, today's date, active week/day info, and recent session summaries.

### View a specific day's workout
```bash
scripts/htp.sh day 2026-02-27 <planId>
```
Returns the day's sessions with exercises, sets, reps, load guidance, and running prescription.

### Log a session
```bash
scripts/htp.sh log-session '{"planId":"...","sessionId":"...","dayDate":"2026-02-27","sessionType":"strength","strengthSets":[{"exerciseName":"Squat","exerciseKey":"squat","setIndex":0,"reps":5,"weightKg":100}]}'
```

### Mark a day complete
```bash
scripts/htp.sh complete 2026-02-27 <planId>
```

### Skip a day
```bash
scripts/htp.sh skip 2026-02-27 <planId>
```

### View session logs for a day
```bash
scripts/htp.sh session-logs <planId> 2026-02-27
```

### View exercise 1RMs (maxes)
```bash
scripts/htp.sh maxes
```

### Update a 1RM
```bash
scripts/htp.sh set-max "Squat" 120
```

## Notes

- Weights are always in **kg** in the API regardless of the user's display preference
- `sessionId` is the UUID of the specific session inside the plan (visible in the day view response)
- `planId` is the UUID of the training plan (visible in the dashboard response)
- See `references/api.md` for full request/response schemas
