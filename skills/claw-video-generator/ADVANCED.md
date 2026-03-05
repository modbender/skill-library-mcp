# JSON2Video Pinterest Skill - Advanced Usage

## Multi-Scene Video Architecture

When creating videos with voiceover, the recommended pattern is:

```
Scene 1: Hook (3-5 seconds)
  └─ Image + Short attention-grabbing voiceover

Scene 2: Value/Benefit (5-8 seconds)
  └─ Image + Explain the benefit

Scene 3: How-to/Steps (10-15 seconds)
  └─ Image + Walk through the process

Scene 4: Social Proof (5-8 seconds)
  └─ Image + Results/testimonial

Scene 5: CTA (3-5 seconds)
  └─ Image + Call-to-action
```

Total: ~30-45 seconds (optimal for Pinterest)

## Image Source Strategies

### Strategy 1: Full AI Generation (Simplest)
- Pros: Fully automated, unique images
- Cons: Consumes more credits, slower
- Best for: Testing ideas, rapid prototyping

### Strategy 2: Hybrid (Production Recommended)
- Create images with Nano Banana Pro / DALL-E
- Upload to Cloudinary
- Use URLs in JSON2Video config
- Pros: Faster renders, cheaper, reusable assets
- Cons: Requires external image generation step

### Strategy 3: Stock + AI Enhancement
- Start with stock images
- Use AI for specific elements or backgrounds
- Pros: Professional quality
- Cons: Requires design skills

## Voiceover Patterns

### Pattern A: Generated TTS (Fully Automated)
```json
{
  "voice": {
    "source": "generated",
    "text": "Your script here",
    "voice_id": "en-US-Neural2-F"
  }
}
```

### Pattern B: Pre-Recorded Segments (Highest Quality)
```json
{
  "voice": {
    "source": "https://your-cdn.com/scene-1.mp3"
  }
}
```

### Pattern C: Mixed (Best of Both)
- Use TTS for simple scenes
- Use pre-recorded for important CTAs

## Subtitle Styling

Customize subtitle appearance:

```json
{
  "subtitles": true,
  "subtitle_style": {
    "font-family": "Montserrat",
    "font-size": "32px",
    "color": "#ffffff",
    "background-color": "rgba(0,0,0,0.7)",
    "text-align": "center",
    "font-weight": "bold"
  }
}
```

## Zoom Effect Variations

### Subtle (Recommended)
- Scale 1.05x to 1.0x over duration
- Adds motion without distraction

### Dramatic
- Scale 1.2x to 1.0x
- Good for emotional moments

### Ken Burns (Pan + Zoom)
Not directly supported, but can be simulated with multiple elements.

## Content Ideas for Pinterest Affiliate Videos

### "Listicle" Format (High Engagement)
- "5 Affiliate Networks for Beginners"
- "3 Mistakes Killing Your Commissions"
- "7 Passive Income Ideas"

### "How-To" Format (High Saves)
- "How to Set Up Your First Affiliate Link"
- "How I Made $X in My First Month"
- "How to Choose Profitable Products"

### "Myth Busting" Format (High Comments)
- "Affiliate Marketing Myths Debunked"
- "Why Most Affiliates Fail"
- "The Truth About Passive Income"

### "Before/After" Format (High Conversions)
- "My Income: Month 1 vs Month 6"
- "From $0 to $X: The Journey"

## Pinterest-Specific Tips

1. **First 3 seconds matter most** - Hook immediately
2. **Text overlays boost engagement** - Add key phrases as text
3. **Vertical format is non-negotiable** - 9:16 aspect ratio
4. **Loop consideration** - Pinterest autoplays; design for seamless loops
5. **Muted autoplay** - Ensure visuals work without sound
6. **CTA timing** - Put CTA at 80-90% of video length

## Credit Consumption Optimization

### Reduce Costs:
- Use `cache: true` (default)
- Pre-generate AI images
- Use `flux-schnell` instead of `flux-pro`
- Reuse successful templates
- Lower quality for drafts (`quality: "medium"`)

### Expected Costs:
- Simple video (3 scenes, TTS, subtitles): ~50-100 credits
- Complex video (5 scenes, AI images, TTS): ~150-250 credits

## Integration with Existing Workflow

```
1. Nano Banana Pro → Generate pin images
2. Cloudinary → Store images
3. This Skill → Create video from images + voice
4. Pinterest API → Post video pin
```

## Batch Processing

To create multiple videos:

```python
import json
from scripts.generate_video import create_pinterest_video

# Load batch config
with open('batch-videos.json') as f:
    batch = json.load(f)

for video_name, config in batch.items():
    print(f"Creating: {video_name}")
    url = create_pinterest_video(config['scenes'], wait=True)
    print(f"Done: {url}\n")
```

## Error Recovery

If a render fails:

1. Check project status: `--project-id ID`
2. If status is "error", review the message
3. Common fixes:
   - Invalid image URL → Use public HTTPS URL
   - Content policy violation → Adjust AI prompt
   - Timeout → Reduce scene count or complexity

## Future Enhancements

Potential additions to the skill:
- Direct ElevenLabs integration for premium voices
- Auto-scene-splitting based on script analysis
- A/B testing variant generation
- Analytics integration for performance tracking
