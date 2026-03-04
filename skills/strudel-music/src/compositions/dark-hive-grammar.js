// Dark Hive — Tabernis (grammar-extracted composition)
// DNA: 92 BPM, E minor, texture-driven ritual
// Wall of sound — monks don't do crescendos
// Other (synths/pads) loudest, vocals borderline (chanting?)
// 8.5 LU dynamic range. Dense, consistent.
// Credit: Tabernis — Dark Hive

setcpm(92/4)

stack(
  // === DRUMS: present but not dominant ===
  // Ritual percussion — slower, heavier than EDM
  s("bd ~ ~ ~ bd ~ ~ ~").gain(0.5),
  s("~ ~ ~ sd ~ ~ ~ ~").gain(0.4),
  s("hh*4").gain(0.2),

  // === BASS: E minor root, dark and heavy ===
  note("<[e1 ~ ~ ~ e1 ~ ~ ~] [e1 ~ ~ ~ f#1 ~ ~ ~] [e1 ~ ~ ~ a1 ~ ~ ~] [e1 ~ ~ ~ g1 ~ e1 ~]>")
    .s("sawtooth")
    .lpf(300)
    .gain(0.16)
    .decay(0.5)
    .sustain(0.3)
    .release(0.2),

  // === OTHER (dominant): ritual texture wall ===
  // E/F#/A/G natural minor — dense pad
  note("<[e3,g3,b3] [f#3,a3,c#4] [a3,c4,e4] [g3,b3,d4]>")
    .s("square")
    .lpf("<600 800 1000 1200 1400 1200 1000 800>")
    .gain(0.08)
    .decay(1.5)
    .sustain(0.6)
    .release(0.8)
    .room(0.35),

  // === SECOND TEXTURE: darker, lower ===
  note("[e2,b2,e3]")
    .s("sawtooth")
    .lpf("<400 500 600 700 600 500 400 350>")
    .gain(0.06)
    .decay(2.0)
    .sustain(0.5)
    .release(1.0)
    .room(0.3),

  // === CHANTING: borderline vocal layer ===
  // Barely there — monks humming underneath
  note("<[e4 ~ ~ ~] [~ ~ ~ ~] [f#4 ~ ~ ~] [~ ~ ~ ~] [g4 ~ ~ ~] [~ ~ ~ ~] [a4 ~ ~ ~] [~ ~ ~ ~]>")
    .s("triangle")
    .lpf(2000)
    .gain(0.025)
    .decay(2.5)
    .sustain(0.7)
    .release(1.2)
    .room(0.5)
)
