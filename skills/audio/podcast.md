# Podcast Production Workflow

## Pre-Recording Checklist

- [ ] Room quiet (no AC, fans, outside noise)
- [ ] Mic positioned correctly (fist distance from mouth)
- [ ] Gain set properly (peaks around -12 dB)
- [ ] Recording software configured (44.1kHz or 48kHz, 16 or 24-bit)
- [ ] Headphones on to monitor

---

## Post-Production Pipeline

### 1. Backup Raw Recording
```bash
cp raw_episode.wav raw_episode_backup.wav
```

### 2. Noise Reduction (if needed)
```bash
# Basic cleanup
ffmpeg -i raw.wav -af "highpass=f=80,lowpass=f=12000" cleaned.wav

# For persistent background noise
ffmpeg -i raw.wav -af "afftdn=nf=-20" cleaned.wav
```

### 3. Remove Silence/Dead Air
```bash
# Compress long silences (>1s) to 0.5s
ffmpeg -i cleaned.wav -af "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-40dB" trimmed.wav
```

### 4. Normalize Loudness
```bash
# Target -16 LUFS for podcast standard
ffmpeg -i trimmed.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11" normalized.wav

# Or use ffmpeg-normalize for two-pass (more accurate)
ffmpeg-normalize trimmed.wav -o normalized.wav -t -16 -tp -1.5
```

### 5. Add Compression (Optional)
```bash
# Make quiet parts audible, prevent loud parts from blasting
ffmpeg -i normalized.wav -af "acompressor=threshold=-20dB:ratio=3:attack=5:release=100" compressed.wav
```

### 6. Add Intro/Outro
```bash
# Create list file
echo "file 'intro.wav'" > episode.txt
echo "file 'compressed.wav'" >> episode.txt
echo "file 'outro.wav'" >> episode.txt

# Concatenate
ffmpeg -f concat -safe 0 -i episode.txt -c copy episode_final.wav
```

### 7. Export for Distribution
```bash
# MP3 for hosting (most compatible)
ffmpeg -i episode_final.wav -acodec libmp3lame -b:a 128k -ar 44100 episode.mp3

# MP3 higher quality (if bandwidth not a concern)
ffmpeg -i episode_final.wav -acodec libmp3lame -b:a 192k -ar 44100 episode_hq.mp3

# Add metadata
ffmpeg -i episode.mp3 -metadata title="Episode 42: Topic" -metadata artist="Podcast Name" -metadata album="Season 2" -c copy episode_tagged.mp3
```

---

## Generate Transcript
```bash
# Extract audio for Whisper (16kHz mono)
ffmpeg -i episode.mp3 -ar 16000 -ac 1 episode_whisper.wav

# Transcribe
whisper episode_whisper.wav --model medium --output_format all

# Outputs: .txt, .srt, .vtt, .json
```

---

## Create Audiogram (Waveform Video)
```bash
# Generate waveform video for social media
ffmpeg -i highlight.mp3 -filter_complex \
  "[0:a]showwaves=s=1080x1920:mode=cline:colors=white[wave]; \
   color=c=black:s=1080x1920[bg]; \
   [bg][wave]overlay" \
  -c:v libx264 -c:a aac audiogram.mp4
```

---

## Extract Highlight Clips
```bash
# Cut 60-second clip starting at 15:30
ffmpeg -i episode.mp3 -ss 15:30 -t 60 -af "afade=t=in:d=1,afade=t=out:st=59:d=1" highlight.mp3
```

---

## Quality Checklist Before Publishing

- [ ] Loudness at -16 LUFS (check with `loudnorm=print_format=summary`)
- [ ] True peak below -1 dB
- [ ] No clipping or distortion
- [ ] Intro/outro attached
- [ ] Metadata (title, artist, album) added
- [ ] File plays correctly in different players
- [ ] File size reasonable for hosting limits

---

## Platform Export Specs

| Platform | Format | Bitrate | Sample Rate | Notes |
|----------|--------|---------|-------------|-------|
| Spotify | MP3 | 128-192 kbps | 44.1kHz | |
| Apple Podcasts | MP3/M4A | 128-192 kbps | 44.1kHz | |
| Google Podcasts | MP3 | 128+ kbps | 44.1kHz | |
| YouTube | AAC | 192+ kbps | 44.1/48kHz | Needs video for upload |

---

## Batch Episode Processing

```bash
#!/bin/bash
# Process all raw episodes in current directory

for raw in raw_*.wav; do
  name="${raw#raw_}"
  name="${name%.wav}"
  
  echo "Processing: $name"
  
  # Clean, normalize, export
  ffmpeg -i "$raw" \
    -af "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11" \
    -acodec libmp3lame -b:a 128k \
    "processed_${name}.mp3"
done
```
