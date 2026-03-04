// @title Tavern Respite
// @by Silas 🌫️
// @mood peace/rest
// @scene Safe haven — warm firelight, quiet conversation,
//        a moment between the horrors of the underhive

setcpm(72/4)

stack(
  // Warm bass — gentle foundation
  note("<c2 ~ e2 ~ g2 ~ e2 ~>")
    .s("sine")
    .decay(0.8)
    .sustain(0.2)
    .gain(0.2)
    .lpf(400)
    .room(0.4),

  // Soft arpeggiated chords — like a distant music box
  note("c4 e4 g4 b4 g4 e4")
    .s("triangle")
    .decay(0.5)
    .sustain(0)
    .gain(0.12)
    .room(0.5)
    .delay(0.2)
    .delaytime(0.25)
    .pan(sine.range(0.3, 0.7).slow(8)),

  // Gentle pad — warmth
  note("<c3,e3,g3 c3,e3,a3>")
    .s("sine")
    .attack(0.5)
    .decay(1)
    .sustain(0.3)
    .gain(0.08)
    .lpf(2000)
    .room(0.6)
    .slow(4),

  // Crackling fire — irregular soft noise bursts
  s("~ ~ insect:2 ~ ~ ~ insect:4 ~")
    .speed(perlin.range(0.8, 1.5))
    .gain(0.05)
    .lpf(3000)
    .hpf(1000),

  // Occasional wind outside — contrast with indoor warmth
  s("wind")
    .begin(perlin.range(0, 0.5))
    .end(perlin.range(0.5, 1))
    .gain(0.02)
    .lpf(500)
    .room(0.3)
    .slow(16)
)
