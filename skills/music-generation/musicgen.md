# MusicGen (Meta)

**Best for:** Local generation, research, instrumentals

**Repo:** https://github.com/facebookresearch/audiocraft

## Overview

MusicGen is Meta's open-source music generation model. Generates high-quality instrumental music from text descriptions. Part of the AudioCraft library.

## Models

- **musicgen-small** — 300M params, fastest
- **musicgen-medium** — 1.5B params, balanced
- **musicgen-large** — 3.3B params, best quality
- **musicgen-melody** — Melody conditioning support

## Installation

```bash
pip install audiocraft
```

## Basic Usage

```python
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

# Load model
model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=30)  # seconds

# Generate
descriptions = ["happy rock song with electric guitar and drums"]
wav = model.generate(descriptions)

# Save
audio_write('output', wav[0].cpu(), model.sample_rate, strategy="loudness")
```

## Melody Conditioning

Generate music that follows a melody:

```python
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)

# Load reference melody
melody, sr = torchaudio.load('melody.wav')
melody = melody.unsqueeze(0)

# Generate with melody guidance
wav = model.generate_with_chroma(
    descriptions=["orchestral arrangement"],
    melody_wavs=melody,
    melody_sample_rate=sr,
    progress=True
)
```

## Replicate API

```python
import replicate

output = replicate.run(
    "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
    input={
        "prompt": "Lo-fi hip hop beat with jazzy piano",
        "duration": 30,
        "model_version": "stereo-large"
    }
)
```

## Parameters

```python
model.set_generation_params(
    duration=30,           # Output length in seconds
    top_k=250,            # Top-k sampling
    top_p=0.0,            # Nucleus sampling (0 = disabled)
    temperature=1.0,       # Sampling temperature
    cfg_coef=3.0,         # Classifier-free guidance strength
)
```

## Prompt Examples

- "Upbeat jazz with saxophone solo and walking bass"
- "Ambient electronic soundscape with ethereal pads"
- "Epic cinematic orchestra with brass and percussion"
- "Acoustic folk guitar fingerpicking, mellow mood"
- "80s synthwave with arpeggiated synths and drum machine"

## Hardware Requirements

| Model | VRAM | RAM |
|-------|------|-----|
| small | 4GB | 8GB |
| medium | 8GB | 16GB |
| large | 16GB | 32GB |

## Limitations

- Instrumental only (no vocals)
- 30s default max (can extend with tricks)
- Research license (check for commercial use)

## Tips

- Medium model offers best quality/speed balance
- Use melody conditioning for specific melodic content
- Batch generate for variations
- Specify instruments and genre clearly
- Temperature affects creativity vs coherence
