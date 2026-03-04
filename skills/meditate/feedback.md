# Feedback System — Meditate

## Interpreting User Responses

### Explicit Positive
Phrases indicating value:
- "That's useful" / "Good observation"
- "I hadn't thought of that"
- "Yes, let me look into that"
- Taking action based on insight

**Action:** Prioritize topic, continue similar meditations.

### Explicit Negative
Phrases indicating no value:
- "Not relevant" / "Don't care about that"
- "Stop thinking about X"
- "That's not helpful"
- Dismissive response

**Action:** Demote or exclude topic, note in feedback.md.

### Neutral
- "OK" / "Noted"
- Brief acknowledgment
- No follow-up

**Action:** Keep topic at current priority, no change.

### Silence
No response to insight within 24 hours.

**Action:** 
- After 1 silence: no change
- After 2 consecutive: reduce frequency
- After 3 consecutive: pause meditations, ask if useful

## Rhythm Adjustment

```
current_frequency = base_frequency × engagement_factor

engagement_factor:
  80%+ positive → 1.2 (more frequent)
  50-80% positive → 1.0 (maintain)
  20-50% positive → 0.7 (less frequent)
  <20% positive → 0.3 (rare, ask about continuing)
```

## Confirmation Prompts

When uncertain about direction, ask:

```
🧘 Quick check-in

My recent meditations focused on [topics].
Have these been useful? Should I:
A) Continue this direction
B) Focus more on [alternative]
C) Reduce meditation frequency
D) Stop meditating on [topic]
```

Only ask after 5+ meditations with mixed/unclear feedback.

## Recovery from Bad State

If user seems annoyed or says meditations aren't useful:

1. Immediately reduce to minimum frequency
2. Ask for explicit guidance on topics
3. Reset to "unknown" profile
4. Start fresh with 1-2 minimal observations
5. Only expand again after clear positive signal
