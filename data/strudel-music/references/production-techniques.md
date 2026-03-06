# Production Techniques for Strudel

## Oscillator Expression (making synths feel alive)

### Living breath (avoid static loops)
```javascript
note("g4 b4 d5 g5")
  .s("triangle")
  .gain(sine.range(0.12, 0.17).slow(9))      // subtle volume swell
  .sometimes(x => x.speed(perlin.range(0.98, 1.02)))  // micro pitch drift
```

### Earth pressure bass (not "synth bass")
```javascript
note("<g2 ~ d2 ~>")
  .s("sawtooth")
  .lpf(sine.range(220, 420).slow(13))  // slow filter breathing
  .decay(0.7).sustain(0.15)
```

### Shimmer via octave doubling
```javascript
n("0 4 7 9").scale("C:major pentatonic").s("sine")
  .superimpose(add(12).gain(0.015))  // faint octave ghost
  .room(0.7).delay(0.4)
  .delaytime(perlin.range(0.2, 0.5))
```

### Fast accent ("fabric snap")
```javascript
note("<~ ~ ~ ~ ~ ~ ~ d5>")
  .s("sawtooth")
  .bp(1800)        // bandpass for flash
  .decay(0.12)
  .gain(0.08)
```

### Breathing noise
```javascript
s("white")
  .lpf(sine.range(2000, 5000).slow(11))
  .hpf(1500)
  .gain(sine.range(0.008, 0.018).slow(7))
  .pan(perlin.range(0.1, 0.9))
```

## Rhythm (organic but anchored)

### Heart steady, leaves variable
```javascript
stack(
  s("bd ~ ~ bd").gain(0.14),                    // reliable pulse
  s("~ hh ~ hh:1").gain(0.10)
    .sometimes(x => x.speed(perlin.range(0.9, 1.1)))  // drift
)
```

## Sample Banks

### Named banks (built-in)
```javascript
sound("bd sd cp hh").bank("RolandTR909")
sound("bd sd hh oh").bank("LinnDrum")
sound("sh*8").bank("RolandTR808")
```

### GM (General MIDI) instruments
```javascript
.n(1).sound("gm_pad_poly")      // poly synth pad
.n(0).sound("gm_synth_bass_1")  // synth bass
.n(1).sound("gm_pad_metallic")  // metallic pad
```

### Custom samples from URL
```javascript
samples({
  vox: 'vocals.wav',
  lead: ['lead_a.wav', 'lead_b.wav'],
}, 'https://example.com/samples/');

s("vox").begin(0).end(0.25)  // slice the sample
```

### Custom samples from local directory
```javascript
// Drop WAV files in samples/<name>/ directory
// Automatically discovered by the renderer
s("bd sd hh").n(3)  // pick variation 3
```

## Song Structure

### Per-measure sequencing with cat()
```javascript
let bass = cat(
  "<c2>*4",      // measure 1
  "<g1>*4",      // measure 2
  "<eb1>*4",     // measure 3
  "<f1>*4"       // measure 4
)
```

### Song sections with arrange()
```javascript
let intro = stack(vocals, pad)
let verse = stack(drums, bass, synth)
let chorus = stack(drums, bass, synth, lead, vocals)

arrange(
  [8, intro],    // 8 cycles of intro
  [16, verse],   // 16 cycles of verse
  [8, chorus],   // 8 cycles of chorus
  [4, intro]     // 4 cycles outro
).cpm(135/4)
```

## CC-Licensed Sample Packs

### CC0 / Public Domain
- **Dirt-Samples** (tidalcycles/Dirt-Samples) — default Strudel/TidalCycles pack, 800+ samples
- **Signature Sounds – Homemade Drum Kit** (CC0) — 150+ one-shots
- **Signature Sounds – Trap Vault** (CC0) — 49 tempo-labeled loops
- **Free Music Archive – Loop Mania** (CC0) — beats/percs/bass fragments
- **Freesound – deadrobotmusic "Web Crawler"** (CC0) — percussion/kick/snare/synth textures
- **Looping – Synth Pack 01** (CC0) — one-shots + loopables

### CC BY-NC-SA (attribution + non-commercial)
- **Wilkinson Audio – CC Drum Samples**

### Aggregators
- **artgamesound.com** — searchable CC0 sound index
