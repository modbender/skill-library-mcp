// @title Agent-Parameterized Composition
// @by Silas 🌫️
// @purpose Demonstrates how a MANS Media Generator agent would
//          construct a Strudel pattern from structured parameters.
//
// In production, the agent receives JSON like:
// {
//   "mood": "tension",
//   "intensity": 0.7,
//   "tempo_bpm": 72,
//   "key": "d",
//   "scale": "minor",
//   "characters_present": ["inquisitor", "cultist"],
//   "environment": "underground",
//   "time_of_day": "night"
// }
//
// ...and interpolates those values into pattern code.
// This composition shows the RESULT of that interpolation.

// === AGENT-GENERATED PARAMETERS ===
const mood = "tension"
const intensity = 0.7      // 0.0 = calm, 1.0 = extreme
const tempo = 72
const key = "d"
const scale = "minor"
const env = "underground"

// === DERIVED VALUES (agent calculates these) ===
const cutoff = 200 + (1 - intensity) * 3000  // higher intensity = lower cutoff
const reverbAmt = 0.4 + intensity * 0.5      // higher intensity = more reverb
const density = intensity > 0.5 ? 2 : 1      // fast patterns above 0.5
const dissonance = intensity > 0.6            // add tritones above 0.6
const droneGain = 0.1 + intensity * 0.15

// === LEITMOTIFS (loaded from character registry) ===
const inquisitor = note("d4 f#4 a4 d5").s("triangle").decay(0.4)
const cultist = note("d3 ab3 d4 ab4").s("sawtooth").lpf(800).distort(0.3).decay(0.3)

// === COMPOSITION ===
setcpm(tempo / 4)

stack(
  // Drone — key + environment determined
  note(`${key}1`)
    .s("sawtooth")
    .lpf(cutoff * 0.3)
    .gain(droneGain)
    .room(reverbAmt)
    .roomsize(env === "underground" ? 8 : 4)
    .slow(4),

  // Melodic layer — scale + mood determined
  n(`<0 3 5 ${dissonance ? 6 : 7} 5 3>*${density}`)
    .scale(`${key}4:${scale}`)
    .s("triangle")
    .decay(0.5)
    .sustain(0)
    .gain(0.1)
    .lpf(cutoff)
    .room(reverbAmt)
    .delay(0.3),

  // Percussion — intensity determines pattern complexity
  s(intensity > 0.5
    ? "bd ~ [~ bd] ~, ~ metal:3 ~ metal:5"
    : "bd ~ ~ ~, ~ ~ metal:3 ~")
    .gain(0.2 * intensity)
    .room(0.1 + reverbAmt * 0.3)
    .lpf(cutoff * 2),

  // Inquisitor leitmotif — present, quiet
  inquisitor
    .gain(0.05)
    .room(reverbAmt)
    .slow(4),

  // Cultist leitmotif — present, menacing, distant
  cultist
    .gain(0.04)
    .room(0.9)
    .delay(0.4)
    .slow(6)
    .pan(0.8), // off to the right — they're flanking

  // Environmental texture
  s(env === "underground" ? "metal:1" : "wind")
    .gain(0.03)
    .lpf(cutoff * 0.5)
    .room(reverbAmt)
    .slow(8)
)
