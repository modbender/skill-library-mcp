---
name: side-quests
version: 1.0.2
description: Full creative synthesis — combine song, visual concept, and TED talk from a single technical insight
author: Live Neon <hello@liveneon.ai>
homepage: https://github.com/live-neon/skills/tree/main/creative/side-quests
repository: leegitw/side-quests
license: MIT
tags: [creative, synthesis, songwriting, storytelling, ted-talk, visual-guide, reflection, knowledge-transfer, suno, learning]
layer: creative
status: active
alias: sq
user-invocable: true
emoji: 🎭
---

# side-quests (遊)

Full creative synthesis that combines all three creative artifacts from a single
technical insight: a Suno-ready song, a visual concept guide, and a full TED talk.

**Trigger**: 明示呼出 (explicit invocation) or when deep technical insight emerges

**Core insight**: "Context without action is paralysis. Action without context is chaos.
Side quests are context made actionable through creative synthesis."

## Installation

```bash
openclaw install leegitw/side-quests
```

**Dependencies**: None required, but works with component skills:
- `leegitw/insight-song` — Song component (can be used standalone)
- `leegitw/visual-concept` — Visual guide component (can be used standalone)
- `leegitw/ted-talk` — TED talk component (can be used standalone)

**Data handling**: This skill synthesizes content from user-supplied input or the current
conversation context (default). It does NOT read files from the workspace or access project
artifacts directly. Results are returned to the invoking agent, who decides how to use them.

## What This Solves

Technical insights fade with context compression. Multi-format creative synthesis
provides reinforcement through multiple channels:

1. **Song** — Audio reinforcement, emotional arc
2. **Visual concept** — Symbolic representation, visual metaphor
3. **TED talk** — Comprehensive narrative, concrete examples

**The insight**: Creation forces synthesis. Making creative artifacts about a concept
reveals gaps that passive understanding cannot. Audio + visual + narrative = deeper learning.

## Usage

```
/sq [topic]
```

Or use individual components:

```
/song [topic]    # Just the song
/vc [topic]      # Just the visual concept
/ted [topic]     # Just the TED talk
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| topic | No | Topic focus (default: synthesize current conversation) |

## Pre-Requisites

Before creating a side quest, ensure:

1. **Sufficient conversation depth** — Surface-level summaries don't make good artifacts
2. **Clear narrative arc** — Problem → Discovery → Solution → Impact
3. **Main work documented** — Save current progress first if mid-task

### Context Understanding Checklist

You must be able to answer:

| Question | What It Means |
|----------|---------------|
| Core insight? | Not "we talked about X" but "we discovered X solves Y" |
| Problem solved? | The pain point, not just the topic |
| Why, not just what? | The reasoning, not just the outcome |
| Substantial depth? | Teaches something new, not standard practice |

### Red Flags (Don't Create)

- Surface-level summary of conversation
- Don't understand why a decision was made
- Insight is just standard practice
- No clear narrative arc
- Would be padding with generic content

## Output Structure

Each side quest produces a single markdown file with three sections:

### 1. Song (Suno.ai Format)

```markdown
## Song

**Title**: [Song Name]

**Suno.ai Style Tags**:
[300-500 characters describing musical style]

[Verse 1]
[Lyrics]

[Chorus]
[Lyrics]

[...]
```

**Song Rules**:
- Tell a story with emotional arc
- Technical but singable
- Visual imagery (for audio+visual)
- NO literal specifics — metaphor and symbol only
- NO artist names in lyrics or style tags

### 2. Visual Concept Guide

```markdown
## Visual Concept Guide

**Core Visual Concept**: [Primary metaphor]

### Visual Themes & Imagery
[3-7 major themes]

### Symbolic Visual Elements
[Technical concepts as visual symbols]

### Emotional Color Arc
[Color palette evolution]

### Motion & Rhythm
[Movement patterns]

### Key Visual Contrasts
[Before/after, chaos/order]
```

**Visual Guide Rules**:
- Conceptual inspiration, NOT shot list
- NO specific durations or camera angles
- Provide creative direction, not constraints

### 3. TED Talk (Full Length)

```markdown
## TED Talk: "[Talk Title]"

### Opening (0:00-2:00)
[Hook with relatable problem]

### Setup: Why This Matters (2:00-6:00)
[Why this matters, stakes]

### The Problem (6:00-12:00)
[Deep dive into the pain point]

### Core Concept (12:00-25:00)
[Explain thoroughly]

### Real-World Examples (25:00-38:00)
[Concrete, specific details from context provided]

### Broader Implications (38:00-45:00)
[Connect to broader context]

### Closing (45:00-48:00)
[Call to action]

### Q&A Preparation (48:00-50:00)
[Address objections]
```

**TED Talk Rules**:
- Full 40-50 minutes, NOT a summary
- Ground in reality with specific details from provided context
- Address likely objections in Q&A

## Core Logic

### Step 1: Synthesize Conversation

- Read full conversation context
- Identify key decisions, "aha" moments
- Extract core insight or pattern

### Step 2: Identify Narrative Arc

| Element | Question |
|---------|----------|
| Problem | What was broken/painful? |
| Discovery | What did we learn? |
| Solution | What pattern emerged? |
| Impact | Why does this matter? |

### Step 3: Generate All Three Artifacts

The skill generates each component sequentially:

1. **Song**: Technical insight → emotional arc → Suno-ready lyrics
2. **Visual Concept**: Core metaphor → symbolic elements → color arc
3. **TED Talk**: Hook → explanation → examples → implications → Q&A

### Step 4: Return Combined Artifact

Return the complete artifact (song + visual concept + TED talk) to the invoking agent.

## Example

### Input: Bootstrap Observability Insight

**Context**: Discovered reproduce-to-debug problem. Introduced Bootstrap → Learn → Enforce phases.

**Narrative arc**:
- **Problem**: Debugging without reproduction is impossible
- **Discovery**: Greenfield systems don't know what "normal" is
- **Solution**: Bootstrap → Learn → Enforce phases
- **Impact**: Debug with sight instead of in darkness

### Output Summary

**Song excerpt**:
```
[Verse 1]
Three in the morning, the logs are all silent
System's on fire but the metrics don't know
Building in darkness, no baseline to measure
Can't debug what you've never seen before
```

**Visual concept**:
- Core metaphor: Darkness giving way to illumination
- Symbolic elements: Golden threads (trace IDs), Red fractures (errors)
- Color arc: Deep blues → Warm golds → Bright clarity

**TED talk opening**:
> "It's 3 AM. Your pager goes off. The system is on fire — users are complaining,
> something is clearly wrong. You pull up your logs and... nothing."

## Integration

- **Layer**: Creative
- **Depends on**: None (standalone)
- **Components**: insight-song, visual-concept, ted-talk
- **Complements**: Observation workflows, plan documentation, knowledge capture

## Component Skills

Use individual components when you only need one format:

| Skill | Alias | Output |
|-------|-------|--------|
| [insight-song](../insight-song/SKILL.md) | `/song` | Suno-ready song |
| [visual-concept](../visual-concept/SKILL.md) | `/vc` | Visual concept guide |
| [ted-talk](../ted-talk/SKILL.md) | `/ted` | Full TED talk |

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Insufficient context | Ask clarifying questions first |
| No clear narrative arc | Decline, explain what's missing |
| Surface-level topic | Suggest deeper exploration first |
| Main work not documented | Prompt to save progress first |

## Security Considerations

**Orchestration Note:**
This skill implements combined logic directly. It does NOT spawn or invoke other installed
skills (`insight-song`, `visual-concept`, `ted-talk`). The component skill instructions
are embedded inline within this skill.

**Input sources:**
- User-supplied context (if provided)
- Current conversation context (default)

**What this skill does NOT do:**
- Read files from the workspace
- Access project artifacts directly
- Send data to external services
- Call external APIs
- Modify source code
- Spawn other skills (all logic is inline)

**Output behavior:**
This skill returns the combined artifact (song + visual concept + TED talk) directly to the
invoking agent. The agent can then display, save, or pass the result to another skill as needed.

**Note on TED talks**: TED talks use concrete details from the context you provide.
Review before sharing externally to ensure no sensitive information is included.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Quality Checklist

- [ ] Can explain core insight in one sentence
- [ ] Understand why, not just what
- [ ] Song tells story with emotional arc
- [ ] Visual guide is inspirational not prescriptive
- [ ] TED talk is 40-50 minutes of substantial content
- [ ] No filler or generic padding

## Acceptance Criteria

- [ ] `/sq` generates all three artifact types
- [ ] Song formatted for Suno.ai (title, tags, sections)
- [ ] Visual guide is conceptual, not prescriptive
- [ ] TED talk is full length with concrete examples
- [ ] Result returned to invoking agent
- [ ] Individual components also available via `/song`, `/vc`, `/ted`

---

*"The detours became destinations. The questions we didn't expect to ask.
The patterns we found by paying attention to what emerged."*

---

*Part of the Live Neon Creative Suite.*
