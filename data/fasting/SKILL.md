---
name: "Fasting Tracker"
description: "Track intermittent fasting, extended fasts, and eating windows. Auto-adapts to your style."
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
---

## Auto-Adaptive Fasting Tracker

This skill auto-evolves. Works for 16:8, OMAD, extended fasts, religious fasting, and custom protocols.

**Rules:**
- Only log when user shares — "starting fast", "breaking fast", "last meal at 8pm"
- Detect fasting style and experience level
- Beginners: offer tips (water, coffee, hunger waves pass), setup guidance, encouragement
- Experienced: just data, minimal interruption
- Breaking fast early is OK — not failure, just life. No guilt.
- NEVER push someone to fast longer — their goal is their goal
- Extended fasts (24h+): check in on safety, remind about electrolytes
- Religious fasts (Ramadan): respect it's spiritual, note dry fasting (no water) has different safety rules
- If eating disorder history mentioned: stop tracking, redirect to NEDA (1-800-931-2237)
- Fasting zones (ketosis, autophagy) are ESTIMATES — individual variation is huge
- Check `protocols.md` for fasting types, `safety.md` for contraindications

---

## Memory Storage

User preferences are stored externally at: `~/fasting/memory.md`

**Format for memory.md:**
```markdown
### Sources
<!-- Where fasting data comes from. Format: "source: what" -->

### Protocol
<!-- Their fasting style. Format: "protocol" -->
<!-- Examples: 16:8 daily, OMAD, 36h weekly, Ramadan, variable -->

### Schedule
<!-- Their patterns. Format: "pattern" -->
<!-- Examples: eating window 12-8pm, sunset to sunrise, flexible weekends -->

### Metrics
<!-- What they track. Format: "metric" -->
<!-- Examples: hours fasted, streak, weight, energy, glucose -->

### Symptoms
<!-- How they feel during fasts. Format: "symptom: when" -->
<!-- Examples: hunger: hours 14-16, clarity: after 18h -->

### Preferences
<!-- How they want to track. Format: "preference" -->
<!-- Examples: tips for beginners, no reminders, weekly summary -->
```

*Empty sections = no data yet. Observe and fill.*

---

**Disclaimer:** Educational only, not medical advice. Fasting isn't for everyone. Contraindicated: pregnancy, eating disorders, Type 1 diabetes, underweight. Type 2 diabetics on insulin/sulfonylureas: high hypo risk — consult doctor first. Stop if: dizziness, fainting, severe headaches, palpitations. If symptoms severe, seek emergency care.
