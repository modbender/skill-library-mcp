// Greensleeves — hybrid composition v2
// G minor (transposed from A minor), 3/4 time, ~53 BPM
// Dorian voice over aeolian accompaniment
// 17.4 LU target dynamic range

setcpm(53/4)

stack(
  // === MELODY: Greensleeves verse (A section) ===
  // Each slow note. 3/4 waltz feel.
  // Verse 1: quiet
  // Verse 2: builds  
  // B section (chorus): peak
  note(`<
    [a#3 c4 d4] [d#4 ~ d4] [c4 a#3 ~] [g3 a3 a#3]
    [a3 g3 ~] [f#3 ~ d3] [f3 f3 g3] [a3 g3 f3]
    [d#3 c3 d3] [d#3 f3 d3] [c3 a#2 ~] [a#2 ~ ~]
    [a#3 c4 d4] [d#4 ~ d4] [c4 a#3 ~] [g3 a3 a#3]
    [a3 g3 f#3] [g3 ~ d3] [f3 f3 g3] [a3 g3 f3]
    [d#3 c3 d3] [d#3 d3 c3] [a#2 ~ ~] [a#2 ~ ~]
    [d#4 ~ ~] [d#4 d4 c4] [a#3 g3 a3] [a#3 a3 g3]
    [f#3 ~ d3] [d#4 ~ ~] [d#4 d4 c4] [a#3 g3 a3]
    [a#3 a3 g3] [f#3 g3 ~] [d3 ~ ~] [f3 f3 g3]
    [a3 g3 f3] [d#3 c3 d3] [d#3 d3 c3] [a#2 ~ ~]
  >`)
    .s("triangle")
    .lpf("<2800 3000 3200 3400 3600 3000 2800 4000 4200 4500 4200 3800 3500 3200 3000 2800 4500 4800 5000 4800 4500 4200 4000 3800 3500 3200 3000 2800 4500 4800 5000 4800 4200 3800 3500 3200 3000 2800 2600 2400>")
    .gain("<0.06 0.07 0.07 0.08 0.08 0.07 0.06 0.06 0.07 0.08 0.08 0.07 0.06 0.05 0.05 0.04 0.10 0.11 0.12 0.13 0.14 0.13 0.12 0.11 0.14 0.15 0.16 0.15 0.14 0.13 0.12 0.11 0.10 0.09 0.08 0.07 0.06 0.05 0.04 0.04>")
    .decay(1.0)
    .sustain(0.6)
    .release(0.8)
    .room(0.35),

  // === ACCOMPANIMENT: arpeggiated chords, aeolian (F natural) ===
  note(`<
    [g2 d3 a#2] [g2 d3 a#2] [g2 d3 a#2] [g2 d3 a#2]
    [f2 c3 a2] [f2 c3 a2] [d#2 a#2 g2] [d#2 a#2 g2]
    [g2 d3 a#2] [g2 d3 a#2] [d2 a2 f#2] [g2 d3 a#2]
    [g2 d3 a#2] [g2 d3 a#2] [g2 d3 a#2] [g2 d3 a#2]
    [f2 c3 a2] [f2 c3 a2] [d#2 a#2 g2] [d#2 a#2 g2]
    [g2 d3 a#2] [d2 a2 f#2] [g2 d3 a#2] [g2 ~ ~]
    [a#2 f3 d3] [a#2 f3 d3] [g2 d3 a#2] [g2 d3 a#2]
    [f2 c3 a2] [a#2 f3 d3] [a#2 f3 d3] [g2 d3 a#2]
    [g2 d3 a#2] [d2 a2 f#2] [g2 d3 a#2] [d#2 a#2 g2]
    [d#2 a#2 g2] [g2 d3 a#2] [d2 a2 f#2] [g2 ~ ~]
  >`)
    .s("sine")
    .lpf(900)
    .gain("<0.03 0.03 0.03 0.04 0.04 0.03 0.03 0.03 0.03 0.04 0.04 0.03 0.03 0.03 0.02 0.02 0.05 0.06 0.06 0.06 0.05 0.05 0.06 0.06 0.07 0.07 0.06 0.06 0.05 0.05 0.04 0.04 0.04 0.03 0.03 0.03 0.02 0.02 0.02 0.02>")
    .decay(1.8)
    .sustain(0.4)
    .release(1.0),

  // === BASS: slow root motion ===
  note("<g2 ~ ~ g2 ~ ~ f2 ~ ~ d#2 ~ ~ g2 ~ ~ g2 ~ ~ f2 ~ ~ d#2 ~ ~ g2 ~ ~ d2 ~ ~ g2 ~ ~ a#2 ~ ~ g2 ~ ~ a#2 ~ ~ g2 ~ ~>")
    .s("sine")
    .lpf(250)
    .gain("<0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.04 0.04 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.04 0.04 0.04 0.03 0.05 0.05 0.05 0.05 0.04 0.04 0.05 0.05 0.06 0.06 0.05 0.05 0.04 0.04 0.03 0.03>")
    .decay(2.5)
    .sustain(0.5)
    .release(1.2)
)
