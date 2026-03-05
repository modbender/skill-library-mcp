# Video Upscale - Installation

## Required Tools

This skill requires:
- `ffmpeg` - Video processing
- `bc` - Math calculations  
- `md5sum` - File hashing

## AI Upscaling Tools

Install in your home directory or anywhere accessible:

### Waifu2x (recommended for anime)
```bash
mkdir -p ~/video-tools/waifu2x-ncnn-vulkan
cd ~/video-tools/waifu2x-ncnn-vulkan
curl -L -o waifu2x.zip "https://github.com/nihui/waifu2x-ncnn-vulkan/releases/download/20220728/waifu2x-ncnn-vulkan-20220728-ubuntu.zip"
unzip waifu2x.zip
# Rename folder to: waifu2x-ncnn-vulkan-20220728-ubuntu
```

### Real-ESRGAN (better for real footage)
```bash
mkdir -p ~/video-tools/real-video-enhancer
cd ~/video-tools/real-video-enhancer
curl -L -o realesrgan.zip "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
unzip realesrgan.zip
chmod +x realesrgan-ncnn-vulkan
```

## Environment Variables

Set these to point to your tool locations:

```bash
# Add to ~/.bashrc or ~/.zshrc
export VIDEO_UPSCALE_REALESRGAN="$HOME/video-tools/real-video-enhancer"
export VIDEO_UPSCALE_WAIFU2X="$HOME/video-tools/waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan-20220728-ubuntu"
export VIDEO_UPSCALE_CACHE="$HOME/.openclaw/cache/video-upscale"
```

## Directory Structure

```
~/video-tools/
├── real-video-enhancer/
│   ├── upscale_video.sh (from this skill)
│   ├── realesrgan-ncnn-vulkan
│   └── models/
└── waifu2x-ncnn-vulkan/
    └── waifu2x-ncnn-vulkan-20220728-ubuntu/
        ├── waifu2x-ncnn-vulkan
        └── models-cunet/
```
