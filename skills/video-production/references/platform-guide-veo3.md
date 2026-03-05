# Veo 3 Platform Guide

## Overview
Google's Veo 3 generates high-quality cinematic video clips from detailed text prompts. Supports up to 1080p, 60 seconds per generation.

## Setup

### 1. Google Cloud Project
1. Go to: https://console.cloud.google.com
2. Create new project (e.g., "Video Production")
3. Enable Generative AI API in APIs & Services

### 2. Billing
1. Go to Billing → Create Billing Account
2. Add payment method (credit card)
3. Link billing account to project
4. Wait 5-15 minutes for activation

### 3. API Key
1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → API Key
3. Copy the key (format: `AIza...`)

### 4. Local Setup
```bash
export GOOGLE_API_KEY="AIza..."
echo 'export GOOGLE_API_KEY="AIza..."' >> ~/.zshenv

python3 -m venv venv
source venv/bin/activate
pip install google-genai==1.45.0
```

## Model Selection

- **veo-3.1-generate-preview** (Higher quality, slower)
  - Recommended for final projects
  - ~2-10 min per video

- **veo-3.1-fast-generate-preview** (Faster, good quality)
  - Recommended for iteration
  - ~1-5 min per video

- **veo-3.0-generate-001** / **veo-3.0-fast-generate-001** (Older)
  - Use only if 3.1 unavailable

## Prompting for Cinema

### Structure
```
[SHOT TYPE] of [SUBJECT] [ACTION].
[LIGHTING].
[CAMERA MOVEMENT].
[STYLE/REFERENCE].
[SPECIFIC DETAILS].
```

### Shot Types
- Wide shot / Extreme wide
- Close-up / Macro close-up
- Medium shot / Over-the-shoulder
- Low angle / High angle
- Dutch angle (tilted frame)

### Camera Movements
- Static (no movement)
- Slow push-in (toward subject)
- Whip pan (quick pan)
- Smooth tracking shot
- Crane up/down

### Lighting Keywords
- Golden hour
- Cool blue / Cyan
- Warm orange
- Rim lighting
- Lens flare
- Film grain

### Style References
- "Denis Villeneuve style" (epic, wide, contemplative)
- "Michael Bay cinematography" (dramatic, high-energy)
- "Blade Runner 2049 aesthetic" (sci-fi, cool-toned, detailed)
- "Hans Zimmer energy" (dramatic, intense)
- "Terrence Malick" (intimate, poetic, introspective)

### Example Prompts

**Hero Shot**
```
Epic low-angle hero shot of a woman standing in front of a massive wall of holographic screens 
displaying data, charts, and code. Cool blue and orange lighting. Dramatic rim lighting. 
Michael Bay cinematography. The woman looks confident, determined. Futuristic command center. 
Lens flare on transitions.
```

**Intimate Character**
```
Intimate close-up of a man's face in natural light, looking directly at camera with 
a thoughtful expression. Soft golden hour light streaming from a window. Extremely shallow 
depth of field. Terrence Malick cinematography. Film grain. Vulnerable, introspective moment.
```

**Establishing Shot**
```
Extreme wide shot at sunset. A lone figure stands on a rooftop overlooking a sprawling cityscape. 
Silhouette against an epic orange and purple sky. Cinematic 2.39:1 aspect ratio. 
Denis Villeneuve composition. Contemplative, existential mood.
```

## API Usage

```python
from google import genai

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

response = client.models.generate_videos(
    model="veo-3.1-fast-generate-preview",
    prompt="Your detailed prompt here"
)

# response.video contains the MP4 file URI
print(response.video)
```

## Cost

| Duration | Cost | Notes |
|----------|------|-------|
| 6 sec | ~$0.05 | Fast model |
| 12 sec | ~$0.10 | Requires extension |
| 24 sec | ~$0.20 | Requires extension |

**Budget tip**: Start with fast model for iteration, use regular model for finals.

## Limitations

- Max ~60 seconds per video (via extension)
- ~1080p resolution max
- Generates auto audio (can be replaced in assembly)
- Rate limited (queue times during peak hours)

## Troubleshooting

**429 RESOURCE_EXHAUSTED**
- Billing not activated (wait 5-15 min)
- Check: https://console.cloud.google.com/billing/projects

**API rate limit hit**
- Add delay between requests: `time.sleep(10)`
- Reduce concurrent requests

**Video quality low**
- Switch from fast to regular model
- More detailed prompt with specific cinematic language
- Add style references ("Denis Villeneuve style", etc.)

## Workflow Example

```bash
# 1. Create prompts
cat > prompts.json << 'EOF'
{
  "scenes": [
    {
      "id": "shot01",
      "prompt": "Epic low-angle hero shot of..."
    },
    {
      "id": "shot02",
      "prompt": "Intimate close-up of..."
    }
  ]
}
EOF

# 2. Generate videos
python3 veo3_generator.py --prompts prompts.json

# 3. Download videos (if URIs returned)
# 4. Assemble with audio
python3 video_compositor.py --clips veo_outputs/ --vo vo/ --music music/
```

## Next: Compare Platforms

Once you have Veo 3 videos, generate same scenes with DALL-E or Stable Diffusion to compare output quality and choose best for final edit.
