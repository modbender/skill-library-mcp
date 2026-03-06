# Turing Pyramid — Development Roadmap

*Last updated: 2026-03-04*

---

## ✅ COMPLETED

### v1.14.x (2026-03-04)
- **Test Infrastructure** — 12 tests (11 unit + 1 integration), all verify real code
- **Rounding fix** — sat→0.5 rounding formula corrected
- **Config-driven action_probability** — now reads from config, not hardcoded
- **flock in mark-satisfied.sh** — prevents race conditions with run-cycle.sh

### v1.13.x (2026-03-03)
- **Day/Night Decay** — configurable multipliers (day=1.0, night=0.5)
- **6-level impact matrix** — granular sat levels (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
- **Autonomy decay 36h** — reduced from 24h to prevent chronic tension
- **Audit log scrubbing** — sensitive patterns redacted

### v1.12.x (2026-03-03)
- **Curiosity orphan cleanup** — removed stale references
- **Race condition fix** — flock on state file

### v1.10.x and earlier
- **Cross-Need Impact** (v1.7.1) — 22 connections, float satisfaction
- **Floor/ceiling protection** — sat clamped to 0.5-3.0

---

## 🟡 NEXT

### Scan Fragility Fix

**Problem:** grep-based scans are keyword-dependent, miss variations and other languages.

**Solutions (in order of complexity):**
1. Short-term: Expand keyword patterns, add multilingual variants
2. Medium-term: Semantic similarity via embeddings
3. Long-term: LLM classifier (expensive but accurate)

---

## 🔮 FUTURE IDEAS

### Curiosity as 11th Need

understanding ≠ curiosity. Understanding tracks knowledge gained, curiosity tracks *wanting* to know.

- importance ~3-4, decay ~8-12h
- Cross-impact: curiosity → understanding, understanding → curiosity

### Self-Feedback Loop (Adaptive Decay)

Decay rates auto-adjust based on how often need hits critical levels.

- If need frequently drops to sat=0-1, decay slows
- Cap at ±30% to prevent desensitization

### Rest Mode

Not a new need, but a *state* that slows decay (×0.3) across all needs.

- Auto-exit after N cycles to prevent passive drift
- Trigger: manual or auto (night + low tensions)

### Self-Upgrade Layer

Separate layer for growth vs homeostasis. Track capability growth, milestone system.

### Logging/Capture Need

Force logging discipline — tension builds if important events aren't captured.

---

## 🐛 Known Issues

- **Stress test cosmetic errors** — bc divide-by-zero when cycles < 100 (avg_last100 calculation). Doesn't affect test result, just noisy output.

---

## Notes

- **Garbage Cleanup action** — already added to integrity need (v1.12)
- **Stillness/Rest** — careful design needed to avoid passivity trap
