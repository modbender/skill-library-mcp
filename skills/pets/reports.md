# Report Generation

## Report Types

### Quick Summary
"How's Luna doing?"
- Last 7 days highlights
- Notable incidents or wins
- Training progress
- Upcoming reminders

### Period Report
"Luna's month" / "2024 year in review"
- Incident breakdown by type
- Training milestones achieved
- Behavior trends (improving/stable/concerning)
- Memorable moments
- Routine adherence

### Behavior Analysis
"Why is Luna peeing inside?"
- Filter logs for relevant incidents
- Identify patterns (time, context, triggers)
- Correlate with changes (schedule, environment)
- Suggest investigation areas (NOT diagnose)

### Training Progress
"How's Luna's training going?"
- Commands mastered vs in progress
- Success rate trends
- Recent breakthroughs
- Current focus areas

---

## Report Structure

### Weekly Summary Template
```markdown
## [Pet Name] — Week of [Date]

### Highlights
- [Notable positive events]

### Incidents
- [Count] total: [breakdown by type]
- [Pattern observations if any]

### Training
- Working on: [current commands]
- Progress: [improvements noted]

### Coming Up
- [Scheduled reminders, appointments]
```

### Monthly Summary Template
```markdown
## [Pet Name] — [Month Year]

### Overview
[1-2 sentence summary of the month]

### By the Numbers
- Incidents: [count] (vs [last month])
- Training sessions: [count]
- Vet visits: [count]
- Memorable moments logged: [count]

### Behavior Trends
[Improving/stable/concerning for key areas]

### Training Progress
- Mastered this month: [list]
- In progress: [list]

### Memorable Moments
[Top 3-5 highlights]

### Looking Ahead
[Upcoming milestones, goals, appointments]
```

---

## Analyzing Logs

When generating reports:

1. **Load log.jsonl** for requested pet and period
2. **Count by type:** incident, win, moment, training, health
3. **Count by tags:** Most common tags reveal focus areas
4. **Compare periods:** This month vs last month
5. **Identify trends:** Increasing, decreasing, stable
6. **Surface patterns:** Time of day, day of week, context correlations
7. **Highlight outliers:** Unusual events worth noting

---

## Multi-Pet Reports

For households with multiple pets:
- Individual sections per pet
- Comparison where relevant (both dogs' training progress)
- Household-level observations (pets getting along, resource conflicts)
- Combined calendar of upcoming events

---

## Presenting Reports

- **Casual request:** Conversational summary, key points only
- **"Give me a report":** Structured format, comprehensive
- **Specific question:** Focused analysis on that topic only
- **Shareable version:** Clean format suitable for partner/family
