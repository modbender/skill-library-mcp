# SKILL.md - cutmv Video Tool

## Skill Name
cutmv-video-tool

## Description
A video processing skill for OpenClaw that leverages FFmpeg to perform video/audio cutting, format conversion, and compression. Perfect for handling video files for messaging apps with file size limits.

## Capabilities

- **Video Cutting**: Split video/audio by time range
- **Format Conversion**: Convert between video/audio formats (mp4, avi, mp3, wav, etc.)
- **Video Compression**: Compress videos with adjustable bitrate
- **Frame Extraction**: Extract frames from videos at specified intervals
- **Audio Extraction**: Extract audio track from video
- **Audio Replacement**: Replace or mix audio in video
- **Text Watermark**: Add text overlay on video (requires freetype)
- **Subtitle**: Add .srt/.ass subtitle files to video

## Use Cases

1. Compress videos to send via WeChat/Lark/Telegram (16MB limit)
2. Extract screenshots from videos for analysis
3. Convert video formats for different platforms
4. Cut specific segments from long videos

## Requirements

### System Requirements
- FFmpeg installed and available in PATH
- Python 3.7+

### Python Dependencies
- None (uses subprocess to call ffmpeg)

## Installation

1. Ensure FFmpeg is installed on your system:
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`
   - Windows: Download from ffmpeg.org or `winget install ffmpeg`

2. Place the skill files in your workspace:
   ```
   ~/openclaw-workspace/skills/cutmv-video-tool/
   ├── SKILL.md
   ├── skill.py
   ├── README.md
   └── README-CN.md
   ```

## Usage

### Python API

```python
from skill import VideoTool

tool = VideoTool()

# Compress video for messaging
tool.compress("input.mp4", "output.mp4", bitrate="1000k")

# Cut video segment
tool.cut("input.mp4", "clip.mp4", start_time=30, end_time=90)

# Convert format
tool.convert("input.mp4", "output.avi", "avi")

# Extract frames every 10 seconds
tool.extract_frames("input.mp4", "./frames/", interval=10)
```

### CLI Usage

```bash
# Compress video
python skill.py compress input.mp4 output.mp4 1000k

# Cut video
python skill.py cut input.mp4 clip.mp4 0 60

# Convert format
python skill.py convert input.mp4 output.mp3 mp3
```

## Configuration

No additional configuration required. The skill uses system FFmpeg installation.

## Testing

Run the built-in tests:

```bash
python skill.py test
```

## License

MIT License

## Author

- Isaac (@QiaoTuCodes)

## Acknowledgments

- OpenClaw team for the platform
- FFmpeg team for media processing tools


---

**Author Identity**: yanyan@3c3d77679723a2fe95d3faf9d2c2e5a65559acbc97fef1ef37783514a80ae453
