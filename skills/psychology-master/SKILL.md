---
name: psychology-master
description: World-class psychology expertise for human mind optimization. Masters learning science (age-appropriate skill acquisition for languages, coding, etc.), cognitive psychology, behavioral economics, and ethical marketing/conversion psychology. Use when designing learning programs, understanding human motivation, optimizing user experiences, creating persuasive messaging, improving conversion rates, or analyzing human behavior patterns. Covers developmental psychology, memory systems, habit formation, decision-making biases, and customer psychology.
---

# Psychology Master

The definitive psychology skill combining cognitive science, developmental psychology, learning science, and ethical marketing psychology. Provides evidence-based frameworks for understanding and optimizing human behavior.

## Quick Start

```
1. Identify domain → Learning OR Marketing OR Both
2. Gather context → Audience, goals, constraints
3. Apply framework → Select from references below
4. Validate → Run ethics and measurement checks
```

## Triggers

- "Design a learning plan for [age] to learn [skill]"
- "How should a [age]-year-old learn [coding/English/math]?"
- "Optimize conversion rate using psychology"
- "Create persuasive messaging without manipulation"
- "Understand customer decision-making process"
- "Build habit-forming product experience"
- "Age-appropriate teaching strategy for [topic]"
- "Behavioral analysis for [user segment]"

## Core Capabilities

### 1. Learning Psychology (Age-Optimized)

Design evidence-based learning experiences for any age:

| Age Band | Key Principles | Reference |
|----------|----------------|-----------|
| 3-6 | Play-based, sensory, attachment | `references/learning-development.md` |
| 7-12 | Concrete→abstract, scaffolding | `references/learning-development.md` |
| 13-17 | Autonomy, identity, peer influence | `references/learning-development.md` |
| 18-25 | Deliberate practice, metacognition | `references/learning-development.md` |
| 26-64 | Efficiency, transfer, constraints | `references/learning-development.md` |
| 65+ | Pacing, confidence, multimodal | `references/learning-development.md` |

**Skill-Specific Guidance:**
- **Languages**: See `references/skill-acquisition.md#languages`
- **Coding**: See `references/skill-acquisition.md#programming`
- **Mathematics**: See `references/skill-acquisition.md#mathematics`
- **Music/Sports**: See `references/skill-acquisition.md#motor-skills`

### 2. Cognitive Psychology

Core mental processes that drive behavior:

| System | Application | Reference |
|--------|-------------|-----------|
| Memory | Encoding, retrieval, spacing | `references/cognitive-systems.md#memory` |
| Attention | Focus, dual-task, load | `references/cognitive-systems.md#attention` |
| Decision | Heuristics, biases, choice | `references/cognitive-systems.md#decision` |
| Motivation | Intrinsic/extrinsic, goals | `references/motivation-frameworks.md` |

### 3. Marketing & Conversion Psychology

Ethical persuasion and conversion optimization:

| Framework | Use Case | Reference |
|-----------|----------|-----------|
| JTBD | Customer motivation | `references/marketing-psychology.md#jtbd` |
| Behavioral Economics | Choice architecture | `references/marketing-psychology.md#behavioral-econ` |
| Persuasion Science | Ethical influence | `references/marketing-psychology.md#persuasion` |
| Conversion Optimization | Funnel psychology | `references/conversion-optimization.md` |
| Customer Journey | Touchpoint design | `references/customer-psychology.md` |

### 4. Assessment & Analysis

Use scripts for personalized recommendations:

```bash
# Learner profile assessment
python scripts/learner_assessment.py --age 25 --skill coding --context work

# Conversion audit
python scripts/conversion_audit.py --funnel signup --segment new_users

# Bias detection in messaging
python scripts/bias_detector.py --copy "marketing_copy.txt"

# Search reference files
python scripts/search.py --query "habit formation" --ignore-case
```

## Workflow

### Phase 1: Context Gathering

Collect minimum viable context:

**For Learning:**
- Age and developmental stage
- Prior knowledge and skills
- Time availability and constraints
- Motivation level and source
- Learning environment (tools, support)

**For Marketing:**
- Target audience demographics
- Current conversion metrics
- Customer pain points and goals
- Competitive landscape
- Ethical constraints

### Phase 2: Framework Selection

```
Learning Task?
├── What age? → Select developmental approach
├── What skill? → Select acquisition framework
└── What constraint? → Optimize for time/depth/retention

Marketing Task?
├── Awareness stage? → Use attention + salience frameworks
├── Consideration? → Use social proof + comparison
├── Decision? → Use friction removal + risk reduction
└── Retention? → Use habit + loyalty frameworks
```

### Phase 3: Implementation

Generate specific, actionable plans using the detailed reference materials.

### Phase 4: Validation

Run ethics checklist from `references/safety-ethics.md` before final output.

## Guardrails (Hard Rules)

- **No medical/psychiatric advice** - Refer to professionals
- **No diagnosis** - Assessment tools are informational only
- **No manipulation** - All persuasion must be ethical and transparent
- **Minors: safety-first** - Conservative guidance, guardian involvement
- **Context-specific** - Avoid universal claims; tailor recommendations
- **Evidence-based** - Cite frameworks and principles, not anecdotes

## Output Templates

### Learning Plan Template

```markdown
## Learning Plan: [Skill] for [Age/Context]

### Learner Profile
- Age/Stage: 
- Prior Knowledge: 
- Time Budget: 
- Primary Motivation: 

### Goals & Milestones
| Week | Goal | Success Indicator |
|------|------|-------------------|

### Method Mix
- Primary Method: 
- Practice Structure: 
- Feedback Mechanism: 

### Motivation & Habit Support
- Intrinsic drivers: 
- Habit triggers: 
- Progress visibility: 

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|
```

### Marketing/Conversion Plan Template

```markdown
## Conversion Optimization: [Funnel Stage]

### Audience Profile
- Segment: 
- Job-to-be-Done: 
- Current Behavior: 

### Psychological Levers (Ethical)
| Lever | Application | Why It Works |
|-------|-------------|--------------|

### Messaging Hierarchy
1. Primary Promise: 
2. Proof Point: 
3. Differentiator: 
4. Risk Reducer: 

### Experiment Design
- Hypothesis: 
- Metric: 
- Segment: 
- Duration: 

### Ethical Validation
☐ No deception
☐ No dark patterns
☐ Transparent value exchange
☐ User empowerment preserved
```

## Reference Loading Guide

### Core References (Original 8)

| Task | Load These References |
|------|----------------------|
| Child learning (3-12) | `learning-development.md`, `skill-acquisition.md` |
| Teen/Adult learning | `learning-development.md`, `motivation-frameworks.md` |
| Conversion optimization | `conversion-optimization.md`, `marketing-psychology.md` |
| Messaging/copywriting | `marketing-psychology.md`, `customer-psychology.md` |
| Habit design | `motivation-frameworks.md`, `cognitive-systems.md` |
| Full audit | All references + `safety-ethics.md` |

### Extended References (12 Additional Domains)

| Task | Load These References |
|------|----------------------|
| Group dynamics, social influence | `social-psychology.md` |
| Audience segmentation, personas | `personality-psychology.md` |
| UI/UX design, usability | `ux-psychology.md` |
| Emotional design, empathy | `emotional-intelligence.md` |
| Brain-based learning, neuroscience | `neuropsychology-basics.md` |
| Interpersonal skills, feedback | `communication-psychology.md` |
| Business deals, salary negotiation | `negotiation-psychology.md` |
| Design, branding, marketing visuals | `color-psychology.md` |
| Learning timing, optimal scheduling | `sleep-circadian.md` |
| Innovation, ideation, brainstorming | `creativity-psychology.md` |
| Burnout, coping, well-being | `stress-resilience.md` |
| Teams, leadership, culture | `organizational-psychology.md` |

### Complete Reference List (20 files)

**Learning & Development**: `learning-development.md`, `skill-acquisition.md`, `cognitive-systems.md`, `neuropsychology-basics.md`, `sleep-circadian.md`

**Motivation & Behavior**: `motivation-frameworks.md`, `stress-resilience.md`, `creativity-psychology.md`

**Marketing & Conversion**: `marketing-psychology.md`, `conversion-optimization.md`, `customer-psychology.md`, `color-psychology.md`

**Interpersonal & Social**: `social-psychology.md`, `personality-psychology.md`, `emotional-intelligence.md`, `communication-psychology.md`, `negotiation-psychology.md`

**Design & Organization**: `ux-psychology.md`, `organizational-psychology.md`

**Ethics**: `safety-ethics.md`
