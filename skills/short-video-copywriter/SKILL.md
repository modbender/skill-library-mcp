---
name: Short Video Copywriter
description: Generate viral short video copy for TikTok, Xiaohongshu, Kuaishou, and more.
---

# Short Video Copywriter

Generate viral short video copy for TikTok, Xiaohongshu, Kuaishou, and more.

## Supported Platforms

- **Douyin (抖音)**: Trendy, fast-paced, viral style
- **Xiaohongshu (小红书)**: Authentic, lifestyle, product reviews
- **Kuaishou (快手)**: Down-to-earth, relatable
- **Bilibili (B站)**: In-depth, niche, community style

## Usage

### Interactive Mode

```bash
npx short-video-copywriter
```

### API Mode

```typescript
import { generateShortVideoCopy } from 'short-video-copywriter';

// Generate copy for Xiaohongshu
const result = await generateShortVideoCopy({
  topic: "职场穿搭",
  platform: "xiaohongshu",
  tone: "亲和",
  length: "short"
});
```

## Input Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| topic | any text | required | Video topic or theme |
| platform | douyin/xiaohongshu/kuaishou/bilibili | douyin | Target platform |
| tone | professional/casual/humor/heartwarming | casual | Writing style |
| length | short/medium/long | short | Copy length |

## Output Format

```typescript
{
  hook: "开头金句",
  body: "正文内容",
  hashtags: ["#标签1", "#标签2", "#标签3"],
  tips: "发布建议"
}
```

## Examples

### Xiaohongshu Product Review

```typescript
Input: {
  topic: "平价面膜测评",
  platform: "xiaohongshu",
  tone: "亲和"
}

Output: {
  hook: "救命！30块的面膜竟然吊打大牌？！",
  body: "...",
  hashtags: ["#平价护肤", "#面膜测评", "#学生党"],
  tips: "建议晚8点发布，互动率更高"
}
```

### Douyin Vlog

```typescript
Input: {
  topic: "租房攻略",
  platform: "douyin",
  tone: "幽默"
}

Output: {
  hook: "租房血泪史！建议收藏！",
  body: "...",
  hashtags: ["#租房", "#避坑", "#租房攻略"],
  tips: "配合热门BGM效果更好"
}
```

## Environment Variables

```env
OPENAI_API_KEY=your_api_key_here
```

## Best Practices

1. **Hook First**: The first 3 seconds are critical
2. **Platform Match**: Use platform-specific slang and trends
3. **Hashtags**: Use 3-5 relevant tags
4. **Call to Action**: End with engagement prompts
