# Example: Step-Based Explainer

A 30-second explainer video walking through a process in numbered steps.

## Structure

| Scene | Duration | Content |
|-------|----------|---------|
| Intro | 4s | Problem statement |
| Step 1 | 5s | First step with visual |
| Step 2 | 5s | Second step with visual |
| Step 3 | 5s | Third step with visual |
| Result | 5s | Outcome / benefit |
| CTA | 3s | Next steps |

## Pattern: Numbered steps

```tsx
const StepScene: React.FC<{ number: number; title: string; description: string }> = ({
  number, title, description
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill>
      <Background gradient="linear-gradient(135deg, #0a0a0a, #1a1a2e)" />
      <SafeArea style={{ justifyContent: 'center', gap: 32 }}>
        <div style={{
          ...popIn({ frame, fps, delay: 0.1 }),
          fontSize: 120,
          fontWeight: 800,
          color: 'rgba(99, 102, 241, 0.15)',
        }}>
          {number}
        </div>
        <div style={{
          ...fadeUp({ frame, fps, delay: 0.3 }),
          fontSize: 48,
          fontWeight: 700,
          color: '#f1f5f9',
        }}>
          {title}
        </div>
        <div style={{
          ...fadeUp({ frame, fps, delay: 0.5 }),
          fontSize: 24,
          color: '#94a3b8',
          maxWidth: 600,
        }}>
          {description}
        </div>
      </SafeArea>
    </AbsoluteFill>
  );
};
```

## Transition choice

Use `wipe()` or `pushLeft()` for step-based content — the directional motion implies forward progression.
