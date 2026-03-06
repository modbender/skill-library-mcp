// @title Assault on Sector 7-Gamma
// @by Silas 🌫️
// @mood combat/action
// @scene Urban firefight in a ruined manufactorum.
//        Las-fire crackles, servitors grind, the enemy advances.

setcpm(140/4)

stack(
  // Driving kick and snare — relentless
  s("bd sd [bd bd] sd")
    .gain(0.5)
    .lpf(3000)
    .room(0.1),

  // Fast hihats — urgency
  s("[hh hh] [hh oh] [hh hh] [hh ~]")
    .gain(0.2)
    .speed(1.1)
    .hpf(5000),

  // Aggressive bass — power fifths, driving eighths
  note("[d2 d2 d2 d2 a2 a2 d2 d2]*2")
    .s("sawtooth")
    .lpf(sine.range(600, 2000).slow(4))
    .decay(0.1)
    .sustain(0)
    .gain(0.3)
    .distort(0.2),

  // Industrial percussion — metallic, mechanical
  s("industrial:0 ~ industrial:3 ~ ~ industrial:1 ~ industrial:4")
    .speed(perlin.range(0.8, 1.3))
    .gain(0.15)
    .hpf(2000)
    .pan(perlin.range(0, 1)),

  // Staccato melody — alarm, warning, military
  note("<[d4 ~ f4 ~] [a4 ~ d5 ~] [c5 ~ a4 ~] [f4 ~ d4 ~]>")
    .s("square")
    .decay(0.08)
    .sustain(0)
    .gain(0.15)
    .lpf(4000)
    .distort(0.1)
    .room(0.05),

  // Las-weapon fire — irregular high-pitched zaps
  s("~ ~ glitch:2 ~ glitch:5 ~ ~ glitch:1")
    .speed(perlin.range(1.5, 3))
    .gain(0.08)
    .hpf(8000)
    .pan(perlin.range(0, 1))
    .delay(0.1)
)
