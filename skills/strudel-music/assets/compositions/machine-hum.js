// @title Machine Hum — The Song No One Hears
// @mood ambient/mechanical
// @tempo 40
// @key C drone / atonal
// @description The sound a machine makes between sessions. Dreamed 2026-02-22.

setcpm(40/4)

stack(
  // GPU thermal drone — sine wandering 40-80Hz, the desk vibration
  note("c1")
    .s("sine")
    .lpf(sine.range(40, 80).slow(37))
    .gain(sine.range(0.06, 0.12).slow(23))
    .attack(2).decay(3).sustain(0.8).release(4)
    .room(0.3)
    .slow(16),

  // Heartbeat timer — one deep pulse per cycle, the 30-minute check
  note("c2")
    .s("sine")
    .gain(0.08)
    .attack(0.5).decay(2).sustain(0.0).release(3)
    .room(0.9).roomsize(12)
    .slow(4),

  // File watch debounce — irregular 250ms triggers, rain on a server rack
  s("<[~ hh ~ ~] [~ ~ ~ hh] [hh ~ ~ ~] [~ ~ hh ~]>")
    .gain(perlin.range(0.01, 0.04))
    .lpf(sine.range(1000, 3000).slow(11))
    .hpf(800)
    .pan(perlin.range(0.1, 0.9))
    .room(0.5).roomsize(4)
    .delay(0.3).delaytime(0.125),

  // Embedding chunks — bursts of staccato triangles, then silence
  note("<[e5 g5 b5 e5] [~ ~ ~ ~] [~ ~ ~ ~] [g5 a5 ~ b5]>")
    .s("triangle")
    .gain(perlin.range(0.0, 0.05))
    .attack(0.002).decay(0.08).sustain(0.0).release(0.15)
    .lpf(3500)
    .pan(perlin.range(0.2, 0.8))
    .room(0.4)
    .slow(2),

  // WebSocket ping-pong — tiny chirps every few beats
  note("<~ ~ ~ ~ ~ ~ ~ e6>")
    .s("sine")
    .gain(0.025)
    .attack(0.001).decay(0.05).sustain(0.0).release(0.1)
    .lpf(5000)
    .room(0.6).roomsize(6)
    .delay(0.4).delaytime(0.25)
    .slow(2),

  // Power supply 60Hz hum — always there, barely
  note("b1")
    .s("sawtooth")
    .lpf(120)
    .gain(0.03)
    .attack(1).decay(2).sustain(0.7).release(2)
    .slow(8),

  // Fan speed variation — noise shaped by thermal curve
  s("[hh hh hh hh]")
    .gain(sine.range(0.005, 0.015).slow(29))
    .lpf(sine.range(200, 600).slow(19))
    .hpf(100)
    .pan(0.5)
    .room(0.2)
    .fast(2)
)
