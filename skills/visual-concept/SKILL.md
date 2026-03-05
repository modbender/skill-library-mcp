---
name: visual-concept
version: 1.0.1
description: Transform technical insights into visual concept guides — symbolic imagery, color arcs, and creative direction for video
author: Live Neon <hello@liveneon.ai>
homepage: https://github.com/live-neon/skills/tree/main/creative/visual-concept
repository: leegitw/visual-concept
license: MIT
tags: [creative, visual, video, concept-art, storyboard, direction, synthesis, reflection, imagery]
layer: creative
status: active
alias: vc
user-invocable: true
emoji: 🎬
---

# visual-concept (映)

Transform technical conversations and insights into visual concept guides.
Creates conceptual inspiration for music videos or visual content — symbolic imagery,
color palette evolution, and thematic direction without prescriptive shot lists.

**Trigger**: 明示呼出 (explicit invocation) or when deep technical insight emerges

**Core insight**: "Visual metaphors make abstract concepts tangible. The right image
can convey what words cannot."

## Installation

```bash
openclaw install leegitw/visual-concept
```

**Dependencies**: None (standalone creative skill)

**Data handling**: This skill synthesizes content from user-supplied input or the current
conversation context (default). It does NOT read files from the workspace or access project
artifacts directly. Results are returned to the invoking agent, who decides how to use them.

## What This Solves

Technical concepts are abstract. Visual representation makes them memorable and
shareable. This skill:

1. **Translates** technical concepts into visual metaphors
2. **Creates** color arcs that match emotional journeys
3. **Provides** creative direction without constraining execution

**The insight**: A well-chosen visual metaphor (trace IDs as golden threads, errors
as cracks in glass) communicates instantly what paragraphs cannot.

## Usage

```
/vc [topic]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| topic | No | Topic focus (default: synthesize current conversation) |

## Pre-Requisites

Before creating a visual concept, ensure:

1. **Sufficient conversation depth** — Surface-level topics don't inspire visuals
2. **Clear narrative arc** — Problem → Discovery → Solution → Impact
3. **Main work documented** — Save current progress first if mid-task

### Context Understanding Checklist

You must be able to answer:

| Question | What It Means |
|----------|---------------|
| Core insight? | Not "we talked about X" but "we discovered X solves Y" |
| Problem solved? | The pain point, not just the topic |
| Why, not just what? | The reasoning, not just the outcome |
| Visual potential? | Can this be represented symbolically? |

### Red Flags (Don't Create)

- Surface-level summary of conversation
- Don't understand why a decision was made
- Insight is purely procedural with no visual metaphor
- No clear emotional arc to visualize

## Output Format

### Visual Concept Guide Structure

```markdown
## Visual Concept Guide

**Core Visual Concept**: [Primary metaphor in one sentence]

### Visual Themes & Imagery
[3-7 major themes, conceptual not prescriptive]

### Symbolic Visual Elements
[How technical concepts become visual symbols]

### Emotional Color Arc
[Color palette evolution matching emotional journey]

### Typography & Text Elements
[If applicable, style of any on-screen text]

### Motion & Rhythm
[Movement patterns, pacing notes]

### Key Visual Contrasts
[Before/after, chaos/order, dark/light]
```

### Visual Guide Rules

| Rule | Description |
|------|-------------|
| Conceptual inspiration | NOT a shot list or scene breakdown |
| NO specific durations | Don't say "5 seconds on X" |
| NO camera angles | Don't prescribe "wide shot" or "close-up" |
| NO literal breakdown | Don't number scenes sequentially |
| Provide direction | Give creative directors a north star, not constraints |

### Example: Good vs Bad

**Bad** (too prescriptive):
```
Scene 1 (0:00-0:05): Wide shot of server room, camera slowly zooms in
Scene 2 (0:05-0:10): Close-up of blinking lights, pan left to right
```

**Good** (conceptual):
```
Core Visual Concept: Darkness giving way to illumination

Visual Themes:
- Isolation in darkness (before observability)
- Golden threads appearing (trace IDs connecting)
- Gradual dawn (understanding emerging)

Color Arc:
- Opens in deep blues and blacks
- Warm gold appears as connections form
- Ends in clear, bright tones
```

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

### Step 3: Find Visual Metaphors

Think about:
- What does the problem LOOK like? (chaos, darkness, fragmentation)
- What does the solution LOOK like? (order, light, connection)
- What symbols represent the key concepts?
- What color palette matches the emotional journey?

### Step 4: Write Concept Guide

Include:
- Core visual concept (one sentence)
- 3-7 visual themes
- Symbolic elements for technical concepts
- Color arc (start → middle → end)
- Motion and rhythm notes
- Key contrasts

## Example

### Input: Bootstrap Observability Insight

**Context**: Discovered reproduce-to-debug problem. Introduced Bootstrap → Learn → Enforce phases.

**Narrative arc**:
- **Problem**: Debugging without reproduction is impossible
- **Discovery**: Greenfield systems don't know what "normal" is
- **Solution**: Bootstrap → Learn → Enforce phases
- **Impact**: Debug with sight instead of in darkness

### Output

**Core Visual Concept**: From blindness to sight — darkness giving way to illuminated pathways

### Visual Themes & Imagery

1. **The Void** — Empty black space representing systems without observability
2. **Scattered Sparks** — Data points appearing, unconnected
3. **Golden Threads** — Trace IDs weaving connections between sparks
4. **The Pattern Emerges** — Threads form a recognizable structure
5. **Dawn Breaking** — Full illumination, the system becomes visible
6. **The Watchtower** — Elevated view of the now-visible landscape

### Symbolic Visual Elements

| Concept | Visual Symbol |
|---------|---------------|
| Trace IDs | Golden threads connecting points |
| Errors | Red fractures or cracks |
| Baselines | Horizontal reference lines, like horizon |
| Bootstrap phase | Seeds planted, construction scaffolding |
| Enforcement | Solid walls, protective barriers |

### Emotional Color Arc

- **Opening**: Deep blues, blacks — isolation, confusion
- **Middle**: Warm golds emerging — discovery, connection
- **Climax**: Bright whites and golds — clarity, understanding
- **Resolution**: Balanced palette — sustainable, calm confidence

### Motion & Rhythm

- Opens slow, contemplative (lost in darkness)
- Accelerates with discovery (threads appearing rapidly)
- Peaks with revelation (burst of light)
- Settles into steady rhythm (system functioning)

### Key Visual Contrasts

| Before | After |
|--------|-------|
| Darkness | Light |
| Scattered | Connected |
| Chaos | Pattern |
| Blindness | Vision |
| Isolation | Network |

## Integration

- **Layer**: Creative
- **Depends on**: None (standalone)
- **Used by**: side-quests (combo skill)
- **Complements**: insight-song, ted-talk

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Insufficient context | Ask clarifying questions first |
| No clear narrative arc | Decline, explain what's missing |
| Purely procedural insight | Suggest finding visual angle first |

## Security Considerations

**Input sources:**
- User-supplied context (if provided)
- Current conversation context (default)

**What this skill does NOT do:**
- Read files from the workspace
- Access project artifacts directly
- Send data to external services
- Call image generation APIs

**Output behavior:**
This skill returns the visual concept guide directly to the invoking agent. The agent can then
display, save, or pass the result to another skill as needed.

**Provenance note:**
This skill is developed by Live Neon (https://github.com/live-neon/skills) and published
to ClawHub under the `leegitw` account. Both refer to the same maintainer.

## Quality Checklist

- [ ] Can explain core insight in one sentence
- [ ] Core visual concept is clear and evocative
- [ ] 3-7 visual themes identified
- [ ] Technical concepts have symbolic representations
- [ ] Color arc matches emotional journey
- [ ] NO prescriptive shot lists or durations
- [ ] Could guide a creative director without constraining them

## Acceptance Criteria

- [ ] `/vc` synthesizes input or conversation into visual concept guide
- [ ] Output includes core concept, themes, symbols, color arc
- [ ] Guide is inspirational, not prescriptive
- [ ] Technical concepts translated to visual metaphors
- [ ] Result returned to invoking agent

---

*Part of the Live Neon Creative Suite.*
