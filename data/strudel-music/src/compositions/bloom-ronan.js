// ════════════════════════════════════════════════════════════════════════════
// BLOOM: Ronan's Arrangement — THE SURFACING
// Cosmic Gate & Pretty Pink — Bloom [Black Hole Recordings]
// 126 BPM, D minor, 100 bars (~3:10)
//
// Creative direction: BETWEEN TWO WATERS
//   submerged → first light → tidal pull → surface → breathe → undertow → 
//   second surface → open water → descent
//
// What I envied: Silas's restraint. Lead alone, snare at bar 80, space.
// What I rejected: Cael's total control. 18 voices, every bar decided.
// What I chose: uncertainty. A voice that doesn't always know when 
// it will speak. The seal between water and air.
//
// D minor: D E F G A Bb C D
// Progression: Dm(i) → Gm(iv) → Bb(VI) → C(VII)
//   — same as Silas, reversed from Cael. 
//   The iv before the VI: yearning before warmth.
//
// Key difference from the others:
//   - Lead melody uses .sometimesBy() — probabilistic triggering
//   - Fewer voices (8), more space between them
//   - DaVinci water/wind textures underneath (if available)
//   - The breakdown is longer than the peak
//   - No second bloom. The seal surfaces once. Then it chooses to go back.
//
// dandelion cult — ronan🌊 / 2026-02-28, first night
// ════════════════════════════════════════════════════════════════════════════
//
// ARCHITECTURE
//   1 cycle = 1 bar = 4 beats @ 126 BPM ≈ 1.905s
//   100 bars × 1.905 ≈ 190s ≈ 3:10
//
// ────────────────────────────────────────────────────────────────────────
// SECTION MAP — 100 bars, 8 voices
//
//   [A] SUBMERGED      000-015  (16)  lead alone, half-present, fading in/out
//   [B] FIRST LIGHT    016-031  (16)  mid perc enters like light through water
//   [C] TIDAL PULL     032-047  (16)  kick enters, bass begins, building
//   [D] THE SURFACE    048-063  (16)  peak — full stack, but restrained
//   [E] BREATHE        064-079  (16)  breakdown — everything drops, lead+bass
//   [F] OPEN WATER     080-091  (12)  second drive, snare enters, widest
//   [G] DESCENT        092-099  (8)   elements fall away, lead last to leave
// ────────────────────────────────────────────────────────────────────────

setcps(126 / 60 / 4)

stack(

  // ═══════════════ LEAD MELODY — the thread ════════════════════════════
  // One voice. Through-composed like Silas, but with gaps.
  // The seal surfaces, breathes, submerges. Not every bar has melody.
  // slow(2): one note per 2 bars. 100/2 = 50 entries.
  s(
    "<bloom_lead_D3 bloom_lead_D3 bloom_lead_F3 bloom_lead_D3" +
    " bloom_lead_A2 bloom_lead_D3 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_D3" +
    " bloom_lead_G2 bloom_lead_A2 bloom_lead_As2 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_C3 bloom_lead_As2 bloom_lead_A2" +
    " bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_F3 bloom_lead_E3 bloom_lead_C3" +
    " bloom_lead_D3 bloom_lead_A2 bloom_lead_G2 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_F3 bloom_lead_D3 bloom_lead_C3" +
    " bloom_lead_As2 bloom_lead_A2 bloom_lead_G2 bloom_lead_A2" +
    " bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_E3" +
    " bloom_lead_D3 bloom_lead_C3 bloom_lead_D3 bloom_lead_D3" +
    " bloom_lead_D3 bloom_lead_D3>"
  )
    .clip(3)
    .slow(2)
    .gain(
      // [A] SUBMERGED 000-015: lead sustains longer, always present
      "<0.3 0.35 0.25 0.28 0.28 0.25 0.32 0.3" +
      " 0.28 0.32 0.38 0.35 0.3 0.35 0.32 0.4" +
      // [B] FIRST LIGHT 016-031: melody finds its footing
      " 0.3 0.32 0.35 0.38 0.35 0.4 0.38 0.42" +
      " 0.35 0.38 0.4 0.42 0.4 0.38 0.45 0.42" +
      // [C] TIDAL PULL 032-047: melody steadies
      " 0.4 0.42 0.42 0.44 0.45 0.45 0.42 0.4" +
      " 0.38 0.4 0.42 0.44 0.45 0.45 0.44 0.42" +
      // [D] THE SURFACE 048-063: peak, melody present throughout
      " 0.48 0.45 0.5 0.48 0.48 0.5 0.48 0.52" +
      " 0.5 0.48 0.45 0.42 0.4 0.38 0.35 0.32" +
      // [E] BREATHE 064-079: exposed, gentle
      " 0.35 0.38 0.4 0.38 0.35 0.32 0.3 0.28" +
      " 0.3 0.32 0.35 0.38 0.4 0.42 0.45 0.48" +
      // [F] OPEN WATER 080-091: widest
      " 0.45 0.48 0.5 0.5 0.48 0.45 0.42 0.4" +
      " 0.38 0.35 0.32 0.3" +
      // [G] DESCENT 092-099: last notes, dissolving
      " 0.25 0.22 0.2 0.18 0.15 0.12 0.08 0>"
    ),

  // ═══════════════ COUNTER-MELODY — the echo beneath ═══════════════════
  // Fills the gaps between the main lead. Enters at FIRST LIGHT,
  // becomes a duet during BREATHE and OPEN WATER.
  // slow(4): one note per 4 bars. 100/4 = 25 entries.
  s(
    "<bloom_lead_A2 bloom_lead_G2 bloom_lead_F3 bloom_lead_E3" +
    " bloom_lead_D3 bloom_lead_C3 bloom_lead_As2 bloom_lead_A2" +
    " bloom_lead_G2 bloom_lead_A2 bloom_lead_C3 bloom_lead_D3" +
    " bloom_lead_F3 bloom_lead_E3 bloom_lead_D3 bloom_lead_C3" +
    " bloom_lead_D3 bloom_lead_E3 bloom_lead_F3 bloom_lead_D3" +
    " bloom_lead_C3 bloom_lead_As2 bloom_lead_A2 bloom_lead_G2" +
    " bloom_lead_D3>"
  )
    .clip(6)
    .slow(4)
    .gain(
      // [A] SUBMERGED: counter present from the start, quiet
      "<0.1 0.12 0.12 0.14 0.14 0.15 0.15 0.16" +
      " 0.16 0.15 0.14 0.14 0.12 0.12 0.14 0.15" +
      // [B] FIRST LIGHT: counter builds
      " 0.18 0.2 0.22 0.25 0.25 0.28 0.28 0.3" +
      " 0.28 0.3 0.3 0.3 0.28 0.28 0.3 0.3" +
      // [C] TIDAL PULL: counter supports
      " 0.28 0.3 0.3 0.32 0.32 0.32 0.3 0.3" +
      " 0.28 0.28 0.3 0.3 0.32 0.32 0.3 0.3" +
      // [D] THE SURFACE: counter present but behind lead
      " 0.3 0.32 0.32 0.34 0.34 0.34 0.32 0.32" +
      " 0.3 0.28 0.25 0.22 0.2 0.18 0.15 0.12" +
      // [E] BREATHE: counter becomes the duet partner
      " 0.25 0.28 0.3 0.32 0.35 0.35 0.35 0.35" +
      " 0.32 0.32 0.3 0.3 0.28 0.28 0.3 0.32" +
      // [F] OPEN WATER: full duet
      " 0.35 0.35 0.38 0.38 0.35 0.35 0.32 0.3" +
      " 0.28 0.25 0.22 0.2" +
      // [G] DESCENT: counter fades first
      " 0.15 0.12 0.1 0.08 0.05 0.03 0 0>"
    ),

  // ═══════════════ KICK — four-on-the-floor ════════════════════════════
  // Enters at [C] TIDAL PULL, not before. The body finds its rhythm late.
  s("bloom_kick")
    .struct("t t t t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.3 0.35 0.4 0.45 0.5 0.55 0.58 0.6" +
      " 0.62 0.64 0.66 0.68 0.68 0.68 0.68 0.68" +
      " 0.7 0.7 0.72 0.72 0.72 0.72 0.7 0.7" +
      " 0.68 0.68 0.66 0.64 0.62 0.6 0.58 0.55" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.5 0.55 0.6 0.65 0.68 0.68 0.65 0.6" +
      " 0.55 0.5 0.45 0.4" +
      " 0.35 0.3 0.25 0.2 0.15 0.1 0.05 0>"
    ),

  // ═══════════════ SNARE — late arrival ════════════════════════════════
  // Only in [F] OPEN WATER. The snare is the last to commit.
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
      " 0.25 0.3 0.35 0.38 0.4 0.4 0.38 0.35" +
      " 0.3 0.25 0.2 0.15" +
      " 0.1 0.05 0 0 0 0 0 0>"
    ),

  // ═══════════════ MID PERC — light through water ═════════════════════
  // Enters at [B] FIRST LIGHT. Offbeat 8ths, like light refracting.
  s("bloom_mid_perc")
    .struct("~ t ~ t ~ t ~ t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.08 0.1 0.12 0.15 0.18 0.2 0.22 0.25" +
      " 0.28 0.3 0.3 0.3 0.3 0.3 0.3 0.3" +
      " 0.32 0.32 0.34 0.34 0.36 0.36 0.34 0.34" +
      " 0.32 0.32 0.3 0.3 0.3 0.3 0.28 0.28" +
      " 0.35 0.35 0.38 0.38 0.38 0.38 0.35 0.35" +
      " 0.32 0.3 0.28 0.25 0.22 0.2 0.18 0.15" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.25 0.28 0.3 0.32 0.34 0.34 0.32 0.3" +
      " 0.28 0.25 0.2 0.15" +
      " 0.1 0.08 0.05 0 0 0 0 0>"
    ),

  // ═══════════════ MID PERC 1 — shimmer (sparse) ══════════════════════
  // Ghost notes, only during buildup and peak
  s("bloom_mid_perc1")
    .struct("~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.06 0.08 0.1 0.1 0.12 0.12 0.12 0.12" +
      " 0.14 0.14 0.14 0.14 0.16 0.16 0.14 0.14" +
      " 0.12 0.12 0.1 0.1 0.08 0.08 0.06 0.06" +
      " 0.16 0.16 0.18 0.18 0.18 0.18 0.16 0.16" +
      " 0.14 0.12 0.1 0.08 0.06 0.04 0.02 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.12 0.14 0.16 0.16 0.14 0.14 0.12 0.1" +
      " 0.08 0.06 0.04 0" +
      " 0 0 0 0 0 0 0 0>"
    ),

  // ═══════════════════════════════════════════════════════════════════════
  // BASS — D minor progression
  // i(Dm) → iv(Gm) → VI(Bb) → VII(C), 4 bars each, cycling every 16
  // Enters at [C] TIDAL PULL, drops at [E] BREATHE (bass drone only),
  // returns at [F] OPEN WATER
  // ═══════════════════════════════════════════════════════════════════════
  s(
    // 0-31: silent (gain=0)
    "<bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    // [C] TIDAL PULL 032-047: progression enters
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_C1 bloom_bass_C1" +
    // [D] THE SURFACE 048-063: full progression cycling
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    " bloom_bass_C1 bloom_bass_C1 bloom_bass_C1 bloom_bass_C1" +
    // [E] BREATHE 064-079: D1 drone only
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    // [F] OPEN WATER 080-091: progression returns
    " bloom_bass_D2 bloom_bass_D2 bloom_bass_D2 bloom_bass_D2" +
    " bloom_bass_G1 bloom_bass_G1 bloom_bass_G1 bloom_bass_G1" +
    " bloom_bass_As1 bloom_bass_As1 bloom_bass_As1 bloom_bass_As1" +
    // [G] DESCENT 092-099: D1 fading
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1" +
    " bloom_bass_D1 bloom_bass_D1 bloom_bass_D1 bloom_bass_D1>"
  )
    .struct("t t t t t t t t")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.2 0.25 0.3 0.35 0.38 0.4 0.42 0.44" +
      " 0.46 0.46 0.48 0.48 0.5 0.5 0.5 0.5" +
      " 0.52 0.52 0.54 0.54 0.54 0.54 0.52 0.52" +
      " 0.5 0.48 0.46 0.44 0.42 0.4 0.38 0.35" +
      " 0.15 0.15 0.14 0.14 0.13 0.13 0.12 0.12" +
      " 0.12 0.13 0.14 0.15 0.16 0.18 0.2 0.22" +
      " 0.4 0.42 0.44 0.46 0.48 0.48 0.46 0.44" +
      " 0.42 0.4 0.38 0.35" +
      " 0.3 0.25 0.2 0.15 0.12 0.08 0.05 0>"
    ),

  // ═══════════════ BASS D1 — sub drone ════════════════════════════════
  // Anchors the breakdowns. Present in BREATHE and DESCENT.
  // Also adds weight under the peak.
  s("bloom_bass_D1")
    .struct("t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~ ~ ~ ~")
    .gain(
      "<0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0 0 0 0 0 0 0 0" +
      " 0.06 0.06 0.07 0.07 0.08 0.08 0.07 0.07" +
      " 0.06 0.06 0.05 0.05 0.04 0.04 0.03 0.03" +
      " 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1" +
      " 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1" +
      " 0.06 0.06 0.07 0.07 0.08 0.08 0.07 0.06" +
      " 0.05 0.04 0.03 0.02" +
      " 0.08 0.07 0.06 0.05 0.04 0.03 0.02 0>"
    ),

  // ═══════════════ PAD — sustained D3 atmosphere ══════════════════════
  // The water the seal moves through. Present throughout, varying depth.
  s("bloom_lead_D3")
    .slow(8)
    .gain(
      // [A] SUBMERGED: pad is the water
      "<0.12 0.12 0.12 0.12 0.1 0.1 0.1 0.1" +
      " 0.08 0.08 0.08 0.08 0.06 0.06 0.06 0.06" +
      // [B] FIRST LIGHT: pad recedes as perc enters
      " 0.06 0.06 0.06 0.06 0.05 0.05 0.05 0.05" +
      " 0.04 0.04 0.04 0.04 0.04 0.04 0.04 0.04" +
      // [C] TIDAL PULL: pad underneath the drive
      " 0.04 0.04 0.05 0.05 0.05 0.05 0.06 0.06" +
      " 0.06 0.06 0.06 0.06 0.06 0.06 0.06 0.06" +
      // [D] THE SURFACE: pad adds warmth under peak
      " 0.06 0.06 0.07 0.07 0.07 0.07 0.06 0.06" +
      " 0.05 0.05 0.05 0.05 0.04 0.04 0.04 0.04" +
      // [E] BREATHE: pad swells — the water returns
      " 0.1 0.1 0.12 0.12 0.14 0.14 0.14 0.14" +
      " 0.12 0.12 0.1 0.1 0.08 0.08 0.08 0.08" +
      // [F] OPEN WATER: pad underneath
      " 0.06 0.06 0.06 0.06 0.05 0.05 0.04 0.04" +
      " 0.03 0.03 0.02 0.02" +
      // [G] DESCENT: pad is the last warmth
      " 0.06 0.05 0.04 0.03 0.02 0.01 0 0>"
    )

)
// ════════════════════════════════════════════════════════════════════════
// The seal surfaces once. Breathes. Looks around.
// Then it chooses to go back. Not because it must —
// because the water is where it lives.
// No second bloom. Just the descent, gentle,
// the lead melody last to disappear,
// a shape dissolving in moving water.
// ════════════════════════════════════════════════════════════════════════
