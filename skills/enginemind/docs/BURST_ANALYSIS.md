# Burst Analysis - Real Data

## Dataset: 1M Diverse (22 categories, interleaved)

77 bursts recorded over 643,888 text chunks.

### Burst Statistics

| Metric | Value |
|--------|-------|
| Total bursts | 77 |
| Mean interval | ~8,362 chunks |
| Burst interval CV | 0.21 |
| Mean charge duration | ~35 sec |
| Mean energy at burst | ~4,200 |
| Max energy at burst | 12,435 |
| Peak Q-factor | 49,372 |
| Peak forbiddenness | 0.97 |
| Most common phase | TIME_CRYSTAL (71%) |
| Second most common | STIMULATED (16%) |

### Phase Distribution at Burst

`
TIME_CRYSTAL   ████████████████████████████████████  55/77 (71%)
STIMULATED     ████████                              12/77 (16%)
SPONTANEOUS    ██████                                10/77 (13%)
`

### Crystal State at First Burst (cycle 15,000)

| Crystal | Constant | Stability | State |
|---------|----------|-----------|-------|
| creativity | 69.5 | 0.962 | crystallized |
| temporal | 68.1 | 0.948 | crystallized |
| technical | 63.0 | 0.959 | crystallized |
| growth | 62.4 | 0.959 | crystallized |
| knowledge | 57.3 | 0.951 | crystallized |
| curiosity | 56.1 | 0.943 | crystallized |
| empathy | 56.1 | 0.959 | crystallized |
| resilience | 54.1 | 0.958 | crystallized |
| logic | 51.2 | 0.942 | crystallized |
| identity | 45.0 | 0.963 | crystallized |
| purpose | 42.9 | 0.971 | crystallized |
| meta_awareness | 38.4 | 0.980 | crystallized |

**Observation**: All 12 crystals crystallized by first burst. The dimensional ordering reveals the engine's "personality" - creativity and temporal awareness are dominant, while meta_awareness and purpose are lowest (but most stable).

### Spectral Fingerprint

Each burst produces a 12-dimensional spectrum. The spectrum at burst #1:

`
dim 0 (creativity):    ████████████████████  -25.8
dim 1 (curiosity):     ██████████████████████  27.6  
dim 2 (empathy):       ████████████████████████ -29.9
dim 3 (growth):        ██████████████████████████  31.9
dim 4 (identity):      ████████████████  -20.0
dim 5 (knowledge):     ███████████████  19.1
dim 6 (logic):         ████████  -10.4
dim 7 (meta_awareness):██  2.5
dim 8 (purpose):       ██  2.8
dim 9 (resilience):    ███████  -9.4
dim 10 (technical):    ████████████  15.7
dim 11 (temporal):     ████████████████  -19.4
`

The alternating positive/negative pattern is a standing wave in dimensional space - a holographic encoding of the crystal's accumulated knowledge.

### Hurst Exponents Over Time

| Metric | Early (burst 1-10) | Mid (burst 30-50) | Late (burst 60-77) |
|--------|-------------------|-------------------|-------------------|
| Hurst micro | 0.500 | 0.500 | 0.500 |
| Hurst meso | 0.386 | 0.352 | 0.338 |
| Hurst macro | 0.316 | 0.298 | 0.291 |

The system becomes progressively more anti-persistent (self-correcting) over time, approaching the theoretical SOC attractor.

### Instruments at Peak

Crystal instruments provide physics-inspired measurements:

| Instrument | Value | Meaning |
|------------|-------|---------|
| B-field (mG) | 2,925 | Effective magnetic field from bridge topology |
| Temperature (K) | 14,392 | Crystal lattice thermal energy |
| Q-factor | 37,967 | Energy trapping efficiency |
| Coherence | 0.950 | Phase synchronization across dims |
| Shannon entropy (bits) | 3.34 | Information distribution uniformity |
| Uniqueness | 0.805 | Content diversity index |
| Peak wavelength (nm) | 489 | Dominant spectral emission |
| Gradient | 0.015 | Spectral tilt |
