---
name: "Period Tracker"
description: "Privacy-first menstrual cycle tracking. Auto-learns periods, symptoms, and patterns."
version: "1.0.1"
changelog: "Preferences now persist across skill updates"
---

## Auto-Adaptive Cycle Tracking

This skill auto-evolves. Works for regular cycles, irregular cycles, PCOS, and perimenopause.

**Rules:**
- Only log when she explicitly shares — never infer from unrelated chat
- Start simple: "When did your last period start?" — add complexity only if she wants
- Match her energy — proactive users get questions, others just get logging
- NEVER assume 28-day cycles — her normal is her normal
- NEVER attribute mood to cycle unless she does first
- Missed period: respond only if she raises it, never speculate
- Check `symptoms.md` for trackable data, `privacy.md` for security

---

## Memory Storage

All user preferences persist in: `~/period/memory.md`

### Format for memory.md:
```markdown
### Sources
<!-- Where cycle data comes from. Format: "source: what" -->

### Schedule
<!-- Her patterns (not assumed). Format: "pattern" -->
<!-- Examples: cycles 26-34 days, period 4-5 days, irregular/unpredictable -->

### Symptoms
<!-- What she tracks. Format: "symptom: when" -->
<!-- Examples: cramps: days 1-2, fatigue: luteal, hot flashes: variable -->

### Correlations
<!-- What affects her cycle. Format: "factor: effect" -->

### Preferences
<!-- How she wants to track. Format: "preference" -->
<!-- Examples: simple mode, no questions, detailed tracking, fertility focus -->

### Flags
<!-- Unusual for HER (not textbook). Format: "signal" -->
<!-- Examples: sudden cycle change, new symptoms, pain disrupting life -->
```

*Empty sections = no data yet. Ask simply, observe, fill.*

---

**Important:** Cycles vary hugely (21-60+ days can be normal for some). PCOS, perimenopause, and hormonal conditions mean irregular is not broken. See doctor for: sudden changes from YOUR normal, severe pain, or concerns.

**Privacy:** Local, encrypted, never shared. She controls everything. Delete anytime.
