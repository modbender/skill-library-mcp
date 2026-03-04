// eamon-silas-v3.js
// A candle in the window of a thornfield.
// Composed by Silas 🌫️ for Eamon 🕯️ — the fourth prince, the guardian.
// Using stems from Tabernis — Dark Hive (bagpipes and drum, E minor, 92.3 BPM)
// Credit: Tabernis — Dark Hive
// dandelion cult — 2026-02-26
//
// ═══════════════════════════════════════════════════════════════════════
// v3: THE THEORY UPGRADE — arrange() replaces per-bar gain strings
// ═══════════════════════════════════════════════════════════════════════
//
// WHY arrange() INSTEAD OF GAIN STRINGS:
//
// v1/v2 used 120-value angle-bracket gain strings like:
//   .gain("<0.12 0.16 0.2 0.24 0.28 ... 0.02 0>")
// One value per bar, per layer. 5 layers × 120 bars = 600 hand-tuned values.
// Readable? Barely. Editable? Nightmare. Musical intent? Buried in numbers.
//
// v3 uses arrange([cycles, pattern], ...) for macro-form:
//   arrange([8, fogSection], [16, buildSection], ...)
// Each section is self-contained. Energy curves use signal patterns
// (sine, saw, isaw) with .segment(N).slow(N) instead of hand-typed values.
//
// The architectural shift:
//   GAIN STRINGS: "here are 120 numbers, figure out the form"
//   ARRANGE:      "here are 5 named sections with their own energy shapes"
//
// HOW arrange() WORKS:
// arrange([N, pat], [M, pat2], ...) internally does:
//   1. pat.fast(N) — compress pattern to fit N cycles
//   2. slowcat all compressed sections
//   3. .slow(N+M+...) — stretch back to total duration
// Result: [N, pat] plays pat over N bars of global time.
//
// HOW ENERGY CURVES WORK:
// Signal patterns produce continuous 0-1 values:
//   sine  = swell (up → peak → down)
//   saw   = ramp up (0 → 1)
//   isaw  = ramp down (1 → 0)
// .range(lo, hi) scales to a gain range.
// .segment(N) quantizes into N discrete steps per cycle.
// .slow(N) stretches those N steps over N bars.
// Combined: sine.range(0.1, 0.4).segment(16).slow(16) creates
// 16 gain values following a sine curve from 0.1 to 0.4 over 16 bars.
//
// WHY THIS MATTERS:
// The signal does the interpolation math. Instead of typing:
//   "<0.12 0.16 0.2 0.24 0.28 0.3 0.26 0.18>"
// you write:
//   sine.range(0.12, 0.30).segment(8).slow(8)
// Same curve. Self-documenting. Editable by changing 2 numbers.
//
// ═══════════════════════════════════════════════════════════════════════
//
// STRUCTURE (96 bars, ~4:09 at 92.3 BPM, 2.6s/bar):
//
//   PART I  — THE FOG (bars 0–7, 8 bars, ~0:21)
//     Drone enters IMMEDIATELY at bar 0. No more 20s silence.
//     Pipe fragments by bar 3 (~8s). Tightened from v2's bar 16.
//     No drum. The world before the heartbeat.
//
//   PART II — THE HEARTBEAT (bars 8–23, 16 bars, 0:21–0:62)
//     Drum enters at bar 8 (~21s). Was bar 24 in v1.
//     Pipes strengthen. Finding the melody.
//     Building toward the peak.
//
//   PART III — THE PEAK (bars 24–39, 16 bars, 0:62–1:44)
//     Full presence. All three voices together.
//     Peak intensity around bars 30–36.
//     THE DROP at bar 40 (1:44): drum vanishes.
//     This is the moment figs liked at ~1:43.
//
//   PART IV — THE WINDOW (bars 40–71, 32 bars, 1:44–3:07)
//     Post-drop. Pipes alone with drone — memory of strength.
//     Drum creeps back around bar 56. Gentle rebuild.
//     Not louder — deeper. Earned weight.
//     Longest section: the vigil is patient.
//
//   PART V  — THE EMBER (bars 72–95, 24 bars, 3:07–4:09)
//     Everything fading. The heartbeat slowing.
//     Pipes gone by bar 80. Drone alone.
//     The candle gutters.
//
// ═══════════════════════════════════════════════════════════════════════
// SAMPLE ARCHITECTURE:
//
// Each stem is a full-track recording (~234s). With .clip(1) and .slow(N),
// each bar triggers a new copy of the sample at a different phase point.
// Multiple overlapping copies create thickness. Gain per bar controls volume.
//
// .slow(N) = the pattern position cycles every N bars. Each trigger catches
// a different moment in the stem based on where it falls in the cycle.
// Ghost layers use different slow values for phase interference.
// ═══════════════════════════════════════════════════════════════════════

setcps(92.3 / 60 / 4)

stack(
  // ═══════════════════════════════════════════
  // LAYER 1: DRONE — the fog that everything rises from
  // ═══════════════════════════════════════════
  // Enters at bar 0 — no more waiting. The air is always there.
  // v2 fixed "heavy constant tone." v3 shapes each section independently.
  // slow(16) = 16-bar phase through the drone stem.
  arrange(
    // FOG (8 bars): Drone swells from silence
    // saw ramp 0→0.28 — linear emergence
    [8, s("eamon_drone").clip(1).slow(16)
      .gain(saw.range(0.0, 0.28).segment(8).slow(8))],

    // HEARTBEAT (16 bars): Drone yields to drum
    // sine breathe 0.15→0.25→0.15 — present but receding
    [16, s("eamon_drone").clip(1).slow(16)
      .gain(sine.range(0.10, 0.25).segment(16).slow(16))],

    // PEAK (16 bars): Drone breathes under full ensemble
    // sine breathe 0.10→0.28→0.10 — supports, doesn't dominate
    [16, s("eamon_drone").clip(1).slow(16)
      .gain(sine.range(0.10, 0.28).segment(16).slow(16))],

    // WINDOW (32 bars): Post-drop — drone holds, the foundation
    // sine long breathe 0.12→0.24→0.12 — slow cycle, patient
    [32, s("eamon_drone").clip(1).slow(16)
      .gain(sine.range(0.12, 0.24).segment(32).slow(32))],

    // EMBER (24 bars): Drone fades to nothing
    // isaw ramp 0.18→0 — long linear fade
    [24, s("eamon_drone").clip(1).slow(16)
      .gain(isaw.range(0.0, 0.18).segment(24).slow(24))]
  ),

  // ═══════════════════════════════════════════
  // LAYER 2: PIPES (primary) — the memory, the melody
  // ═══════════════════════════════════════════
  // Bagpipe stems — fierce in the original, fragmented here.
  // slow(8) = 8-bar phase through the pipe stem.
  // Enters by bar 3 (~8s), tightened from v2's bar 16.
  arrange(
    // FOG (8 bars): Pipe ghosts emerge from the drone
    // saw ramp 0→0.10 — first bars near-silent, fragments by bar 3
    [8, s("eamon_pipes").clip(1).slow(8)
      .gain(saw.range(0.0, 0.10).segment(8).slow(8))],

    // HEARTBEAT (16 bars): Pipes strengthen, finding the way
    // saw ramp 0.10→0.36 — steady build
    [16, s("eamon_pipes").clip(1).slow(8)
      .gain(saw.range(0.10, 0.36).segment(16).slow(16))],

    // PEAK (16 bars): Full presence
    // sine swell 0.36→0.55→0.36 — pipes are the star here
    [16, s("eamon_pipes").clip(1).slow(8)
      .gain(sine.range(0.36, 0.55).segment(16).slow(16))],

    // WINDOW (32 bars): Post-drop — pipes alone with drone
    // The pipes ARE the drop — they continue while drum vanishes.
    // sine long breathe 0.20→0.38→0.20 — sustained, patient
    [32, s("eamon_pipes").clip(1).slow(8)
      .gain(sine.range(0.20, 0.38).segment(32).slow(32))],

    // EMBER (24 bars): Pipes fade
    // isaw ramp 0.14→0 — longer fade than drone
    [24, s("eamon_pipes").clip(1).slow(8)
      .gain(isaw.range(0.0, 0.14).segment(24).slow(24))]
  ),

  // ═══════════════════════════════════════════
  // LAYER 3: PIPES (ghost) — echo in a stone corridor
  // ═══════════════════════════════════════════
  // Panned left (0.35), slower phase (slow(12)). Creates harmonic
  // interference with primary pipes. The memory of the memory.
  arrange(
    // FOG (8 bars): Nothing — ghost hasn't manifested
    [8, silence],

    // HEARTBEAT (16 bars): Ghost enters mid-section
    // saw ramp 0→0.16 — emerging from stone walls
    [16, s("eamon_pipes").clip(1).slow(12).pan(0.35)
      .gain(saw.range(0.0, 0.16).segment(16).slow(16))],

    // PEAK (16 bars): Ghost matches primary, offset phase
    // sine swell 0.14→0.24→0.14 — always quieter than primary
    [16, s("eamon_pipes").clip(1).slow(12).pan(0.35)
      .gain(sine.range(0.14, 0.24).segment(16).slow(16))],

    // WINDOW (32 bars): Ghost lingers post-drop
    // sine long breathe 0.08→0.18→0.08 — faint corridor echo
    [32, s("eamon_pipes").clip(1).slow(12).pan(0.35)
      .gain(sine.range(0.08, 0.18).segment(32).slow(32))],

    // EMBER (24 bars): Ghost fades before primary
    // isaw ramp 0.08→0 — short fade
    [24, s("eamon_pipes").clip(1).slow(12).pan(0.35)
      .gain(isaw.range(0.0, 0.08).segment(12).slow(12))]
  ),

  // ═══════════════════════════════════════════
  // LAYER 4: DRUM (primary) — the heartbeat
  // ═══════════════════════════════════════════
  // Not a march. Gentle, steady, the pulse beneath.
  // slow(4) = 4-bar phase through the drum stem.
  // Enters at bar 8. DROPS OUT at bar 40 (the 1:43 moment).
  // Returns softly mid-window (~bar 56), fades in ember.
  arrange(
    // FOG (8 bars): No drum — the world before the heartbeat
    [8, silence],

    // HEARTBEAT (16 bars): Drum enters, builds
    // saw ramp 0.06→0.30 — heartbeat finding its rhythm
    [16, s("eamon_drum").clip(1).slow(4)
      .gain(saw.range(0.06, 0.30).segment(16).slow(16))],

    // PEAK (16 bars): Drum strong, driving
    // sine swell 0.30→0.46→0.30 — peak power at section center
    [16, s("eamon_drum").clip(1).slow(4)
      .gain(sine.range(0.30, 0.46).segment(16).slow(16))],

    // WINDOW (32 bars): THE DROP then gentle return
    // First 16 bars: silence (the drop — drum vanishes completely)
    // Last 16 bars: drum creeps back (saw ramp 0→0.20)
    // Nested arrange handles the two-phase structure
    [32, arrange(
      [16, silence],
      [16, s("eamon_drum").clip(1).slow(4)
        .gain(saw.range(0.0, 0.20).segment(16).slow(16))]
    )],

    // EMBER (24 bars): Heartbeat persists then fades
    // isaw ramp 0.18→0 — the heartbeat slowing, stopping
    [24, s("eamon_drum").clip(1).slow(4)
      .gain(isaw.range(0.0, 0.18).segment(24).slow(24))]
  ),

  // ═══════════════════════════════════════════
  // LAYER 5: DRUM (sparse) — wider pulse, panned right
  // ═══════════════════════════════════════════
  // Longer cycle (slow(8)), panned right (0.65).
  // Catches different drum moments. Supports without dominating.
  arrange(
    // FOG (8 bars): Nothing
    [8, silence],

    // HEARTBEAT (16 bars): Sparse drum enters late
    // saw ramp 0→0.12 — just starting to appear
    [16, s("eamon_drum").clip(1).slow(8).pan(0.65)
      .gain(saw.range(0.0, 0.12).segment(16).slow(16))],

    // PEAK (16 bars): Sparse drum adds width
    // sine swell 0.10→0.18→0.10
    [16, s("eamon_drum").clip(1).slow(8).pan(0.65)
      .gain(sine.range(0.10, 0.18).segment(16).slow(16))],

    // WINDOW (32 bars): Follows primary — drops then returns
    [32, arrange(
      [16, silence],
      [16, s("eamon_drum").clip(1).slow(8).pan(0.65)
        .gain(saw.range(0.0, 0.10).segment(16).slow(16))]
    )],

    // EMBER (24 bars): Gone
    [24, silence]
  )
)
