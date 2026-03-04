# Video Effects

AI-powered video effects and transformations.

## Frame Interpolation (Slow Motion)

### RIFE (Real-Time Intermediate Flow Estimation)

```bash
# Install
pip install rife-ncnn-vulkan

# Interpolate (2x frames)
rife-ncnn-vulkan -i input.mp4 -o output.mp4 -m rife-v4.6

# 4x interpolation
rife-ncnn-vulkan -i input.mp4 -o output.mp4 -m rife-v4.6 -x
```

### Topaz Video AI

```bash
tvai_cli -i input.mp4 -o output.mp4 --model chronos --slowmo 4
```

**Models:**
- Chronos — best quality slow motion
- Apollo — fast motion

### FFmpeg (minterpolate)

```bash
# Basic frame interpolation
ffmpeg -i input.mp4 -vf "minterpolate=fps=60:mi_mode=mci" output.mp4

# Better quality (slower)
ffmpeg -i input.mp4 -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1" output.mp4
```

## Style Transfer

### Runway

Video-to-video style transfer:
- Upload reference style image
- Apply to video
- Adjust strength

### EbSynth

Free style transfer for video:
1. Create keyframe artwork
2. Propagate style to all frames
3. Manual but high quality

### FFmpeg Neural Filters

```bash
# Cartoon effect
ffmpeg -i input.mp4 -vf "edgedetect=low=0.1:high=0.4,negate" output.mp4
```

## Face Effects

### Face Swap (Rope/SimSwap)

```bash
# Using roop (controversial)
python run.py --source face.jpg --target video.mp4 --output swapped.mp4
```

**Note:** Use responsibly, ethical concerns.

### Face Blur

```bash
# FFmpeg with detection
ffmpeg -i input.mp4 -vf "drawbox=x=100:y=100:w=200:h=200:c=black@0.5:t=fill" output.mp4

# For auto-detection, use DaVinci Resolve Face Refinement
```

### De-aging/Aging

Runway and specialized tools can modify apparent age.

## Object Tracking

### Runway Object Tracking

1. Upload video
2. Click object to track
3. Apply effect to tracked region
4. Export

### DaVinci Fusion

1. Add Tracker node
2. Track point/area
3. Connect to transform/effect
4. Animate based on track data

## Speed Ramping

### DaVinci Resolve

1. Right-click clip
2. Retime Controls
3. Add speed points
4. Adjust speed between points
5. Use "Retime Process" > Optical Flow

### FFmpeg

```bash
# 2x speed
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" output.mp4

# 0.5x speed (slow)
ffmpeg -i input.mp4 -vf "setpts=2*PTS" -af "atempo=0.5" output.mp4
```

## Text & Captions

### Auto-Captions (Descript, Premiere)

1. Import video
2. Auto-transcribe
3. Style captions
4. Burn in or export SRT

### FFmpeg Subtitles

```bash
# Burn in subtitles
ffmpeg -i input.mp4 -vf "subtitles=captions.srt" output.mp4

# Style subtitles
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF&'" output.mp4
```

## Popular Effect Combos

| Effect | Tools | Result |
|--------|-------|--------|
| Cinematic | Color grade + letterbox + grain | Film look |
| Vlog | Stabilize + color + music | Clean content |
| Music video | Speed ramps + effects + transitions | Dynamic |
| Tutorial | Zoom + highlight + captions | Educational |
