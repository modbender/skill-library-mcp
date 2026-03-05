# Strudel Pattern Transforms — Deep Reference

The core pattern engine (`@strudel/core/pattern.mjs`) provides transforms that turn simple seeds into complex evolving music.

## Time Transforms

### `.slow(n)` / `.fast(n)`
Stretch or compress time. `.slow(2)` = half speed, `.fast(3)` = triple speed.
```javascript
note("c e g").slow(2)   // takes 2 cycles instead of 1
s("bd sd").fast(4)       // 4x speed, fills one cycle with 4 repetitions
```

### `.early(n)` / `.late(n)`
Shift pattern in time without changing speed.
```javascript
s("bd sd").late(0.25)   // delays by quarter cycle
```

## Structure Transforms

### `.every(n, fn)`
Apply a function every N cycles — creates evolution without repetition.
```javascript
s("bd sd bd sd").every(4, fast(2))       // double speed every 4th cycle
note("c e g b").every(3, x => x.rev())  // reverse every 3rd cycle
```

### `.sometimes(fn)` / `.often(fn)` / `.rarely(fn)`
Apply function with probability (50%, 75%, 25% respectively).
```javascript
s("hh hh hh hh").sometimes(x => x.speed(2))  // randomly double speed
note("c e g").rarely(rev)                       // occasionally reverse
```

### `.someCyclesBy(p, fn)`
Apply function with custom probability p (0-1).
```javascript
s("bd sd").someCyclesBy(0.3, fast(2))  // 30% chance each cycle
```

## Polyphonic Transforms

### `.off(time, fn)`
Play the original + a transformed copy offset in time. Creates self-harmony.
```javascript
note("c4 e4 g4").off(0.125, x => x.add(7))  // echo a fifth up, offset by 1/8
note("c4 e4 g4").off(0.25, x => x.add(12))  // octave up, offset by 1/4
```

### `.jux(fn)`
Apply function to right channel only — instant stereo depth.
```javascript
s("bd sd hh oh").jux(rev)              // right channel reversed
note("c e g b").jux(x => x.add(7))    // right channel a fifth up
```

### `.superimpose(fn)`
Stack the original with a transformed copy (both centered).
```javascript
note("c4 e4 g4").superimpose(x => x.add(12).gain(0.5))  // octave doubling
s("bd sd").superimpose(x => x.speed(1.5).gain(0.3))      // pitched copy
```

### `stack(a, b, ...)`
Layer multiple patterns simultaneously.
```javascript
stack(
  s("bd sd bd sd"),
  s("hh*8"),
  note("c3 g3").s("bass")
)
```

## Melodic Transforms

### `.add(n)` / `.sub(n)`
Transpose by semitones (with note) or scale degrees (with n + scale).
```javascript
note("c4 e4 g4").add(7)  // transpose up a fifth
n("0 2 4").scale("C:minor").add(2)  // up 2 scale degrees
```

### `.rev()`
Reverse the pattern.
```javascript
note("c d e f g").rev()  // g f e d c
```

### `.palindrome()`
Play forward then backward.
```javascript
note("c d e f").palindrome()  // c d e f f e d c
```

## Rhythmic Transforms

### `.euclid(pulses, steps, [offset])`
Distribute pulses evenly across steps — generates complex rhythms from simple parameters.
```javascript
s("bd").euclid(3, 8)    // . x . x . x . .  (tresillo)
s("hh").euclid(5, 8)    // x . x x . x x .
s("sd").euclid(7, 16)   // complex 7-over-16
```

### `.mask(pattern)`
Use a binary pattern to gate another.
```javascript
note("c d e f g a b c5").mask("1 1 0 1 0 1 0 1")  // selective notes
```

## Modulation Sources

### `sine`, `cosine`, `saw`, `square`, `tri`
LFO-style continuous patterns for parameter modulation.
```javascript
.lpf(sine.range(400, 4000).slow(8))    // sweeping filter
.gain(sine.range(0.1, 0.4).slow(4))    // tremolo
.pan(sine.range(0, 1).slow(7))         // autopan
```

### `perlin`
Perlin noise — smooth randomness.
```javascript
.speed(perlin.range(0.9, 1.1))  // subtle pitch drift
.pan(perlin.range(0, 1))        // random panning
```

## Composition Patterns

### Minimal seed → maximum variation
```javascript
// Start with just 4 notes
note("c4 eb4 g4 bb4")
  .s("triangle")
  .off(0.125, x => x.add(12).gain(0.3))  // octave echo
  .jux(rev)                                // stereo reverse
  .every(4, x => x.fast(2))               // rhythmic variation
  .sometimes(x => x.add(7))               // harmonic variation
  .slow(2)
  .room(0.5)
```

### Generative evolution
```javascript
n("0 2 4 7 9")
  .scale("C:pentatonic")
  .s("piano")
  .every(3, x => x.add(2))       // shift up every 3 cycles
  .every(5, x => x.rev())        // reverse every 5 cycles
  .every(7, x => x.fast(1.5))    // speed up every 7 cycles
  .off(0.25, x => x.add(7))      // fifth harmony
  .slow(2)
  .room(0.6)
```
The prime numbers (3, 5, 7) ensure patterns don't align, creating long non-repeating sequences.
