# Example: Investor Update / Metrics Video

A 20-second video showcasing key metrics with animated counters.

## Structure

| Scene | Duration | Content |
|-------|----------|---------|
| Title | 3s | Company name + period |
| Metrics | 6s | 3 animated KPI cards |
| Growth | 5s | Key achievement highlight |
| Closing | 4s | Thank you + next steps |

## Pattern: Metrics scene

```tsx
const metrics = [
  { label: 'Revenue', value: 125000, prefix: '$', suffix: '' },
  { label: 'Users', value: 5200, prefix: '', suffix: '+' },
  { label: 'Growth', value: 340, prefix: '', suffix: '%' },
];

const MetricsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill>
      <Background gradient="linear-gradient(135deg, #0c1222, #162032)" />
      <SafeArea style={{ justifyContent: 'center', alignItems: 'center', gap: 48 }}>
        <div style={{
          ...fadeUp({ frame, fps, delay: 0.1 }),
          fontSize: 36,
          color: '#94a3b8',
          textTransform: 'uppercase',
          letterSpacing: '0.15em',
        }}>
          Q4 2025 Highlights
        </div>

        <div style={{ display: 'flex', gap: 32 }}>
          {metrics.map((m, i) => (
            <Card key={i} delay={0.3 + i * 0.2} style={{ width: 300, textAlign: 'center' }}>
              <div style={{ fontSize: 18, color: '#64748b', marginBottom: 12 }}>
                {m.label}
              </div>
              <CountUp
                to={m.value}
                delay={0.5 + i * 0.2}
                duration={1.5}
                prefix={m.prefix}
                suffix={m.suffix}
                style={{ fontSize: 56, fontWeight: 700, color: '#e0f2fe' }}
              />
            </Card>
          ))}
        </div>
      </SafeArea>
    </AbsoluteFill>
  );
};
```

## Color palette

Use `palettes.ocean` for a professional, corporate feel with blue tones.

## Tips

- `CountUp` component makes numbers feel dynamic
- Stagger cards with increasing delays for a cascade effect
- Keep the design clean — data should be the hero
- Use `palettes.ocean` or `palettes.midnight` for professional tone
