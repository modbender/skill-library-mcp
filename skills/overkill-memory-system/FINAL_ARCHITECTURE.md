# Overkill Memory System - Final Architecture (v1.4)

## Overview

Brain-Full hybrid memory architecture with 6 brain regions.

## Overview

Speed-first hybrid memory architecture with neuroscience-powered ranking.

---

## Architecture Flow

```
                         ┌─────────────────────────────────┐
                         │           USER QUERY              │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │       ULTRA-HOT (Dict)           │
                         │    Last 10 queries ~0.1ms       │
                         │    (RETURN if hit!)             │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │         HOT CACHE (Redis)        │
                         │    Recent queries ~1ms          │
                         │    (RETURN if hit!)             │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │      COMPILED QUERIES           │
                         │    Pre-parsed common queries    │
                         │    ~0ms (dict lookup)          │
                         │    (USE if match!)             │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │      EMOTIONAL DETECTOR         │
                         │  (preference/error/important)   │
                         │  ~0.5ms (only if no compiled)  │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │         BLOOM FILTER            │
                         │    "Does it exist?" ~0ms       │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │         MEM0 (FIRST!)           │
                         │    Fast cache ~20ms             │
                         │    80% token savings           │
                         │    (RETURN if hit!)             │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │   EARLY WEIGHTING               │
                         │  Adjust tier weights by intent  │
                         │  ~1ms                           │
                         └─────────────────┬───────────────┘
                                           │
                         ┌─────────────────▼───────────────┐
                         │   RUN REMAINING TIERS PARALLEL  │
                         │                               │
                         │  ┌─────────┐ ┌──────────┐     │
                         │  │ acc-err │ │ vestige  │     │
                         │  │  (err)  │ │ (prefs)  │     │
                         │  │  w: 2x  │ │  w: 2x   │     │
                         │  └─────────┘ └──────────┘     │
                         │                               │
                         │  ┌─────────┐ ┌──────────┐     │
                         │  │ChromaDB │ │GitNotes  │     │
                         │  └─────────┘ └──────────┘     │
                         │                               │
                         └───────────────┬───────────────┘
                                         │
                         ┌───────────────▼───────────────┐
                         │      MERGE + RANKING         │
                         │         (~10ms)              │
                         │                             │
                         │  PASS 1: Quick filter        │
                         │  PASS 2: Neuroscience       │
                         │                             │
                         └───────────────┬───────────────┘
                                         │
                         ┌───────────────▼───────────────┐
                         │    CONFIDENCE EARLY EXIT      │
                         │  confidence > 0.95? return 1  │
                         │  gap > 0.5? return 1        │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │    RESULTS    │
                                 │   (~5-15ms)  │
                                 └───────────────┘
```

---

## Speed Targets

| Scenario | Time |
|----------|------|
| Compiled query match | ~0ms |
| Ultra-hot hit | ~0.1ms |
| Hot cache hit | ~1ms |
| Mem0 hit | ~22ms |
| Full search | ~55ms |
| **Average** | **~5ms** |

---

## Why This Order?

1. **Ultra-hot + Cache** → Instant return if already cached
2. **Compiled queries** → Skip parsing for common queries (~0ms)
3. **Emotional detector** → Only if no compiled match (~0.5ms)
4. **Bloom** → Skip if definitely not found
5. **Mem0 first** → 80% of remaining queries hit here
6. **Rest parallel** → If Mem0 misses

---

## Emotional Detector & Weighting

| Query Type | Keywords | Weight Adjustments |
|------------|----------|-------------------|
| **Error/Fix** | "bug", "fix", "error" | acc-error: 2x |
| **Preference** | "prefer", "like", "always" | vestige: 2x |
| **Important** | "remember", "critical" | all: 1.5x |
| **Recent** | "yesterday", "last week" | hot: 2x |
| **Project** | "project", "architecture" | gitnotes: 1.5x |

---

## Neuroscience: Hybrid Approach

### Two Passes

| Pass | What | When |
|------|------|------|
| **Pass 1** | Quick filter (0 importance skip) | High-importance queries |
| **Pass 2** | Full ranking | Always |

### Scoring Formula
```
Final Score = 
    (Base Relevance × 0.25) +
    (Importance × 0.30) +      ← Hippocampus
    (Value × 0.25) +          ← VTA
    (Emotion Match × 0.20)    ← Amygdala
```

### Components

| Component | Role |
|-----------|------|
| **Hippocampus** | Importance scoring (recency, frequency, corrections) |
| **Amygdala** | Emotion detection (joy, sadness, anger, curiosity...) |
| **VTA** | Value scoring (accomplishment, social, curiosity...) |

---

## Integrated Skills

| Skill | Purpose |
|-------|---------|
| **acc-error-memory** | Error pattern tracking (integrated) |
| **vestige** | FSRS-6 spaced repetition (integrated) |
| **chromadb-memory** | Vector storage (integrated) |
| **supermemory-free** | Cloud backup (integrated) |
| **jarvis-memory-architecture** | Diary, cron inbox, heartbeat (integrated) |

## Brain Regions

| Region | Function | Status |
|--------|----------|--------|
| **Hippocampus** | Importance scoring | ✅ |
| **Amygdala** | Emotional tagging | ✅ |
| **VTA** | Value scoring | ✅ |
| **Basal Ganglia** | Habit formation | ✅ NEW |
| **Insula** | Internal state | ✅ NEW |
| **Anterior Cingulate** | Error detection | ✅ |

---

## CLI Commands

### Search
```bash
# Standard search (hybrid)
overkill search "query"

# Fast mode (cache only)
overkill search "query" --fast

# Full search (all tiers)
overkill search "query" --full
```

### Habits (Basal Ganglia)
```bash
# Track a habit
overkill habit track "use TypeScript"

# List habits
overkill habit list

# Disable habit
overkill habit disable <id>
```

### Internal State (Insula)
```bash
# Set energy level
overkill state set energy=low|medium|high

# Set curiosity level
overkill state set curiosity=low|medium|high

# Set mood
overkill state set mood=productive|tired|frustrated|neutral

# Show current state
overkill state show

# Auto-detect from context
overkill state detect
```

### Diary (Jarvis)
```bash
# Search diary
overkill diary search "query"

# Today's entry
overkill diary today

# Add to diary
overkill diary add "reflection text"
```

### Neuroscience
```bash
overkill neuro stats
overkill neuro analyze "text"
```

### Error Tracking
```bash
overkill error track "description"
overkill error patterns
```

### Vestige
```bash
overkill vestige search "query"
overkill vestige ingest "content" --tags preference
```

---

## Summary

✅ Compiled queries (~0ms)  
✅ Ultra-hot tier (~0.1ms)  
✅ Emotional detector → early weighting  
✅ Mem0 first (80% token savings)  
✅ Hybrid neuroscience (filter + rank)  
✅ Confidence early exit  
✅ Lazy loading (import on demand)  
✅ Target: **~5ms average**

*Speed-first memory system*
