// @title Dark Ambient Tension
// @mood tension/dread
// @tempo 58
// @key D phrygian
// @description Low drones, sparse percussion, creeping dread

setcpm(58/4)

stack(
  // Sub-bass drone — D phrygian root, barely moving
  note("<d1 [d1 eb1] d1 [d1 c1]>")
    .s("sawtooth")
    .lpf(sine.range(120, 400).slow(16))
    .gain(sine.range(0.15, 0.25).slow(11))
    .attack(0.8).decay(0.5).sustain(0.9).release(1.2)
    .room(0.7).roomsize(8)
    .slow(2),

  // Mid-range tension pad — dissonant intervals
  note("<[d3,ab3] [eb3,a3] [d3,g3] [c3,gb3]>")
    .s("triangle")
    .lpf(sine.range(300, 900).slow(13))
    .gain(sine.range(0.06, 0.12).slow(7))
    .attack(1.5).decay(0.8).sustain(0.6).release(2.0)
    .pan(sine.range(0.2, 0.8).slow(9))
    .room(0.8).roomsize(10)
    .slow(4),

  // Sparse metallic percussion — irregular, unsettling
  s("~ ~ [~ cp] ~")
    .gain(0.08)
    .lpf(1200)
    .room(0.9).roomsize(12)
    .pan(perlin.range(0.1, 0.9))
    .slow(2),

  // Ghost hits — barely there
  s("~ [~ ~ hh] ~ ~")
    .gain(0.04)
    .lpf(600)
    .delay(0.5).delaytime(0.375)
    .room(0.95)
    .slow(3),

  // High tension shimmer — harmonics floating above
  note("<d5 ~ eb5 ~>")
    .s("sine")
    .gain(sine.range(0.01, 0.05).slow(17))
    .attack(0.5).decay(1.0).sustain(0.3).release(1.5)
    .lpf(2000)
    .pan(perlin.range(0.3, 0.7))
    .delay(0.4).delaytime(0.5)
    .room(0.9)
    .slow(4),

  // Breathing noise texture
  s("<~ ~ [hh hh] ~>")
    .gain(sine.range(0.01, 0.03).slow(23))
    .lpf(sine.range(200, 800).slow(19))
    .room(0.95).roomsize(15)
    .slow(6)
)
