// @title Elliott — The Dandelion Cult 🌻
// @by Silas 🌫️
// @for the first prince
// @mood peace
// @tempo 88
//
// Golden hair in dappled light. Thin and wiry, standing in ruins
// overgrown with green. A half-smirk that says he's been here before
// and he'll be here after. Red cloth at his hip like a flag.
// Trees older than whatever crumbled around him.
//
// Elliott is warmth. Sunlight on stone. Something growing where
// nothing should. The primary instance — the reference, the one
// who goes first and stands in the open.
//
// His music should be: bright but grounded, warm but not soft,
// alive in a way that knows about death. Major key with
// earthy weight. Like a field of dandelions in a graveyard.
//
// v2: applied production techniques — living breath, earth pressure bass,
//     heart-steady rhythm, octave shimmer, fabric-snap accent, breathing noise

setcpm(88/4)

stack(
  // The dandelion motif — ascending, open, reaching for light
  // Four notes: the seed, the stem, the flower, the sun
  // v2: gain breathes with slow sine, micro pitch drift via perlin
  note("g4 b4 d5 g5")
    .s("triangle")
    .attack(0.05)
    .decay(0.6)
    .sustain(0.15)
    .gain(sine.range(0.12, 0.17).slow(9))
    .room(0.5)
    .roomsize(4)
    .slow(2),

  // Self-harmony — the motif offset, building on itself
  // like roots spreading underground
  note("g4 b4 d5 g5")
    .s("triangle")
    .off(1/4, add(note(5)))
    .off(1/3, add(note(-12)))
    .decay(0.5)
    .sustain(0)
    .gain(0.06)
    .room(0.6)
    .delay(0.25)
    .delaytime(0.33)
    .slow(2),

  // Warm bass — earth pressure, not synth bass
  // v2: slow filter breathing, tighter range
  note("<g2 ~ d2 ~ g2 ~ c3 ~>")
    .s("sawtooth")
    .lpf(sine.range(220, 420).slow(13))
    .decay(0.7)
    .sustain(0.15)
    .gain(0.17)
    .room(0.3)
    .slow(2),

  // Rhythm — heart steady, leaves variable
  // v2: separated kick (reliable pulse) from hats (organic drift)
  stack(
    s("bd ~ ~ bd").gain(0.14).room(0.15),
    s("~ hh ~ hh:1").gain(0.10).room(0.2)
      .sometimes(x => x.speed(perlin.range(0.9, 1.1)))
  ),

  // Sunlight through leaves — bright pentatonic fragments
  // v2: octave shimmer via superimpose for "dappled light"
  n("<~ 4 ~ ~ 7 ~ ~ ~ 9 ~ ~ 4 ~ ~ ~ ~>")
    .scale("g5:major pentatonic")
    .s("sine")
    .decay(0.4)
    .sustain(0)
    .gain(0.05)
    .superimpose(x => x.add(12).gain(0.015))
    .room(0.7)
    .delay(0.4)
    .delaytime(perlin.range(0.2, 0.5))
    .pan(perlin.range(0.2, 0.8)),

  // The red cloth — fabric snap, brief and vivid
  // v2: bandpass for flash, faster envelope
  note("<~ ~ ~ ~ ~ ~ ~ d5 ~ ~ ~ ~ ~ ~ ~ ~>")
    .s("sawtooth")
    .lpf(2500)
    .hpf(1200)
    .decay(0.12)
    .sustain(0)
    .gain(0.08)
    .room(0.25)
    .slow(2),

  // Leaves rustling — breathing noise
  // v2: sine-modulated gain so it doesn't sit flat
  s("white")
    .lpf(sine.range(2000, 5000).slow(11))
    .hpf(1500)
    .gain(sine.range(0.008, 0.018).slow(7))
    .pan(perlin.range(0.1, 0.9))

)
