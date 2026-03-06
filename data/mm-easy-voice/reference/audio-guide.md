# Audio Processing Guide

Audio processing commands using FFmpeg.

## Merge Audio

Combine multiple audio files:

```bash
python mmvoice.py merge file1.mp3 file2.mp3 file3.mp3 -o combined.mp3

# With crossfade
python mmvoice.py merge a.mp3 b.mp3 -o merged.mp3 --crossfade 300
```

## Convert Format

Convert between audio formats:

```bash
# Basic conversion
python mmvoice.py convert input.wav -o output.mp3

# With specific parameters
python mmvoice.py convert input.wav -o output.mp3 --format mp3 --bitrate 192k --sample-rate 32000
```

## Notes

- FFmpeg must be installed for audio processing
- Supported formats: mp3, wav, flac, ogg, m4a, aac, wma, opus, pcm
