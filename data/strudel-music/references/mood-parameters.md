# Mood → Pattern Parameter Decision Tree

## Mood Classes

### tension (60-80 BPM)
- **Key**: D minor, A phrygian
- **Filter**: Low cutoff (200-800 Hz), slow sweep
- **Percussion**: Sparse, metallic, irregular
- **Dynamics**: pp → mf builds
- **Pattern**: Drones + sparse melody, `.slow(3)`, heavy reverb
- **Transition in**: Gradual filter close from exploration/peace
- **Transition out**: Sharp cut to combat, slow open to resolution

### combat (120-160 BPM)
- **Key**: D minor, E minor
- **Filter**: Wide band (600-4000 Hz), aggressive sweep
- **Percussion**: Driving kick-snare, fast hihats, distorted
- **Dynamics**: ff throughout, accented downbeats
- **Pattern**: `s("bd sd [bd bd] sd")`, `.fast(2)`, `.distort(0.2)`
- **Transition in**: Sharp cut from any mood
- **Transition out**: Gradual to tension (tempo + filter drop), sharp to victory

### exploration (80-100 BPM)
- **Key**: C dorian, G mixolydian
- **Filter**: Mid-high (1000-3000 Hz), moderate movement
- **Percussion**: Light, syncopated, `.euclid(3,8)`
- **Dynamics**: mp, dynamic swells
- **Pattern**: Open voicings, `.delay(0.3)`, `.jux(rev)`
- **Transition in**: Gradual from peace (add percussion), from tension (open filter)
- **Transition out**: To mystery (introduce whole tones), to tension (close filter)

### peace (60-80 BPM)
- **Key**: C pentatonic, F major
- **Filter**: Warm (800-2000 Hz), minimal movement
- **Percussion**: None or very sparse
- **Dynamics**: pp-p, gentle
- **Pattern**: Sustained pads, `.slow(4)`, `.room(0.8)`, pentatonic arpeggios
- **Transition in**: Gradual from any (fade percussion, open filter, slow tempo)
- **Transition out**: Gradual to exploration (add rhythm), to tension (darken scale)

### mystery (70-90 BPM)
- **Key**: C whole tone, Bb lydian
- **Filter**: Varied, unpredictable
- **Percussion**: Sparse, irregular timing, unusual samples
- **Dynamics**: pp with sudden mf stabs
- **Pattern**: `.sometimes(rev)`, wide `.delay()`, `perlin` modulation
- **Transition in**: From exploration (introduce augmented/whole tone intervals)
- **Transition out**: To tension (resolve to minor), to discovery (add harmonic clarity)

### victory (110-130 BPM)
- **Key**: D major, Bb major
- **Filter**: Bright, wide open (2000-8000 Hz)
- **Percussion**: Triumphant, marcato, brass-like patterns
- **Dynamics**: ff, crescendo builds
- **Pattern**: Major fanfare, `.fast(1)`, stacked fifths, rising sequences
- **Transition in**: Sharp cut from combat (key change to major)
- **Transition out**: Gradual to peace (reduce energy), to exploration (reduce intensity)

### sorrow (48-65 BPM)
- **Key**: A minor, E minor
- **Filter**: Low-mid (400-1500 Hz), static
- **Percussion**: None or very sparse brushes
- **Dynamics**: pp, barely audible
- **Pattern**: Long sustained notes, `.slow(8)`, `.room(0.9)`, minor 7ths
- **Transition in**: Gradual from any (strip layers, slow tempo, darken)
- **Transition out**: To peace (introduce pentatonic warmth), to tension (add edge)

### ritual (45-60 BPM)
- **Key**: D dorian, A mixolydian
- **Filter**: Low-mid, resonant peaks
- **Percussion**: Ceremonial, repetitive, tabla/bells
- **Dynamics**: mp, steady, hypnotic
- **Pattern**: Organ drones, canon/round patterns, `.off(0.5, id)`, chant-like melody
- **Transition in**: From peace (add modal color), from mystery (add rhythmic structure)
- **Transition out**: To tension (darken), to peace (strip to drone)

## Leitmotif System

Characters get signature patterns stored as named variables:

```javascript
// Define a character theme
const hero = note("c4 e4 g4 c5").s("piano").decay(0.5).gain(0.1)

// Weave into scene composition at low gain
stack(currentScene, hero.slow(4).room(0.6))
```

Leitmotif intensity scales with narrative prominence:
- Background presence: `.gain(0.03)`, `.slow(6)`
- Active scene: `.gain(0.08)`, `.slow(2)`
- Featured moment: `.gain(0.15)`, no slow

## Transition Rules

- **Sharp cut**: Immediate change, no crossfade. Use for combat entry, dramatic reveals.
- **Gradual build**: 4-8 cycles of parameter interpolation. Use for tension building, mood shifts.
- **Crossfade**: Overlap two patterns, one fading in as other fades out. Use for scene changes.

In Strudel, transitions are achieved by evaluating new pattern code — the engine crossfades automatically when you call `evaluate()` with a new pattern.
