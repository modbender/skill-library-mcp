# Asset Generation

Generate images for your videos using the oanim CLI.

## Setup

Sign in to the oanim platform:
```bash
oanim login
```

## Commands

### Generate an image
```bash
oanim assets gen-image --prompt "dark abstract gradient with purple and blue tones, 16:9" --out public/bg.png
```

### Edit an existing image
```bash
oanim assets edit-image --in public/bg.png --prompt "add subtle grid pattern" --out public/bg-grid.png
```

### Remove background
```bash
oanim assets remove-bg --in public/product.png --out public/product-cutout.png
```

### Upscale 2x
```bash
oanim assets upscale --in public/logo-small.png --out public/logo-2x.png
```

## When to use asset generation

| Scenario | Command |
|----------|---------|
| Background textures/gradients | `gen-image` |
| Product screenshots with edits | `edit-image` |
| Product photos for compositing | `remove-bg` |
| Low-res logos or icons | `upscale` |

## Video generation

```bash
oanim assets run --model fal-ai/kling-video/v1/standard/text-to-video \
  --input '{"prompt":"slow cinematic zoom, abstract flowing shapes, warm tones","duration":"5"}' \
  --out public/clip.mp4
```

Other video models: `fal-ai/minimax-video/video-01-live`, `fal-ai/hunyuan-video`, `fal-ai/kling-video/v1.5/pro/text-to-video`

## Audio generation

```bash
oanim assets run --model fal-ai/stable-audio \
  --input '{"prompt":"minimal ambient electronic, warm pads, no vocals","duration_in_seconds":30}' \
  --out public/bg-music.mp3
```

## Using generated assets in compositions

All generated assets go in `public/` and are referenced via `staticFile()`:

```tsx
import { Img, OffthreadVideo, Audio, staticFile } from 'remotion';

// Image background
<Img
  src={staticFile('bg.png')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>

// Video background (use OffthreadVideo, not Video — decodes on separate thread)
<OffthreadVideo
  src={staticFile('clip.mp4')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>

// Global audio track (place outside TransitionSeries for cross-scene audio)
<Audio src={staticFile('bg-music.mp3')} volume={0.25} />
```

Always add a dark overlay between media backgrounds and text:
```tsx
<AbsoluteFill style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }} />
```

## Tips

- Generate backgrounds at the video resolution (1920x1080 by default)
- Use `staticFile()` in Remotion to reference files in `public/`
- Remove backgrounds for product shots so they composite cleanly over gradient backgrounds
- For text-heavy videos, generate abstract/blurred backgrounds that don't compete with text
- Use `objectFit: 'cover'` for full-bleed backgrounds
- Keep audio at `volume={0.2}` to `volume={0.3}` for background music
