# FFmpeg Commands by Task

## Inspect Video
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

---

## Convert Format
```bash
# To MP4 (universal)
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4

# Keep original quality (copy streams)
ffmpeg -i input.mkv -c copy output.mp4
```

---

## Compress
```bash
# Good quality, smaller file
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -c:a aac -b:a 128k output.mp4

# Aggressive compression (WhatsApp)
ffmpeg -i input.mp4 -vf "scale=720:-2" -c:v libx264 -crf 28 -c:a aac -b:a 96k output.mp4

# Target specific file size (50MB)
ffmpeg -i input.mp4 -c:v libx264 -b:v 800k -c:a aac -b:a 96k output.mp4
```

---

## Change Aspect Ratio
```bash
# 16:9 → 9:16 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih" output.mp4

# 16:9 → 9:16 (letterbox with blur)
ffmpeg -i input.mp4 -vf "split[original][copy];[copy]scale=1080:1920,boxblur=20[bg];[bg][original]overlay=(W-w)/2:(H-h)/2" output.mp4

# 16:9 → 1:1 (square with padding)
ffmpeg -i input.mp4 -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:black" output.mp4
```

---

## Trim/Cut
```bash
# Cut from 00:30 to 01:30
ffmpeg -i input.mp4 -ss 00:00:30 -to 00:01:30 -c copy output.mp4

# First 60 seconds
ffmpeg -i input.mp4 -t 60 -c copy output.mp4

# Remove first 10 seconds
ffmpeg -i input.mp4 -ss 10 -c copy output.mp4
```

---

## Merge Clips
```bash
# Create list file
echo "file 'clip1.mp4'" > list.txt
echo "file 'clip2.mp4'" >> list.txt
echo "file 'clip3.mp4'" >> list.txt

# Merge
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4
```

---

## Extract Audio
```bash
# To MP3
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3

# To AAC (keep quality)
ffmpeg -i input.mp4 -vn -acodec copy output.aac
```

---

## Add/Remove Audio
```bash
# Remove audio
ffmpeg -i input.mp4 -an -c:v copy output.mp4

# Replace audio
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v -map 1:a output.mp4
```

---

## Add Subtitles
```bash
# Burn into video
ffmpeg -i input.mp4 -vf "subtitles=captions.srt" output.mp4

# Styled subtitles
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF&'" output.mp4
```

---

## Create GIF
```bash
# Generate palette (better colors)
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen" palette.png

# Create GIF with palette
ffmpeg -i input.mp4 -i palette.png -filter_complex "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
```

---

## Extract Frames/Thumbnails
```bash
# One frame at specific time
ffmpeg -i input.mp4 -ss 00:00:05 -vframes 1 thumbnail.jpg

# One frame per second
ffmpeg -i input.mp4 -vf "fps=1" frame_%04d.jpg

# Best quality frame extraction
ffmpeg -i input.mp4 -ss 00:00:05 -vframes 1 -q:v 2 thumbnail.jpg
```

---

## Stabilize
```bash
# Analyze
ffmpeg -i input.mp4 -vf vidstabdetect -f null -

# Apply stabilization
ffmpeg -i input.mp4 -vf vidstabtransform output.mp4
```

---

## Speed Change
```bash
# 2x speed
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" output.mp4

# 0.5x speed (slow motion)
ffmpeg -i input.mp4 -vf "setpts=2*PTS" -af "atempo=0.5" output.mp4
```

---

## Rotate
```bash
# 90° clockwise
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4

# 90° counter-clockwise
ffmpeg -i input.mp4 -vf "transpose=2" output.mp4

# 180°
ffmpeg -i input.mp4 -vf "transpose=1,transpose=1" output.mp4
```

---

## Add Watermark
```bash
# Bottom right corner
ffmpeg -i input.mp4 -i logo.png -filter_complex "overlay=W-w-10:H-h-10" output.mp4

# With opacity
ffmpeg -i input.mp4 -i logo.png -filter_complex "[1:v]format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=W-w-10:H-h-10" output.mp4
```

---

## Resolution/Scale
```bash
# To 1080p (maintain aspect)
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease" output.mp4

# To 720p
ffmpeg -i input.mp4 -vf "scale=-2:720" output.mp4
```

---

## Audio Enhancement
```bash
# Normalize volume
ffmpeg -i input.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp4

# Remove background noise (basic)
ffmpeg -i input.mp4 -af "highpass=f=200,lowpass=f=3000" output.mp4
```

---

## Frame Rate Conversion
```bash
# Change to 30fps
ffmpeg -i input.mp4 -r 30 -c:a copy output.mp4

# Change to 24fps (cinematic)
ffmpeg -i input.mp4 -r 24 -c:a copy output.mp4

# 60fps to 30fps (smoother)
ffmpeg -i input.mp4 -vf "fps=30" -c:a copy output.mp4
```

---

## Brightness/Contrast
```bash
# Increase brightness
ffmpeg -i input.mp4 -vf "eq=brightness=0.1" output.mp4

# Increase contrast
ffmpeg -i input.mp4 -vf "eq=contrast=1.2" output.mp4

# Both (dark video fix)
ffmpeg -i input.mp4 -vf "eq=brightness=0.1:contrast=1.2:saturation=1.1" output.mp4
```

---

## Add Text Overlay
```bash
# Simple text
ffmpeg -i input.mp4 -vf "drawtext=text='My Title':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=50" output.mp4

# With background box
ffmpeg -i input.mp4 -vf "drawtext=text='Subscribe':fontsize=36:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=50:y=h-100" output.mp4

# Multi-line (use \n)
ffmpeg -i input.mp4 -vf "drawtext=text='Line 1\nLine 2':fontsize=32:fontcolor=white:x=50:y=50" output.mp4
```

---

## Blur/Censor Regions
```bash
# Blur specific area (x, y, width, height)
ffmpeg -i input.mp4 -vf "delogo=x=100:y=100:w=200:h=100:show=0" output.mp4

# Pixelate region
ffmpeg -i input.mp4 -vf "crop=200:100:100:100,scale=20:10,scale=200:100[blur];[0:v][blur]overlay=100:100" output.mp4

# Full face blur (requires face detection - use with external tool)
# For manual: identify face coordinates per scene, apply delogo or boxblur
```

---

## Create Audiogram (Waveform Visualization)
```bash
# Audio waveform video
ffmpeg -i audio.mp3 -filter_complex "[0:a]showwaves=s=1280x720:mode=line:rate=25:colors=white[v]" -map "[v]" -map 0:a -c:v libx264 -c:a copy audiogram.mp4

# Circular waveform
ffmpeg -i audio.mp3 -filter_complex "[0:a]avectorscope=s=1280x720:draw=dot:scale=cbrt[v]" -map "[v]" -map 0:a audiogram.mp4
```
