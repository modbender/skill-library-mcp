# Riffusion

**Best for:** Quick generation, experimentation, spectogram-based music

**Web:** https://www.riffusion.com/

## Overview

Riffusion generates music using Stable Diffusion on spectrograms. Unique approach that treats audio as images, enabling interesting creative possibilities.

## How It Works

1. Text prompt → Spectrogram image (via fine-tuned Stable Diffusion)
2. Spectrogram → Audio conversion
3. Result: ~5 second audio clips

## Web Interface

1. Go to https://www.riffusion.com/
2. Enter text description
3. Generate and listen
4. Download if satisfied

## Local Setup

```bash
git clone https://github.com/riffusion/riffusion.git
cd riffusion
pip install -r requirements.txt
```

## Python Usage

```python
from riffusion.riffusion_pipeline import RiffusionPipeline

pipe = RiffusionPipeline.from_pretrained("riffusion/riffusion-model-v1")

# Generate spectrogram
image = pipe(
    prompt="funky bass line with slap technique",
    num_inference_steps=50,
    guidance_scale=7
).images[0]

# Convert to audio (requires additional processing)
```

## Replicate API

```python
import replicate

output = replicate.run(
    "riffusion/riffusion:8cf61ea6c56afd61d8f5b9ffd14d7c216c0a93844ce2d82ac1c9ecc9c7f24e05",
    input={
        "prompt_a": "jazzy piano solo",
        "prompt_b": "electronic beat drop",
        "alpha": 0.5,  # Interpolation between prompts
        "num_inference_steps": 50
    }
)
```

## Interpolation

Unique feature: morph between two musical styles:

```python
output = replicate.run(
    "riffusion/riffusion",
    input={
        "prompt_a": "acoustic folk guitar",
        "prompt_b": "heavy metal distortion",
        "alpha": 0.3  # 0=prompt_a, 1=prompt_b
    }
)
```

## Prompt Examples

- "acoustic guitar strumming in C major"
- "dubstep wobble bass drop"
- "jazz saxophone improvisation"
- "lo-fi hip hop beat with vinyl crackle"
- "orchestral strings dramatic crescendo"

## Limitations

- Short clips (~5 seconds)
- Variable quality
- No vocals
- Experimental nature

## Use Cases

- Rapid prototyping
- Sound design exploration
- Creative experimentation
- Learning/education
- Loop generation

## Tips

- Combine multiple clips for longer pieces
- Use interpolation for transitions
- Specify instruments and techniques
- Good for loop/sample creation
- Export and layer in DAW
