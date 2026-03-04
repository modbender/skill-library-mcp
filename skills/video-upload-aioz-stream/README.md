# W3Stream Video Upload Skill

This skill enables quick video uploads to W3Stream API with custom encoding configurations.

## Features

- ✅ Default upload (quick, title only)
- ✅ Custom upload (full encoding control)
- ✅ Multi-part upload for large files
- ✅ Multiple quality presets (240p - 8K)
- ✅ H.264 and H.265 codec support
- ✅ HLS and DASH streaming formats
- ✅ Thumbnail upload
- ✅ Transcode cost calculation

## Scripts

### Core Upload Scripts
- `create_video_default.sh` - Create video object with minimal config
- `create_video_custom.sh` - Create video with custom quality settings
- `upload_video_file.sh` - Upload video file (supports multi-part)
- `get_video_detail.sh` - Retrieve video details and streaming URLs

### Additional Utilities
- `calculate_cost.sh` - Estimate transcoding costs
- `upload_thumbnail.sh` - Upload custom thumbnail

## Quick Start

```bash
# 1. Create video object (default)
./scripts/create_video_default.sh <public_key> <secret_key> "My Video Title"
# Returns: {"data": {"id": "VIDEO_ID", ...}}

# 2. Upload video file
./scripts/upload_video_file.sh <public_key> <secret_key> <VIDEO_ID> /path/to/video.mp4

# 3. Get video details (streaming URL)
./scripts/get_video_detail.sh <public_key> <secret_key> <VIDEO_ID>
```

## API Endpoint

Base URL: `https://api-w3stream.attoaioz.cyou`

## Authentication

Requires two headers on all API calls:
- `stream-public-key`: Your W3Stream public key
- `stream-secret-key`: Your W3Stream secret key

## Supported Resolutions

| Resolution | Dimensions | Max Bitrate |
|------------|------------|-------------|
| 240p | 426 × 240 | 700 Kbps |
| 360p | 640 × 360 | 1.2 Mbps |
| 480p | 854 × 480 | 2 Mbps |
| 720p | 1280 × 720 | 4 Mbps |
| 1080p | 1920 × 1080 | 6 Mbps |
| 1440p | 2560 × 1440 | 12 Mbps |
| 2160p | 3840 × 2160 | 30 Mbps |
| 4320p | 7680 × 4320 | 60 Mbps |

## Dependencies

- `curl` - HTTP client
- `jq` - JSON processor (optional, for parsing)
- `md5sum` - MD5 hash computation

## See Also

- Main documentation: `SKILL.md`
- Related skill: `audio-upload-aioz-stream`
