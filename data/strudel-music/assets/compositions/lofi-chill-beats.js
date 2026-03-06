// @title Lo-fi Chill Beats
// @mood peace/ambient
// @tempo 75
// @key Eb major pentatonic
// @description Muted piano, vinyl crackle texture, warm and slow

setcpm(75/4)

stack(
  // Muted piano — jazzy pentatonic chords, low velocity feel
  note("<[eb4 g4 bb4] [f4 ab4 c5] [eb4 g4 bb4] [db4 f4 ab4]>")
    .s("triangle")
    .lpf(900)
    .gain(0.15)
    .attack(0.02).decay(0.4).sustain(0.2).release(0.6)
    .room(0.5).roomsize(3)
    .pan(0.4)
    .delay(0.2).delaytime(0.2),

  // Piano melody — sparse, wandering pentatonic
  note("<[~ eb5 ~ g5] [~ ~ f5 ~] [bb4 ~ ~ eb5] [~ db5 ~ ~]>")
    .s("sine")
    .lpf(1200)
    .gain(sine.range(0.06, 0.12).slow(11))
    .attack(0.03).decay(0.3).sustain(0.15).release(0.8)
    .room(0.6).roomsize(4)
    .pan(0.6)
    .delay(0.25).delaytime(0.3),

  // Bass — warm, round, pillowy
  note("<eb2 [eb2 ~] [ab2 ~] [bb2 eb2]>")
    .s("sine")
    .lpf(400)
    .gain(0.2)
    .attack(0.05).decay(0.4).sustain(0.6).release(0.5),

  // Drums — lo-fi, laid back, slightly swung feel
  s("[bd ~ ~ bd] [~ sd ~ ~]")
    .gain(0.2)
    .lpf(2000)
    .room(0.3),

  // Hats — gentle, muted, tape-degraded feel
  s("[~ hh ~ hh] [~ hh ~ [~ hh]]")
    .gain(0.08)
    .lpf(sine.range(1500, 3000).slow(7))
    .pan(perlin.range(0.3, 0.7)),

  // Vinyl crackle texture — noise layer
  s("[hh hh hh hh] [hh hh hh hh]")
    .gain(0.02)
    .lpf(800)
    .hpf(200)
    .pan(perlin.range(0.1, 0.9))
    .room(0.4),

  // Warm pad — slow breathing background
  note("<eb3 ab3>")
    .s("triangle")
    .lpf(sine.range(300, 600).slow(16))
    .gain(sine.range(0.03, 0.07).slow(13))
    .attack(0.5).decay(1).sustain(0.4).release(1)
    .room(0.7).roomsize(5)
    .slow(4)
)
