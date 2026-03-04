# Kling Video Generation Skill

Generate AI videos using Kling 2.6 (via Kie.ai).

## Commands

```bash
# Generate video and wait for result
/root/clawd/skills/kling/kling.js generate "A gym owner high-fiving a member"

# Quick start (returns task ID immediately)
/root/clawd/skills/kling/kling.js quick "Professional fitness environment"

# Check status
/root/clawd/skills/kling/kling.js status <task_id>
```

## Parameters

- **Model**: kling-2.6/text-to-video (default)
- **Aspect Ratio**: 16:9 (default)
- **Duration**: 5 seconds (default)
- **Negative Prompt**: Filters out blurry/low quality

## Use Cases

- UGC-style marketing videos
- Gym/fitness promotional content
- LinkedIn video posts
- Client testimonial visualizations
- Product demos

## Notes

- Videos take 1-5 minutes to generate
- Results include video URL in the response
- API key stored in `.env` as `KIE_API_KEY`
