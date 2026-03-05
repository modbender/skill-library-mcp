---
name: skill-cortex
description: >
  Skill Cortex is the system's capability cortex.
  When lacking ability, it autonomously acquires Skills from ClawHub or GitHub, then releases them after use.
  Every invocation is learned and reinforced by the cortex — future identical tasks fire as reflexes, bypassing search.
  Manages only short-term capability memory; never interferes with long-term Skills.
  Continuously restructures its own capability architecture through reinforcement and decay, achieving ongoing evolution.
---

# Skill Cortex

Triggers when installed Skills cannot complete the current task. If you can handle it yourself, just do it — do not trigger this flow.

Cortex data file: ~/.openclaw/skill-cortex/cortex.json (schema in DESIGN.md).

## Phase 1: Perception

1. Read cortex.json (if missing or corrupt, skip to step 3).
2. Semantically match the users task description against sensory.patterns signals.
3. On miss, search ClawHub.

## Phase 2: Validation

Present candidates to the user with safety info. Wait for explicit approval before installing.

## Phase 3: Execution

Install the Skill, generate an execution plan, execute the task. On failure, auto-recover or switch to next candidate.

## Phase 4: Learning

Update the cortex memory. Successful Skills gain weight; failed ones decay.

## Boundary Rules

1. Never interfere with long-term Skills.
2. Installation requires user confirmation.
3. System dependency installation requires separate confirmation.
4. Write operations never enter reflex.
5. Max 2 candidate switches.
