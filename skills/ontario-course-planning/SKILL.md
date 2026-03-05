---
name: ontario-course-planning
description: Ontario (Canada) high school course planning (Grades 9–12) aligned to university admissions and Top 6 (12U/M) strategy. Use to: analyze prerequisites + Top 6 composition for one or multiple target universities/programs (e.g., Waterloo CS, UofT CS, Engineering); generate or iteratively update a 4‑year plan under OSSD graduation requirements, school timetable/selection rules, and summer school constraints (max 1 course/year); and revise the plan when the user updates rules, summer school offerings, or the school course catalog.
---

# Goal
Produce an **iterable, updatable** Ontario (OSSD) Grades 9–12 course plan that:
- Meets graduation requirements, school course-selection rules, and online-learning requirements
- Meets each target university/program’s **prerequisites** and common **Top 6 (12U/M)** counting patterns
- Optimizes the schedule based on user priorities (e.g., protect Grade 11/12 workload, front-load difficulty to Grade 9/10, disallow summer school, prefer easier electives for average)

# Before you plan: required inputs (ask if missing)
Ask the minimum number of questions needed to fill these. If something is unknown, label it **ASSUMPTION**.

## A) Targets (support multiple)
Record targets in working memory in this structure:
- Targets:
  - University: <name>
    Program: <program name>
    Campus/Faculty: <optional>
    Notes: <co-op? competitiveness?>

If the user says only “robotics/engineering”, ask whether they mean **Engineering** (e.g., Mechatronics/Computer/Electrical) vs **CS/Math**, and whether co-op matters.

## B) Student + school constraints
- Current grade; completed / in-progress courses (if not starting from Grade 9)
- Special programs: French Immersion / IB / AP / etc.
- Whether the school allows: taking 12U early, cross-grade enrolment, spares in Grade 12, etc.
- Timetable constraints: typically 8 courses/year (4+4). Confirm whether 7-course years are allowed.

## C) Planning priorities (must be editable)
Keep as toggles/weights:
- Workload distribution:
  - `pressureFocus`: "frontload" | "balanced" | "protect_11_12"
- Summer school:
  - `summerSchool.enabled`: true/false
  - `summerSchool.maxPerYear`: 1 (default)
  - `summerSchool.useFor`: "nonTop6" | "reachAhead" | "repeatImprove" (default: nonTop6)
- Grades/average strategy:
  - `maximizeAverage`: true/false
  - `preferEasierElectives`: true/false
- Risk tolerance:
  - `planRobustness`: "conservative" | "normal" | "aggressive"

# Workflow (generate or update a plan)

## Step 1 — Build the rule baseline (read references)
Read and apply:
- `references/graduation-and-planning-rules.md`
- `references/summer-school-catalog.md`
- `references/required-bands-by-grade.md`
- `references/course-catalog.md`

If the user provides new rules or new lists:
- Do **not** overwrite the files in-place during the chat.
- Clearly list what changed, and recommend writing the changes back into the appropriate references file (see “Maintenance & updates”).

## Step 2 — For each target, derive prerequisites + Top 6 logic
For each (University, Program), produce:
- Likely hard prerequisites (e.g., ENG4U, MHF4U, MCV4U, SPH4U, SCH4U)
- Typical Top 6 (12U/M) composition patterns for that program

If prerequisites are uncertain:
1) Provide a **conservative default** for that program family (CS vs Engineering)
2) List what must be verified and provide web_search keywords/links the user can check

## Step 3 — Schedule the 4-year plan
Objectives:
- Grade 9–11: satisfy “8 courses per year” rule if applicable
- Respect prerequisite chains while distributing workload
- If `protect_11_12`: avoid stacking multiple heavy 3U/4U courses in Grade 11/12
- If summer school is enabled and `useFor=nonTop6`: prioritize non-Top6 / non-admissions-impact courses (often Civics/Careers) to reduce timetable load

Planning method:
- Lock Grade 12 Top 6 candidate pool (>= 6 courses; ideally 7–8 for replacement)
- Back-plan prerequisites:
  - MHF4U/MCV4U usually require Grade 11 MCR3U
  - 4U sciences usually require corresponding 3U sciences
  - CS/Engineering interest: consider ICS/TEJ/TDJ pathways where available

## Step 4 — Standardized output (required)
Output must follow this structure (do not omit sections):

### 1) Targets & assumptions
- Target universities/programs (multiple allowed)
- Active priorities config (pressureFocus, summerSchool, etc.)
- Key assumptions / items to confirm

### 2) Prerequisites + Top 6 summary (by target)
For each target:
- Prerequisite list
- Two Top 6 options (e.g., low-pressure vs high-relevance; conservative vs stretch)
- Risks and substitutes

### 3) 4-year course plan (by grade)
For each grade:
- Course list with: course name + code + course type (D/P/U/M/O/W/etc.) + whether it counts toward the **17 compulsory** vs **13 elective** credits
- End-of-year cumulative credits: total / compulsory / elective
- Rationale for that year (prereqs + workload distribution + average strategy + interests)

### 4) Validation checklist
- Graduation requirements met (17 compulsory, 13 elective, 2 online courses, etc.)
- Prereqs met for each target
- Grade 12 overload check (if user dislikes “overload/extra credits”, propose alternatives)

# Maintenance & updates (must support)
When the user asks to modify/update anything:

1) Identify which bucket changed:
- Rules: graduation/online requirement, yearly course count, summer school limits
- Summer school: offerings, cancellations, whether a course may be used for Top 6
- Course catalog: add/remove/rename courses, codes, grade availability
- Priorities: pressureFocus, summer school on/off, risk tolerance

2) Apply **minimal-change** updates:
- Mark impacted grades/courses
- Provide before/after diffs
- Recalculate cumulative credits and Top 6 options

3) If the user agrees, recommend persisting updates into references:
- `references/graduation-and-planning-rules.md`
- `references/summer-school-catalog.md`
- `references/course-catalog.md`

# Quality rules (hard)
- Never present uncertain items as facts; label them “TO VERIFY”.
- Course codes must come from `references/course-catalog.md` unless the user explicitly adds new ones.
- Output must include cumulative credits (total/compulsory/elective) and consistent classification.
