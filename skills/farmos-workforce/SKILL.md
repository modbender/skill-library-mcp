---
name: farmos-workforce
description: Query employee data, time clock entries, schedules, and requests. Requires authentication — employees see own data, managers see team.
tags: [farming, workforce, employees, timeclock]
---

# FarmOS Workforce

Employee profiles, time clock, skills tracking, employee requests, and team calendar.

## When to Use This

**What this skill handles:** Time clock (clock in/out), schedules, availability, time-off requests, certifications, employee profiles, overtime tracking, and payroll exports.

**Trigger phrases:** "I need [day] off", "who's working", "schedule", "clock in/out", "who's clocked in?", "overtime this week?", "any pending time-off requests?", "employee list", "CDL certifications"

**What this does NOT handle:** Task assignments or work orders (use farmos-tasks), equipment scheduling or maintenance (use farmos-equipment), pay rates or financial compensation questions (restricted to admin only via farmos-finance).

**Minimum viable input:** Any mention of schedule, availability, time off, or who is working. "I need Friday off" is enough.

## Data Completeness

1. **Always state the count** of employees, time entries, or requests returned: "Found 8 active employees" or "12 time entries this pay period."
2. **Time entry queries are date-bounded** — always include `start_date` and `end_date` parameters to get the full picture for the requested period.
3. **If an endpoint fails**, report it — don't silently present empty results as "no employees" or "no time entries."
4. **For payroll exports**, verify the date range covers the full pay period before exporting.

## Authentication

This skill accesses protected FarmOS endpoints that require a JWT token.

**To get a token:**
```bash
TOKEN=$(~/clawd/scripts/farmos-auth.sh manager)
```

**Role mapping:** Check `~/.clawdbot/farmos-users.json` for the sender's role.
- **admin/manager:** Can see all employee data, hours, payroll info.
- **employee:** Can only see own profile and time entries. Do NOT use a manager token for employee queries — use the employee token so the API scopes correctly.

## API Base

http://100.102.77.110:8006

## Integration Endpoints (No Auth)

### Employee List (for assignments)
GET /api/integration/employees

Returns: All employees with id, name, role. Use for task assignment dropdowns.

### Active Employees
GET /api/integration/employees/active

Returns: Currently active employees only.

## Authenticated Endpoints (JWT Required)

### Employee Profiles
GET /api/employees — List all employees (manager+)
GET /api/employees/{id} — Employee detail (manager+ or own profile)
GET /api/employees/me — Current user's profile

### Time Clock
POST /api/time/clock-in — Clock in (with optional GPS)
POST /api/time/clock-out — Clock out
GET /api/time/status — Current clock status for user
GET /api/time/entries?start_date=2026-02-01&end_date=2026-02-13 — Time entries

### Timesheet Approval (Manager)
POST /api/time/entries/{id}/approve — Approve timesheet entry
GET /api/time/export?start_date=2026-02-01&end_date=2026-02-13&format=csv — Payroll export

### Employee Requests
POST /api/requests — Submit time off/leave request
GET /api/requests/my — My requests
GET /api/requests/pending — Pending approvals (manager)
POST /api/requests/{id}/approve — Approve
POST /api/requests/{id}/reject — Reject with reason body: {"reason": "..."}

### Calendar
GET /api/calendar/events?start=2026-02-01&end=2026-02-28 — Team calendar

### Skills & Certifications
GET /api/skills — Skill definitions
GET /api/employees/{id}/skills — Employee's skills and certifications

## Usage Notes

- Time entries include GPS coordinates if the employee clocked in from the field.
- Overtime calculation: hours over 40/week.
- Payroll export generates CSV compatible with common payroll systems.
- Skills have expiry dates — flag any certifications expiring within 30 days.
- NEVER share employee pay rates, hours, or personal info with other employees. Only managers and admins can see team-wide data.


---

## Conversational Schedule Capture

Crew members communicate schedule needs casually. Recognize these patterns and capture them without making it feel like paperwork.

### Capture Patterns

| What They Say | What It Is | Action |
|--------------|-----------|--------|
| "I need Thursday afternoon off" | Time-off request | Log time-off, notify manager |
| "I can come in early tomorrow" | Availability note | Log availability change |
| "I'll be late Monday, doctor appointment" | Schedule note | Log late arrival, note reason |
| "Can I swap shifts with Jake on Friday?" | Shift swap request | Route to Brian/manager for approval |
| "I'm not going to be able to make it Saturday" | Absence notification | Log absence, notify manager |
| "I've got a thing next Wednesday" | Vague time-off | Log it — don't ask what "thing" is |

### Bot Behavior

**Extract from message:**
- Who (from Slack user identity or name mention)
- When (day, date, time range)
- How long (half day, full day, a few hours)
- Reason (ONLY if volunteered — NEVER ask "what kind of appointment?")

**Response pattern:**
- Confirm what you understood: "Got it — flagging Thursday afternoon off for you."
- Tell them it's visible: "Brian will see it in the schedule."
- If unclear timing, ask ONE clarifying question: "Need the whole afternoon or just leaving early?"
- NEVER interrogate about reasons. "Appointment" is sufficient. Period.

**Routing:**
- Log to workforce module API (POST /api/requests for time-off, use appropriate endpoint for availability)
- Notify in #farm-workforce channel for visibility
- For swap requests: notify both parties and Brian

### Availability Updates

When crew mentions availability changes mid-conversation (not a formal request), still capture it:
- "I might be able to work this Saturday if you need me" → log as tentative availability
- "My kid has a game Friday evening so I need to leave by 3" → log early departure
- "I can stay late tonight if we need to finish" → log extended availability
