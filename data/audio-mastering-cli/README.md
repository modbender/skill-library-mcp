# OpenClaw Skill: Audio Mastering CLI

A skill compatible with OpenClaw/AgentSkills for CLI audio mastering without a reference track.

## Features
- Masters audio files (`wav`, `aiff`, `flac`, `mp3`, `m4a`).
- Masters audio inside video files (`mp4`, `mov`, `m4v`, `mkv`, `webm`) and outputs `mp4`.
- Reproducible chain: EQ + compression + limiter + 2-pass loudnorm.

## Requirements
- `ffmpeg` available in `PATH`
- `powershell` (Windows)

## Installation
Clone this repo and place it inside your OpenClaw workspace `skills/` folder.

```powershell
git clone https://github.com/alesys/openclaw-skill-audio-mastering-cli.git
```

## Usage (examples)
Audio to WAV + MP3:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\master_media.ps1" -InputFile ".\water.wav" -MakeMp3
```

MOV/MP4 video to mastered MP4:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\master_media.ps1" -InputFile ".\coyo2.mov" -MakeMp3
```

Expected outputs:
- `<base>_master.wav`
- `<base>_master.mp3` (if `-MakeMp3`)
- `<base>_master.mp4` (if input contains video)

## Known limitations
- If source material is too hot, you may see internal clipping warnings in EQ stages.
- Loudness target is conservative and cross-platform (`~ -14 LUFS`), not tuned for aggressive loud masters.
- For video output, the video stream is preserved (`-c:v copy`) and only audio is re-encoded to AAC 320k.

## Version
- `v1.0.0`
