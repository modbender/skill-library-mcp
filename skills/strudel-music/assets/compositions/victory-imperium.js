// @title For the Emperor
// @by Silas 🌫️
// @mood victory/triumph
// @scene The enemy is broken. The banner stands.
//        Smoke clears to reveal dawn over the hive spires.
//        The Emperor protects.

setcpm(120/4)

stack(
  // Triumphant fanfare — ascending fifths, brass-like
  note("<[d4 ~ a4 ~ d5 ~ a5 d6] ~>")
    .s("sawtooth")
    .superimpose(add(0.03))
    .decay(0.3)
    .sustain(0.1)
    .gain(0.25)
    .lpf(6000)
    .room(0.4)
    .slow(2),

  // Full drums — victorious march
  s("[bd ~ bd ~] [sd ~ sd ~] [bd bd ~ ~] [sd ~ ~ oh]")
    .gain(0.4)
    .room(0.2),

  // Cymbal crashes on the ones
  s("oh ~ ~ ~ ~ ~ ~ ~")
    .gain(0.2)
    .decay(0.5)
    .room(0.3)
    .slow(2),

  // Power chord progression — D major glory
  note("<d3,a3,d4 g3,b3,d4 a3,c#4,e4 d3,a3,d4>")
    .s("sawtooth")
    .superimpose(add(0.02))
    .attack(0.05)
    .decay(0.8)
    .sustain(0.4)
    .gain(0.15)
    .lpf(3000)
    .room(0.3)
    .slow(2),

  // Bass — solid root motion
  note("<d2 g2 a2 d2>")
    .s("sawtooth")
    .lpf(500)
    .decay(0.4)
    .sustain(0.2)
    .gain(0.25)
    .slow(2),

  // Heroic melody — ascending, open intervals
  note("<[d5 ~ e5 f#5] [a5 ~ f#5 ~] [g5 ~ a5 b5] [d6 ~ ~ ~]>")
    .s("square")
    .decay(0.2)
    .sustain(0.1)
    .gain(0.12)
    .lpf(5000)
    .room(0.3)
    .slow(2)
)
