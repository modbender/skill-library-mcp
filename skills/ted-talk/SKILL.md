---
name: ted-talk
version: 1.0.2
description: Transform technical insights into full 40-50 minute TED-style talks with concrete examples and Q&A
author: Live Neon <hello@liveneon.ai>
homepage: https://github.com/live-neon/skills/tree/main/creative/ted-talk
repository: leegitw/ted-talk
license: MIT
tags: [creative, presentation, speaking, storytelling, teaching, synthesis, reflection, knowledge-transfer]
layer: creative
status: active
alias: ted
user-invocable: true
emoji: 🎤
---

# ted-talk (話)

Transform technical conversations and insights into full-length TED-style talks.
Creates comprehensive 40-50 minute presentations with hooks, concrete examples,
broader implications, and Q&A preparation.

**Trigger**: 明示呼出 (explicit invocation) or when deep technical insight emerges

**Core insight**: "The best technical talks don't just explain what — they reveal why
it matters, with examples concrete enough to apply and implications broad enough to inspire."

## Installation

```bash
openclaw install leegitw/ted-talk
```

**Dependencies**: None (standalone creative skill)

**Data handling**: This skill synthesizes content from user-supplied input or the current
conversation context (default). It does NOT read files from the workspace or access project
artifacts directly. Results are returned to the invoking agent, who decides how to use them.

## What This Solves

Technical insights often stay trapped in conversations. A well-structured talk
makes them teachable and shareable. This skill:

1. **Expands** technical conversations into comprehensive narratives
2. **Grounds** abstract insights in concrete, real-world examples
3. **Prepares** for audience questions and objections

**The insight**: A 50-minute talk forces you to truly understand something — if you
can't explain the why, address objections, and connect to broader implications,
you don't fully understand it.

## Usage

```
/ted [topic]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| topic | No | Topic focus (default: synthesize current conversation) |

## Pre-Requisites

Before creating a TED talk, ensure:

1. **Sufficient conversation depth** — Surface-level topics make shallow talks
2. **Clear narrative arc** — Problem → Discovery → Solution → Impact
3. **Main work documented** — Save current progress first if mid-task
4. **Concrete context available** — Real problems, real decisions, real outcomes

### Context Understanding Checklist

You must be able to answer:

| Question | What It Means |
|----------|---------------|
| Core insight? | Not "we talked about X" but "we discovered X solves Y" |
| Problem solved? | The pain point, not just the topic |
| Why, not just what? | The reasoning, not just the outcome |
| Concrete examples? | Specific details from the context provided |
| Broader implications? | Why does this matter beyond the immediate context? |

### Red Flags (Don't Create)

- Surface-level summary of conversation
- Don't understand why a decision was made
- No concrete examples to draw from
- Insight doesn't have broader implications
- Would be padding the talk with generic content

## Output Format

### TED Talk Structure

```markdown
## TED Talk: "[Talk Title]"

### Opening (0:00-2:00)
[Hook with relatable problem]

### Setup: Why This Matters (2:00-6:00)
[Context, stakes, personal connection]

### The Problem (6:00-12:00)
[Deep dive into the pain point]

### Core Concept (12:00-25:00)
[Explain the insight thoroughly]

### Real-World Examples (25:00-38:00)
[Concrete applications with specifics]

### Broader Implications (38:00-45:00)
[Why this matters beyond immediate context]

### Closing (45:00-48:00)
[Call to action or reflection]

### Q&A Preparation (48:00-50:00)
[Common objections and responses]
```

### Talk Rules

| Rule | Description |
|------|-------------|
| Full 40-50 minutes | NOT a summary — comprehensive content |
| Hook with problem | Start with relatable pain, not abstract concept |
| Concrete examples | Specific, real details — not hypothetical scenarios |
| Address objections | Q&A section anticipates pushback |
| No filler | Every section should teach something |
| Accessible but not condescending | Technical depth without jargon overload |

### Example: Section Length Guide

| Section | Duration | Purpose |
|---------|----------|---------|
| Opening | 2 min | Hook with relatable problem |
| Setup | 4 min | Why this matters, stakes |
| Problem | 6 min | Deep dive into pain point |
| Core Concept | 13 min | The main insight, thoroughly explained |
| Examples | 13 min | Real-world applications |
| Implications | 7 min | Broader impact |
| Closing | 3 min | Call to action |
| Q&A Prep | 2 min | Objections and responses |

## Core Logic

### Step 1: Synthesize Conversation

- Read full conversation context
- Identify key decisions, "aha" moments
- Extract core insight or pattern
- Note concrete details from the context provided

### Step 2: Identify Narrative Arc

| Element | Question |
|---------|----------|
| Problem | What was broken/painful? |
| Discovery | What did we learn? |
| Solution | What pattern emerged? |
| Impact | Why does this matter? |

### Step 3: Expand to Talk

For each section:
- Opening: What relatable problem hooks the audience?
- Setup: Why should they care? What's at stake?
- Problem: Deep dive — make them feel the pain
- Concept: Explain thoroughly, with analogies if helpful
- Examples: Specific, concrete, from real work
- Implications: Connect to broader context
- Closing: What should they do with this knowledge?
- Q&A: What will skeptics ask?

### Step 4: Ground in Reality

TED talks resonate when they're specific, not hypothetical. Draw from:
- Real problems encountered (not abstract scenarios)
- Actual decisions and their reasoning
- Specific outcomes and what changed
- Stories with concrete details the audience can visualize

Use what the user provides — don't invent specifics or assume access to files.

## Example

### Input: Bootstrap Observability Insight

**Context**: Discovered reproduce-to-debug problem. Introduced Bootstrap → Learn → Enforce phases.

### Output Excerpt

**Title**: "Bootstrap Before You Break: Why Greenfield Systems Need to Learn What Normal Looks Like"

### Opening (0:00-2:00)

It's 3 AM. Your pager goes off. The system is on fire — users are complaining,
something is clearly wrong. You pull up your logs and... nothing. Metrics?
Flat lines. Traces? What traces?

You're debugging blind.

And the worst part? You built this system. You know every line of code.
But you have no idea what's happening.

This happened to me six months ago. And the solution we found changed how
I think about every system I'll ever build.

### Setup: Why This Matters (2:00-6:00)

We've all been taught: instrument your code, add logging, set up dashboards.
The standard advice works great — for existing systems.

But what about greenfield? What about day one?

Here's the thing nobody tells you: **you can't set meaningful thresholds
for a system that's never run in production.** What's a normal response time?
What's an acceptable error rate? You don't know. You can't know. The system
hasn't told you yet.

[... continues for full 50 minutes ...]

*Note: Full TED talk outputs are 40-50 minutes of content. This excerpt demonstrates the opening sections.*

### Q&A Preparation

**Q: "This seems like overkill for small projects."**

A: Fair point. The full three-phase approach is designed for systems where
debugging cost is high — production services, distributed systems, anything
where "just add a log line and redeploy" isn't an option. For a weekend
project, you probably don't need this. But the core insight — bootstrap
before you enforce — scales down too. Even a simple `log.Debug` everywhere
is a form of bootstrap phase.

**Q: "How long should the bootstrap phase last?"**

A: We found 7-14 days covers most patterns. You want at least one full
business cycle (weekly patterns), and ideally two. The key indicator is
when your anomaly detection stops alerting on normal behavior.

## Integration

- **Layer**: Creative
- **Depends on**: None (standalone)
- **Used by**: side-quests (combo skill)
- **Complements**: insight-song, visual-concept

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Insufficient context | Ask clarifying questions first |
| No concrete context | Ask for specific details before proceeding |
| Surface-level insight | Suggest deeper exploration first |
| No broader implications | Suggest finding wider relevance |

## Security Considerations

**Input sources:**
- User-supplied context (if provided)
- Current conversation context (default)

**What this skill does NOT do:**
- Read files from the workspace
- Access project artifacts directly
- Send data to external services
- Record or publish content

**Output behavior:**
This skill returns the full TED talk directly to the invoking agent. The agent can then
display, save, or pass the result to another skill as needed.

**Note on concrete details**: The skill uses only what the user provides in the conversation
or as explicit input. It does not access workspace files. Review output before sharing
externally to ensure no sensitive information is included.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Quality Checklist

- [ ] Can explain core insight in one sentence
- [ ] Opening hooks with relatable problem
- [ ] Full 40-50 minutes of substantial content
- [ ] Concrete details from provided context included
- [ ] Broader implications explored
- [ ] Q&A addresses likely objections
- [ ] No filler or generic padding
- [ ] Accessible to non-experts but not condescending

## Acceptance Criteria

- [ ] `/ted` synthesizes input or conversation into full-length talk
- [ ] Output includes all sections (opening through Q&A)
- [ ] Talk is 40-50 minutes of substantial content
- [ ] Concrete details from input/conversation included
- [ ] Q&A section addresses common objections
- [ ] Result returned to invoking agent

---

*Part of the Live Neon Creative Suite.*
