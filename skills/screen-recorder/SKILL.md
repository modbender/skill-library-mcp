---
description: Record screen with ffmpeg — full screen, region capture, audio, and GIF conversion.
---

# Screen Recorder

Record the screen using ffmpeg with start/stop controls.

## Requirements

- `ffmpeg` (pre-installed on most Linux distros)
- X11 or Wayland display server
- Optional: `wf-recorder` for Wayland, PulseAudio/PipeWire for audio

## Instructions

### Detect display server
```bash
echo $XDG_SESSION_TYPE  # "x11" or "wayland"
```

### Full screen recording
```bash
# X11
ffmpeg -f x11grab -framerate 30 -i :0.0 -c:v libx264 -preset ultrafast -crf 23 output.mp4

# X11 with audio (PulseAudio)
ffmpeg -f x11grab -framerate 30 -i :0.0 -f pulse -i default -c:v libx264 -preset ultrafast -crf 23 -c:a aac output.mp4

# Wayland
wf-recorder -f output.mp4
wf-recorder -a -f output.mp4  # with audio
```

### Region recording (X11)
```bash
# Get screen resolution first
xdpyinfo 2>/dev/null | grep dimensions || xrandr | grep '*'

# Record 1280x720 region at offset 100,200
ffmpeg -f x11grab -framerate 30 -video_size 1280x720 -i :0.0+100,200 -c:v libx264 -preset ultrafast output.mp4
```

### Stop recording
```bash
pkill -INT ffmpeg      # Graceful stop (finalizes file)
pkill -INT wf-recorder
# ⚠️ Do NOT use pkill -9 — this corrupts the output file
```

### Post-processing
```bash
# Compress
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac compressed.mp4

# Convert to GIF (for sharing)
ffmpeg -i input.mp4 -vf "fps=10,scale=640:-1:flags=lanczos" -gifflags +transdiff output.gif

# Trim (start at 10s, duration 30s)
ffmpeg -i input.mp4 -ss 10 -t 30 -c copy trimmed.mp4
```

## Edge Cases

- **No display**: Headless servers have no screen to record. Use virtual framebuffer (`Xvfb`) if needed.
- **Multiple monitors**: Specify geometry with `-video_size` and offset. Use `xrandr` to find monitor layout.
- **Permission denied (Wayland)**: Some compositors restrict screen capture. Check compositor settings.
- **Large files**: Use `-preset ultrafast` during recording for low CPU, then compress afterward.
- **Recording already running**: Check with `pgrep ffmpeg` before starting a new one.

## Security

- Screen recordings may capture sensitive information (passwords, tokens, private messages).
- Warn user before starting. Save to a private directory with restricted permissions.
- Delete recordings when no longer needed.
