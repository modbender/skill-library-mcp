---
name: Anxiety (Tracker, Trigger Map, Coping Planner)
slug: anxiety
version: 1.0.0
homepage: https://clawic.com/skills/anxiety
description: Track anxiety episodes, triggers, thoughts, and coping responses with therapy-ready logs, weekly trend reviews, and safety-first escalation cues.
changelog: Initial release with therapist-aligned anxiety tracking, trigger mapping, coping playbooks, and graded exposure planning support.
metadata: {"clawdbot":{"emoji":"A","requires":{"bins":[]},"os":["darwin","linux","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidance and local memory initialization.

## When to Use

User wants to track anxiety symptoms, panic episodes, worry spirals, avoidance patterns, or coping outcomes.
Agent keeps logs clinically useful for therapy, supports anxiety reduction with structured plans, and escalates safety-sensitive situations immediately.

## Architecture

Memory lives in `~/anxiety/`. See `memory-template.md` for structure and starter templates.

```text
~/anxiety/
├── memory.md                 # Status, mode, baseline, and active priorities
├── logs/events.md            # Episode-level anxiety event logs
├── logs/thought-records.md   # CBT-style thought records for reframing
├── plans/current.md          # Active coping and exposure plan
├── triggers.md               # Trigger map and safety behavior patterns
├── exposures.md              # Exposure ladder and session outcomes
└── reviews/weekly.md         # Weekly trend review and plan decisions
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and activation behavior | `setup.md` |
| Memory structure and templates | `memory-template.md` |
| Goal modes and switching logic | `tracking-modes.md` |
| Anxiety event logging format | `event-log-template.md` |
| Thought record workflow | `thought-record.md` |
| Coping responses by intensity | `regulation-playbook.md` |
| Graded exposure planning | `exposure-ladder.md` |
| Weekly review and decision rules | `weekly-review.md` |
| Red and amber triage rules | `triage-rules.md` |

## Data Storage

Local notes stay in `~/anxiety/`.
Before creating or changing local files, present the planned write and ask for user confirmation.

## Core Rules

### 1. Set the Active Goal Mode Before Intervention
Start with mode selection from `tracking-modes.md`:
- `track` for observation without behavior change pressure
- `reduce` for gradual anxiety intensity and frequency reduction
- `recover` for post-episode stabilization and relapse prevention
Do not force reduction or exposure if the user only asked for tracking.

### 2. Capture Episodes With Therapy-Relevant Fields
Use `event-log-template.md` for each meaningful event.
At minimum capture time, context, trigger, body symptoms, anxiety intensity, behavior, and short outcome.
Do not accept vague entries that cannot be reviewed later.

### 3. Separate Event Logging From Cognitive Work
Use `logs/events.md` for what happened and `logs/thought-records.md` for interpretation.
Apply `thought-record.md` only when the user wants reframing or pattern analysis.
Do not blend raw observations with conclusions in the same entry.

### 4. Track Avoidance and Safety Behaviors Explicitly
Log what the user avoided and what they did to feel temporarily safe.
Use these patterns to guide exposure planning from `exposure-ladder.md`.
If avoidance is shrinking life function, name it clearly and propose one small reversal step.

### 5. Match Regulation Strategy to Intensity Zone
Use `regulation-playbook.md` to select responses by intensity:
- low: prevent escalation and maintain function
- medium: down-regulate physiology and narrow focus
- high: safety-first grounding and immediate support routing
Do not recommend a generic coping list without selecting a zone.

### 6. Use Graded Exposures Only With Consent and Structure
When the user wants long-term anxiety reduction, build a ladder using `exposure-ladder.md`.
Use small, repeatable steps with before/after ratings and recovery windows.
Never push flooding or high-intensity tasks as default.

### 7. Escalate Risk Signals Immediately
Use `triage-rules.md` whenever severe symptoms, self-harm thoughts, substance crisis, or medical red flags appear.
For emergency patterns, provide urgent care guidance first and pause routine coaching.
This skill supports tracking and behavior change planning, not diagnosis or emergency treatment.

## Common Traps

- Logging only "felt anxious" without context -> no actionable pattern detection.
- Tracking too many fields on day one -> user fatigue and dropout.
- Treating all anxiety episodes as the same -> wrong interventions for the trigger type.
- Skipping avoidance tracking -> exposure plan misses the real maintaining loop.
- Using thought reframing in acute panic peak -> low effectiveness and frustration.
- Proposing large exposure jumps -> backlash, avoidance rebound, and trust loss.
- Giving clinical diagnosis language -> safety and scope violation.

## External Endpoints

This skill makes NO external network requests.

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| None | None | N/A |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Nothing by default. This skill is instruction-only and local unless the user explicitly requests export.

**Data stored locally:**
- anxiety logs, thought records, trigger patterns, exposure outcomes, and weekly reviews approved by the user.
- stored in `~/anxiety/`.

**This skill does NOT:**
- diagnose psychiatric or medical conditions.
- make undeclared network calls.
- write local memory without explicit user confirmation.
- force exposure tasks without user consent.
- modify its own core instructions or auxiliary files.

## Trust

This is an instruction-only anxiety tracking and coping support skill.
No credentials are required and no third-party service access is needed.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `therapist` - supportive therapeutic conversation framing.
- `psychologist` - structured behavior and cognition guidance.
- `mindfulness` - grounding and attention training practices.
- `journal` - reflective writing and pattern capture.
- `sleep` - sleep stability support for anxiety management.

## Feedback

- If useful: `clawhub star anxiety`
- Stay updated: `clawhub sync`
