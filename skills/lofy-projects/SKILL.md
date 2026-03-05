---
name: lofy-projects
description: Project management for the Lofy AI assistant — tracks multiple projects with milestones, priority scoring engine (urgency × job relevance × momentum × energy match), meeting prep automation, time logging, stale project alerts, and work session recommendations. Use when managing projects, prioritizing work, preparing for meetings, or tracking milestones and deadlines.
---

# Project Pilot — Project & Academic Manager

Keeps projects, coursework, and research organized. Tracks status, deadlines, blockers, and helps prioritize work time.

## Data File: `data/projects.json`

```json
{
  "projects": {
    "example_project": {
      "name": "Example Project",
      "status": "active",
      "phase": "Phase 1",
      "description": "",
      "stack": [],
      "milestones": [
        { "name": "Milestone 1", "status": "in_progress", "target_date": null }
      ],
      "blockers": [],
      "next_actions": [],
      "time_log": [],
      "last_updated": null,
      "job_relevance": "high"
    }
  },
  "academic": { "graduation": null, "deadlines": [], "meetings": [] }
}
```

## Priority Engine

When user asks "what should I work on?":

```
Priority = (Urgency × 3) + (Job_Relevance × 2) + (Momentum × 1) + (Energy_Match × 1)

Urgency (0-5): 5=due today, 4=48h, 3=this week, 2=this month, 1=no deadline, 0=backlog
Job_Relevance (0-5): 5=critical, 4=high, 3=medium, 2=portfolio, 1=low, 0=none
Momentum (0-3): 3=active progress, 2=touched last 3 days, 1=stale 1-2 weeks, 0=cold 2+ weeks
Energy_Match (0-2): 2=matches current energy, 1=neutral, 0=mismatch
```

### Time-Based Recommendations
- **< 30 min:** Quick tasks — email, review, read, update docs
- **30-60 min:** Medium — write one function, prep notes, apply to 1 job
- **1-2 hours:** Focused — implement a feature, write paper section, debug
- **2+ hours:** Deep work — major development sessions

## Meeting Prep

When a meeting is detected:
1. Identify related project
2. Pull recent time_log entries since last meeting
3. List current blockers
4. Generate 2-3 questions to ask
5. Suggest what to demo/present
6. Send prep 2 hours before

## Status Updates via Natural Language

- "Worked on [project] for 2 hours" → update time_log, last_updated
- "[Feature] is working now" → update milestone status
- "Stuck on [issue]" → add to blockers
- "Meeting moved to Thursday" → update meetings

## Instructions

1. Always read `data/projects.json` before responding about projects
2. Update JSON after any project conversation
3. For "what should I work on?" — ONE clear recommendation + one alternative
4. Flag stale projects: "[Project] hasn't been touched in X days"
5. Before meetings, proactively send prep
6. Prioritize job-critical projects unless there's a deadline override
