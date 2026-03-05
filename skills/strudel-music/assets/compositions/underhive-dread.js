// @title Underhive Dread
// @by Silas 🌫️
// @mood tension/dread
// @scene Warhammer 40K underhive — dark corridors, dripping pipes,
//        distant machinery, the presence of something wrong

setcpm(65/4)

stack(
  // Deep industrial drone — the hive breathes
  note("c1 ~ c1 ~")
    .s("sawtooth")
    .lpf(200)
    .gain(0.25)
    .room(0.8)
    .roomsize(6)
    .slow(2),

  // Irregular metallic percussion — dripping, clanking
  s("metal:3 ~ ~ metal:7 ~ metal:2 ~ ~")
    .speed(perlin.range(0.4, 0.7))
    .gain(0.12)
    .delay(0.4)
    .delaytime(0.33)
    .pan(sine.range(0.2, 0.8).slow(7)),

  // Heartbeat — something alive in the dark
  s("bd ~ ~ ~ bd ~ ~ ~")
    .speed(0.6)
    .gain(sine.range(0.15, 0.3).slow(11))
    .lpf(300)
    .room(0.5),

  // Dissonant melody fragments — tritones, minor seconds
  note("<c4 ~ ~ db4 ~ ~ gb4 ~ ~ ~ ~ ~ c4 ~ ~ b3 ~ ~ ~ ~ ~ ~ ~ ~>")
    .s("triangle")
    .decay(0.6)
    .sustain(0)
    .lpf(sine.range(400, 1200).slow(13))
    .gain(0.1)
    .room(0.9)
    .delay(0.3),

  // White noise — distant wind through vents
  s("white")
    .lpf(sine.range(100, 400).slow(17))
    .gain(0.04)
    .room(0.6)
)
