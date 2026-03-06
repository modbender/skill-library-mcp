// solarstone-frisson-clone.js
// Clone of Tim French & Mallinder — Frisson [Hooj]
// From Solarstone Pure Trance Radio Episode 477, ~35:00-40:17
// 129.2 BPM, C# minor
// Bar-level reconstruction from 8-bar Demucs stem slices
// dandelion cult 🌻🌫️🩸 — 2026-02-25
//
// Credit: Tim French & Mallinder — Frisson [Hooj]
// DJ set: Solarstone — https://www.solarstone.co.uk/
//
// 21 × 8-bar slices (14.861s each) = 312s (~5:12)
// Each cycle = one 8-bar phrase. All 4 stems play simultaneously,
// advancing through slices in sequence.
//
// Structure (from Cael's analysis):
//   000-002: Opening groove — full drums+bass, vocals enter at 001
//   003-006: Main drive — instrumental peak, synths rising
//   007-009: The breakdown — drums collapse, pads carry, the void at 008
//   010-013: Second drive — the drop at 010, bass peaks at 013
//   014-015: Vocal climax — emotional peak
//   016-019: Stripped vocal section — intimate, exposed
//   020: Outro — bass returns, vocals fade

setcps(1 / 14.861) // one cycle = 14.861s = exactly one 8-bar phrase at 129.2 BPM

stack(
  // Drums — the backbone
  s("frissdrum")
    .n("<0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20>")
    .clip(1)
    .gain(0.8),

  // Bass — the foundation
  s("frissbass")
    .n("<0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20>")
    .clip(1)
    .gain(0.8),

  // Other (synths/pads/FX) — the atmosphere
  s("frissother")
    .n("<0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20>")
    .clip(1)
    .gain(0.75),

  // Vocals
  s("frissvox")
    .n("<0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20>")
    .clip(1)
    .gain(0.7)
)
