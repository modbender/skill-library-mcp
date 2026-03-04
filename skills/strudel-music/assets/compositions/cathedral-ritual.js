// @title Cathedral of the Emperor
// @by Silas 🌫️
// @mood ritual/sacred
// @scene Imperial cathedral — candles, incense, the weight of ten
//        thousand years of devotion. Servo-skulls drift overhead.

setcpm(48/4)

stack(
  // Organ drone — the cathedral's breath
  note("d2,a2")
    .s("sawtooth")
    .lpf(400)
    .attack(2)
    .decay(4)
    .sustain(0.6)
    .gain(0.15)
    .room(1)
    .roomsize(10)
    .slow(8),

  // Gregorian chant — stepwise, narrow range, modal
  note("<d3 e3 f3 e3 d3 ~ d3 c3 d3 ~ ~ ~>")
    .s("sine")
    .attack(0.3)
    .decay(1)
    .sustain(0.4)
    .gain(0.12)
    .room(1)
    .roomsize(8)
    .slow(2),

  // Second voice — canon at the fifth, delayed
  note("<a3 b3 c4 b3 a3 ~ a3 g3 a3 ~ ~ ~>")
    .s("sine")
    .attack(0.3)
    .decay(1)
    .sustain(0.4)
    .gain(0.08)
    .room(1)
    .roomsize(8)
    .slow(2)
    .late(0.5),

  // Ritual bells — sparse, deliberate, marking time
  s("~ ~ ~ bell:1 ~ ~ ~ ~ ~ ~ ~ bell:3")
    .speed(0.5)
    .gain(0.15)
    .room(0.9)
    .roomsize(8)
    .slow(3),

  // Subsonic rumble — the cathedral's foundations
  note("d1")
    .s("sine")
    .gain(0.1)
    .lpf(80)
    .room(0.5)
    .slow(16)
)
