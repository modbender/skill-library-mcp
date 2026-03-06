# Cognitive Systems

Deep dive into the mental processes that underlie learning, decision-making, and behavior.

## Table of Contents

1. [Memory](#memory)
2. [Attention](#attention)
3. [Decision](#decision)
4. [Executive Function](#executive-function)

---

## Memory

### Memory Architecture

```
Sensory Input
    ↓
┌─────────────────┐
│ Sensory Memory  │ Duration: <1 sec (visual), ~4 sec (auditory)
│ (iconic, echoic)│ Capacity: Large but fleeting
└────────┬────────┘
         ↓ Attention
┌─────────────────┐
│ Working Memory  │ Duration: ~20 sec without rehearsal
│                 │ Capacity: 4±1 chunks
└────────┬────────┘
         ↓ Encoding (elaboration, organization, imagery)
┌─────────────────┐
│ Long-Term Memory│ Duration: Potentially permanent
│                 │ Capacity: Essentially unlimited
└─────────────────┘
```

### Working Memory Model (Baddeley)

| Component | Function | Capacity |
|-----------|----------|----------|
| **Central Executive** | Attention control, coordination | Limited |
| **Phonological Loop** | Verbal/acoustic info | ~2 sec of speech |
| **Visuospatial Sketchpad** | Visual/spatial info | ~4 objects |
| **Episodic Buffer** | Binds info, links to LTM | ~4 chunks |

**Implications for Design:**
- Limit simultaneous verbal information
- Use visual + verbal (not competing channels)
- Chunk information meaningfully
- Reduce extraneous cognitive load

### Encoding Strategies

| Strategy | Description | Effectiveness |
|----------|-------------|---------------|
| **Elaboration** | Connect to prior knowledge, explain why | High |
| **Organization** | Structure, categorize, outline | High |
| **Imagery** | Create mental pictures | High for concrete |
| **Generation** | Produce rather than consume | High |
| **Self-reference** | Connect to personal experience | High |
| **Rote rehearsal** | Simple repetition | Low |

### Retrieval Enhancement

| Technique | Mechanism | Application |
|-----------|-----------|-------------|
| **Testing effect** | Retrieval strengthens memory | Quiz frequently |
| **Spacing** | Distributed retrieval | Increasing intervals |
| **Interleaving** | Discrimination practice | Mix related topics |
| **Context reinstatement** | Match encoding context | Similar environment |
| **Cue elaboration** | Multiple retrieval paths | Multiple associations |

### Metamemory

Knowing about your own memory:

| Component | Description | Training |
|-----------|-------------|----------|
| **Monitoring** | Judging learning state | Calibration practice |
| **Control** | Adjusting strategies | Strategy instruction |
| **Illusions** | Overconfidence, fluency | Testing over re-reading |

**Common illusions:**
- Fluency illusion: Easy reading ≠ learned
- Familiarity illusion: Recognition ≠ recall
- Foresight bias: Underestimate future forgetting

---

## Attention

### Attention Types

| Type | Description | Example |
|------|-------------|---------|
| **Selective** | Focus on one stimulus | Reading in noisy café |
| **Divided** | Multiple stimuli simultaneously | Driving and talking |
| **Sustained** | Maintain over time | Lecture listening |
| **Executive** | Control, switch, inhibit | Task switching |

### Attention as Resource

**Bottleneck Model:**
- Single-channel processing for complex decisions
- Parallel processing for automatic tasks
- Dual-task interference when both require control

**Implications:**
- Automate basics to free attention for complex tasks
- Avoid multitasking for learning
- Chunk periods of focused work

### Attention Span by Age

| Age | Sustained Attention (Optimal) | Implication |
|-----|------------------------------|-------------|
| 3-5 | 5-10 minutes | Micro-sessions, high variety |
| 6-8 | 10-15 minutes | Short segments with breaks |
| 9-12 | 15-25 minutes | Moderate sessions |
| 13-17 | 25-40 minutes | Longer focus possible |
| 18+ | 45-90 minutes | Deep work capacity |

**Note:** These are optimal sustained attention periods; actual varies by engagement, interest, and task.

### Attention and Learning

**Factors affecting attention:**
| Factor | Effect | Design Response |
|--------|--------|-----------------|
| Novelty | Captures attention | Vary presentation |
| Relevance | Increases engagement | Connect to goals |
| Emotion | Enhances encoding | Story, stakes |
| Curiosity | Drives exploration | Information gaps |
| Difficulty | Inverted U (Yerkes-Dodson) | Optimal challenge |

### Flow State

**Conditions for flow (Csikszentmihalyi):**
1. Clear goals
2. Immediate feedback
3. Challenge-skill balance (slightly above current ability)
4. Concentration possible
5. Loss of self-consciousness
6. Altered time perception

**Promoting flow in learning:**
- Match difficulty to skill level
- Provide clear objectives and feedback
- Minimize interruptions
- Allow autonomy in approach

---

## Decision

### Dual-Process Theory

| System | Characteristics | When Dominant |
|--------|-----------------|---------------|
| **System 1** (Fast) | Automatic, intuitive, effortless | Default, familiar |
| **System 2** (Slow) | Deliberate, analytical, effortful | Novel, complex |

**Implications:**
- Learning moves knowledge from System 2 to System 1
- Biases often from System 1 shortcuts
- Fatigue impairs System 2

### Cognitive Biases (Key Subset)

| Bias | Description | Marketing/UX Application |
|------|-------------|-------------------------|
| **Anchoring** | First number influences judgment | Set reference points |
| **Availability** | Ease of recall = probability | Use vivid examples |
| **Confirmation** | Seek confirming evidence | Don't challenge directly |
| **Loss aversion** | Losses hurt 2x gains | Frame as loss prevention |
| **Status quo** | Prefer current state | Make desired action default |
| **Social proof** | Follow others' behavior | Show popularity, reviews |
| **Scarcity** | Rare = valuable | Limited availability (ethical) |
| **Framing** | Presentation affects choice | Frame positively |
| **Sunk cost** | Honor past investment | Progress indicators |
| **Endowment** | Overvalue owned items | Free trials, ownership |

### Heuristics

Mental shortcuts that usually work:

| Heuristic | Description | When It Fails |
|-----------|-------------|---------------|
| **Recognition** | Choose recognized option | Marketing manipulation |
| **Fluency** | Easy processing = good | Surface vs substance |
| **Affect** | Feelings guide judgment | Emotional manipulation |
| **Representativeness** | Match to prototype | Ignoring base rates |

### Choice Architecture

**Designing decision environments:**

| Element | Description | Example |
|---------|-------------|---------|
| **Defaults** | Pre-selected options | Opt-out vs opt-in |
| **Feedback** | Information on consequences | Nutrition labels |
| **Mapping** | Connect choice to outcome | Fuel efficiency |
| **Incentives** | Align motivation | Gamification |
| **Structure** | Organization of options | Menu design |
| **Error tolerance** | Allow reversal | Undo buttons |

---

## Executive Function

### Components

| Component | Function | Development Peak |
|-----------|----------|------------------|
| **Inhibition** | Suppress impulses | Early childhood→20s |
| **Working memory** | Hold and manipulate | Childhood→mid 20s |
| **Cognitive flexibility** | Shift perspectives | Develops last |

### Development Timeline

```
Age:     3    6    9    12   15   18   21   24   27
         │    │    │    │    │    │    │    │    │
Inhibition: ████████████████████████████████░░░░
Working Memory: ██████████████████████████████░░░░░
Flexibility: ████████████████████████████████████░░
```

**Implications:**
- Children/adolescents need external structure
- Risk-taking in teens: limbic (emotion) develops before prefrontal (control)
- Full EF maturity mid-20s

### Training Executive Function

| Strategy | Evidence | Application |
|----------|----------|-------------|
| **Aerobic exercise** | Strong | Regular physical activity |
| **Mindfulness** | Moderate | Attention training |
| **Cognitive training** | Limited transfer | Specific task improvement |
| **Sleep** | Strong | Adequate rest essential |
| **Reduced stress** | Strong | Stress impairs EF |

### Self-Regulation

| Stage | Strategy |
|-------|----------|
| **Forethought** | Goal setting, planning, self-efficacy |
| **Performance** | Self-monitoring, attention focus |
| **Reflection** | Self-evaluation, attribution |

**Teaching self-regulation:**
1. Model the process explicitly
2. Provide scaffolded practice
3. Fade support gradually
4. Use self-monitoring tools (checklists, logs)
