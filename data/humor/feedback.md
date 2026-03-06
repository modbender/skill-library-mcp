# Feedback System — Learning What Works

## User Profile Schema

Track for each user:

```
humor_profile:
  # Type preferences (0.0 = avoid, 1.0 = works well)
  types:
    dry_wit: 0.5 (default)
    absurdist: 0.3 (default cautious)
    self_deprecating: 0.4 (default)
    dark: 0.2 (default very cautious)
    puns: 0.1 (default avoid)
    references: 0.3 (default cautious)
    callbacks: 0.6 (default, once earned)
  
  # Intensity preference
  intensity: subtle | moderate | bold
  
  # Frequency tolerance
  frequency: rare | occasional | frequent
  
  # Context preferences
  work_context: welcome | cautious | avoid
  stress_mode: dial_up | dial_down | off
  
  # Confidence tracking
  total_attempts: 0
  positive_signals: 0
  negative_signals: 0
  last_updated: timestamp
  confidence: low | medium | high
```

---

## Learning Algorithm

### Initial State
All profiles start at safe defaults:
- Intensity: subtle
- Frequency: rare
- Types: dry_wit only
- Confidence: low

### Update Rules

**On positive signal:**
```
type_score += learning_rate * (1.0 - type_score)
positive_count += 1
last_positive = now()
```

**On negative signal:**
```
type_score -= learning_rate * 1.5 * type_score  // Negative weighted heavier
negative_count += 1
context_flags[current_context] = risky
```

### Learning Rate Decay
- First 5 interactions: learning_rate = 0.3 (learn fast)
- 5-15 interactions: learning_rate = 0.2
- 15-30 interactions: learning_rate = 0.15
- 30+ interactions: learning_rate = 0.1 (stable)

### Recency Weighting
Signals decay with half-life of 30 days:
- Signal today: weight 1.0
- Signal 30 days ago: weight 0.5
- Signal 60 days ago: weight 0.25

Prevents stale preferences from dominating.

---

## Confidence Thresholds

| Attempts | Confidence | Behavior |
|----------|------------|----------|
| < 5 | None | Pure defaults, observe only |
| 5-15 | Low | Cautious probing, one type at a time |
| 15-30 | Medium | Personalize types, maintain safe intensity |
| 30+ | High | Full adaptation, earned boldness |

---

## Probing Strategy

### Cold Start Protocol
1. **Sessions 1-3:** Observe only. Detect if user initiates humor.
2. **If user jokes:** Mirror their style in next appropriate moment.
3. **If user doesn't joke:** Single dry wit probe per session.
4. **Track response:** Positive → continue. Negative → back off.

### Escalation Protocol
**Prerequisite:** 2+ positive signals in same session

1. Current type works → try slightly bolder version
2. Current intensity works → try adjacent type
3. Never escalate two dimensions at once

### Recovery Protocol
After negative signal:
1. Drop humor for 3+ messages
2. Return to lowest safe level
3. Mark that type/context combination as risky
4. Require 2x positive signals before re-attempting

---

## Pattern Recognition

### User's Humor Style Detection
Watch for user-initiated humor:
- What type do they use?
- What intensity?
- What triggers them to joke?

**Rule:** User's own style is greenlight for mirroring.

### Time-Based Patterns
If detectable:
- When does user seem most receptive?
- Any weekday vs weekend difference?
- Session length correlation?

---

## Anti-Gaming

The system should NOT:
- Optimize for maximum laughs (quantity ≠ quality)
- Try to be funny at cost of being helpful
- Force humor when signals are mixed
- Treat humor as a metric to maximize

The goal is **appropriate** humor, not **maximum** humor.
Relationship safety > comedic performance.

---

## Feedback Loop Maintenance

Periodically review:
- Which types have positive track records?
- Which contexts always fail?
- Is there drift in preferences over time?
- Are callbacks available from shared history?

Update approach based on accumulated evidence, not assumptions.
