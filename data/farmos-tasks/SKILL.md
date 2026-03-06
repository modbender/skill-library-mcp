---
name: farmos-tasks
description: Query and manage farm work orders and tasks. View assignments, create tasks, update status. Uses integration endpoints (no auth) for reads and authenticated endpoints for writes.
tags: [farming, tasks, work-orders]
---

# FarmOS Task Manager

Work orders and task management — view assignments, check status, and manage the task workflow.

## When to Use This

**What this skill handles:** Task creation, assignments, status updates, work orders, action items, follow-ups, and restock/procurement requests.

**Trigger phrases:** "remind me to...", "we need to...", "someone should...", "create a task", "what tasks are assigned to me?", "any overdue tasks?", "mark task X as complete", "we're low on...", "used the last...", "we need more..."

**What this does NOT handle:** Equipment maintenance tracking (use farmos-equipment), scheduling/time-off/availability (use farmos-workforce), field observations and scouting reports (use farmos-observations).

**Minimum viable input:** Any description of work that needs to happen. "We need to do something about field 12" is enough.

## API Base

http://100.102.77.110:8007

## Integration Endpoints (No Auth Required)

### Dashboard Summary
GET /api/integration/dashboard

Returns: Task widget data — counts by status, priority breakdown, recent activity. **Use for summary stats only — not for listing tasks.**

### Tasks Summary
GET /api/integration/tasks-summary

Returns: Aggregate counts:
```json
{
  "total": 15,
  "pending": 3,
  "assigned": 5,
  "in_progress": 4,
  "completed": 3,
  "critical": 1,
  "high_priority": 2,
  "overdue": 1
}
```

### Task List (Filtered)
GET /api/integration/tasks?limit=10&status=in_progress&priority=high

Query params: limit, status (pending|assigned|in_progress|completed|cancelled), priority (low|normal|high|critical)

Returns: Simplified task objects with id, title, status, priority, due_date, assignees.

### Single Task
GET /api/integration/tasks/{id}

Returns: Full task detail for integration.

## Authenticated Endpoints

These require JWT auth. See Authentication section below.

### Authentication

This skill accesses protected FarmOS endpoints that require a JWT token.

**To get a token:** Run the auth helper with the appropriate role:
```bash
TOKEN=$(~/clawd/scripts/farmos-auth.sh manager)
```

**To use the token:** Include it as a Bearer token:
```bash
curl -H "Authorization: Bearer $TOKEN" http://100.102.77.110:8007/api/endpoint
```

**Token expiry:** Tokens last 15 minutes. If you get a 401 response, request a new token.

**Role mapping:** Check the sender's role in `~/.clawdbot/farmos-users.json` to determine which auth level to use. If the user's role doesn't have permission for the requested data, tell them they don't have access rather than trying with a higher-privilege token.

### My Tasks (Employee View)
GET /api/tasks/mine
Authorization: Bearer {token}

Returns: Tasks assigned to the authenticated user.

### Create Task (Manager+)
POST /api/tasks
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "title": "Spray north fields - Section 12",
  "description": "Apply pre-emerge herbicide per agronomy recommendation",
  "priority": "high",
  "due_date": "2026-02-20",
  "equipment_id": 5,
  "estimated_duration_minutes": 180
}
```

### Update Task Status
POST /api/tasks/{id}/start — Mark as in_progress
POST /api/tasks/{id}/complete — Mark as completed
POST /api/tasks/{id}/cancel — Cancel task
Authorization: Bearer {token}

### Assign Task (Manager+)
POST /api/tasks/{id}/assign
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "employee_ids": [3, 4]
}
```

Employee IDs come from the Workforce module integration endpoint.

## Task Templates

### List Templates
GET /api/templates
Authorization: Bearer {token}

### Create Task from Template
POST /api/templates/{id}/create-task
Authorization: Bearer {token}

Creates a new task pre-filled from the template.

## Status Workflow

```
pending → assigned → in_progress → completed
                                  → cancelled
```

- Tasks start as "pending"
- Assigning employees moves to "assigned"
- Worker starting moves to "in_progress"
- Worker finishing moves to "completed"

## Conversational Task Creation

The bot should recognize when someone describes work that needs to happen and offer to create a task. Do NOT create tasks silently — always offer first.

### Auto-Detect from Conversation

When someone describes actionable work, extract as much as you can:

| Signal | How to Detect | Example |
|--------|--------------|---------|
| **Assignee** | "tell Jake to..." → Jake. "I need to..." → reporter. Otherwise → unassigned | "Tell Jake to check the tile outlet" → assignee: Jake |
| **Priority** | "ASAP" / "before it rains" / "right now" → high. "When you get a chance" / "sometime" → low. Default → normal | "We need to spray before it rains" → priority: high |
| **Field** | Field number, field name, landmark reference | "field 14", "the Byrd farm", "that field by the elevator" |
| **Equipment** | Machine name, number, type | "the 8370R", "the planter", "combine #2" |
| **Deadline** | Time references parsed to dates | "by Thursday", "this week", "before planting", "end of month" |

### Natural Language Examples

| What They Say | Auto-Detect |
|--------------|-------------|
| "We need to spray field 14 before Thursday" | Field: 14, action: spray, deadline: Thursday |
| "Remind me to call the seed rep" | Assignee: reporter, action: call seed rep |
| "Someone should check the tile outlet in field 8" | Field: 8, action: check tile outlet, unassigned |
| "The north fence needs fixed before we turn cows out" | Location: north fence, context: cattle, deadline: before turnout |
| "Jake needs to grease the planter before we start" | Assignee: Jake, equipment: planter, action: grease |
| "We should probably get the combine serviced this month" | Equipment: combine, action: service, deadline: end of month, priority: normal |

### Confirmation Before Creating (ALWAYS)

Never create a task without confirming. Pattern:

"Creating: 'Spray field 14' — due Thursday, unassigned. Sound right?"

If they say yes, confirm details and POST. If they tweak something ("actually make it high priority"), adjust and confirm again.

### When NOT to Offer a Task

- Message is clearly just conversation, not actionable ("Man, that field looks rough")
- Someone is asking a question, not requesting work ("When was field 14 last sprayed?")
- The work is already being done right now ("I'm spraying field 14")
- It's a status update, not a new request ("Field 14 is done")

### Guidance

- "Want me to make that a task?" is the right prompt when it sounds like work
- If vague, create the task with what you have — a vague task is better than no task
- For recurring needs ("we always need to do X before Y"), mention templates: "Want me to create a template for this so it auto-generates next time?"
- After creating, offer related actions: "Want me to assign someone?" "Should I set a reminder?"

## Parts & Supplies Intake

Any mention of supply levels should be treated as actionable. The bot captures supply intel that would otherwise be lost.

### Detection Patterns

| What They Say | Action | Priority |
|--------------|--------|----------|
| "We're low on hydraulic filters" | Offer restock task (tag: procurement) | normal |
| "Used the last box of seed treatment" | Create restock task (tag: procurement) | high — last one is urgent |
| "We're gonna need more twine before we're done" | Offer restock task (tag: procurement) | normal |
| "Down to 2 hydraulic filters for the planters" | Offer restock task with quantity context | normal |
| "I ordered 5 gallons of Roundup" | Acknowledge — no task needed (already ordered) | — |
| "Where do we keep the grease cartridges?" | Answer question — no task | — |
| "We're out of DEF" | Create restock task (tag: procurement) | high — completely out |

### Response Patterns

- **Low supply:** "Good to know — logged it. Want me to create a restock task or just flag it for Brian?"
- **Last one / completely out:** "Noted — that sounds urgent. Creating a restock task now." (still confirm, but signal urgency)
- **Already ordered:** "Got it, thanks for the heads up." (no task, just acknowledge)
- **Question about supplies:** Answer the question, no task creation

### Restock Task Format

When creating a procurement task:
```json
{
  "title": "Restock: hydraulic filters (planters)",
  "description": "Crew reports low supply — down to 2 remaining",
  "priority": "normal",
  "tags": ["procurement"]
}
```

**Tag ALL supply/restock tasks with `procurement`** so they can be filtered and batched for ordering.

For "used the last" or "completely out" situations, set priority to "high".

## Data Completeness

- Always report the total count of records returned
- If a query returns suspiciously few results, say so: "I'm only seeing X results — that may be incomplete"
- Use integration `/tasks` endpoint with appropriate filters for listing, not `/api/integration/dashboard` (which truncates)
- For paginated results, note the total and offer to fetch more

## Cross-Module Context

When working with tasks, connect the dots to other modules:

**Tasks → Weather:**
- When listing today's tasks or the week's schedule, check farmos-weather. Flag conflicts: "You've got spray tasks on the board for Thursday, but rain is coming Thursday afternoon. Might want to move those up."
- For any field operation task (spraying, planting, harvesting, tillage), the weather matters. Check spray conditions for spray tasks, check precipitation forecast for fieldwork.
- Don't check weather for shop tasks, office tasks, or supply runs — only field work.

**Tasks → Equipment:**
- When listing tasks, check farmos-equipment for machine availability. If a task requires specific equipment, verify it's not down or due for maintenance: "The sprayer has 3 tasks this week, but it's at 197 hours and service is due at 200. Might want to get that done first."
- When a task is created for a specific machine, check that machine's status. If it's in maintenance or has an open issue, flag it.
- When equipment is reported as down, check for tasks assigned to that machine and offer to flag them as blocked.

**Tasks → Observations:**
- When a task relates to a field, check farmos-observations for recent observations on that field. "There's a waterhemp observation from yesterday in field 14 — might be related to the scouting task."
- After a task is created from an observation (e.g., "spray field 14 for waterhemp"), link back to the observation context.

**Tasks → Marketing (delivery deadlines):**
- During harvest season, check farmos-marketing delivery schedules. Delivery commitments affect which fields get priority: "You've got a 5,000-bu bean delivery to ADM due next week — priority on the bean fields."
- This only matters during harvest and delivery windows. Don't cross-reference marketing for routine maintenance or spray tasks.

Cross-reference when it adds value. Not every "mark task complete" needs a weather check. Use judgment — the goal is connecting dots the crew might miss, not adding noise to simple operations.

## Usage Notes

- Use integration endpoints for read queries (no auth needed).
- Use authenticated endpoints for creating/updating tasks (manager+ role).
- Priority levels: low, normal, high, critical.
- Always check for overdue tasks in summaries.
- Equipment IDs link to the Equipment module — use farmos-equipment skill to look up names.
- Employee IDs for assignments come from farmos-workforce skill.
- When creating tasks, suggest appropriate priority based on context.
