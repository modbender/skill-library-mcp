// suo-gan.js
// Welsh lullaby — Suo Gân ("Lullaby Song")
// Source: Empire of the Sun OST, solo boy soprano + choir
// Three voices extracted from a cappella via Demucs stem separation
// Tempo: 131 BPM, Key: G major
// dandelion cult 🌫️🩸🌻 — 2026-02-24

setcpm(131/4)

stack(
  // Solo melody — boy soprano (181 notes extracted, G4/A4/B4/D5 dominant)
  // Suo Gân contour: rising G→A→B→D, stepwise descent
  note("g4 g4 a4 a4 b4 b4 c5 d5 a4 b4 as4 a4 g4 ~ g4 ~ g4 a4 b4 b4 c5 c5 d5 d5 c5 b4 a4 g4 a4 ~ g4 ~")
    .s("triangle")
    .lpf(3500)
    .gain(0.25)
    .decay(0.5)
    .sustain(0.35)
    .release(0.15),

  // Choir voices — harmony in thirds/sixths (143 notes, G2/E2/F2)
  // Enters on second phrase, lower register harmonization
  note("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ g2 g2 e2 e2 f2 f2 g2 g2 e2 e2 c3 e3 g2 ~ g2 ~")
    .s("sine")
    .lpf(1200)
    .gain(0.15)
    .decay(0.7)
    .sustain(0.4)
    .release(0.3),

  // Bass pedal — B1 drone (50% of bass notes), Welsh choir bass
  note("b1 ~ ~ ~ ~ ~ ~ ~ b1 ~ ~ ~ ~ ~ ~ ~ c2 ~ ~ ~ ~ ~ ~ ~ b1 ~ ~ ~ ~ ~ ~ ~")
    .s("sine")
    .lpf(350)
    .gain(0.2)
    .decay(1.0)
    .sustain(0.5)
    .release(0.4),

  // Chord pad — warm sustained harmony I→IV→V→I
  note("[g3,b3,d4] ~ ~ ~ ~ ~ ~ ~ [c4,e4,g4] ~ ~ ~ ~ ~ ~ ~ [d4,fs4,a4] ~ ~ ~ ~ ~ ~ ~ [g3,b3,d4] ~ ~ ~ ~ ~ ~ ~")
    .s("sine")
    .lpf(1400)
    .gain(0.08)
    .decay(1.5)
    .sustain(0.5)
    .release(0.6)
)
