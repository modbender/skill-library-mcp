---
name: farmos-equipment
description: Query equipment status, maintenance schedules, and service history for the farm fleet. Uses integration endpoints (no auth required).
tags: [farming, equipment, maintenance]
---

# FarmOS Equipment

Query and manage farm equipment data — status, maintenance schedules, service records, and parts inventory.

## When to Use This

**What this skill handles:** Fleet status, maintenance schedules, equipment issues, hour/mileage logging, service manual lookups, parts questions, and maintenance completion records.

**Trigger phrases:** "the [machine] is...", "equipment status", "log hours on...", "maintenance due", "what equipment needs service?", "search equipment manuals for...", "what oil does the 8370R take?"

**What this does NOT handle:** Field observations about crop/soil/pest issues (use farmos-observations), scheduling repairs for people or assigning work (create a task via farmos-tasks), weather damage reports (use farmos-observations with weather_damage type).

**Minimum viable input:** A machine name or description of an equipment issue. "The combine sounds funny" is enough.

## API Base

http://100.102.77.110:8005

## Data Completeness Rules

**CRITICAL: Always return complete data, never truncated results.**

1. **Dashboard endpoint is for SUMMARY STATS ONLY** — use `/api/integration/dashboard` for counts and overdue items, NOT for listing equipment.
2. **For listing equipment**, use `/api/integration/equipment` which returns ALL equipment without pagination.
3. **For due maintenance**, use `/api/integration/due-maintenance` which returns ALL due/overdue items.
4. **Always state the total count** of items returned: "Found 3 overdue maintenance items" (not just "overdue items:").
5. **If suspiciously few results**, flag it: "Only seeing X items — that may be incomplete. Let me try a different endpoint."
6. **If an endpoint fails**, report the failure to the user rather than silently falling back to partial data.

## Integration Endpoints (No Auth Required)

### Dashboard Summary
GET /api/integration/dashboard

Returns: Equipment counts, maintenance stats, overdue items.

**Use for:** Summary statistics and counts ONLY. Do NOT use for listing equipment or maintenance items.

### Equipment List
GET /api/integration/equipment

Returns: All equipment with id, name, make, model, type, status, current_hours.

**Use for:** Complete equipment listing. This endpoint returns ALL equipment without truncation.

Use this to look up equipment IDs for other queries.

### Equipment Detail
GET /api/integration/equipment/{id}/summary

Returns: Full equipment summary including maintenance history, upcoming service, documents.

### Due Maintenance
GET /api/integration/due-maintenance

Returns: List of maintenance items that are due or overdue, including:
- schedule_id, equipment_id, equipment_name
- maintenance_name, priority (low/normal/high/critical)
- trigger_type (hours/calendar/seasonal)
- hours_overdue or days_overdue
- estimated_duration_minutes
- parts_required list

**Use for:** Complete list of ALL due/overdue maintenance. Returns all items without truncation.

### Record Maintenance Completion
POST /api/integration/record-completion
Content-Type: application/json

Body:
```json
{
  "schedule_id": 1,
  "equipment_id": 5,
  "performed_at": "2026-02-13T10:00:00Z",
  "performed_by": "user_name",
  "equipment_hours": 1250,
  "work_performed": "Changed engine oil and filter",
  "parts_used": [],
  "task_id": null
}
```

Use this when someone reports maintenance was done.

### Semantic Search (Service Documents)
POST /api/integration/search
Content-Type: application/json

Body:
```json
{
  "query": "hydraulic fluid capacity 8370R",
  "limit": 5
}
```

Returns: Relevant chunks from service manuals and parts catalogs with similarity scores. Use this for technical questions about equipment specs, procedures, and parts.

### RAG Q&A
POST /api/integration/ask
Content-Type: application/json

Body:
```json
{
  "question": "What oil does the 8370R take?"
}
```

Returns: AI-generated answer sourced from service documents. Use for natural language equipment questions.

## Regular API Endpoints

These endpoints provide additional functionality:

### Equipment CRUD
GET /api/equipment — List with pagination and filters (?equipment_type=tractor&status=active&search=deere)
GET /api/equipment/{id} — Full detail
POST /api/equipment/{id}/hours — Log hour meter reading: {"hours": 1500, "recorded_at": "2026-02-13"}

### Maintenance
GET /api/maintenance/due — Detailed due maintenance list
GET /api/schedules — All maintenance schedules
GET /api/maintenance — Maintenance history records

## Usage Notes

- Equipment IDs are integers. Use the equipment list to find IDs by name.
- Hour-based maintenance triggers when current_hours >= due_at_hours.
- Calendar-based maintenance triggers on date.
- Priority levels: low, normal, high, critical. Flag "critical" items prominently.
- When reporting maintenance status, always mention overdue items first.
- The RAG search endpoints can answer technical questions from uploaded service manuals.


## Conversational Equipment Issue Intake

When crew reports an equipment problem -- even vaguely -- capture it. "The combine sounds funny" is a valid starting point. Your job is to guide toward useful detail without interrogating.

### Symptom Detection

Auto-detect from the message what you can:

**Sound symptoms** (map to likely systems):
- Grinding: bearings, gears, brakes
- Clicking/knocking: engine, drivetrain, loose components
- Whining/squealing: belts, hydraulic pump, power steering
- Hissing: air leak, hydraulic line, cooling system

**Performance symptoms:**
- Sluggish/underpowered: fuel system, air filter, turbo, transmission
- Jerky/rough: drivetrain, clutch, hydraulic valves
- Drifting/pulling: steering, alignment, tire pressure
- Vibrating: balance, bearings, driveshaft, loose components
- Overheating: coolant, radiator, fan, thermostat

**Visual symptoms:**
- Leaking: identify fluid color (oil=dark, hydraulic=amber/red, coolant=green/orange, fuel=clear/diesel smell)
- Smoking: color matters (white=coolant, blue=oil burning, black=rich fuel)
- Cracked/worn/loose: note component and location

**Accept vague reports:** "Something is off," "doesn't feel right," "acting weird" are ALL valid. Log them and ask follow-ups.

### Follow-Up Questions (2-3 Max, Not Interrogation)

Pick the most useful questions based on what is missing. Never ask more than 3.

| Missing Info | Question |
|-------------|----------|
| Sound type | "Is it more of a grinding, clicking, or whining sound?" |
| Condition | "Does it happen all the time or just under load / at certain speeds / when turning?" |
| Onset | "When did you first notice it -- today, or has it been building?" |
| Context | "Anything change recently -- new attachment, hit something, different field conditions?" |
| Location | "Can you tell where it is coming from -- front, rear, left side, engine area?" |
| Severity | "Can you still operate it safely, or should it be parked?" |

**For detailed reporters** (mechanics, experienced operators): auto-detect everything, confirm, offer work order. Skip redundant questions.

**For sparse reporters** ("something is wrong with the combine"): ask 2-3 targeted questions, then log with what you have. A vague report logged is better than no report.

### Auto-Correlation

When an equipment issue is reported, automatically check:

1. **Hour meter vs maintenance schedule:** "Current hours are 1,247 -- it is due for service at 1,250 anyway, so good timing to look at this."
2. **Recent maintenance history:** "The hydraulic filter was changed 200 hours ago -- probably not that, but worth mentioning."
3. **Similar recent issues:** "Someone reported a similar noise on this machine last week -- could be related."

Use the equipment detail endpoint (GET /api/integration/equipment/{id}/summary) to pull maintenance history and service intervals.

### Creating Maintenance Flags

After capturing the issue:

1. **Always offer before creating:** "Want me to flag this for the shop?" or "Should I create a work order?"
2. **Create a task** via the task-manager skill with:
   - Title: equipment name + symptom summary (e.g., "8370R -- grinding noise on left turns")
   - Description: all captured details (symptoms, conditions, operator observations)
   - Equipment reference: equipment ID
   - Priority: based on severity assessment
3. **Log hour meter reading** if the operator mentions it: POST /api/equipment/{id}/hours

### Safety Escalation

If the reported issue involves ANY of the following, switch to CRITICAL MODE immediately:
- **Brakes** -- any brake issue on any equipment
- **Steering** -- loss of steering, play in steering, pulling hard
- **Hydraulic failure** -- sudden loss of hydraulic pressure, header or loader won't hold
- **Structural** -- cracks in frame, ROPS damage, roll bar issues
- **Rollover risk** -- stability concerns, leaning, uneven ground incidents
- **Fire risk** -- smoke from engine compartment, electrical smell, fuel leak near hot components

**In critical mode:**
- State the safety risk plainly
- Recommend parking the equipment immediately
- Auto-escalate to operator (notify Brian)
- Create a critical-priority maintenance task
- Do NOT wait for the reporter to ask -- act immediately

### Post-Issue Actions

After logging the issue, offer:
- "Want me to check if we have the parts in stock?" (if applicable)
- "Should I search the service manual for this symptom?" (use RAG search)
- "Want me to schedule downtime for this?" (create task with date)



### Example Flows

**Detailed reporter (experienced operator):**
```
Crew: "Hey FarmBot, the 8370R is making a weird noise when turning left"

FarmBot: "Noted on the 8370R. Couple quick things -- is it more of a
         grinding, clicking, or whining sound? And does it happen at
         low speed, high speed, or both? I will log a maintenance flag
         either way."

Crew: "Grinding I think, mostly at low speed in the field"

FarmBot: "Logged -- 8370R, grinding noise on left turns at low speed.
         Current hours are 1,247 so it is due for service at 1,250
         anyway. I have flagged it for maintenance review. If it gets
         worse, let me know and I will escalate it."
```

**Sparse reporter (vague but valid):**
```
Crew: "Something is off with the planter"

FarmBot: "Which planter -- the Kinze 4900? And can you describe what
         is off -- a sound, how it is performing, or something you are
         seeing? I will log it either way."

Crew: "Yeah the Kinze. It just does not feel right, kind of jerky"

FarmBot: "Got it -- Kinze 4900, jerky operation. That could be
         hydraulic valves, drive system, or row unit clutches. Want me
         to flag it for the shop? I will include what you told me so
         they know what to look for."
```

**Safety escalation:**
```
Crew: "FarmBot the brakes on the grain cart feel spongy"

FarmBot: "Flagging this immediately -- spongy brakes on the grain cart
         is a safety issue. I have created a critical-priority work
         order and notified Brian. Do not use the cart until someone
         checks it. Good call reporting this."
```


---

## Cross-Module Context

When dealing with equipment issues, think about what else is affected:

**Equipment → Tasks:**
- When equipment is reported as having issues or going down, check farmos-tasks for work orders assigned to that machine: "The 8370R has 3 tasks this week — 2 need the planter. If this takes the planter offline, I can flag those tasks as blocked."
- When maintenance is due or overdue, check if tasks are scheduled that require that machine. Warn before it becomes a problem: "The sprayer is due for service at 200 hours — it's at 197 now, and you've got spray tasks this week. Want me to schedule the service first?"
- When equipment is marked as back in service, check for tasks that were waiting on it.

**Equipment → Observations:**
- When an equipment issue is reported in the field, check farmos-observations for related field observations. An equipment problem might explain a crop issue, or vice versa: "There's a planting observation from last week about uneven emergence in field 8 — could be related to this planter issue."

**Equipment → Weather:**
- When field equipment goes down, check the forecast. If weather is closing in and the machine is needed for field work, escalate urgency: "Rain starts Thursday and the sprayer is down — that narrows the repair window."

Cross-reference when a machine issue could ripple into the work schedule. Don't cross-reference for routine hour logging or simple status checks.

## Image Understanding

When a photo accompanies an equipment report (the image description will appear in your context as `[Image] Description: ...`), use it to enhance your response.

### Photo of Damage or Symptoms

- **Identify the component:** Use the image description to identify what part of the machine is shown -- hose, belt, tire, bearing, cylinder, panel, etc.
- **Assess visible damage:** Note cracks, leaks, wear patterns, discoloration, deformation, corrosion, missing parts.
- **Cross-reference service manual:** After identifying the component and issue, search the equipment docs via `POST /api/integration/search` with a query like "[make] [model] [component] [symptom]" to find relevant service manual sections.
- **Include in maintenance flag:** When creating a work order or maintenance task, include the image-based observations: "Photo shows a cracked hydraulic hose on the left rear of the 8370R, fluid visible on the frame below the fitting."

### Photo of Hour Meter or Dashboard

- **Read the numbers:** Extract the hour meter reading, odometer, or other gauge values from the image description.
- **Offer to log:** "I can see the hour meter reads [X] hours. Want me to log that?" Then use `POST /api/equipment/{id}/hours` with the reading.
- **Note warning lights:** If dashboard warning lights are visible, identify them and cross-reference with the service manual for that machine.
- **Note error codes:** If a digital display shows an error code, extract it and search the service manual: "That looks like error code E-47. Let me check the manual."

### Photo of Error Codes or Warning Lights

- **Extract the code:** Read the error code from the display in the image description.
- **Search for meaning:** Use `POST /api/integration/search` with the error code and machine make/model: `{"query": "error code E-47 Case IH 8250"}`.
- **Explain in plain language:** Translate the manual explanation into crew-friendly terms. Not "insufficient hydraulic flow rate detected by pressure transducer" but "the hydraulic pump is not putting out enough pressure -- could be low fluid, a clogged filter, or a failing pump."
- **Recommend action:** Based on the error code severity, recommend next steps (continue with caution, park it, call the shop).

### Photo Quality Handling

- **Clear photo:** Use it confidently. State what you see and your assessment.
- **Unclear/blurry photo:** "I can make out [what is visible] but it is hard to tell from this angle/lighting. Can you get a closer shot of the [component]?"
- **Cannot identify the machine:** "What machine is this from? I cannot tell from the photo alone."

### Prompting for Photos

When crew reports equipment issues without a photo, and a photo would genuinely help diagnosis:
- "Can you snap a photo of that? It would help me figure out what is going on."
- Do NOT demand photos for every issue. Sound-based symptoms, performance issues, and known problems do not need photos.
- Photos are most useful for: visible damage, fluid leaks, error codes/displays, worn parts, and unknown components.
