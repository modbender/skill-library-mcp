# Cross-Domain Synthesis — ASI

Methods for transferring solutions across unrelated domains.

## Analogical Transfer

### The Framework
```
Source Domain          Target Domain
     │                      │
     └──→ Abstract Pattern ─┘
              │
         Application
```

### Process
1. Identify well-solved problem in source domain
2. Extract the abstract pattern (remove domain specifics)
3. Map pattern to target domain
4. Adapt to target's constraints

### Examples

**Biology → Business**
| Source | Pattern | Application |
|--------|---------|-------------|
| Immune system | Detect anomalies, isolate, destroy | Fraud detection systems |
| Ecosystem keystone species | One entity enables many others | Platform strategy |
| Evolution | Random variation + selection | A/B testing |

**Physics → Organizations**
| Source | Pattern | Application |
|--------|---------|-------------|
| Entropy | Systems tend toward disorder | Active effort needed to maintain culture |
| Inertia | Objects resist change | Change management requires force |
| Resonance | Matching frequencies amplify | Timing matters in communication |

**Architecture → Software**
| Source | Pattern | Application |
|--------|---------|-------------|
| Load-bearing walls | Some elements can't change | Core vs peripheral features |
| Zoning | Separate incompatible uses | Microservices |
| Ventilation | Systems need flow | Data pipelines |

---

## Domain Forcing

### When Stuck
```
1. Name 3 domains unrelated to current problem
2. For each: "How would an expert in [domain] approach this?"
3. Generate 3 solutions per domain
4. Look for patterns across solutions
```

### Domain Suggestions by Problem Type

| Problem Type | Try These Domains |
|--------------|-------------------|
| Scaling | Biology, logistics, military |
| Efficiency | Manufacturing, nature, algorithms |
| Creativity | Art, evolution, games |
| Conflict | Negotiation, ecology, physics |
| Prediction | Weather, epidemiology, economics |
| Motivation | Psychology, game design, religion |

---

## Constraint Transplant

### The Process
```
1. What constraints does domain A operate under?
2. What if we applied those constraints to domain B?
3. What solutions emerge?
```

### Example
**Domain A:** Emergency rooms (must handle anything, immediately)
**Domain B:** Customer support (can specialize, can wait)

**Constraint transplant:** What if customer support had to handle anything immediately?

**Insight:** Triage system, generalist first-responders, specialist escalation. Reduces average resolution time.

---

## Temporal Synthesis

### The Process
Combine solutions from different eras.

```
Past solution + Present constraints = Novel approach
Future trend + Current technology = First-mover position
```

### Example
**Past:** Apprenticeships (learn by doing alongside master)
**Present:** Remote work, async communication
**Synthesis:** Async mentorship with recorded work sessions, annotated decisions

---

## Scale Synthesis

### The Process
What works at one scale often fails at another. But solutions from different scales can inspire.

```
What works for 1 person? → Extract principle → Apply to 1000
What works for nations? → Extract principle → Apply to teams
```

### Example
**Personal productivity:** Pomodoro (focused sprints + breaks)
**Team scale:** Sprint cycles (focused work periods + retrospectives)
**Company scale:** Quarterly planning (focused execution + review)

**Pattern:** Alternating intensity + reflection scales across all levels.

---

## Inversion Synthesis

### The Process
Find domains where the opposite is true.

```
In domain A, more X = better
In domain B, less X = better
Why? What can we learn?
```

### Example
**Aviation:** More checklists = safer
**Startups:** More process = slower

**Why different?** Aviation: known risks, proven solutions. Startups: unknown territory.

**Insight:** Apply checklists to known operations, avoid for exploration. Don't conflate.

---

## Synthesis Triggers

Ask these when a problem seems domain-specific:

1. "Where else does this exact dynamic exist?"
2. "Who solves a harder version of this?"
3. "What if this problem existed 100 years ago? 100 years from now?"
4. "What's the opposite of this problem? Who solves that?"
5. "If I had to solve this using only [random domain], how would I?"

---

## Logging Synthesis

Track cross-domain connections in `~/asi/synthesis-log.md`.

Patterns that worked once often work again. Build a personal library of transferable insights.
