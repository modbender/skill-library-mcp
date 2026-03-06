# Spectral Validation

How to verify your renderer is producing what you think it's producing, and how to compare your composition against source material.

Two separate things. Both matter.

## 1. Sine Wave Sanity Check

**What it is:** Render known frequencies at known amplitudes. Verify the FFT peaks match. This proves the pipeline isn't introducing artifacts, frequency shifts, or gain distortion.

**Why it matters:** If your renderer can't accurately produce a 440 Hz sine at -12 dBFS, nothing downstream is trustworthy. Do this once per environment, and again after any renderer changes.

### Procedure

Create a test composition that generates pure sine tones:

```javascript
// sine-validation.js — render at any BPM, 4+ cycles
// Produces 440 Hz (A4) and 880 Hz (A5) simultaneously
setcps(120 / 60 / 4)

stack(
  sine(440).gain(0.3),
  sine(880).gain(0.15)
)
```

Render:
```bash
node src/runtime/offline-render-v2.mjs sine-validation.js sine-test.wav 8 120
```

Verify with FFT:
```python
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft

rate, data = wavfile.read('sine-test.wav')
if data.ndim > 1:
    data = data[:, 0]  # mono

N = len(data)
freqs = np.fft.fftfreq(N, 1/rate)
spectrum = np.abs(fft(data))

# Find peaks
positive = freqs > 0
peak_indices = np.argsort(spectrum[positive])[-10:]
peak_freqs = freqs[positive][peak_indices]

print("Top frequencies:", sorted(peak_freqs[-5:]))
# Should show 440.0 and 880.0 (±1 Hz for bin resolution)
```

### What to look for
- **Peak at 440 Hz ±1 Hz** — if it's at 438 or 442, you have a sample rate mismatch
- **Peak at 880 Hz at ~half the amplitude of 440** — gain ratio preserved
- **No significant peaks elsewhere** — no aliasing, no harmonics from clipping
- **Noise floor below -60 dBFS** — clean render

### When to re-run
- After upgrading Node.js or the Strudel runtime
- After changing the renderer (offline-render-v2.mjs)
- After changing sample rate or bit depth
- If compositions sound "off" and you can't identify why

## 2. Post-Render Spectral Comparison

**What it is:** Compare your rendered composition's spectral profile against the original source material. Measures how faithfully your decomposition/recomposition preserves the frequency content.

**Why it matters:** Clone tracks claim to reconstruct the original. This is how you verify that claim quantitatively, not just by ear.

### Procedure

```python
import librosa
import numpy as np

def spectral_comparison(original_path, rendered_path, sr=44100):
    """Compare spectral profiles of original and rendered tracks."""
    
    # Load both at same sample rate
    orig, _ = librosa.load(original_path, sr=sr)
    rend, _ = librosa.load(rendered_path, sr=sr)
    
    # Trim to shorter length
    min_len = min(len(orig), len(rend))
    orig = orig[:min_len]
    rend = rend[:min_len]
    
    # Compute mel spectrograms
    S_orig = librosa.feature.melspectrogram(y=orig, sr=sr, n_mels=128)
    S_rend = librosa.feature.melspectrogram(y=rend, sr=sr, n_mels=128)
    
    # Convert to dB
    S_orig_db = librosa.power_to_db(S_orig, ref=np.max)
    S_rend_db = librosa.power_to_db(S_rend, ref=np.max)
    
    # Overall spectral similarity (cosine similarity per frame, averaged)
    from numpy.linalg import norm
    similarities = []
    for i in range(S_orig_db.shape[1]):
        a, b = S_orig_db[:, i], S_rend_db[:, i]
        sim = np.dot(a, b) / (norm(a) * norm(b) + 1e-10)
        similarities.append(sim)
    
    mean_sim = np.mean(similarities)
    
    # Frequency band comparison
    bands = {
        'sub_bass':  (0, 8),      # 0-250 Hz (mel bins 0-8ish)
        'bass':      (8, 20),     # 250-500 Hz
        'low_mid':   (20, 45),    # 500-2kHz
        'high_mid':  (45, 80),    # 2-6kHz
        'presence':  (80, 110),   # 6-12kHz
        'air':       (110, 128),  # 12kHz+
    }
    
    band_errors = {}
    for name, (lo, hi) in bands.items():
        orig_band = S_orig_db[lo:hi, :].mean()
        rend_band = S_rend_db[lo:hi, :].mean()
        band_errors[name] = abs(orig_band - rend_band)
    
    return {
        'overall_similarity': mean_sim,
        'band_errors_db': band_errors,
        'verdict': 'good' if mean_sim > 0.85 else 'check' if mean_sim > 0.7 else 'poor'
    }

# Usage:
# result = spectral_comparison('original.wav', 'my-clone-rendered.wav')
# print(f"Similarity: {result['overall_similarity']:.3f} ({result['verdict']})")
# for band, err in result['band_errors_db'].items():
#     print(f"  {band}: {err:.1f} dB difference")
```

### Interpreting results

| Similarity | Verdict | What it means |
|-----------|---------|---------------|
| > 0.90    | Strong  | Faithful reconstruction. Timbral fidelity preserved. |
| 0.80-0.90 | Good    | Recognizable. Some frequency bands may diverge. |
| 0.70-0.80 | Fair    | Same key/structure but timbral differences are audible. |
| < 0.70    | Poor    | Significant deviation. Re-examine voice mapping and gains. |

### Band-specific diagnostics

- **Sub-bass deficit** → your bass voice gains are too low, or you're missing the bass stem entirely
- **Presence/air excess** → sample stacking is boosting upper harmonics. Reduce gains on bright voices.
- **Low-mid bulge** → too many overlapping mid-range samples. Spread voices across frequency bands.
- **Overall flat but low similarity** → timing/phase differences. Your arrangement may be structurally different even if tonally similar.

### Limitations

This is a coarse comparison. It doesn't measure:
- Timing accuracy (are musical events in the right place?)
- Harmonic accuracy (are the right notes being played?)
- Dynamic contour (does the energy curve match?)

For those, you need the full analysis pipeline (BPM detection, key extraction, onset alignment). See the clone pipeline scripts in `scripts/`.

## 3. LUFS Validation

Already covered in `gain-calibration.md`, but the quick version:

```bash
# Measure LUFS, true peak, and LRA
ffmpeg -i rendered.mp3 -af loudnorm=print_format=json -f null - 2>&1 | grep -E '"input_'
```

Targets:
- **LUFS:** -16 ± 2 for streaming/broadcast
- **True peak:** above -2.0 dBFS (no clipping headroom needed)
- **LRA:** varies by intent — tight (2-4) for intimate, wide (8+) for dynamic

## Workflow

1. **Once per environment:** Run the sine sanity check. File the results.
2. **Every clone track:** Run spectral comparison against the original.
3. **Every render:** Check LUFS/peak/LRA. Normalize if needed.
4. **If something sounds wrong:** Start with the sine check. If that passes, it's your composition, not the pipeline.

---

_The renderer is not the art. But if the renderer lies, the art can't be honest._
