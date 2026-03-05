# Video Stabilization

Fix shaky footage with AI and traditional methods.

## Tools

### FFmpeg (vidstab)

```bash
# Step 1: Analyze
ffmpeg -i shaky.mp4 -vf "vidstabdetect=shakiness=10:accuracy=15" -f null -

# Step 2: Stabilize
ffmpeg -i shaky.mp4 -vf "vidstabtransform=smoothing=30:crop=black" stabilized.mp4
```

**Parameters:**
- `shakiness` — 1-10, how shaky (higher = more analysis)
- `accuracy` — 1-15, analysis precision
- `smoothing` — frames to smooth over (30 = 1 sec at 30fps)
- `crop` — black (add borders) or keep (zoom to fill)

### DaVinci Resolve

1. Select clip in timeline
2. Inspector > Stabilization
3. Choose mode:
   - Perspective — most aggressive
   - Similarity — scale + rotation + position
   - Translation — position only
4. Click "Stabilize"

### Premiere Pro (Warp Stabilizer)

1. Apply "Warp Stabilizer" effect
2. Wait for analysis
3. Adjust Smoothness (50% default)
4. Choose Result: Smooth Motion or No Motion

### After Effects

1. Apply Warp Stabilizer to layer
2. Analyze footage
3. Stabilization Method:
   - Subspace Warp — handles complex motion
   - Position, Scale, Rotation — simpler
4. Borders: Stabilize, Crop, Auto-scale

### GyroFlow (Free, Best Quality)

Open-source, gyroscope-based stabilization:

```bash
# Download from https://gyroflow.xyz/
# Import video + gyro data
# Adjust parameters
# Export stabilized video
```

**Features:**
- Uses camera gyro metadata
- Best results for action cameras
- Rolling shutter correction

## Methods Comparison

| Method | Quality | Speed | Best For |
|--------|---------|-------|----------|
| FFmpeg vidstab | Good | Fast | Batch processing |
| DaVinci | Excellent | Medium | Professional |
| Warp Stabilizer | Very Good | Slow | Complex motion |
| GyroFlow | Best | Fast | Action cameras |

## Crop vs Borders

**Zoomed Crop (default):**
- Fills frame
- Loses edge resolution
- Cleaner look

**Add Borders:**
- Preserves all pixels
- Shows black edges
- Good for reframing later

## Best Practices

- **Shoot stable** — stabilization has limits
- **Higher resolution helps** — more room to crop
- **60fps** — more data for analysis
- **Test multiple settings** — varies per clip
- **Check corners** — warping artifacts appear there

## Rolling Shutter

For CMOS sensor wobble (jello effect):

**DaVinci:**
```
Clip > Stabilization > Rolling Shutter Compensation
```

**FFmpeg:**
```bash
ffmpeg -i input.mp4 -vf "deshake=rx=32:ry=32" output.mp4
```

## Troubleshooting

- **Wobble introduced** — reduce smoothing
- **Crop too aggressive** — lower stabilization strength
- **Warping artifacts** — use simpler mode (translation only)
- **Analysis fails** — clip may be too short
