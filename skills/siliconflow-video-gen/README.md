# SiliconFlow Video Generation Skill

Generate videos using SiliconFlow API with Wan2.2 model. Supports both Text-to-Video and Image-to-Video.

## Features

- 🎬 **Text-to-Video**: Generate videos from text descriptions
- 🖼️ **Image-to-Video**: Animate static images with motion
- 🎥 **Cinematic Quality**: Powered by Wan2.2 (14B params)
- 🔑 **Auto API Key Detection**: Reads from environment or OpenClaw config
- 📱 **OpenClaw Ready**: Designed for OpenClaw Agent integration

## Installation

```bash
# Via ClawHub
npx clawhub install siliconflow-video-gen

# Or manual
git clone https://github.com/your-repo/siliconflow-video-gen.git ~/.openclaw/workspace/skills/siliconflow-video-gen
```

## Configuration

Set your SiliconFlow API key:

```bash
export SILICONFLOW_API_KEY="your-api-key"
```

Or the skill will auto-detect from `~/.openclaw/openclaw.json`

## Usage

### Command Line

```bash
# Text-to-Video
python3 scripts/generate.py "A woman walking in a blooming garden, cinematic shot"

# Image-to-Video
python3 scripts/generate.py "Camera slowly zooming in" --image-url https://example.com/image.jpg

# Specify custom model
python3 scripts/generate.py "Sunset over mountains" --model "Wan-AI/Wan2.2-T2V-A14B"
```

### OpenClaw Agent

```
生成视频：一位女士在盛开的花园中漫步，电影级镜头
```

Or for image-to-video:

```
基于图片生成视频：https://example.com/image.jpg，镜头缓慢推进
```

## Available Models

| Model | Type | Cost | Quality |
|-------|------|------|---------|
| `Wan-AI/Wan2.2-T2V-A14B` | Text-to-Video | ¥2/video | Cinematic |
| `Wan-AI/Wan2.2-T2V-A14B` | Image-to-Video | ¥2/video | Cinematic |

## Model Details

**Wan2.2-T2V-A14B**
- Released: July 28, 2025
- Parameters: 14B
- Architecture: MoE (Mixture of Experts)
- Resolution: Up to 1080P
- Features: First open-source 14B video model with cinematic quality

## API Response

The script returns a JSON response:

```json
{
  "success": true,
  "message": "Job submitted successfully",
  "mode": "Text-to-Video",
  "request_id": "wylhsk14i432",
  "model": "Wan-AI/Wan2.2-T2V-A14B",
  "prompt": "A woman walking in garden",
  "image_url": null,
  "note": "Video generation is async. Use request_id to check status."
}
```

## Important Notes

- Video generation is **asynchronous**
- Use the returned `request_id` to check generation status
- Each video costs ¥2 (about $0.28 USD)
- Generation typically takes 1-5 minutes depending on complexity

## Author

MaxStorm Team

## License

MIT
