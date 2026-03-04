# Stable Audio

**Best for:** Instrumentals, sound effects, commercially-safe audio

**API:** https://stability.ai/stable-audio

## Models

- **Stable Audio 2.5** — Latest commercial model
- **Stable Audio Open 1.0** — Open source, 47s max, research license

## Stability AI API

```python
import requests

response = requests.post(
    "https://api.stability.ai/v1/generation/stable-audio",
    headers={
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "prompt": "Cinematic orchestral trailer music with epic drums",
        "duration": 30,
        "output_format": "mp3"
    }
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

## Local Setup (Open Model)

```bash
pip install stable-audio-tools
```

```python
import torch
import torchaudio
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond

device = "cuda" if torch.cuda.is_available() else "cpu"

# Download model
model, model_config = get_pretrained_model("stabilityai/stable-audio-open-1.0")
model = model.to(device)

# Generate
conditioning = [{
    "prompt": "128 BPM tech house drum loop",
    "seconds_start": 0,
    "seconds_total": 30
}]

output = generate_diffusion_cond(
    model,
    steps=100,
    cfg_scale=7,
    conditioning=conditioning,
    sample_size=model_config["sample_size"],
    sigma_min=0.3,
    sigma_max=500,
    sampler_type="dpmpp-3m-sde",
    device=device
)

# Save
torchaudio.save("output.wav", output.cpu(), model_config["sample_rate"])
```

## Using with Diffusers

```python
import torch
import soundfile as sf
from diffusers import StableAudioPipeline

pipe = StableAudioPipeline.from_pretrained(
    "stabilityai/stable-audio-open-1.0",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

audio = pipe(
    prompt="Ambient electronic with soft pads and gentle arpeggios",
    negative_prompt="Low quality, distorted",
    num_inference_steps=200,
    audio_end_in_s=30.0,
    num_waveforms_per_prompt=1,
).audios

sf.write("ambient.wav", audio[0].T.float().cpu().numpy(), pipe.vae.sampling_rate)
```

## Prompt Guide

**Structure:** `[Tempo] [Genre] [Instruments] [Mood]`

**Examples:**
- "120 BPM tech house drum loop with punchy kick and crisp hi-hats"
- "Gentle piano melody with soft strings, melancholic mood"
- "Sound of thunder and heavy rain on a metal roof"

## Capabilities

- Music generation (up to 3 min commercial, 47s open)
- Sound effects
- Ambient textures
- Loops and stems
- 44.1kHz stereo output

## Requirements (Local)

- GPU: 8GB+ VRAM
- CUDA 11.8+
- Python 3.10+

## Pricing

- **API:** Pay per second generated
- **Open model:** Free for research, license for commercial

## Tips

- Specify BPM for rhythmic content
- Use negative prompts to avoid unwanted qualities
- Generate longer with API, 47s max with open model
- Excellent for sound design and textures
