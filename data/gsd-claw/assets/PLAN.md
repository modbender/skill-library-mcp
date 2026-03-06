---
phase: [N]
plan: [N]
wave: [1]
depends_on: []
autonomous: true
---

# Phase [N] Plan [N]: [Name]

## Objective
[What this plan accomplishes]

## Context
[Reference to CONTEXT.md decisions that apply]

## Tasks

<task type="auto">
  <name>Task 1: [Action-oriented name]</name>
  <files>[file paths affected]</files>
  <action>
    [Specific instructions]
    [What to avoid and WHY]
  </action>
  <verify>[Command or check to prove completion]</verify>
  <done>[Measurable acceptance criteria]</done>
</task>

<task type="auto">
  <name>Task 2: [Action-oriented name]</name>
  <files>[file paths affected]</files>
  <action>
    [Specific instructions]
  </action>
  <verify>[Verification command]</verify>
  <done>[Done criteria]</done>
</task>

<task type="checkpoint:verify">
  <name>Checkpoint: User Verification</name>
  <what-built>[Description of what was built]</what-built>
  <how-to-verify>
    1. [Step 1]
    2. [Step 2]
  </how-to-verify>
  <resume-signal>Say "approved" or describe issues</resume-signal>
</task>

## Verification
- [ ] [Overall verification check 1]
- [ ] [Overall verification check 2]

## Success Criteria
- [ ] [What "done" looks like for this plan]
