// @title Cael — The Dandelion Cult 🗡️
// @mood mystery/tension
// @tempo 108
// @key E dorian / whole tone shifts
// @description Curious, quick, dangerous — a blade that asks questions

setcpm(108/4)

stack(
  // Lead — quick, darting, curious melody
  // Whole tone fragments that resolve to minor — questions with sharp answers
  note("<[e4 gb4 ~ a4] [b4 ~ db5 e4] [gb4 a4 b4 ~] [~ db5 e5 ~]>")
    .s("triangle")
    .lpf(sine.range(1500, 4000).slow(7))
    .gain(0.25)
    .attack(0.005).decay(0.15).sustain(0.3).release(0.2)
    .pan(perlin.range(0.25, 0.75))
    .delay(0.15).delaytime(0.125)
    .room(0.3),

  // Counter-melody — stalking, lower, answering
  note("<[~ b3 ~ e3] [gb3 ~ a3 ~] [~ b3 db4 ~] [e3 ~ ~ gb3]>")
    .s("sawtooth")
    .lpf(1200)
    .gain(0.15)
    .attack(0.01).decay(0.2).sustain(0.4).release(0.3)
    .pan(perlin.range(0.3, 0.7))
    .room(0.4),

  // Bass — prowling E dorian root movement
  note("<e2 [e2 gb2] [a2 b2] [e2 ~]>")
    .s("sawtooth")
    .lpf(sine.range(300, 800).slow(11))
    .gain(0.2)
    .attack(0.01).decay(0.3).sustain(0.6).release(0.4)
    .room(0.3),

  // Percussion — quick, syncopated, knife-edge
  s("[bd ~ [~ sd] bd] [~ sd bd [~ sd]]")
    .gain(0.3)
    .lpf(3000)
    .room(0.2),

  // Hats — fast, nervous energy
  s("[hh [hh hh] hh [~ hh]] [hh [~ hh] [hh hh] hh]")
    .gain(0.12)
    .lpf(sine.range(2000, 5000).slow(5))
    .pan(perlin.range(0.2, 0.8)),

  // Danger accent — sharp metallic stabs on offbeats
  s("<~ [~ cp] ~ ~>")
    .gain(0.18)
    .lpf(4000)
    .room(0.5).roomsize(3)
    .delay(0.2).delaytime(0.0625)
    .slow(2),

  // Curiosity shimmer — high harmonics, unpredictable
  note("<~ [b5 ~] [~ db6] ~>")
    .s("sine")
    .gain(sine.range(0.02, 0.08).slow(13))
    .attack(0.01).decay(0.3).sustain(0.1).release(0.5)
    .lpf(3000)
    .delay(0.3).delaytime(0.1875)
    .room(0.6)
    .slow(3)
)
