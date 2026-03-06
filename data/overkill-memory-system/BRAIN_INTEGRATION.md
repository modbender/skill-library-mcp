# Integration Analysis: Basal Ganglia, Insula, Jarvis

## Overview

Adding 3 new brain regions to the overkill-memory-system:

| Component | Function | Integration Point |
|-----------|----------|-------------------|
| **Basal Ganglia** | Habits, procedural memory, preferences | CLI + search weighting |
| **Insula** | Internal state (energy, mood, fatigue) | Session context |
| **Jarvis** | Daily logs, cron inbox, diary | Already partially integrated |

---

## Current Architecture

```
QUERY → UltraHot → Cache → Compiled → Emotion → Bloom → Mem0 → Weighting → Parallel → Rank → Results
```

---

## Proposed: Add Brain Regions

```
QUERY → UltraHot → Cache → Compiled → Emotion → Bloom → Mem0 → Weighting → Parallel → Rank → Results
          │          │           │              │            │          │          │
          │          │           │              │            │          │          └─────────────┐
          │          │           │              │            │          │                        │
          ▼          ▼           ▼              ▼            ▼          ▼                        ▼
    ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                              BRAIN REGIONS (Context)                                              │
    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
    │  │  Hippocampus    │  │    Amygdala     │  │       VTA       │  │ Basal Ganglia   │          │
    │  │  (Importance)   │  │   (Emotions)    │  │    (Value)     │  │    (Habits)     │          │
    │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
    │                                                                                                   │
    │  ┌─────────────────┐  ┌─────────────────┐                                                         │
    │  │     Insula      │  │     Jarvis      │                                                         │
    │  │ (Internal State)│  │  (Logs/Diary)  │                                                         │
    │  └─────────────────┘  └─────────────────┘                                                         │
    └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Details

### 1. Basal Ganglia (Habits)

**What it adds:**
- Habit tracking (repeated actions → automatic preferences)
- Procedural memory (workflows that work)
- "I always do X this way"

**How to integrate:**
```python
# In search weighting
def get_habit_boost(query):
    # Check if query matches known habits
    habits = load_habits()  # From basal-ganglia data
    for habit in habits:
        if habit.matches(query):
            return habit.confidence
    return 0.0
```

**CLI integration:**
```bash
# Track a habit
overkill habit track "use TypeScript for projects"

# List habits
overkill habit list

# Disable a habit
overkill habit disable "always use dark mode"
```

**Impact on search:**
- Boost results that match learned habits
- Lower results that conflict with habits

---

### 2. Insula (Internal State)

**What it adds:**
- Energy level (high/medium/low)
- Curiosity level (engaged/bored)
- Mood state (productive/tired/frustrated)
- "Gut feelings" based on internal signals

**How to integrate:**
```python
# Session context loading
def load_internal_state():
    """Load insula state for current session"""
    state = {
        "energy": "medium",      # high, medium, low
        "curiosity": "high",     # high, medium, low  
        "mood": "productive",    # productive, tired, frustrated, neutral
        "fatigue": 0.3           # 0.0 - 1.0
    }
    return state

# Adjust search based on state
def adjust_for_state(query, results, state):
    if state["energy"] == "low":
        # Prefer shorter, simpler results
        results = prefer_short(results)
    if state["curiosity"] == "high":
        # Boost exploratory results
        results = boost_novel(results)
    return results
```

**CLI integration:**
```bash
# Set internal state
overkill state set energy=low
overkill state set mood=tired
overkill state set curiosity=high

# Show current state
overkill state show

# Auto-detect from conversation
overkill state detect
```

**Impact on search:**
- Low energy → Prefer concise answers
- High curiosity → Boost novel/explorative results
- Tired mood → Skip complex reasoning

---

### 3. Jarvis (Logs/Diary)

**What it already has:**
- Daily logs (YYYY-MM-DD.md)
- Diary entries
- Cron inbox
- Platform post tracking
- Heartbeat state
- Strategy notes

**What's already integrated:**
- ✅ Daily logs (file tier)
- ✅ Cron inbox (WAL protocol)
- ✅ Platform posts (platform tracking)
- ✅ Diary search (implemented in v1.4)

**Future enhancements:**
- Strategy notes as memory source

**How to integrate:**
```python
# Add diary as searchable tier
def search_diary(query):
    """Search diary entries"""
    diary_path = Path("~/.openclaw/memory/diary").expanduser()
    results = []
    for entry in diary_path.glob("*.md"):
        if query.lower() in entry.read_text().lower():
            results.append(entry)
    return results
```

---

## Updated Brain Regions

| Region | Function | Status |
|--------|----------|--------|
| Hippocampus | Importance scoring | ✅ Integrated |
| Amygdala | Emotional tagging | ✅ Integrated |
| VTA | Value scoring | ✅ Integrated |
| **Basal Ganglia** | Habit formation | 🔄 NEW |
| **Insula** | Internal state | 🔄 NEW |
| **Jarvis** | Diary search | ✅ Implemented |

---

## Updated Search Flow

```
QUERY
   │
   ├─► UltraHot → Cache → Compiled → Emotion → Bloom → Mem0
   │
   └─► Load Brain State ──────────────────────────────────┐
        │                                                      │
        ├─► Hippocampus (importance)                          │
        ├─► Amygdala (emotions)                              │
        ├─► VTA (value)                                      │
        ├─► Basal Ganglia (habits) ← NEW                     │
        ├─► Insula (state) ← NEW                             │
        └─► Jarvis (diary) ← Partial                         │
                                                                 │
   ───────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Parallel Tiers + Brain
                              │
                              ▼
                    Merge + Rank + Results
```

---

## CLI Updates

### New Commands

```bash
# Habits (Basal Ganglia)
overkill habit track <action>
overkill habit list
overkill habit disable <habit>

# Internal State (Insula)  
overkill state set <key>=<value>
overkill state show
overkill state detect

# Enhanced Diary (Jarvis)
overkill diary search <query>
overkill diary today
overkill diary stats

# Combined Brain Stats
overkill brain status
```

---

## Implementation Priority

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| P0 | Basal Ganglia (habits) | Medium | High |
| P1 | Insula (state) | Low | Medium |
| P2 | Jarvis (diary search) | Low | Medium |

---

## Summary

| New Component | What it adds | Search Impact |
|--------------|--------------|--------------|
| Basal Ganglia | Habit preferences | Boost habit-matching results |
| Insula | Internal state | Adjust result style |
| Jarvis | Diary/Logs | More searchable content |

*Framework v1.4 - Adding brain regions*
