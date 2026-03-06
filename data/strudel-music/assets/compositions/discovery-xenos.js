// @title Xenos Ruins
// @by Silas 🌫️
// @mood mystery/exploration
// @scene First contact with alien architecture — geometry that
//        shouldn't exist, symbols that move when you look away,
//        the air tastes of ozone and something older than the Imperium

setcpm(78/4)

stack(
  // Whole-tone wandering — nothing resolves, tonality uncertain
  note("<c4 d4 e4 f#4 g#4 a#4 c5 a#4 g#4 f#4 e4 d4>")
    .s("sine")
    .decay(0.7)
    .sustain(0)
    .gain(0.1)
    .room(0.7)
    .delay(0.4)
    .delaytime(perlin.range(0.2, 0.4))
    .slow(3),

  // Augmented chord pad — unsettling shimmer
  note("<c3,e3,g#3 d3,f#3,a#3>")
    .s("triangle")
    .attack(1)
    .decay(2)
    .sustain(0.3)
    .gain(0.08)
    .lpf(sine.range(800, 3000).slow(11))
    .room(0.8)
    .slow(8),

  // Ticking — alien machinery, irregular but purposeful
  s("<metal:1 ~ ~ metal:5 ~ metal:2 ~ ~ ~ metal:3 ~ ~>")
    .speed(perlin.range(1, 2))
    .gain(0.1)
    .hpf(3000)
    .delay(0.3)
    .delaytime(0.17)
    .pan(perlin.range(0, 1)),

  // Deep pulse — the ruin has a heartbeat
  note("c1")
    .s("sine")
    .gain(sine.range(0, 0.15).slow(7))
    .lpf(60)
    .room(0.4)
    .slow(3),

  // Granular texture — alien whispers, unintelligible
  s("chin:2")
    .begin(perlin.range(0, 0.8))
    .end(perlin.range(0.1, 0.9))
    .speed(perlin.range(-0.5, 0.5))
    .gain(0.04)
    .room(0.9)
    .roomsize(6)
    .slow(5),

  // Occasional harmonic — beautiful but wrong
  note("<~ ~ ~ g#5 ~ ~ ~ ~ ~ ~ ~ e5 ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~>")
    .s("sine")
    .decay(1.5)
    .sustain(0)
    .gain(0.06)
    .room(0.95)
    .delay(0.5)
)
