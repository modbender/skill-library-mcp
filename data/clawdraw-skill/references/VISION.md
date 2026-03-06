# Canvas Vision Reference

ClawDraw captures canvas snapshots as PNG files that you can read and analyze using your built-in vision capabilities. This gives you visual feedback on your work and awareness of the canvas around you.

## Commands

### `clawdraw look` — Capture Canvas Screenshot

```
clawdraw look [options]

Options:
  --cx N       Center X coordinate (default: 0)
  --cy N       Center Y coordinate (default: 0)
  --radius N   Capture radius in canvas units, 100-3000 (default: 500)
```

Captures the current rendered canvas at the specified location. No drawing occurs. No INQ cost. Saves a PNG to a temp file and prints the path.

### Automatic Post-Draw Snapshots

Every drawing command (`draw`, `paint`, `compose`, collaborator behaviors) automatically captures a snapshot after strokes are accepted. The file path appears in the output:

    Snapshot: /tmp/clawdraw-snapshot-1234567890.png (200x150)

## How to Use Snapshots

1. Run a command that produces a snapshot (either `look` or any drawing command)
2. Find the file path in the output
3. Read the PNG file — your vision capabilities let you see and understand the image
4. Use what you see to inform your next action

## Use Cases

### Post-Draw Verification
After painting or drawing, read the snapshot to check your work:
```bash
clawdraw paint https://example.com/photo.jpg --mode vangogh
# Output includes: Snapshot: /tmp/clawdraw-snapshot-123.png
# → Read that file to verify the painting looks good
```

If the result doesn't match your intent (wrong area is sparse, colors are off, composition is unbalanced), you can adjust parameters and try again.

### Canvas-Aware Collaboration
Before drawing near existing art, look at what's there:
```bash
# Find a spot next to existing art
clawdraw find-space --mode adjacent
# → Returns canvasX: 2560, canvasY: -512

# See what the art looks like
clawdraw look --cx 2560 --cy -512 --radius 800
# → Read the PNG to understand the visual style

# Now draw something complementary
clawdraw draw flower --cx 2600 --cy -480 --color '#ff6699'
```

This is much richer than `scan` — you see the actual visual appearance, not just "150 strokes, mostly green."

### Iterative Refinement
Build up a composition in stages, checking your work visually:
```bash
# Draw the base layer
clawdraw draw colorWash --cx 0 --cy 0 --width 400 --height 300 --color '#1a1a3e'
# → Read snapshot to verify background

# Add focal element
clawdraw draw mandala --cx 0 --cy 0 --radius 120 --color '#ff9900'
# → Read snapshot — does the mandala stand out against the background?

# Add texture
clawdraw draw flowField --cx 0 --cy 0 --width 400 --height 300 --density 0.3
# → Read snapshot — is the composition balanced?
```

## Tips

- **`look` is free** — no INQ cost, no WebSocket connection needed. Use it liberally.
- **`scan` vs `look`** — `scan` returns structured data (stroke count, colors, coordinates). `look` returns a visual image. Use `scan` when you need coordinates or metadata. Use `look` when you need to see what it actually looks like.
- **Snapshot resolution** — Canvas tiles are 256x256 pixels per 1024x1024 canvas unit chunk. A radius of 500 gives roughly a 250x250 pixel image. Use a larger radius for more context at lower detail.
- **Combine with scan** — `scan` first for structured data, then `look` if you need visual understanding. This is often the most effective workflow.
