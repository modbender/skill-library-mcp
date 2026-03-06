# FFmpeg Audio Commands

## Inspect Audio
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp3
```

---

## Format Conversion
```bash
# To MP3 (VBR, good quality)
ffmpeg -i input.wav -acodec libmp3lame -q:a 2 output.mp3

# To MP3 (CBR, specific bitrate)
ffmpeg -i input.wav -acodec libmp3lame -b:a 192k output.mp3

# To AAC/M4A
ffmpeg -i input.wav -acodec aac -b:a 192k output.m4a

# To FLAC (lossless)
ffmpeg -i input.wav -acodec flac output.flac

# To WAV (from any format)
ffmpeg -i input.mp3 -acodec pcm_s16le output.wav

# To Opus (small, efficient)
ffmpeg -i input.wav -acodec libopus -b:a 128k output.opus
```

---

## Extract Audio from Video
```bash
# Keep original codec (fastest)
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# Convert to MP3
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# Convert to WAV for editing
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 44100 audio.wav
```

---

## Trim/Cut
```bash
# Cut from 00:30 to 02:00
ffmpeg -i input.mp3 -ss 00:00:30 -to 00:02:00 -c copy output.mp3

# First 60 seconds
ffmpeg -i input.mp3 -t 60 -c copy output.mp3

# Remove first 10 seconds
ffmpeg -i input.mp3 -ss 10 -c copy output.mp3
```

---

## Merge Multiple Files
```bash
# Create list file
echo "file 'clip1.mp3'" > list.txt
echo "file 'clip2.mp3'" >> list.txt
echo "file 'clip3.mp3'" >> list.txt

# Concatenate
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp3
```

---

## Volume & Loudness

```bash
# Simple volume adjustment
ffmpeg -i input.mp3 -af "volume=1.5" output.mp3  # 1.5x louder
ffmpeg -i input.mp3 -af "volume=-3dB" output.mp3  # 3dB quieter

# Normalize to target loudness (podcast standard)
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3

# Peak normalize (maximize without clipping)
ffmpeg -i input.mp3 -af "volume=0dB:precision=double:replaygain=track" output.mp3

# Using ffmpeg-normalize (more accurate, two-pass)
ffmpeg-normalize input.mp3 -o output.mp3 -t -16
```

---

## Noise Reduction

```bash
# Basic highpass (remove rumble <200Hz)
ffmpeg -i input.mp3 -af "highpass=f=80" output.mp3

# Basic lowpass (remove hiss >8kHz)
ffmpeg -i input.mp3 -af "lowpass=f=8000" output.mp3

# Combined for voice cleanup
ffmpeg -i input.mp3 -af "highpass=f=80,lowpass=f=8000" output.mp3

# Noise gate (reduce quiet noise between speech)
ffmpeg -i input.mp3 -af "afftdn=nf=-25" output.mp3
```

---

## Speed/Tempo

```bash
# Speed up 1.5x (changes pitch too)
ffmpeg -i input.mp3 -af "asetrate=44100*1.5,aresample=44100" output.mp3

# Speed up WITHOUT changing pitch
ffmpeg -i input.mp3 -af "atempo=1.5" output.mp3

# Slow down to 0.75x
ffmpeg -i input.mp3 -af "atempo=0.75" output.mp3

# Extreme speed (chain atempo, each max 2.0)
ffmpeg -i input.mp3 -af "atempo=2.0,atempo=2.0" output.mp3  # 4x speed
```

---

## Fade In/Out

```bash
# Fade in first 3 seconds
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=3" output.mp3

# Fade out last 3 seconds (need duration first)
duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp3)
start=$(echo "$duration - 3" | bc)
ffmpeg -i input.mp3 -af "afade=t=out:st=$start:d=3" output.mp3

# Both fades
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=2,afade=t=out:st=58:d=2" output.mp3
```

---

## Silence Removal

```bash
# Remove silence longer than 0.5s, threshold -50dB
ffmpeg -i input.mp3 -af "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB" output.mp3

# Remove silence from beginning
ffmpeg -i input.mp3 -af "silenceremove=start_periods=1:start_threshold=-50dB" output.mp3

# Trim silence from both ends
ffmpeg -i input.mp3 -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse" output.mp3
```

---

## Channel Manipulation

```bash
# Stereo to mono
ffmpeg -i input.mp3 -ac 1 output.mp3

# Mono to stereo (duplicate channel)
ffmpeg -i input.mp3 -ac 2 output.mp3

# Extract left channel only
ffmpeg -i input.mp3 -af "pan=mono|c0=FL" output.mp3

# Extract right channel only
ffmpeg -i input.mp3 -af "pan=mono|c0=FR" output.mp3
```

---

## Sample Rate Conversion

```bash
# Convert to 44.1kHz
ffmpeg -i input.mp3 -ar 44100 output.mp3

# Convert to 48kHz (for video)
ffmpeg -i input.mp3 -ar 48000 output.mp3

# Convert to 16kHz (for Whisper)
ffmpeg -i input.mp3 -ar 16000 output.wav
```

---

## Compression (Dynamics)

```bash
# Basic compression (reduce dynamic range)
ffmpeg -i input.mp3 -af "acompressor=threshold=-20dB:ratio=4:attack=5:release=50" output.mp3

# Limiter (prevent clipping)
ffmpeg -i input.mp3 -af "alimiter=limit=0.9" output.mp3

# Normalize + compress for podcast
ffmpeg -i input.mp3 -af "acompressor=threshold=-20dB:ratio=3:attack=5:release=100,loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3
```

---

## EQ (Basic)

```bash
# Boost bass (below 200Hz)
ffmpeg -i input.mp3 -af "bass=g=5" output.mp3

# Boost treble (above 3kHz)
ffmpeg -i input.mp3 -af "treble=g=3" output.mp3

# Voice presence boost (3-4kHz)
ffmpeg -i input.mp3 -af "equalizer=f=3500:t=q:w=1:g=3" output.mp3

# De-ess (reduce sibilance around 6-8kHz)
ffmpeg -i input.mp3 -af "equalizer=f=7000:t=q:w=2:g=-4" output.mp3
```

---

## Create Ringtone

```bash
# 30-second clip with fades
ffmpeg -i song.mp3 -ss 60 -t 30 -af "afade=t=in:st=0:d=1,afade=t=out:st=29:d=1" -acodec libmp3lame -b:a 192k ringtone.mp3

# iPhone ringtone (M4R format)
ffmpeg -i song.mp3 -ss 60 -t 30 -af "afade=t=in:st=0:d=1,afade=t=out:st=29:d=1" -acodec aac -b:a 192k ringtone.m4r
```

---

## Batch Processing

```bash
# Convert all WAV to MP3
for f in *.wav; do ffmpeg -i "$f" -acodec libmp3lame -q:a 2 "${f%.wav}.mp3"; done

# Normalize all files in directory
for f in *.mp3; do ffmpeg -i "$f" -af "loudnorm=I=-16" "normalized_$f"; done
```
