<p align="center">
    <picture>
        <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/QiaoTuCodes/openclaw-skill-cutmv-video-tool/main/openclaw-skill-logo.png">
        <img src="https://raw.githubusercontent.com/QiaoTuCodes/openclaw-skill-cutmv-video-tool/main/openclaw-skill-logo.png" alt="OpenClaw Skill" width="500">
    </picture>
</p>

<p align="center">
  <strong>🎬 Video Processing Skill for OpenClaw</strong>
</p>

<p align="center">
  <a href="https://github.com/QiaoTuCodes/openclaw-skill-cutmv-video-tool/releases"><img src="https://img.shields.io/github/v/release/QiaoTuCodes/openclaw-skill-cutmv-video-tool?include_prereleases&style=for-the-badge" alt="GitHub release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://github.com/QiaoTuCodes/openclaw-skill-cutmv-video-tool/stargazers"><img src="https://img.shields.io/github/stars/QiaoTuCodes/openclaw-skill-cutmv-video-tool?style=for-the-badge" alt="Stars"></a>
</p>

A powerful video processing skill for OpenClaw that leverages FFmpeg to perform video/audio cutting, format conversion, compression, and more.

## ✨ Features

- ✂️ **Video Cutting** - Split video/audio by time range
- 🔄 **Format Conversion** - Convert between video/audio formats
- 🗜️ **Video Compression** - Compress videos with quality control
- 🖼️ **Frame Extraction** - Extract frames from videos
- 🎵 **Audio Extraction** - Extract audio track from video
- 🔊 **Audio Replacement** - Replace or mix audio in video
- 📝 **Text Watermark** - Add text overlay on video
- 💬 **Subtitle** - Add .srt/.ass subtitle files

## 📦 Installation

```bash
# Clone this skill to your OpenClaw workspace
cp -r openclaw-skill-cutmv-video-tool ~/openclaw-workspace/skills/

# Install dependencies
brew install ffmpeg  # macOS
# or: sudo apt install ffmpeg  # Ubuntu
```

## 🚀 Quick Start

```python
from skill import VideoTool

tool = VideoTool()

# Compress video
tool.compress("input.mp4", "output.mp4", "1000k")

# Cut video
tool.cut("input.mp4", "clip.mp4", start_time=0, end_time=60)

# Convert format
tool.convert("input.mp4", "output.avi", "avi")

# Extract frames
tool.extract_frames("input.mp4", "./frames/", interval=10)
```

## 📖 Documentation

- [English README](README.md)
- [中文文档](README-CN.md)
- [Skill Definition](SKILL.md)

## 🔧 Requirements

- FFmpeg installed
- Python 3.7+

## 📂 Project Structure

```
openclaw-skill-cutmv-video-tool/
├── SKILL.md           # OpenClaw skill definition
├── skill.py           # Main Python module
├── README.md          # English documentation
├── README-CN.md       # Chinese documentation
├── LICENSE            # MIT License
└── .gitignore
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 👥 Authors

- **Isaac** - [GitHub](https://github.com/QiaoTuCodes)
- **焱焱 (Yanyan)** - yanyan@3c3d77679723a2fe95d3faf9d2c2e5a65559acbc97fef1ef37783514a80ae453

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) team for the amazing platform
- FFmpeg team for the powerful media processing tools

---

<p align="center">
  <sub>Built with ❤️ for the OpenClaw community</sub>
</p>
