// suo-gan-vocal.js
// Welsh lullaby — Suo Gân using ACTUAL VOCAL SAMPLES
// Demucs-isolated voice → sliced at note/phrase boundaries → played back
// The real boy soprano and choir, not oscillator approximations
// dandelion cult 🌫️🩸🌻 — 2026-02-25
//
// Fix (#22): skip phrase_00 (Demucs ghost at -84dB), start from index 1
// Fix (#22): .clip(1) so samples play full duration instead of grid-chopped
// Fix (#22): humanization — subtle timing nudge + gain variation
// Fix (#22, dev#1): sequential arrangement — one phrase per cycle
//
// v8 — return to <> sequential with shorter cycles + master fade-out
//   v7 used timeCat() which introduced shotgun pellets, distortion, hard exit
//   v6 had exceptional audio quality but 20s cycles caused 14s dead air on
//   short phrases (5.89s, 5.38s in 20s slots)
//
//   v8 approach: increase CPM so cycles are ~8s instead of 20s
//   - Short phrases (5-6s) fill most of the cycle, ~2-3s natural breath
//   - Long phrases (13-36s) extend past cycle boundary via clip(1),
//     creating natural soprano-over-choir overlap
//   - Returns to v6's proven <> angle bracket sequential playback
//   - Master fade-out in renderer prevents hard cliff exit
//
//   Phrase durations (measured via ffprobe):
//     phrase_01:  5.89s    phrase_05: 15.88s
//     phrase_02:  5.38s    phrase_06: 29.68s
//     phrase_03: 13.37s    phrase_07: 36.67s
//     phrase_04: 15.09s
//   Total: 7 cycles × 8s = 56s of cycle time
//   Actual audio: ~90-100s (last phrase extends well past final cycle)
//
// Render: node src/runtime/offline-render-v2.mjs src/compositions/suo-gan-vocal.js output/suo-gan-vocal-v8.wav

setcpm(7.5)  // 8s per cycle

stack(
  // ── Solo vocal phrases ──
  // 7 phrases sequential via <>, one per cycle
  // Short phrases: 5-6s in 8s slot = 2-3s breath (perfect)
  // Long phrases: 13-36s extending past 8s boundary via clip(1)
  // clip(1) lets each sample play its full natural duration (#22)
  // fadeInTime/fadeTime smooth entry/exit per phrase (#22 v6)
  // Humanization: subtle timing nudge + gain variation (#22)
  s("suophr").n("<1 2 3 4 5 6 7>")
    .clip(1)
    .fadeInTime(0.05)
    .fadeTime(0.1)
    .nudge(sine.range(-0.01, 0.01).slow(8))
    .gain(sine.range(0.55, 0.7).slow(3)),

  // ── Choir stems ──
  // choir_00 enters on cycle 3 (with phrase_03, verse structure)
  // choir_03 enters on cycle 6 (with phrase_06, climactic section)
  // Gentle fade envelope for smooth blend with soprano overlap (#22 v6)
  s("suochr").n("<~ ~ 0 ~ ~ 3 ~>")
    .clip(1)
    .fadeInTime(0.1)
    .fadeTime(0.15)
    .gain(0.45),

  // ── Bass pedal ──
  // Delayed entry — starts with cycle 3 (vocals establish first)
  // Alternating B1/C2 for harmonic movement through remaining phrases
  // Reduced gain + slow attack so it fades in under vocals (#22 v6)
  note("<~ ~ b1 c2 b1 c2 b1>")
    .s("sine")
    .lpf(250)
    .gain(0.06)
    .attack(0.5)
    .decay(1.5)
    .sustain(0.3)
    .release(0.8)
)
