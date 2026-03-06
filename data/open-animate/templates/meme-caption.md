# Example: Meme / Social Clip

A 5-8 second captioned clip for social media (vertical 1080x1920).

## animate.json

```json
{
  "name": "Meme Clip",
  "compositionId": "MemeClip",
  "render": {
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "codec": "h264",
    "crf": 18
  }
}
```

## Pattern

```tsx
export const MemeClip: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Top caption */}
      <div style={{
        position: 'absolute',
        top: '8%',
        width: '100%',
        textAlign: 'center',
        padding: '0 10%',
      }}>
        <div style={{
          ...fadeDown({ frame, fps, delay: 0.1 }),
          fontSize: 48,
          fontWeight: 800,
          color: '#fff',
          textShadow: '0 2px 20px rgba(0,0,0,0.8)',
        }}>
          When the deploy works first try
        </div>
      </div>

      {/* Center content area */}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={popIn({ frame, fps, delay: 0.4 })}>
          {/* Image or emoji */}
          <span style={{ fontSize: 200 }}>🚀</span>
        </div>
      </AbsoluteFill>

      {/* Bottom caption */}
      <div style={{
        position: 'absolute',
        bottom: '12%',
        width: '100%',
        textAlign: 'center',
      }}>
        <div style={{
          ...fadeUp({ frame, fps, delay: 0.8 }),
          fontSize: 32,
          color: '#94a3b8',
        }}>
          @yourhandle
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

## Tips

- Vertical format (1080x1920) for Reels/TikTok/Shorts
- Keep text large — minimum 48px for readability on mobile
- Short duration (5-8s) for maximum engagement
- Use `textShadow` for text over images
