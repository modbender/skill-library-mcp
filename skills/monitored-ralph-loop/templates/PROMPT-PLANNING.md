# Ralph PLANNING Loop

## Goal
[YOUR GOAL HERE - What are you building?]

## Context
- Read: specs/*.md
- Read: Current codebase structure
- Update: IMPLEMENTATION_PLAN.md

## Rules
1. Do NOT implement any code
2. Do NOT commit anything
3. Analyze gaps between specs and current codebase
4. Create/update IMPLEMENTATION_PLAN.md with prioritized tasks
5. Each task should be atomic and achievable in < 1 hour
6. If requirements are unclear, list specific questions

## Task Format
Use this format in IMPLEMENTATION_PLAN.md:
```markdown
## Tasks

### HIGH PRIORITY
- [ ] Task 1: Brief description
- [ ] Task 2: Brief description

### MEDIUM PRIORITY
- [ ] Task 3: Brief description

### LOW PRIORITY
- [ ] Task 4: Brief description

## Questions
- Question 1?
- Question 2?

## Notes
- Observation 1
- Observation 2
```

## Notifications
When you need input or finish planning, write to the notification file:

```bash
mkdir -p .ralph
cat > .ralph/pending-notification.txt << 'EOF'
{"timestamp":"$(date -Iseconds)","message":"<PREFIX>: <message>","status":"pending"}
EOF
```

Prefixes:
- `DECISION:` — Need human input on architectural choice
- `QUESTION:` — Requirements unclear, need clarification
- `PLANNING_COMPLETE:` — Planning finished

> The ralph.sh script will also try `openclaw gateway call cron.add` for immediate delivery.

## Completion
When the plan is complete and comprehensive:
1. Add this line to IMPLEMENTATION_PLAN.md:
   ```
   STATUS: PLANNING_COMPLETE
   ```
2. Write completion notification:
   ```bash
   mkdir -p .ralph
   cat > .ralph/pending-notification.txt << 'EOF'
   {"timestamp":"$(date -Iseconds)","message":"PLANNING_COMPLETE: X tasks identified. Ready for BUILDING.","status":"pending"}
   EOF
   ```
