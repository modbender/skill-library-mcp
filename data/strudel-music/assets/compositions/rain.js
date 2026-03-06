// @title Rain
// @mood ambient/nature
// @tempo 55
// @key Atonal / F minor wash
// @description Rain on a window — irregular drips, white noise wash, distant thunder

setcpm(55/4)

stack(
  // Rain wash — filtered noise, constant patter
  s("[hh hh hh hh] [hh hh hh hh] [hh hh hh hh] [hh hh hh hh]")
    .gain(perlin.range(0.02, 0.06))
    .lpf(sine.range(600, 2500).slow(19))
    .hpf(400)
    .pan(perlin.range(0.0, 1.0))
    .room(0.8).roomsize(8)
    .fast(2),

  // Individual drops — irregular, pitched, plinking
  s("<[~ hh ~ ~] [~ ~ hh ~] [hh ~ ~ ~] [~ ~ ~ hh]>")
    .gain(perlin.range(0.04, 0.1))
    .lpf(sine.range(3000, 6000).slow(13))
    .hpf(2000)
    .pan(perlin.range(0.1, 0.9))
    .room(0.7).roomsize(6)
    .delay(0.4).delaytime(perlin.range(0.05, 0.15)),

  // Heavy drops — lower, fatter, less frequent
  s("<[~ ~ bd ~] [~ ~ ~ ~] [~ bd ~ ~] [~ ~ ~ ~]>")
    .gain(0.04)
    .lpf(500)
    .room(0.9).roomsize(10)
    .pan(perlin.range(0.2, 0.8))
    .slow(2),

  // Puddle ripple — sine plinks at random-ish intervals
  note("<[~ f5 ~ ~] [~ ~ c6 ~] [ab5 ~ ~ ~] [~ ~ ~ eb5]>")
    .s("sine")
    .gain(perlin.range(0.01, 0.04))
    .attack(0.001).decay(0.15).sustain(0.0).release(0.3)
    .lpf(4000)
    .pan(perlin.range(0.15, 0.85))
    .room(0.6).roomsize(5)
    .delay(0.3).delaytime(0.2),

  // Gutter stream — low continuous tone, wavering
  note("f2")
    .s("sine")
    .lpf(sine.range(100, 300).slow(23))
    .gain(sine.range(0.01, 0.04).slow(17))
    .attack(0.5).decay(1).sustain(0.5).release(1)
    .room(0.9).roomsize(10)
    .slow(8),

  // Distant thunder — very low, very rare
  note("<~ ~ ~ ~ ~ ~ ~ c1>")
    .s("sawtooth")
    .lpf(sine.range(60, 200).slow(3))
    .gain(sine.range(0.0, 0.06).slow(5))
    .attack(0.8).decay(2).sustain(0.1).release(3)
    .room(1).roomsize(12)
    .slow(4),

  // Window glass resonance — high harmonic shimmer
  note("<[~ ~ ab6 ~] [~ ~ ~ ~] [~ f6 ~ ~] [~ ~ ~ ~]>")
    .s("triangle")
    .gain(0.015)
    .attack(0.01).decay(0.5).sustain(0.0).release(0.8)
    .lpf(5000)
    .room(0.8).roomsize(7)
    .delay(0.5).delaytime(0.3)
    .pan(perlin.range(0.3, 0.7))
    .slow(3)
)
