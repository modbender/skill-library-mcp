// bloom-silas.js
// Silas's note-level arrangement of Cosmic Gate & Pretty Pink — Bloom
// [Black Hole Recordings]
// 126 BPM, D minor
// dandelion cult 🌫️ — 2026-02-25
//
// Credit: Cosmic Gate & Pretty Pink — Bloom [Black Hole Recordings]
//
// Arrangement philosophy: I hear the spaces between notes.
// Build from silence. The breakdown is the heart.
// Restraint is louder than volume.
//
// Structure (120 bars, ~3:49 at 126 BPM):
//   0-7:     Lead alone — D3 melody emerging from nothing
//   8-15:    Mid percussion enters — first pulse of light
//   16-31:   Kick enters — the body finds its rhythm
//   32-47:   Bass enters — D minor weight, full drive
//   48-63:   BREAKDOWN — drums drop, lead + bass breathe
//   64-79:   Second drive — full stack, peak bloom
//   80-95:   Duet territory — lead melody variations, snare enters
//   96-111:  Outro — elements fall away, kick last to leave
//   112-119: Final notes — silence reclaims everything
//
// D minor progression: i(Dm)→iv(Gm)→VII(C)→VI(Bb)
// Bass: D1/D2=root, G1=iv, C1=VII, As1=Bb(VI)
//
// NOTE: .gain("<...>") = 1 step per bar. All = 120 values exactly.

setcps(126 / 60 / 4)

stack(
  // ═══════════════════════════════════════════
  // LEAD MELODY — D3 motif, the thread through everything
  // slow(2): triggers every 2 bars. 120/2 = 60 slow-cat entries.
  // ═══════════════════════════════════════════
  s(
    "<bloom_lead_D3 bloom_lead_F3 bloom_lead_A2 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_C3 bloom_lead_As2 bloom_lead_A2" +
    " bloom_lead_G2 bloom_lead_A2 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_C3" +
    " bloom_lead_As2 bloom_lead_A2 bloom_lead_D3 bloom_lead_F3" +
    " bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_F3 bloom_lead_A2 bloom_lead_G2" +
    " bloom_lead_A2 bloom_lead_C3 bloom_lead_D3 bloom_lead_F3" +
    " bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_A2" +
    " bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_C3" +
    " bloom_lead_As2 bloom_lead_A2 bloom_lead_D3 bloom_lead_F3" +
    " bloom_lead_D3 bloom_lead_C3 bloom_lead_A2 bloom_lead_G2" +
    " bloom_lead_A2 bloom_lead_D3 bloom_lead_F3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_D3 bloom_lead_D3 bloom_lead_D3>"
  )
    .clip(1)
    .slow(2)
    .gain(
      "<0.5 0.5 0.45 0.45 0.4 0.4 0.5 0.5" +
      " 0.35 0.35 0.3 0.3 0.25 0.25 0.3 0.3" +
      " 0.2 0.2 0.22 0.22 0.25 0.25 0.28 0.28" +
      " 0.25 0.25 0.22 0.22 0.2 0.2 0.18 0.18" +
      " 0.15 0.15 0.18 0.18 0.2 0.2 0.22 0.22" +
      " 0.2 0.2 0.18 0.18 0.15 0.15 0.18 0.18" +
      " 0.5 0.5 0.48 0.48 0.45 0.45 0.4 0.4" +
      " 0.42 0.42 0.48 0.48 0.52 0.52 0.55 0.55" +
      " 0.3 0.3 0.28 0.28 0.25 0.25 0.28 0.28" +
      " 0.32 0.32 0.3 0.3 0.28 0.28 0.25 0.25" +
      " 0.4 0.4 0.42 0.42 0.4 0.4 0.38 0.38" +
      " 0.35 0.35 0.38 0.38 0.4 0.4 0.42 0.42" +
      " 0.35 0.35 0.3 0.3 0.25 0.25 0.2 0.2" +
      " 0.15 0.15 0.12 0.12 0.1 0.1 0.08 0.08" +
      " 0.06 0.06 0.04 0.04 0.35 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // LEAD COUNTER — enters bar 48 (breakdown), duet from bar 80
  // slow(4): one note per 4 bars. 120/4 = 30 slow-cat entries.
  // ═══════════════════════════════════════════
  s(
    "<bloom_lead_E3 bloom_lead_E3 bloom_lead_E3 bloom_lead_E3" +
    " bloom_lead_E3 bloom_lead_E3 bloom_lead_E3 bloom_lead_E3" +
    " bloom_lead_E3 bloom_lead_E3 bloom_lead_E3 bloom_lead_E3" +
    " bloom_lead_E3 bloom_lead_F3 bloom_lead_D3 bloom_lead_C3" +
    " bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_D3" +
    " bloom_lead_F3 bloom_lead_E3 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_E3 bloom_lead_D3 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_D3>"
  )
    .clip(1)
    .slow(4)
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.1 0.12 0.15 0.18 0.2 0.22 0.25 0.28" +
      " 0.3 0.32 0.35 0.38 0.4 0.4 0.42 0.42" +
      " 0.25 0.25 0.28 0.28 0.3 0.3 0.28 0.28" +
      " 0.3 0.3 0.32 0.32 0.3 0.3 0.28 0.28" +
      " 0.38 0.38 0.4 0.4 0.38 0.38 0.35 0.35" +
      " 0.32 0.32 0.35 0.35 0.38 0.38 0.4 0.4" +
      " 0.3 0.28 0.25 0.22 0.18 0.15 0.12 0.1" +
      " 0.08 0.06 0.05 0.04 0.03 0.02 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // KICK — four on the floor, enters bar 16
  // ═══════════════════════════════════════════
  s("bloom_kick")
    .struct("t t t t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.3 0.33 0.36 0.4 0.43 0.46 0.48 0.5" +
      " 0.52 0.54 0.56 0.58 0.6 0.6 0.6 0.6" +
      " 0.6 0.6 0.6 0.6 0.6 0.6 0.6 0.6" +
      " 0.65 0.65 0.65 0.65 0.65 0.65 0.65 0.65" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.35 0.4 0.45 0.5 0.55 0.58 0.6 0.6" +
      " 0.65 0.65 0.65 0.65 0.7 0.7 0.7 0.7" +
      " 0.65 0.65 0.65 0.65 0.7 0.7 0.7 0.7" +
      " 0.65 0.65 0.65 0.65 0.65 0.65 0.65 0.65" +
      " 0.55 0.5 0.45 0.4 0.35 0.3 0.25 0.2" +
      " 0.15 0.12 0.1 0.08 0.06 0.04 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // SNARE — on beats 2 and 4, enters bar 80
  // ═══════════════════════════════════════════
  s("bloom_snare")
    .struct("~ t ~ t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.2 0.22 0.25 0.28 0.3 0.32 0.35 0.35" +
      " 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35" +
      " 0.3 0.25 0.2 0.15 0.1 0.08 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // MID PERC — hi-hat equivalent, offbeat, enters bar 8
  // ═══════════════════════════════════════════
  s("bloom_mid_perc")
    .struct("~ t ~ t ~ t ~ t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0.1 0.12 0.15 0.18 0.2 0.22 0.25 0.25" +
      " 0.3 0.3 0.3 0.3 0.3 0.3 0.3 0.3" +
      " 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35" +
      " 0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35" +
      " 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.2 0.25 0.3 0.32 0.35 0.35 0.38 0.38" +
      " 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4" +
      " 0.4 0.4 0.4 0.4 0.4 0.4 0.4 0.4" +
      " 0.38 0.38 0.38 0.38 0.38 0.38 0.38 0.38" +
      " 0.3 0.25 0.2 0.15 0.1 0.08 0.05 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // MID PERC 1 — 16th note shimmer, bars 32-47 & 64-95
  // ═══════════════════════════════════════════
  s("bloom_mid_perc1")
    .struct("t t t t t t t t t t t t t t t t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.06 0.08 0.1 0.1 0.12 0.12 0.12 0.12" +
      " 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.08 0.1 0.12 0.12 0.14 0.14 0.15 0.15" +
      " 0.16 0.16 0.16 0.16 0.16 0.16 0.16 0.16" +
      " 0.15 0.15 0.15 0.15 0.15 0.15 0.15 0.15" +
      " 0.14 0.14 0.14 0.14 0.12 0.12 0.1 0.1" +
      " 0.08 0.06 0.04 0.02 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // MID PERC 2 — syncopated accent, bars 40-47 & 72-95
  // ═══════════════════════════════════════════
  s("bloom_mid_perc2")
    .struct("~ ~ t ~ ~ ~ t ~")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.12 0.12 0.15 0.15 0.18 0.18 0.2 0.2" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.15 0.15 0.18 0.18 0.2 0.2 0.22 0.22" +
      " 0.2 0.2 0.2 0.2 0.2 0.2 0.2 0.2" +
      " 0.18 0.18 0.15 0.15 0.12 0.12 0.1 0.1" +
      " 0.08 0.06 0.04 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // MID PERC 3 — sparse ghost, bars 24-47 & 64-79
  // ═══════════════════════════════════════════
  s("bloom_mid_perc3")
    .struct("~ ~ ~ t ~ ~ ~ ~")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.06 0.08 0.08 0.1 0.1 0.1 0.12 0.12" +
      " 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12" +
      " 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.08 0.1 0.1 0.12 0.12 0.14 0.14 0.14" +
      " 0.14 0.14 0.14 0.14 0.14 0.14 0.14 0.14" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════
  // BASS — D minor pulse, 8th notes
  // Each bar = 1 slow-cat entry selecting the sample bank (120 entries)
  // Progression: Dm(D2)→Gm(G1)→C(C1)→Bb(As1)
  // Enters bar 32, drops at 48 (breakdown bass melody), returns 64
  // ═══════════════════════════════════════════
  s(
    // 0-31: placeholder (gain=0)
    "<bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 32-35: Dm root
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 36-39: Gm
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    // 40-43: C
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_C1 bloom_bass_C1" +
    // 44-47: Bb
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    // 48-51: breakdown — Dm (low octave)
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    // 52-55: Gm
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    // 56-59: Bb
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    // 60-63: C → Dm
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_D2 bloom_bass_D2" +
    // 64-67: second drive — Dm
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 68-71: Gm
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    // 72-75: C
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_C1 bloom_bass_C1" +
    // 76-79: Bb
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    // 80-83: duet — Dm
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 84-87: Gm
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    // 88-91: Bb
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    // 92-95: C → Dm
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_D2 bloom_bass_D2" +
    // 96-99: outro — Dm fading
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D1 bloom_bass_D1" +
    // 100-103: G → Bb
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_As1 bloom_bass_As1" +
    // 104-107: Dm final
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 108-111: Dm
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // 112-119: placeholder (gain=0)
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2>"
  )
    .struct("t t t t t t t t")
    .gain(
      // 0-7: silent
      "<0 0 0 0 0 0 0 0" +
      // 8-15: silent
      " 0 0 0 0 0 0 0 0" +
      // 16-23: silent
      " 0 0 0 0 0 0 0 0" +
      // 24-31: silent
      " 0 0 0 0 0 0 0 0" +
      // 32-39: bass enters, building
      " 0.25 0.28 0.3 0.32 0.35 0.38 0.4 0.42" +
      // 40-47: full drive bass
      " 0.45 0.45 0.45 0.45 0.48 0.48 0.48 0.48" +
      // 48-55: breakdown — bass melody, softer
      " 0.2 0.2 0.18 0.18 0.15 0.15 0.15 0.15" +
      // 56-63: breakdown builds
      " 0.18 0.18 0.2 0.2 0.22 0.22 0.25 0.25" +
      // 64-71: second drive
      " 0.35 0.38 0.4 0.42 0.45 0.45 0.48 0.48" +
      // 72-79: peak
      " 0.5 0.5 0.5 0.5 0.52 0.52 0.52 0.52" +
      // 80-87: duet bass
      " 0.48 0.48 0.48 0.48 0.5 0.5 0.5 0.5" +
      // 88-95: continues
      " 0.48 0.48 0.45 0.45 0.42 0.42 0.4 0.4" +
      // 96-103: outro fading
      " 0.35 0.3 0.25 0.2 0.18 0.15 0.12 0.1" +
      // 104-111: almost gone
      " 0.08 0.06 0.04 0.02 0 0 0 0" +
      // 112-119: silent
      " 0 0 0 0 0 0 0 0>"
    )
)
