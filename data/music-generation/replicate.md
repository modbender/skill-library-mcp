# Replicate (Multi-Provider)

**Best for:** Quick testing, model variety, pay-per-use

**API:** https://replicate.com/

## Setup

```bash
pip install replicate
export REPLICATE_API_TOKEN="r8_xxx"
```

## Available Music Models

### MusicGen (Meta)

```python
import replicate

output = replicate.run(
    "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
    input={
        "prompt": "Upbeat electronic dance music with synth leads",
        "model_version": "stereo-large",
        "duration": 30
    }
)
# Returns URL to audio file
```

### Riffusion

```python
output = replicate.run(
    "riffusion/riffusion:8cf61ea6c56afd61d8f5b9ffd14d7c216c0a93844ce2d82ac1c9ecc9c7f24e05",
    input={
        "prompt_a": "jazz piano",
        "prompt_b": "electronic beats",
        "alpha": 0.5
    }
)
```

### Stable Audio

```python
output = replicate.run(
    "stability-ai/stable-audio-open-1.0",
    input={
        "prompt": "Ambient soundscape with ethereal pads",
        "duration": 30
    }
)
```

### MusicGen Melody

```python
output = replicate.run(
    "meta/musicgen:melody",
    input={
        "prompt": "orchestral arrangement",
        "input_audio": open("melody.wav", "rb"),
        "duration": 30
    }
)
```

## Model Comparison

| Model | Duration | Vocals | Quality | Cost |
|-------|----------|--------|---------|------|
| MusicGen Large | 30s | ❌ | Excellent | ~$0.10 |
| MusicGen Medium | 30s | ❌ | Good | ~$0.05 |
| Riffusion | 5s | ❌ | Variable | ~$0.02 |
| Stable Audio | 47s | ❌ | Good | ~$0.08 |

## Async Pattern

```python
# Start generation
prediction = replicate.predictions.create(
    model="meta/musicgen",
    input={"prompt": "epic orchestral music", "duration": 60}
)

# Poll for completion
import time
while prediction.status not in ["succeeded", "failed"]:
    prediction.reload()
    time.sleep(2)

# Get result
if prediction.status == "succeeded":
    audio_url = prediction.output
```

## Webhook Support

```python
prediction = replicate.predictions.create(
    model="meta/musicgen",
    input={"prompt": "..."},
    webhook="https://your-server.com/webhook",
    webhook_events_filter=["completed"]
)
```

## Batch Generation

```python
prompts = [
    "happy pop song",
    "dark ambient drone",
    "energetic rock riff"
]

predictions = []
for prompt in prompts:
    p = replicate.predictions.create(
        model="meta/musicgen",
        input={"prompt": prompt, "duration": 30}
    )
    predictions.append(p)

# Wait for all
for p in predictions:
    while p.status not in ["succeeded", "failed"]:
        p.reload()
        time.sleep(2)
```

## Tips

- MusicGen Large for best instrumental quality
- Riffusion for quick experiments
- Use webhooks for production
- Batch generations for efficiency
- Cache results — URLs are temporary
