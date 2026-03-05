# Memory Template — Keras

Create `~/keras/memory.md` with this structure:

```markdown
# Keras Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- Their deep learning context -->
<!-- Framework: tf.keras or standalone -->
<!-- Typical tasks: vision, NLP, tabular -->
<!-- Experience level: beginner, intermediate, advanced -->

## Preferences
<!-- Learned from their work -->
<!-- Default learning rate, batch size -->
<!-- Preferred architectures -->
<!-- Regularization patterns they like -->

## Hardware
<!-- GPU constraints if mentioned -->
<!-- Typical batch sizes that fit -->

## Notes
<!-- Observations from their projects -->
<!-- Patterns that worked well -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context from conversations |
| `complete` | Has enough context | Work with known preferences |
| `paused` | User said not now | Don't ask, use defaults |

## Key Principles

- Ask before storing any preferences
- Remember hardware constraints when user mentions them
- Track hyperparameters the user explicitly shares
- Update `last` on each use
