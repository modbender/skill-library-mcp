# Short Video Copywriter

Generate viral short video copy for TikTok, Xiaohongshu, Kuaishou, and more.

## Features

- Platform-specific styles (Douyin, Xiaohongshu, Kuaishou)
- Attention-grabbing hooks
- Popular hashtags generation
- Multi-format support

## Usage

```bash
# Interactive mode
npx short-video-copywriter

# API mode
import { generateCopy } from 'short-video-copywriter';

const result = await generateCopy({
  topic: "产品测评",
  platform: "xiaohongshu",
  tone: "亲和"
});
```

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| topic | string | Video topic or theme |
| platform | string | Target platform (douyin/xiaohongshu/kuaishou) |
| tone | string | Writing style (professional/casual/humor) |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| hook | string | Attention-grabbing opening |
| body | string | Main content |
| hashtags | string[] | Popular tags |
