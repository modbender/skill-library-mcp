// ════════════════════════════════════════════════════════════════════════════
// WO-FRISSON-2-ZB: Cael's Note-Level Arrangement
// Tim French & Mallinder — Frisson [Hooj]
// 129.2 BPM, C# minor, ~170 bars (5:17)
//
// Creative direction: ARC AND TENSION
//   build → release → rebuild → peak → emotion → stop
//
// This is not Elliott's arrangement. Elliott chose subtlety and space —
// ghost teases, chromatic walks, extended breathing room. Beautiful work.
// But this arrangement chooses the other path: the trance narrative.
// Relentless build. Devastating release. The silence after density
// is the loudest thing in trance. And then — it just stops.
//
// dandelion cult — cael🩸 / 2026-02-25
// ════════════════════════════════════════════════════════════════════════════
//
// ARCHITECTURE
//
// 1 cycle = 1 bar = 4 beats @ 129.2 BPM ≈ 1.858 seconds
// Total: 170 bars ≈ 315.8 seconds ≈ 5:16
//
// Sample mapping (frisson_bass .n() index):
//   0=C#1  1=D1  2=D#1  3=E1  4=F1  5=F#1  6=G1  7=G#1  8=A1  9=A#1
//
// Texture pad (frissother .n() index):
//   0-20 = 8-bar slices of the "other" stem (pads/atmosphere)
//
// ────────────────────────────────────────────────────────────────────────
// SECTION MAP — 170 bars, 8 voices
//
//   [A] THE HYPNOSIS — bars 000-019 (20 bars)
//       Kick alone for 8 bars. Then ghost. Then hat. Then clap+bass.
//       Patient. Hypnotic. Each element a deliberate arrival.
//
//   [B] MAIN DRIVE — bars 020-056 (37 bars)
//       Full density. Pulsing bass. Synth leads enter. Relentless.
//
//   [C] THE FALL — bars 057-076 (20 bars)
//       EVERYTHING drops instantly at bar 057. Pad + bass drone only.
//       Hat riser rebuilds over final 4 bars (073-076).
//
//   [D] SECOND DRIVE — bars 077-113 (37 bars)
//       Harder than before. Bass on E1 (tension). Bar 089 = THE PEAK.
//
//   [E] THE HEART — bars 114-160 (47 bars)
//       Synth_lead_2 solo + ghost kick. Then slow rebuild.
//
//   [F] THE STOP — bars 161-169 (9 bars)
//       Full density. Then silence. No fade.
// ────────────────────────────────────────────────────────────────────────

setcps(129.2 / 60 / 4)

stack(

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 1: KICK — the heartbeat
  // Four-on-the-floor. First sound in the arrangement.
  // Pattern: "t t t t" = 4 quarter notes per bar
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_kick").struct("t t t t").gain(
    "<" +
    // [A] THE HYPNOSIS 000-019
    "0.75 0.75 0.75 0.75 0.75 0.75 0.75 0.75 " + // 000-007: kick alone, steady pulse
    "0.78 0.78 0.78 0.78 " +                       // 008-011: ghost enters, kick holds
    "0.80 0.80 0.80 0.80 " +                       // 012-015: hat enters
    "0.82 0.82 0.82 0.82 " +                       // 016-019: full intro
    // [B] MAIN DRIVE 020-056
    "0.85 0.85 0.85 0.85 0.85 0.85 0.85 0.85 " + // 020-027: full drums engaged
    "0.87 0.87 0.87 0.87 0.87 0.87 0.87 0.87 " + // 028-035: synth lead enters
    "0.90 0.90 0.90 0.90 0.90 0.90 0.90 0.90 " + // 036-043: density climbing
    "0.92 0.92 0.92 0.92 0.92 0.92 0.92 0.92 " + // 044-051: maximum drive
    "0.92 0.92 0.92 0.92 0.92 " +                  // 052-056: relentless
    // [C] THE FALL 057-076 — instant silence
    "0 0 0 0 0 0 0 0 " +                           // 057-064: GONE
    "0 0 0 0 0 0 0 0 " +                           // 065-072: still gone
    "0 0 0 0 " +                                    // 073-076: riser, no kick
    // [D] SECOND DRIVE 077-113
    "0.88 0.88 0.90 0.90 0.90 0.90 0.92 0.92 " + // 077-084: the return
    "0.92 0.95 0.95 0.95 0.95 " +                  // 085-089: building → PEAK
    "0.93 0.93 0.93 0.93 0.93 0.93 0.93 0.93 " + // 090-097: sustained
    "0.90 0.90 0.90 0.90 0.90 0.90 0.90 0.90 " + // 098-105: holding
    "0.88 0.88 0.88 0.88 0.88 0.88 0.88 0.88 " + // 106-113: easing
    // [E] THE HEART 114-160
    "0 0 0 0 0 0 0 0 0 0 " +                       // 114-123: ghost kick only
    "0.50 0.50 0.50 0.50 0.55 0.55 0.55 0.55 " + // 124-131: gentle return
    "0.60 0.60 0.60 0.60 0.65 0.65 0.65 0.65 " + // 132-139
    "0.70 0.70 0.70 0.70 0.72 0.72 0.72 0.72 " + // 140-147
    "0.75 0.75 0.75 0.75 0.78 0.78 0.78 0.78 " + // 148-155
    "0.80 0.80 0.80 0.80 0.80 " +                  // 156-160
    // [F] THE STOP 161-169
    "0.90 0.90 0.92 0.92 0.95 0.95 0.95 0.95 " + // 161-168: one last drive
    "0.95" +                                        // 169: CUT TO SILENCE
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 2: GHOST KICK — the haunting
  // Low-energy kick with reverb tail. Downbeat only ("t ~ ~ ~").
  // Stars in vocal territory (114-123) as sole rhythm under synth_lead_2.
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_ghost").struct("t ~ ~ ~").gain(
    "<" +
    // [A] 000-019
    "0 0 0 0 0 0 0 0 " +                           // 000-007: kick is alone
    "0.30 0.35 0.40 0.45 " +                       // 008-011: ghost fades in
    "0.50 0.50 0.50 0.50 " +                       // 012-015: settled
    "0.50 0.50 0.50 0.50 " +                       // 016-019: holding
    // [B] 020-056
    "0.45 0.45 0.45 0.45 0.45 0.45 0.45 0.45 " + // 020-027: behind kick
    "0.40 0.40 0.40 0.40 0.40 0.40 0.40 0.40 " + // 028-035
    "0.35 0.35 0.35 0.35 0.35 0.35 0.35 0.35 " + // 036-043: fading
    "0 0 0 0 0 0 0 0 " +                           // 044-051: gone
    "0 0 0 0 0 " +                                  // 052-056
    // [C] 057-076
    "0 0 0 0 0 0 0 0 " +                           // 057-064: silence
    "0 0 0 0 0 0 0 0 " +                           // 065-072
    "0 0 0 0 " +                                    // 073-076
    // [D] 077-113
    "0.40 0.40 0.40 0.40 0.40 0.40 0.40 0.40 " + // 077-084
    "0.35 0.35 0.35 0.30 0.30 " +                  // 085-089
    "0.30 0.30 0.30 0.30 0.25 0.25 0.25 0.25 " + // 090-097
    "0.20 0.20 0.20 0.20 0.20 0.20 0.20 0.20 " + // 098-105
    "0.15 0.15 0.15 0.15 0.15 0.15 0.15 0.15 " + // 106-113
    // [E] 114-160 — THE GHOST'S MOMENT
    "0.55 0.55 0.55 0.55 0.55 0.55 0.55 0.55 0.55 0.55 " + // 114-123: solo!
    "0.45 0.45 0.45 0.45 0.40 0.40 0.40 0.40 " + // 124-131: fading
    "0.30 0.30 0.30 0.30 0.25 0.25 0.25 0.25 " + // 132-139
    "0.20 0.20 0.20 0.20 0.15 0.15 0.15 0.15 " + // 140-147
    "0 0 0 0 0 0 0 0 " +                           // 148-155: gone
    "0 0 0 0 0 " +                                  // 156-160
    // [F] 161-169
    "0 0 0 0 0 0 0 0 " +                           // 161-168
    "0" +                                            // 169
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 3: HI-HAT — the shimmer
  // Offbeat 8ths: "~ t ~ t ~ t ~ t". Enters bar 012.
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_hat").struct("~ t ~ t ~ t ~ t").gain(
    "<" +
    // [A] 000-019
    "0 0 0 0 0 0 0 0 " +                           // 000-007: kick alone
    "0 0 0 0 " +                                    // 008-011: ghost, no hat
    "0.45 0.50 0.55 0.60 " +                       // 012-015: hat enters!
    "0.65 0.65 0.65 0.65 " +                       // 016-019
    // [B] 020-056
    "0.70 0.70 0.70 0.70 0.70 0.70 0.70 0.70 " + // 020-027
    "0.72 0.72 0.72 0.72 0.72 0.72 0.72 0.72 " + // 028-035
    "0.75 0.75 0.75 0.75 0.75 0.75 0.75 0.75 " + // 036-043
    "0.78 0.78 0.78 0.78 0.78 0.78 0.78 0.78 " + // 044-051
    "0.78 0.78 0.78 0.78 0.78 " +                  // 052-056
    // [C] 057-076 — gone, riser is separate voice
    "0 0 0 0 0 0 0 0 " +                           // 057-064
    "0 0 0 0 0 0 0 0 " +                           // 065-072
    "0 0 0 0 " +                                    // 073-076
    // [D] 077-113
    "0.75 0.75 0.75 0.75 0.78 0.78 0.78 0.78 " + // 077-084
    "0.80 0.80 0.80 0.82 0.82 " +                  // 085-089: PEAK
    "0.80 0.80 0.80 0.80 0.78 0.78 0.78 0.78 " + // 090-097
    "0.75 0.75 0.75 0.75 0.75 0.75 0.75 0.75 " + // 098-105
    "0.72 0.72 0.72 0.72 0.70 0.70 0.70 0.70 " + // 106-113
    // [E] 114-160
    "0 0 0 0 0 0 0 0 0 0 " +                       // 114-123: vocal solo
    "0 0 0 0 0.30 0.30 0.30 0.30 " +               // 124-131
    "0.40 0.40 0.40 0.40 0.50 0.50 0.50 0.50 " + // 132-139
    "0.55 0.55 0.55 0.55 0.60 0.60 0.60 0.60 " + // 140-147
    "0.65 0.65 0.65 0.65 0.68 0.68 0.68 0.68 " + // 148-155
    "0.70 0.70 0.70 0.70 0.70 " +                  // 156-160
    // [F] 161-169
    "0.78 0.78 0.80 0.80 0.82 0.82 0.82 0.82 " + // 161-168
    "0.82" +                                        // 169
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 3b: HAT RISER — bars 073-076 ONLY
  // Classic trance rebuild: 16ths → 32nds over 4 bars.
  // The body knows the drop is coming before the mind does.
  //
  // This voice exists ONLY for 4 bars. 166 bars of silence
  // bracketing 4 bars of escalation. Worth it.
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_hat").struct(
    "<" +
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 000-019
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 020-039
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 040-059
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " +                 // 060-072
    "[t t t t t t t t t t t t t t t t] " +          // 073: 16ths
    "[t t t t t t t t t t t t t t t t] " +          // 074: 16ths louder
    "[t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t] " + // 075: 32nds
    "[t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t t] " + // 076: 32nds MAX
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 077-096
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " +         // 097-113
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 114-133
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " + // 134-153
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~" +            // 154-169
    ">"
  ).gain(
    "<" +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0.45 0.55 0.60 0.70 " +                        // 073-076: escalating riser
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0" +
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 4: CLAP — the punctuation
  // Beats 2 and 4: "~ t ~ t". Drive sections only.
  // Its absence during breakdowns and vocal territory is felt.
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_clap").struct("~ t ~ t").gain(
    "<" +
    // [A] 000-019: no clap
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    // [B] 020-056: enters with drive
    "0.55 0.55 0.55 0.55 0.60 0.60 0.60 0.60 " +
    "0.62 0.62 0.62 0.62 0.65 0.65 0.65 0.65 " +
    "0.68 0.68 0.68 0.68 0.68 0.68 0.68 0.68 " +
    "0.70 0.70 0.70 0.70 0.70 0.70 0.70 0.70 " +
    "0.70 0.70 0.70 0.70 0.70 " +
    // [C] 057-076: gone
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    // [D] 077-113
    "0.65 0.65 0.68 0.68 0.70 0.70 0.72 0.72 " +
    "0.72 0.75 0.75 0.75 0.75 " +                   // 089: PEAK
    "0.72 0.72 0.72 0.72 0.70 0.70 0.70 0.70 " +
    "0.68 0.68 0.68 0.68 0.65 0.65 0.65 0.65 " +
    "0.62 0.62 0.62 0.62 0.60 0.60 0.60 0.60 " +
    // [E] 114-160: absent then creeps back
    "0 0 0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 " +
    "0.30 0.30 0.30 0.30 0.35 0.35 0.35 0.35 " +
    "0.40 0.40 0.40 0.40 0.45 0.45 0.45 0.45 " +
    "0.50 0.50 0.50 0.50 0.50 " +
    // [F] 161-169
    "0.65 0.65 0.70 0.70 0.72 0.72 0.72 0.72 " +
    "0.72" +
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 5: BASS — the undertow
  //
  // Pulsing 8th notes: "t t t t t t t t" (8 per bar).
  // .n() maps: 0=C#1 1=D1 2=D#1 3=E1 4=F1 5=F#1 6=G1 7=G#1 8=A1 9=A#1
  //
  // Harmonic arc:
  //   Drive: i→VI→III cycling (C#1→A1→E1)
  //   Breakdown: C#1 drone (held, low gain — grieving)
  //   Riser: chromatic walk C#→D→D#→E
  //   Peak: E1 (the III — tension, not home, yearning)
  //   Resolution: E1→A1→C#1 walk back
  //   Vocal territory: absent (synth_lead_2 owns the space)
  //   Finale: E1 tension → C#1 home → CUT
  // ═══════════════════════════════════════════════════════════════════════
  s("frisson_bass").struct("t t t t t t t t").n(
    "<" +
    // [A] 000-019: bass enters late
    "~ ~ ~ ~ ~ ~ ~ ~ " +                           // 000-007: no bass
    "~ ~ ~ ~ " +                                    // 008-011: no bass
    "~ ~ ~ ~ " +                                    // 012-015: no bass
    "0 0 0 0 " +                                    // 016-019: C#1 fades in
    // [B] 020-056: harmonic engine
    "0 0 0 0 0 0 0 0 " +                           // 020-027: C#1 (i)
    "8 8 8 8 8 8 8 8 " +                           // 028-035: A1 (VI)
    "0 0 8 8 3 3 0 0 " +                           // 036-043: i→VI→III→i
    "0 0 8 8 3 3 0 1 " +                           // 044-051: cycle + D1 pass
    "2 3 3 3 3 " +                                  // 052-056: D#1→E1 tension
    // [C] 057-076: drone then riser
    "0 0 0 0 0 0 0 0 " +                           // 057-064: C#1 drone
    "0 0 0 0 0 0 0 0 " +                           // 065-072: C#1 drone
    "0 1 2 3 " +                                    // 073-076: chromatic walk!
    // [D] 077-113
    "3 3 3 3 3 3 3 3 " +                           // 077-084: E1 (III) tension
    "3 3 3 3 3 " +                                  // 085-089: E1 through PEAK
    "3 3 8 8 8 8 8 8 " +                           // 090-097: E1→A1 resolution
    "8 8 8 8 0 0 0 0 " +                           // 098-105: A1→C#1 home
    "0 0 0 0 0 0 0 0 " +                           // 106-113: C#1 settled
    // [E] 114-160
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " +                       // 114-123: absent (vocal solo)
    "0 0 0 0 0 0 0 0 " +                           // 124-131: C#1 gentle
    "0 0 0 0 0 0 0 0 " +                           // 132-139: C#1
    "0 0 8 8 0 0 8 8 " +                           // 140-147: i→VI cycle
    "0 0 8 8 3 3 0 0 " +                           // 148-155: i→VI→III→i
    "0 0 0 0 0 " +                                  // 156-160: C#1 home
    // [F] 161-169
    "3 3 3 3 3 3 0 0 " +                           // 161-168: E1→C#1
    "0" +                                            // 169: C#1 CUT
    ">"
  ).gain(
    "<" +
    // [A] 000-019
    "0 0 0 0 0 0 0 0 " +
    "0 0 0 0 " +
    "0 0 0 0 " +
    "0.30 0.35 0.40 0.45 " +                       // 016-019: bass fades in
    // [B] 020-056
    "0.60 0.60 0.60 0.60 0.65 0.65 0.65 0.65 " +
    "0.65 0.65 0.65 0.65 0.68 0.68 0.68 0.68 " +
    "0.70 0.70 0.70 0.70 0.70 0.70 0.70 0.70 " +
    "0.72 0.72 0.72 0.72 0.72 0.72 0.72 0.72 " +
    "0.72 0.72 0.72 0.72 0.72 " +
    // [C] 057-076: drone (low, sustained)
    "0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 " +
    "0.25 0.25 0.25 0.25 0.25 0.25 0.25 0.25 " +
    "0.35 0.40 0.50 0.60 " +                       // 073-076: riser gain climb
    // [D] 077-113
    "0.70 0.70 0.70 0.70 0.72 0.72 0.72 0.72 " +
    "0.72 0.78 0.78 0.78 0.78 " +                   // 089: PEAK bass at 0.78
    "0.75 0.75 0.72 0.72 0.70 0.70 0.70 0.70 " +
    "0.68 0.68 0.68 0.68 0.65 0.65 0.65 0.65 " +
    "0.62 0.62 0.62 0.62 0.62 0.62 0.62 0.62 " +
    // [E] 114-160
    "0 0 0 0 0 0 0 0 0 0 " +                       // 114-123: absent
    "0.35 0.35 0.35 0.35 0.40 0.40 0.40 0.40 " +
    "0.45 0.45 0.45 0.45 0.45 0.45 0.45 0.45 " +
    "0.50 0.50 0.55 0.55 0.55 0.55 0.58 0.58 " +
    "0.58 0.58 0.60 0.60 0.60 0.60 0.60 0.60 " + // 148-155
    "0.62 0.62 0.62 0.62 0.62 " +                  // 156-160
    // [F] 161-169
    "0.70 0.70 0.72 0.72 0.75 0.75 0.72 0.72 " +
    "0.72" +
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 6: SYNTH LEAD — bass register melody
  //
  // The extracted melody: D#3→D3→E3→C3→C#3→A#2→B2→A#2→C#3
  // 7.4-second phrase sample — one trigger = ~4 bars of melody.
  // Present during drives and peak. ABSENT during breakdown + vocal solo.
  //
  // .struct("t ~ ~ ~") triggers once per bar, clip(1) lets it ring.
  // But we only trigger every 4 bars (gain=0 on intervening bars)
  // so phrases don't overlap and fight each other.
  // ═══════════════════════════════════════════════════════════════════════
  s("synth_lead").struct("t ~ ~ ~").clip(1).gain(
    "<" +
    // [A] 000-019: no lead during hypnosis
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    // [B] 020-056: enters bar 028
    "0 0 0 0 0 0 0 0 " +                           // 020-027: drums only
    "0.40 0 0 0 0.50 0 0 0 " +                     // 028-035: first entry!
    "0.55 0 0 0 0.60 0 0 0 " +                     // 036-043: climbing
    "0.65 0 0 0 0.65 0 0 0 " +                     // 044-051: sustained
    "0.65 0 0 0 0.65 " +                            // 052-056
    // [C] 057-076: GONE then ghost
    "0 0 0 0 0 0 0 0 " +                           // 057-064: silence
    "0.25 0 0 0 0.30 0 0 0 " +                     // 065-072: ghost melody
    "0 0 0 0 " +                                    // 073-076: buried under riser
    // [D] 077-113
    "0.55 0 0 0 0.60 0 0 0 " +                     // 077-084
    "0.65 0.68 0 0 0.70 " +                         // 085-089: 089=PEAK
    "0.65 0 0 0 0.60 0 0 0 " +                     // 090-097
    "0.55 0 0 0 0.50 0 0 0 " +                     // 098-105
    "0.45 0 0 0 0.40 0 0 0 " +                     // 106-113: fading
    // [E] 114-160: absent then returns
    "0 0 0 0 0 0 0 0 0 0 " +                       // 114-123: vocal solo
    "0.30 0 0 0 0.35 0 0 0 " +                     // 124-131: returns
    "0.40 0 0 0 0.45 0 0 0 " +                     // 132-139
    "0.50 0 0 0 0.50 0 0 0 " +                     // 140-147
    "0.55 0 0 0 0.55 0 0 0 " +                     // 148-155
    "0.58 0 0 0 0.58 " +                            // 156-160
    // [F] 161-169
    "0.60 0 0 0 0.65 0 0 0 " +                     // 161-168
    "0.65" +                                         // 169: CUT
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 7: SYNTH LEAD 2 — mid-range C#4 motif
  //
  // Repeating C#4 phrase. 7.4s sample, ~4 bars per trigger.
  // This voice OWNS bars 114-123: stripped to just this + ghost kick.
  //
  // The emotional core of the arrangement. When everything else
  // is gone, this motif remains — a single voice in an empty room.
  // ═══════════════════════════════════════════════════════════════════════
  s("synth_lead_2").struct("t ~ ~ ~").clip(1).gain(
    "<" +
    // [A] 000-019: absent
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    // [B] 020-056: enters late
    "0 0 0 0 0 0 0 0 " +                           // 020-027: not yet
    "0 0 0 0 0 0 0 0 " +                           // 028-035: lead_1 only
    "0.35 0 0 0 0.40 0 0 0 " +                     // 036-043: first entry
    "0.45 0 0 0 0.50 0 0 0 " +                     // 044-051
    "0.50 0 0 0 0.50 " +                            // 052-056
    // [C] 057-076: gone
    "0 0 0 0 0 0 0 0 " +
    "0 0 0 0 0 0 0 0 " +
    "0 0 0 0 " +
    // [D] 077-113
    "0.45 0 0 0 0.50 0 0 0 " +                     // 077-084
    "0.55 0.60 0 0 0.65 " +                         // 085-089: PEAK, both leads
    "0.60 0 0 0 0.55 0 0 0 " +                     // 090-097
    "0.50 0 0 0 0.45 0 0 0 " +                     // 098-105
    "0.40 0 0 0 0.35 0 0 0 " +                     // 106-113
    // [E] 114-160: THIS IS YOUR MOMENT
    "0.70 0 0 0 0.72 0 0 0 0.70 0 " +              // 114-123: SOLO
    "0.65 0 0 0 0.60 0 0 0 " +                     // 124-131: sharing space
    "0.55 0 0 0 0.50 0 0 0 " +                     // 132-139
    "0.45 0 0 0 0.40 0 0 0 " +                     // 140-147: fading as rebuild
    "0.38 0 0 0 0.35 0 0 0 " +                     // 148-155
    "0.30 0 0 0 0.30 " +                            // 156-160
    // [F] 161-169
    "0.40 0 0 0 0.45 0 0 0 " +                     // 161-168
    "0.45" +                                         // 169
    ">"
  ),

  // ═══════════════════════════════════════════════════════════════════════
  // VOICE 8: TEXTURE PAD — the atmosphere
  //
  // 8-bar "other" stem slices (~14.86s each). One trigger = 8 bars.
  // .n() selects which 8-bar slice. clip(1) lets full duration ring.
  //
  // The pad OWNS the breakdown. When everything drops at bar 057,
  // the pad is what survives. It is the architecture of absence.
  //
  // During drives: underneath everything, felt not heard.
  // During breakdown: IS everything.
  // During vocal solo: absent (synth_lead_2 owns that space).
  //
  // struct("t ~ ~ ~ ~ ~ ~ ~") = 1 trigger per 8 bars
  // ═══════════════════════════════════════════════════════════════════════
  s("frissother").struct("t ~ ~ ~ ~ ~ ~ ~").clip(1).n(
    "<" +
    // [A] 000-019: no pad in hypnosis
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " +
    // [B] 020-056: subtle atmosphere underneath
    "0 ~ ~ ~ ~ ~ ~ ~ " +                           // 020-027: slice 0
    "1 ~ ~ ~ ~ ~ ~ ~ " +                           // 028-035: slice 1
    "2 ~ ~ ~ ~ ~ ~ ~ " +                           // 036-043: slice 2
    "3 ~ ~ ~ ~ ~ ~ ~ " +                           // 044-051: slice 3
    "4 ~ ~ ~ ~ " +                                  // 052-056: slice 4 (5 bars into 8-bar slice)
    // [C] 057-076: THE BREAKDOWN — pad is EVERYTHING
    "7 ~ ~ ~ ~ ~ ~ ~ " +                           // 057-064: breakdown heart (slice 7)
    "8 ~ ~ ~ ~ ~ ~ ~ " +                           // 065-072: breakdown continues
    "9 ~ ~ ~ " +                                    // 073-076: riser transition
    // [D] 077-113: underneath the drive
    "10 ~ ~ ~ ~ ~ ~ ~ " +                          // 077-084
    "11 ~ ~ ~ ~ " +                                 // 085-089: slice 11 (peak territory)
    "12 ~ ~ ~ ~ ~ ~ ~ " +                          // 090-097
    "13 ~ ~ ~ ~ ~ ~ ~ " +                          // 098-105
    "14 ~ ~ ~ ~ ~ ~ ~ " +                          // 106-113
    // [E] 114-160: absent for vocal solo, then returns
    "~ ~ ~ ~ ~ ~ ~ ~ ~ ~ " +                       // 114-123: absent
    "~ ~ ~ ~ ~ ~ ~ ~ " +                           // 124-131: still absent
    "16 ~ ~ ~ ~ ~ ~ ~ " +                          // 132-139: returns quietly
    "17 ~ ~ ~ ~ ~ ~ ~ " +                          // 140-147
    "18 ~ ~ ~ ~ ~ ~ ~ " +                          // 148-155
    "19 ~ ~ ~ ~ " +                                 // 156-160
    // [F] 161-169: present for finale
    "20 ~ ~ ~ ~ ~ ~ ~ " +                          // 161-168
    "~" +                                            // 169
    ">"
  ).gain(
    "<" +
    // [A] 000-019
    "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " +
    // [B] 020-056: quiet atmosphere
    "0.30 0 0 0 0 0 0 0 " +
    "0.35 0 0 0 0 0 0 0 " +
    "0.38 0 0 0 0 0 0 0 " +
    "0.40 0 0 0 0 0 0 0 " +
    "0.40 0 0 0 0 " +
    // [C] 057-076: BREAKDOWN — pad at full presence
    "0.85 0 0 0 0 0 0 0 " +                        // 057-064: the pad IS the music
    "0.82 0 0 0 0 0 0 0 " +                        // 065-072
    "0.75 0 0 0 " +                                 // 073-076: fading as riser takes over
    // [D] 077-113: back underneath
    "0.40 0 0 0 0 0 0 0 " +
    "0.45 0 0 0 0 " +                               // peak territory
    "0.42 0 0 0 0 0 0 0 " +
    "0.38 0 0 0 0 0 0 0 " +
    "0.35 0 0 0 0 0 0 0 " +
    // [E] 114-160
    "0 0 0 0 0 0 0 0 0 0 " +                       // 114-123: absent
    "0 0 0 0 0 0 0 0 " +                           // 124-131
    "0.25 0 0 0 0 0 0 0 " +                        // 132-139: returns
    "0.30 0 0 0 0 0 0 0 " +
    "0.32 0 0 0 0 0 0 0 " +
    "0.35 0 0 0 0 " +
    // [F] 161-169
    "0.40 0 0 0 0 0 0 0 " +
    "0" +                                            // 169
    ">"
  )

)
// ═══════════════════════════════════════════════════════════════════════
// NO MASTER FADE. The track doesn't end. It stops.
//
// Bar 169 plays at full density.
// Bar 170 is silence.
// That's the arrangement decision.
//
// Elliott ends with a gentle 30-second fade. That's his choice.
// This arrangement ends like a door slamming.
// The listener is left in silence with the memory of sound.
// ═══════════════════════════════════════════════════════════════════════
