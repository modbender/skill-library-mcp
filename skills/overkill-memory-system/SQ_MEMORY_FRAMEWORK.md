# Framework: sq-memory Integration

## Overview

sq-memory provides persistent 11D text storage for OpenClaw agents.⚠️ Flagged as suspicious - needs code review.

---

## What It Does

| Feature | Description |
|---------|-------------|
| Permanent memory | Survives session restarts |
| Cross-session | Share between sessions |
| Multi-agent | Share with other agents |
| Preference storage | Remember user preferences |

---

## How It Works

- Connects to SQ service (self-hosted or hosted)
- Stores as 11D text vectors
- API-based retrieval

---

## Comparison with Our System

| Feature | Our System | sq-memory | Overlap |
|---------|------------|-----------|---------|
| **Persistence** | Yes | Yes | High |
| **Search** | Hybrid | API-based | Medium |
| **Tiers** | 6-tier | Single | None |
| **Brain regions** | Yes | No | None |
| **Learning** | Yes | No | None |

---

## Overlap Analysis

### High Overlap
- Persistent memory storage
- Cross-session recall
- User preferences

### sq-memory is essentially:
- Alternative to our tier storage
- Simpler (no tiers, no brain regions)

---

## Recommendation

### Option 1: Skip (Recommended)
Our system is more comprehensive with:
- 6-tier storage
- Brain regions
- Learning capabilities
- File search

### Option 2: Replace Tiers
Replace tier storage with sq-memory - but loses:
- Tier organization
- Brain region scoring
- Learning features

### Option 3: Use as Backup
Use sq-memory as additional backup layer - but adds complexity

---

## Verdict

**Not needed** - our system already provides what sq-memory offers, plus more.

sq-memory is simpler but less capable than our overkill-memory-system.

---

*sq-memory analysis - overkill-memory-system*
