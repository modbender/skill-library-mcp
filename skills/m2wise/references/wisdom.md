# Wisdom Subsystem

## Overview

M2Wise generates, verifies, and evolves wisdom from accumulated memories.

## Wisdom Types

### Principle

Interaction principles derived from user preferences.

**Example:**
```python
wisdom = {
    "kind": "principle",
    "statement": "Prefer concise Chinese answers for technical questions",
    "confidence": 0.9,
    "applicability": {
        "when": "intent='technical' AND language='chinese'",
        "unless": "user requests detailed explanation"
    }
}
```

### Schema

Behavioral patterns observed from user behavior.

**Example:**
```python
wisdom = {
    "kind": "schema",
    "statement": "Technical questions need concrete examples",
    "confidence": 0.85
}
```

### Skill

Operational skills extracted from user expertise.

**Example:**
```python
wisdom = {
    "kind": "skill",
    "statement": "Use tmux for managing long-running terminal sessions",
    "confidence": 0.8
}
```

### Causal Hypothesis

Causal assumptions from recurring patterns.

**Example:**
```python
wisdom = {
    "kind": "causal_hypothesis",
    "statement": "User repeatedly postpones tasks they find boring, not urgent",
    "confidence": 0.7
}
```

## Wisdom Generation (Sleep Phase)

### Process

1. **Memory Collection**: Gather active memories
2. **Clustering**: Group related memories
3. **Draft Generation**: Create wisdom drafts from clusters
4. **Storage**: Save drafts for verification

### Generation Methods

#### From Preferences

```python
# Input: User preference memories
memories = [
    {"type": "preference", "content": "I like concise answers"},
    {"type": "preference", "content": "Don't use jargon"}
]

# Output: Wisdom draft
draft = {
    "kind": "principle",
    "statement": "Prefer concise, jargon-free answers"
}
```

#### From Facts

```python
# Input: User fact memories
memories = [
    {"type": "fact", "content": "User is a Python developer"},
    {"type": "fact", "content": "User works on backend systems"}
]

# Output: Wisdom draft
draft = {
    "kind": "schema",
    "statement": "Technical explanations can assume Python knowledge"
}
```

## Wisdom Verification (Dream Phase)

### Counterexample Mining

Identifies cases where wisdom doesn't apply:

```python
# Example counterexample
counterexample = {
    "memory_id": "mem_xxx",
    "context": "User asked about cooking",
    "why": "Technical principle doesn't apply to cooking discussion"
}
```

### Verification Process

1. **Selection**: Choose draft for verification
2. **Mining**: Find counterexamples
3. **Analysis**: Evaluate evidence vs counterevidence
4. **Decision**: Publish, revise, or reject

## Self-Evolution

### Confidence Tracking

Wisdom confidence updates based on:

- **Hit Rate**: How often wisdom is applicable
- **Success Rate**: How often applied wisdom worked
- **Time Decay**: Older data has less weight

### Evolution Triggers

| Trigger | Action |
|---------|--------|
| Low hit rate | Decrease confidence |
| High success rate | Increase confidence |
| New evidence | Recalculate confidence |
| Conflict detected | Mark for review |

## Wisdom Fields

```python
{
    "id": "wiz_xxx",                    # Unique identifier
    "user_id": "alice",                 # User identifier
    "kind": "principle",               # Wisdom type
    "statement": "Prefer concise answers", # Wisdom text
    "applicability": {
        "when": "query contains technical", # When to apply
        "unless": "user asks for details"   # When not to apply
    },
    "confidence": 0.9,                # Confidence score
    "version": 1,                     # Version number
    "evidence": [                      # Supporting memories
        {"memory_id": "mem_xxx", "why": "User preference"}
    ],
    "counterevidence": [],             # Contradicting memories
    "created_at": 1234567890,
    "last_validated_at": 1234567890,
    "hit_count": 10,
    "success_count": 9
}
```

## Applicability Conditions

### Condition Types

```python
# Equality
Condition.eq("intent", "technical")

# Contains
Condition.contains("entities", "python")

# Tag presence
Condition.tag_has("language")

# Always true
Condition.true()
```

### Combining Conditions

```python
# AND
Condition.and_(cond1, cond2)

# OR
Condition.or_(cond1, cond2)

# NOT
Condition.not_(cond1)
```
