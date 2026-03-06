// ============================================================================
// BLOOM — Elliott Pipeline Proof (Cosmic Gate & Pretty Pink)
// ============================================================================
// D minor, 126 BPM. 16-bar arrangement: intro → build → drop → outro.
// All samples extracted via Demucs + librosa on Elliott (x86_64).
// ============================================================================

// --- TEMPO ---
// 126 BPM = 126/4 = 31.5 CPM (cycles per minute, 1 cycle = 1 bar)
setcpm(31.5)

// ============================================================================
// 16-bar arrangement with gain envelopes for structure
// ============================================================================

stack(
  // ========================================================================
  // LAYER 1: KICK — four-on-the-floor trance kick
  // Bars 1-4: silent (intro), 5-16: kick
  // ========================================================================
  s("bloom_kick")
    .struct("x ~ ~ ~ x ~ ~ ~ x ~ ~ ~ x ~ ~ ~")
    .gain("<0 0 0 0 0.8 0.8 0.8 0.8 0.85 0.85 0.85 0.85 0.9 0.9 0.9 0.9>"),

  // ========================================================================
  // LAYER 2: SNARE — offbeat accents
  // Bars 1-6: silent, 7-16: snare on beats 2 and 4
  // ========================================================================
  s("bloom_snare")
    .struct("~ ~ ~ x ~ ~ ~ x ~ ~ ~ x ~ ~ ~ x")
    .gain("<0 0 0 0 0 0 0.5 0.5 0.55 0.55 0.6 0.6 0.6 0.6 0.55 0.45>"),

  // ========================================================================
  // LAYER 3: HI-HAT — 16th-note ride from bloom_mid_perc
  // Bars 1-2: sparse, 3-16: building
  // ========================================================================
  s("bloom_mid_perc")
    .struct("x x x x x x x x x x x x x x x x")
    .gain("0.2 0.12 0.25 0.12 0.2 0.12 0.25 0.12 0.2 0.12 0.25 0.12 0.2 0.12 0.25 0.12")
    .mask("<0 0 1 1 1 1 1 1 1 1 1 1 1 1 0 0>"),

  // ========================================================================
  // LAYER 4: PERCUSSION — mid_perc1 offbeat groove
  // ========================================================================
  s("bloom_mid_perc1")
    .struct("~ ~ x ~ ~ ~ x ~ ~ ~ x ~ ~ x ~ ~")
    .gain(0.25)
    .mask("<0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 0>"),

  // ========================================================================
  // LAYER 5: BASS — D minor progression
  // Dm (D) → Bb (As) → C → Gm (G) — classic trance minor progression
  // 4 bars per chord, 8th-note pulse
  // ========================================================================
  s("<bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_D2*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_As1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_C1*8 bloom_bass_G1*8 bloom_bass_G1*8 bloom_bass_G1*8 bloom_bass_G1*8>")
    .gain("<0 0.4 0.5 0.55 0.6 0.6 0.6 0.6 0.65 0.65 0.7 0.7 0.7 0.65 0.5 0.3>"),

  // ========================================================================
  // LAYER 6: LEAD — melodic phrase in D minor
  // Using the "other" stem samples with pitch info
  // Simple motif: D3 → F3 → E3 → D3 → C3 → A2 → As2 → D3
  // ========================================================================
  s("bloom_lead_D3")
    .note(
      "d3 d3 f3 f3 "
      + "e3 e3 d3 d3 "
      + "c3 c3 a2 a2 "
      + "as2 as2 d3 d3 "
    )
    .slow(16)
    .gain("<0 0 0 0 0 0 0 0 0.35 0.38 0.4 0.42 0.45 0.45 0.35 0.2>"),

  // ========================================================================
  // LAYER 7: PAD — bloom_lead used as sustained texture
  // Whole-note D3 pad sustained across bars
  // ========================================================================
  s("bloom_lead_D3")
    .note("d3")
    .slow(4)
    .gain("<0.15 0.18 0.2 0.22 0.25 0.28 0.3 0.3 0.3 0.28 0.25 0.22 0.2 0.18 0.15 0.1>")
)
