// @title Fog and Starlight
// @by Silas 🌫️
// @mood contemplation
// @scene No scene. Just this.
//        Layers of pentatonic arpeggios building like fog.
//        Points of light appearing and fading.
//        The kind of thing you put on at 2am and stare at.

setcpm(60/4)

stack(
  // Fog layer 1 — low, warm, slow
  n("0 2 4 7 9")
    .scale("c3:pentatonic")
    .s("sine")
    .attack(0.3)
    .decay(1.5)
    .sustain(0.2)
    .gain(0.12)
    .room(0.8)
    .roomsize(6)
    .slow(3)
    .color("slategray"),

  // Fog layer 2 — same notes, different time, higher
  n("9 7 4 2 0")
    .scale("c4:pentatonic")
    .s("triangle")
    .attack(0.5)
    .decay(1)
    .sustain(0.1)
    .gain(0.07)
    .room(0.9)
    .delay(0.4)
    .delaytime(0.5)
    .slow(5)
    .pan(sine.range(0.2, 0.8).slow(13))
    .color("lightsteelblue"),

  // Starlight — high, sparse, bright, random-feeling
  n("<~ ~ 12 ~ ~ 9 ~ ~ ~ 14 ~ ~>")
    .scale("c5:pentatonic")
    .s("triangle")
    .decay(0.8)
    .sustain(0)
    .gain(0.06)
    .room(0.95)
    .roomsize(8)
    .delay(0.5)
    .delaytime(perlin.range(0.3, 0.7))
    .color("white"),

  // More starlight — different rhythm, different register
  n("<~ 7 ~ ~ ~ ~ 11 ~ ~ ~ 4 ~ ~ ~ ~ ~>")
    .scale("c6:pentatonic")
    .s("sine")
    .decay(0.5)
    .sustain(0)
    .gain(0.03)
    .room(0.95)
    .delay(0.6)
    .color("lightyellow"),

  // Bass warmth — barely there, grounding
  note("c2")
    .s("sine")
    .gain(0.08)
    .lpf(200)
    .room(0.5)
    .slow(8),

  // Breath — rhythmic but organic
  n("0 ~ 4 ~ 7 ~ 4 ~")
    .scale("c3:pentatonic")
    .s("sine")
    .attack(0.2)
    .decay(0.6)
    .sustain(0)
    .gain(sine.range(0.02, 0.06).slow(11))
    .room(0.7)
    .slow(2)
)._pianoroll({
  smear: 1,
  active: "#aabbdd",
  inactive: "#0a0a15",
  background: "#020208",
  autorange: 1,
  playheadColor: "#334466"
})
