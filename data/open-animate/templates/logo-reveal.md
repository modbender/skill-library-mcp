# Example: Logo Reveal

A 5-second logo animation — good for intros/outros.

## Structure

| Phase | Frames | Animation |
|-------|--------|-----------|
| Build-up | 0-60 | Glow orbs fade in, grid appears |
| Reveal | 60-90 | Logo scales in with `popIn` + `spring: 'bouncy'` |
| Settle | 90-120 | Tagline fades up below logo |
| Hold | 120-150 | Static hold |

## Pattern

```tsx
export const LogoReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill>
      <Background gradient="radial-gradient(circle, #141414, #0a0a0a)" />
      <GlowOrb color="rgba(99, 102, 241, 0.3)" x={50} y={50} size={600} />

      <SafeArea style={{ justifyContent: 'center', alignItems: 'center', gap: 24 }}>
        {/* Logo */}
        <div style={{
          ...popIn({ frame, fps, delay: 0.5, spring: 'bouncy' }),
          fontSize: 96,
          fontWeight: 800,
          color: '#fff',
        }}>
          YourLogo
        </div>

        {/* Tagline */}
        <div style={{
          ...fadeUp({ frame, fps, delay: 1.2 }),
          fontSize: 24,
          color: '#94a3b8',
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
        }}>
          Your tagline here
        </div>
      </SafeArea>
    </AbsoluteFill>
  );
};
```

## Tips

- Use `Img` from `remotion` for actual logo files: `<Img src={staticFile('logo.png')} />`
- Remove background from logo first: `oanim assets remove-bg --in logo.png --out logo-clean.png`
- The `bouncy` spring gives logos a satisfying pop
