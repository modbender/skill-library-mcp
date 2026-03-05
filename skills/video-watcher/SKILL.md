---
name: video-analyzer
description: Analyze video content by extracting frames at regular intervals. Use when you need to understand what's in a video file, review video content, analyze scenes, or describe video without being able to play it directly. Supports MP4, MOV, AVI, MKV, and other common video formats.
---

# Video Analyzer

Analyze video files by extracting frames at 1-second intervals using ffmpeg, then examining the frames to understand the video content.

## Prerequisites

Requires `ffmpeg` installed on the system. Install if missing:

```bash
# Ubuntu/Debian
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg
```

## Usage

### Extract frames from video

```bash
scripts/extract_frames.sh <video_path> [output_dir] [fps]
```

**Arguments:**
- `video_path` (required): Path to the video file
- `output_dir` (optional): Directory for extracted frames. Default: creates `frames_<video_name>` in current directory
- `fps` (optional): Frames per second to extract. Default: 1 (one frame per second)

**Example:**
```bash
scripts/extract_frames.sh /path/to/video.mp4
scripts/extract_frames.sh /path/to/video.mp4 ./my_frames
scripts/extract_frames.sh /path/to/video.mp4 ./my_frames 2  # 2 frames per second
```

**Output:**
- Creates numbered frame images: `frame_001.jpg`, `frame_002.jpg`, etc.
- Prints video metadata (duration, resolution, frame count)

## Workflow

1. Run `extract_frames.sh` on the video file
2. Read key frames using the `read` tool to view images
3. For comprehensive analysis, sample frames at regular intervals (e.g., every 5th frame)
4. Describe what you see in each frame to build understanding of the video

## Tips

- For short videos (<1 min): Review all frames
- For medium videos (1-5 min): Sample every 3-5 frames
- For long videos (>5 min): Sample every 10+ frames, focus on scene changes
- Look for: scene transitions, text/titles, UI elements, actions, characters
