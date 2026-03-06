# Working with Media

## The pattern: Generate → Place → Use

Every media type follows the same workflow:
1. **Generate** with `oanim assets`
2. **Place** in `public/`
3. **Use** via `staticFile()` in Remotion

## Images

```bash
oanim assets gen-image --prompt "abstract warm gradient, dark bg, 16:9" --out public/bg.png
```

```tsx
import { Img, staticFile } from 'remotion';

<Img
  src={staticFile('bg.png')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>
```

## Video

```bash
oanim assets run \
  --model fal-ai/kling-video/v1/standard/text-to-video \
  --input '{"prompt":"cinematic zoom, flowing shapes, warm tones","duration":"5"}' \
  --out public/clip.mp4
```

```tsx
import { OffthreadVideo, staticFile } from 'remotion';

<OffthreadVideo
  src={staticFile('clip.mp4')}
  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
/>
```

Available video models:
| Model | Notes |
|-------|-------|
| `fal-ai/kling-video/v1/standard/text-to-video` | Good quality, 5s clips |
| `fal-ai/kling-video/v1.5/pro/text-to-video` | Higher quality |
| `fal-ai/minimax-video/video-01-live` | Fast generation |
| `fal-ai/hunyuan-video` | High quality |

## Audio

```bash
oanim assets run \
  --model fal-ai/stable-audio \
  --input '{"prompt":"minimal ambient electronic, warm pads, no vocals","duration_in_seconds":30}' \
  --out public/bg-music.mp3
```

```tsx
import { Audio, staticFile } from 'remotion';

// Place at composition level (outside TransitionSeries) for global audio
<Audio src={staticFile('bg-music.mp3')} volume={0.25} />
```

## Layer order (back to front)

1. `<OffthreadVideo>` or `<Img>` — media background
2. `<AbsoluteFill style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>` — dark overlay
3. `<GlowOrb>` — ambient glow
4. `<Vignette>` — edge darkening
5. `<SafeArea>` — content (text, cards, etc.)
6. `<Audio>` — non-visual, position doesn't matter

## Tips

- Use `objectFit: 'cover'` for full-bleed backgrounds
- Always add a dark overlay between media and text
- Keep audio at `volume={0.2}` to `volume={0.3}` for background music
- Use `<OffthreadVideo>` (not `<Video>`) — decodes on separate thread
- Trim clips with `startFrom={30}` to skip frames
- Generate backgrounds at 1920x1080 to match video resolution
