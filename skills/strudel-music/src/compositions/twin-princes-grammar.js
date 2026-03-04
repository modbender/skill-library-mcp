// Twin Princes (Dark Souls 3 OST) — Grammar-extracted composition
// DNA: 77 BPM, G major, density-driven architecture (Motoi Sakuraba)
// Two chords (G/C), accumulating layers, bass+vocals escalate
// Through-composed: 0% bar repetition

setcpm(77/4)

stack(
  // === DRUMS: the clock ===
  // Hat-dominant 51%, uniform ~20 notes/bar, slight offbeat emphasis
  // Drums don't build — they're the constant
  s("hh*8").gain(0.35),
  s("~ hh ~ hh ~ hh ~ hh").gain(0.18),
  s("bd ~ ~ ~ bd ~ ~ ~").gain(0.55),
  s("~ ~ sd ~ ~ ~ sd ~").gain(0.5),

  // === BASS: G-centered, ACCUMULATES ===
  // 88% stepwise, sparse→dense (1.7→9.3 notes/bar)
  // Pattern grows each cycle: 2 notes → 4 → 6 → 8
  note("<g2 [g2 c2] [g2 c2 g2] [g2 c2 g#2 g2] [g2 c2 g#2 c#2 g2] [g2 c2 g#2 d2 c#2 g2] [g2 c2 g#2 d2 c#2 g2 c2 g2] [g2 c2 g#2 d2 c#2 g2 c2 g#2]>")
    .s("sawtooth")
    .lpf("<300 400 500 600 700 900 1100 1400>")
    .gain("<0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2>")
    .decay(0.5)
    .sustain(0.3)
    .release(0.3),

  // === OTHER (lead synth): steady texture ===
  // G/G#/C/F/D# pentatonic-adjacent, flat ~6 notes/bar
  // Does NOT build — contrast to bass/vocals escalation
  note("[g3 g#3 c3 f3 d#3 g3]")
    .s("square")
    .lpf(1600)
    .gain(0.07)
    .decay(0.9)
    .sustain(0.4)
    .release(0.5)
    .room(0.3),

  // === VOCALS: modal tension, builds alongside bass ===
  // D/G/D#/G# — the G# against G instruments = chromatic friction
  // 75% stepwise, median D4, builds from 4→8 notes/bar
  note("<[d4 ~ g4 ~] [d4 g#4 d#4 g4] [d4 g#4 d#4 g4 d5 d#5] [d5 d#5 g4 g#4 d4 d#4 g#4 d5]>")
    .s("triangle")
    .lpf("<2500 3000 3500 4500>")
    .gain("<0.04 0.06 0.09 0.12>")
    .decay(0.7)
    .sustain(0.5)
    .release(0.5)
    .room(0.25),

  // === HARMONIC FIELD: G/C oscillation, occasional Cm ===
  note("<[g2,b3,d4] [c3,e4,g4] [g2,b3,d4] [c3,e4,g4] [g2,b3,d4] [c3,d#4,g4] [g2,b3,d4] [c3,e4,g4]>")
    .s("sine")
    .lpf(1000)
    .gain(0.035)
    .decay(2.5)
    .sustain(0.6)
    .release(1.2)
)
