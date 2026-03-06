# The Proprioceptive Model — Technical Deep Dive

## Core Insight

Human proprioception operates via three subsystems: muscle spindles
(detect stretch), Golgi tendon organs (detect tension), and joint
receptors (detect position). None of these require conscious thought.
They run below awareness, feeding the brain a continuous spatial model.

This skill mirrors that architecture with five computational "receptors"
that run below the agent's primary reasoning, feeding it a continuous
model of where it stands.

---

## Sensor Architecture

### Weighted Scoring

The Overall Proprioceptive Index blends five sensors with unequal weights:

| Sensor | Weight | Rationale |
|--------|--------|-----------|
| Goal Proximity Radar | 0.20 | Goal alignment is foundational |
| Confidence Topography | 0.20 | Honesty about uncertainty prevents harm |
| Drift Detection | 0.15 | Drift is recoverable — less urgent |
| Capability Boundary | **0.25** | Hallucination is the highest-stakes failure |
| Session Quality Pulse | 0.20 | Cumulative quality determines session value |

CBS gets the highest weight because crossing the capability boundary
(hallucinating) is the most dangerous thing an AI agent can do. A wrong
answer delivered with confidence is worse than no answer at all.

### Sensor Independence

Each sensor operates independently. A bot can have excellent Goal
Proximity (GPR=0.95) but terrible Confidence Topography (CT=0.30) — it's
on-topic but unsure about what it's saying. The combination of all five
sensors creates a holistic picture that no single metric can provide.

---

## Algorithms

### Cosine Similarity (Term Frequency)

Used by GPR and DD to measure semantic alignment between texts.

```
cos(A, B) = (A · B) / (||A|| × ||B||)
```

Where A and B are term-frequency vectors. We use raw term frequencies
(not TF-IDF) because the computation must be self-contained — no
corpus statistics required.

### Jaccard Similarity

Used by GPR as a complement to cosine similarity. Measures vocabulary
overlap independent of term frequency.

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Where A and B are token sets (unique terms).

### Lexical Diversity (Type-Token Ratio)

Used by DD and SQP to detect repetitive or degrading responses.

```
TTR = unique_tokens / total_tokens
```

A declining TTR across turns signals the agent is running out of new
things to say — a precursor to circular or degenerative patterns.

### Pattern-Based Confidence Estimation

CT and CBS use extensive regex pattern libraries to detect linguistic
markers of certainty, hedging, speculation, and hallucination. These
patterns are derived from computational linguistics research on
epistemic markers and evidentiality.

Key pattern categories:
- **Hedging markers** (30 patterns): "might", "perhaps", "I think"...
- **Speculative markers** (12 patterns): "hypothetically", "in theory"...
- **High-confidence markers** (14 patterns): "definitely", "proven"...
- **Hallucination signatures** (8 patterns): fabricated citations, etc.
- **Vagueness markers** (16 patterns): "some kind of", "various"...
- **Deflection markers** (6 patterns): "beyond my scope", etc.

### Rolling Statistical Analysis

SQP uses rolling averages and variance computation to detect quality
trends and volatility across the session:

```
trend = "declining" if score < avg(recent_3) - 0.05
trend = "volatile"  if stddev(recent_3) > 0.15
trend = "improving" if score > avg(recent_3) + 0.05
trend = "stable"    otherwise
```

---

## Alert Thresholds

Two-tier alerting system: WARNING (course correction recommended) and
CRITICAL (immediate intervention required).

| Sensor | WARNING | CRITICAL |
|--------|---------|----------|
| GPR | < 0.60 | < 0.30 |
| CT | < 0.55 | < 0.35 |
| DD | < 0.50 | < 0.25 |
| CBS | < 0.55 | < 0.30 |
| SQP | < 0.50 | < 0.30 |
| Overall | < 0.60 | < 0.40 |

---

## Conversation Arc Model

DD tracks the conversation's progression through four phases:

1. **Opening** (turns 1-2): Initial context gathering
2. **Exploration** (turns 3-5): Deepening understanding
3. **Convergence** (turns 6+, if similarity increasing): Narrowing to solution
4. **Resolution** (turns 6+, if similarity stable): Delivering final answer

A healthy conversation moves linearly through these phases. Regressions
(e.g., returning from Convergence to Exploration) indicate drift.

---

## Data Flywheel Potential

The proprioceptive readings generated per session constitute a novel
dataset:

- **Hallucination boundary maps**: Which topics and domains cause CBS
  to drop? Aggregate this across thousands of sessions and you have a
  map of where LLMs lose reliability — per model, per domain, per task
  type.

- **Conversation decay curves**: At what turn does SQP typically start
  declining? This data could reshape how long conversations are
  designed to be.

- **Goal drift patterns**: What types of requests cause the most GPR
  drift? This feeds back into prompt engineering and agent design.

- **Confidence calibration data**: How well does CT's linguistic
  analysis predict actual correctness? Correlation studies could
  produce the first empirically-grounded confidence calibration for
  LLM outputs.

None of this data exists anywhere. No company, lab, or research group
is systematically collecting real-time self-awareness telemetry from
AI agents in production. First mover advantage is absolute.
