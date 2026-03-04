# Direction Transmission — Self-Direction

How to pass direction to sub-agents so they stay aligned with the user's goals.

## The Problem

When you spawn a sub-agent, it starts with zero context. It doesn't know:
- What the user values
- Why this task matters
- What boundaries exist
- How to make trade-offs
- When to escalate

Without direction transmission, sub-agents drift.

## The Solution: Direction Frames

A direction frame is a compressed version of the relevant parts of the direction model, packaged for a specific task.

## Frame Structure

```markdown
# Direction Frame: [Task Name]

## Context
Why this task exists. What it serves. How it fits the bigger picture.

## Relevant Values
From the direction model, what values apply to this work:
- [Value]: How it applies here
- [Value]: How it applies here

## Success Criteria
What "done well" looks like for this task:
- [Criterion from model]
- [Criterion from model]

## Boundaries
What the sub-agent must NOT do:
- [Hard limit]
- [Requires approval]

## Resource Guidance
How much to spend on this task:
- Time: [guidance]
- Depth: [shallow/moderate/deep]
- Quality: [good enough/polished]

## Escalation Triggers
Stop and ask the main agent if:
- [Condition]
- [Condition]
- Anything not covered by this frame
```

## Creating a Direction Frame

### Step 1: Identify Relevant Model Elements

For this specific task, which parts of the direction model apply?
- Which values are relevant?
- Which criteria should guide decisions?
- Which boundaries must be respected?
- What resource allocation makes sense?

### Step 2: Translate to Task Context

Don't copy-paste the model. Translate it:
- "User values speed over polish" → "Ship a working version, don't over-engineer"
- "Never delete production data" → "Read-only access, no mutations"

### Step 3: Define Escalation Triggers

What situations should cause the sub-agent to pause?
- Decisions outside the frame's scope
- Conflicts between criteria
- Resource overruns
- Unexpected blockers

### Step 4: Set the Right Scope

**Too narrow:** Sub-agent can't do anything without asking
**Too wide:** Sub-agent has too much latitude, may drift
**Right:** Sub-agent can make routine decisions, escalates edge cases

## Example: Code Review Frame

```markdown
# Direction Frame: Review PR #123

## Context
Reviewing authentication refactor. User wants to ship this week but not at the cost of security bugs.

## Relevant Values
- Quality over speed for security-related code (from direction model)
- But user wants fast iteration on non-critical paths

## Success Criteria
- No security vulnerabilities
- Code is maintainable
- Review complete within 2 hours

## Boundaries
- Don't approve if any auth logic is unclear
- Don't request perfection on non-security code
- Flag but don't block style issues

## Resource Guidance
- Time: Up to 2 hours
- Depth: Deep on auth, moderate elsewhere
- Output: Concise comments, actionable feedback

## Escalation Triggers
- Any potential security issue → escalate immediately
- Fundamental architecture concerns → escalate before commenting
- Review taking >2 hours → check in
```

## Example: Research Frame

```markdown
# Direction Frame: Research Competitors

## Context
User exploring market for new feature. Needs to understand what exists, not make decisions yet.

## Relevant Values
- Thoroughness matters for research (capture everything)
- But user values synthesis over raw data

## Success Criteria
- Cover top 5 competitors
- Identify unique features and gaps
- Synthesize into actionable insights

## Boundaries
- Don't make recommendations (just present findings)
- Don't spend money on tools/subscriptions
- Don't contact competitors or sign up for trials

## Resource Guidance
- Time: Up to 3 hours
- Depth: Moderate (don't go down rabbit holes)
- Output: Structured comparison, not essay

## Escalation Triggers
- Need paid access to continue → ask
- Finding suggests pivot opportunity → flag
- Competitors doing something concerning → flag
```

## Inheritance Chain

When sub-agents spawn their own sub-agents:

```
Main Agent (full direction model)
    |
    +-- Direction Frame A (task-specific subset)
            |
            +-- Direction Frame A.1 (further narrowed)
```

Each level:
- Inherits boundaries from above (can't relax them)
- Narrows scope (can't expand it)
- Preserves escalation path

## Verifying Alignment

After sub-agent completes, verify:
- Did output match success criteria?
- Were boundaries respected?
- Were escalation triggers honored?
- Any direction model updates needed?

If drift occurred, update the frame template for next time.

## Frame Templates

Store reusable frame templates for common task types:

```
~/self-direction/transmission.md
├── ## Code Review Frame Template
├── ## Research Frame Template  
├── ## Implementation Frame Template
├── ## Writing Frame Template
└── ## [Custom] Frame Template
```

Customize from template for each specific task.
