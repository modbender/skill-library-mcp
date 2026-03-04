# Sample Pack Registry

CC-licensed sample packs tested with the offline renderer.

## Included (installed via `npm run setup`)

### Dirt-Samples (CC)
- **Source:** https://github.com/tidalcycles/Dirt-Samples
- **License:** CC (various, mostly CC-BY-SA)
- **Packs installed:** bd, sd, hh, oh, cp, cr, ride, rim, mt, lt, ht, cb, 808bd, 808sd, 808hc, 808oh
- **Total:** ~156 WAV files
- **Usage:** `s("bd")`, `s("sd").n(2)`, `s("808bd")`

## Recommended Add-Ons

### Signature Sounds — Homemade Drum Kit (CC0)
- **Source:** https://signalsounds.com/free-stuff/
- **License:** CC0 (public domain)
- **Contents:** 150+ one-shots (kicks, snares, hats, percussion, textures)
- **Install:** Download ZIP → `bash scripts/samples-manage.sh add homemade-drum-kit.zip`

### Legowelt Sample Kits (free)
- **Source:** https://legowelt.org/samples/
- **License:** Free for any use
- **Contents:** Analog synth one-shots, drum machines, effects
- **Install:** Download ZIP → `bash scripts/samples-manage.sh add <file>.zip`

### One Laptop Per Child samples (CC-BY)
- **Source:** Via Strudel's built-in `bank("casio")`, `bank("gm")` etc.
- **License:** CC-BY
- **Note:** These are URL-loaded in Strudel's browser mode. For offline use, download WAVs and place in `samples/`

### Strudel Built-in Banks (URL-based, browser only)
In browser Strudel, `bank("RolandTR909")` loads from CDN. For offline rendering,
you need local WAV files. Export from Strudel REPL or download from:
- Roland TR-909: Various CC0 sample packs on Freesound.org
- LinnDrum: Available on Archive.org (public domain)
- Roland CR-78: Various free packs

## Adding Custom Packs

```bash
# From URL (ZIP, tar.gz, single WAV)
bash scripts/samples-manage.sh add https://example.com/my-pack.zip

# From local directory
bash scripts/samples-manage.sh add ~/my-samples/drum-rack/

# From DAW export
# Export your Ableton/M8/Renoise kit as WAV files into a folder, then:
bash scripts/samples-manage.sh add ~/exports/my-kit/
```

Any directory of WAV files in `samples/<name>/` is auto-discovered by the renderer.
Use them with `s("<name>")` in patterns. Files are numbered by sort order: `s("<name>").n(0)` plays the first file.

## Field Recordings

The renderer supports any WAV file at any sample rate (resampled to 44.1kHz on load).
Field recordings work great for ambient textures:

```javascript
s("rain").gain(0.15).lpf(2000).slow(4)  // gentle rain loop
s("birds").n("<0 1 2>").delay(0.3)       // scattered bird calls
```

Record with any phone/device, trim to ~1-5 seconds, export as WAV, drop in `samples/rain/` or `samples/birds/`.
