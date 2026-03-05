# Strudel Composition Guide

Practical lessons from building compositions in Strudel. This isn't music theory — it's "here's what the tool actually does and how to not blow it up."

---

## The Big One: Space-Separated vs Angle-Bracket Patterns

This is the single most important thing to understand about Strudel mini-notation. Getting it wrong doesn't produce a subtle bug — it produces distortion, 2400+ events per cycle, and out-of-memory crashes.

### The Rule

| Syntax | What it does | 4 values = | 170 values = |
|--------|-------------|------------|--------------|
| `"a b c d"` | All values subdivide **one cycle** | 4 events per cycle | 170 events per cycle (💥) |
| `"<a b c d>"` | One value **per cycle** (slow cat) | 1 event/cycle, rotates over 4 cycles | 1 event/cycle, rotates over 170 cycles |

**Space-separated** = subdivision. Every value plays within a single cycle (bar). The cycle gets carved into equal slices.

**Angle-bracket** = alternation. One value per cycle, advancing through the list. Cycle 0 gets value 0, cycle 1 gets value 1, etc.

### Examples

```javascript
// Space-separated: all 4 notes play in every bar
note("c3 e3 g3 b3")
// → 4 notes per cycle, always

// Angle-bracket: one note per bar, rotating
note("<c3 e3 g3 b3>")
// → bar 0: c3, bar 1: e3, bar 2: g3, bar 3: b3, bar 4: c3 (wraps)
```

---

## Case Study: The Frisson Disaster

During the Solarstone — Pure Trance 477 (Frisson) composition, we hit every variant of this bug. Here's what happened and why.

### Bug 1: Gain Explosion

**What we did:** Generated 170 per-bar gain values and put them space-separated:

```javascript
// WRONG — all 170 values subdivide ONE cycle
.gain("0.3 0.5 0.7 0.9 0.4 0.6 ...")  // 170 space-separated values
```

**What happened:** Every single cycle contained 170 gain changes. Combined across multiple layers, this produced 2400+ haps (events) per cycle. The audio distorted. Memory usage spiked. The composition was unplayable.

**The fix:**

```javascript
// RIGHT — one gain value per cycle
.gain("<0.3 0.5 0.7 0.9 0.4 0.6 ...>")  // 170 angle-bracket values
```

Now each bar gets exactly one gain value. Bar 0 = 0.3, bar 1 = 0.5, etc.

### Bug 2: The Wrapping Trap

**What we did:** Had a 44-value gain pattern for a 170-cycle composition:

```javascript
.gain("<0.3 0.5 0.7 ... 0.4>")  // only 44 values, but 170 bars
```

**What happened:** Angle-bracket patterns **wrap** when they run out of values. Bar 44 replayed value 0. Bar 128 played value `128 mod 44 = 40`. The gain envelope was completely wrong for the second half of the track — crescendos happened at random points, the climax section was quiet.

**The fix:** Always match your `<>` value count to your total cycle count:

```javascript
// 170 bars → 170 values
.gain("<v0 v1 v2 ... v169>")  // exactly 170 values
```

### Bug 3: `.slow()` Interaction

**What we did:** Applied `.slow(4)` to a pattern with angle-bracket gain:

```javascript
note("<c3 e3 g3>")
  .gain("<0.3 0.7 1.0>")
  .slow(4)
```

**What we expected:** Each note lasts 4 bars, each gain lasts 4 bars.

**What actually happened:** The `<>` sequences at the **base cycle rate**, not the slowed rate. `.slow(4)` stretches the pattern so one cycle spans 4 bars — but the `<>` still advances once per *base* cycle. So:

- Bars 0–3: one slowed cycle → `<>` index 0 → note c3, gain 0.3
- Bars 4–7: one slowed cycle → `<>` index 1 → note e3, gain 0.7
- Bars 8–11: one slowed cycle → `<>` index 2 → note g3, gain 1.0

Each value spans 4 bars because `.slow(4)` makes one cycle = 4 bars.

**If you want per-bar control with `.slow(4)`**, repeat each value N times:

```javascript
.gain("<0.3 0.3 0.3 0.3 0.7 0.7 0.7 0.7 1.0 1.0 1.0 1.0>")
```

Now each bar within the slowed cycle gets its own gain entry.

---

## How to Verify Your Patterns

### 1. Count your values

Before rendering, count the values inside your `<>`:

```bash
# Quick count — paste your pattern and count spaces + 1
echo "<0.3 0.5 0.7 ...>" | tr ' ' '\n' | wc -l
```

### 2. Match to cycle count

Your composition's total cycles = total bars (at base tempo). If you're rendering 170 bars:
- Every `<>` gain/filter/control pattern should have exactly 170 values
- Or a number that divides evenly into 170 (if you want intentional repetition)

### 3. Check for hap explosion

If your composition sounds distorted or takes forever to render, check the event count. Space-separated values in gain/note patterns are the usual suspect.

### 4. Test with a small slice

Before rendering the full composition, test bars 0–8 with `.late(0).early(8)` or equivalent. Listen for:
- Distortion (too many events)
- Unexpected silence (wrong gain values from wrapping)
- Timing mismatches (`.slow()` interaction)

---

## Quick Reference

| I want... | Use | Example |
|-----------|-----|---------|
| Multiple notes in one bar | Space-separated | `note("c3 e3 g3")` |
| One note per bar, rotating | Angle brackets | `note("<c3 e3 g3>")` |
| Per-bar gain control | Angle brackets | `.gain("<0.3 0.7 1.0>")` |
| A pattern that spans N bars | `.slow(N)` | `note("c3").slow(4)` — c3 for 4 bars |
| Per-bar control inside `.slow(N)` | Repeat values N times in `<>` | `.gain("<0.3 0.3 0.3 0.3 0.7 0.7 0.7 0.7>")` |
| A long automation envelope | `<>` with one value per bar | `.gain("<v0 v1 v2 ... vN>")` — match total bars |

### The Golden Rules

1. **Space = subdivision.** All values play every cycle.
2. **Angle brackets = alternation.** One value per cycle.
3. **`<>` wraps.** If you have fewer values than cycles, it loops. Match your counts.
4. **`.slow()` stretches cycles, not `<>` indices.** One `<>` step per slowed cycle, not per bar.
5. **When in doubt, use `<>` for control patterns** (gain, filter, pan). You almost never want 170 gain changes in a single bar.

---

*Learned the hard way during the Frisson (Solarstone PTR 477) composition, February 2026.*
