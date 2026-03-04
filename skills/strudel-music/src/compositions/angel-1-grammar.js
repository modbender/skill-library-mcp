// Angel 1 — Anyma & Innellea (grammar-extracted composition)
// DNA: 122 BPM, A#/Bb major, drum-driven EDM
// Flat density curve — sustains, doesn't build. Energy in timbre variation.
// 14.9 LU dynamic range. Through-composed (0% bar repetition expected)
// Credit: Anyma & Innellea — "Angel 1" (original track)
// Source: Anyma & Innellea — Angel 1

setcpm(122/4)

stack(
  // === DRUMS: loudest stem, drives everything ===
  // EDM four-on-the-floor + hat pattern
  s("bd bd bd bd").gain(0.6),
  s("~ ~ sd ~ ~ ~ sd ~").gain(0.5),
  s("hh*8").gain(0.3),
  s("~ hh ~ hh ~ hh ~ hh").gain(0.15),

  // === BASS: A#/F centered, EDM sub ===
  // Classic EDM bass — sits on root, occasional movement
  note("<[a#1 ~ ~ ~ a#1 ~ ~ ~] [a#1 ~ ~ ~ f1 ~ ~ ~] [a#1 ~ ~ ~ f#1 ~ ~ ~] [a#1 ~ ~ ~ g#1 ~ ~ ~] [a#1 ~ ~ ~ a#1 ~ f1 ~] [f1 ~ ~ ~ f#1 ~ ~ ~] [a#1 ~ ~ ~ a#1 ~ ~ ~] [f1 ~ ~ ~ g#1 ~ a#1 ~]>")
    .s("sawtooth")
    .lpf("<400 500 600 700 800 700 500 400>")
    .gain(0.18)
    .decay(0.3)
    .sustain(0.2)
    .release(0.15),

  // === OTHER (synths/pads): timbre variation layer ===
  // A#/F/F# chord field — classic EDM progression
  // Flat density but filter sweeps for movement
  note("<[a#3,d4,f4] [f3,a3,c4] [f#3,a#3,c#4] [g#3,c4,d#4]>")
    .s("square")
    .lpf(
      "<800 1200 1800 2400 3200 2400 1800 1200 800 600 800 1200 2000 3000 4000 3000>"
    )
    .gain(0.06)
    .decay(1.2)
    .sustain(0.5)
    .release(0.6)
    .room(0.2),

  // === VOCALS: quiet but present (14.8dB below drums) ===
  // Ethereal EDM vocal pad — sits on top, barely there
  note("<[a#4 ~ ~ ~ ~ ~ ~ ~] [~ ~ ~ ~ ~ ~ ~ ~] [f4 ~ ~ ~ ~ ~ ~ ~] [~ ~ ~ ~ ~ ~ ~ ~] [f#4 ~ ~ ~ ~ ~ ~ ~] [~ ~ ~ ~ ~ ~ ~ ~] [d#4 ~ ~ ~ ~ ~ ~ ~] [~ ~ ~ ~ ~ ~ ~ ~]>")
    .s("triangle")
    .lpf(3000)
    .gain(0.03)
    .decay(2.0)
    .sustain(0.6)
    .release(1.0)
    .room(0.4),

  // === FILTER SWEEP: the energy is in timbre, not volume ===
  // Slow LPF sweep on a noise-like layer
  note("[a#2,f3,a#3]")
    .s("sawtooth")
    .lpf(
      "<200 300 500 800 1200 1800 2400 3000 3600 3000 2400 1800 1200 800 500 300>"
    )
    .gain(0.04)
    .decay(0.8)
    .sustain(0.3)
    .release(0.4)
)
