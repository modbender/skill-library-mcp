# Seedance API Parameters Reference

This document provides complete API parameter reference for the Seedance video generation service.

## API Endpoints

### Generation Request
```
POST https://api.evolink.ai/v1/videos/generations
Authorization: Bearer {EVOLINK_API_KEY}
Content-Type: application/json
```

### Task Status Query
```
GET https://api.evolink.ai/v1/tasks/{task_id}
Authorization: Bearer {EVOLINK_API_KEY}
```

## Generation Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Fixed: `"seedance-1.5-pro"` |
| `prompt` | string | Text description of desired video content |

### Optional Parameters

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `image_urls` | array | `[]` | URLs | Reference images (max 9) |
| `duration` | integer | `5` | `4-12` | Video duration in seconds |
| `quality` | string | `"720p"` | `"480p"`, `"720p"`, `"1080p"` | Video resolution |
| `aspect_ratio` | string | `"16:9"` | `"16:9"`, `"9:16"`, `"1:1"`, `"4:3"`, `"3:4"`, `"21:9"` | Video aspect ratio |
| `generate_audio` | boolean | `true` | `true`, `false` | Generate synchronized audio (voice, SFX, music). Enabled by default; disabling reduces cost. |

### Parameter Constraints

#### Image URLs
- **Maximum count**: 9 images
- **File size limit**: ≤30MB per image
- **Supported formats**: JPEG, PNG, WebP, BMP, TIFF, GIF
- **Format**: Array of strings containing full URLs

#### Duration
- **Range**: 4-12 seconds
- **Type**: Integer
- **Impact**: Longer videos cost more and take longer to generate

#### Quality
- **480p**: Fastest, cheapest, lower quality
- **720p**: Balanced (recommended default)
- **1080p**: Highest quality, slower, most expensive

#### Aspect Ratio
- **16:9**: Standard landscape (YouTube, TV)
- **9:16**: Mobile/vertical (TikTok, Instagram Stories)
- **1:1**: Square (Instagram posts, social media)
- **4:3**: Traditional format
- **3:4**: Portrait format
- **21:9**: Ultra-wide cinematic

## Example Payloads

### Text-to-Video
```json
{
  "model": "seedance-1.5-pro",
  "prompt": "A serene sunset over calm ocean waves",
  "duration": 5,
  "quality": "720p",
  "aspect_ratio": "16:9",
  "generate_audio": false
}
```

### Image-to-Video
```json
{
  "model": "seedance-1.5-pro", 
  "prompt": "Gentle waves rolling onto the shore",
  "image_urls": [
    "https://example.com/beach1.jpg",
    "https://example.com/beach2.jpg"
  ],
  "duration": 8,
  "quality": "1080p",
  "aspect_ratio": "16:9",
  "generate_audio": false
}
```

## Response Format

### Generation Response
```json
{
  "task_id": "task_abc123",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Status Response
```json
{
  "task_id": "task_abc123",
  "status": "completed",
  "video_url": "https://cdn.example.com/video.mp4",
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:01:30Z"
}
```

## Task Status Values

| Status | Description | Action Required |
|--------|-------------|-----------------|
| `pending` | Task queued | Continue polling |
| `processing` | Generation in progress | Continue polling |
| `completed` | Video ready | Retrieve video_url |
| `failed` | Generation failed | Check error field |

## Error Codes

### HTTP Status Codes

| Code | Meaning | Common Causes | Solutions |
|------|---------|---------------|-----------|
| `200` | Success | - | Process response |
| `400` | Bad Request | Invalid parameters, content blocked, file too large | Check parameters and content |
| `401` | Unauthorized | Invalid or missing API key | Verify EVOLINK_API_KEY |
| `402` | Payment Required | Insufficient balance | Add credits at dashboard |
| `429` | Rate Limited | Too many requests | Wait and retry |
| `503` | Service Unavailable | Server maintenance/overload | Retry later |

### Error Response Format
```json
{
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Common Error Messages

#### Content Blocking (400)
- **Trigger**: Realistic human faces, inappropriate content
- **Message**: Contains "face" or "人脸" keywords
- **Solution**: Modify prompt to avoid restricted content

#### File Size (400) 
- **Trigger**: Images >30MB
- **Message**: Contains "file" and "large" or "size exceed"
- **Solution**: Compress images before upload

#### Invalid Key (401)
- **Message**: "Invalid API key" or similar
- **Solution**: Check key at https://evolink.ai/dashboard

#### Insufficient Balance (402)
- **Message**: "Insufficient balance" or similar  
- **Solution**: Add credits at https://evolink.ai/dashboard

## Polling Strategy

### Recommended Pattern
1. **Initial wait**: Start polling immediately
2. **Frequent polling**: Every 5 seconds for first 30 seconds
3. **Slower polling**: Every 10 seconds after 30 seconds
4. **Timeout**: Stop after 3 minutes with warning

### Typical Generation Times
- **4-5 seconds, 480p**: 20-45 seconds
- **5-8 seconds, 720p**: 30-90 seconds  
- **10-15 seconds, 1080p**: 60-180 seconds

### Timeout Handling
After 3 minutes, inform user that generation may still be processing and suggest checking back later.

## Rate Limits

- **Generation requests**: Varies by plan
- **Status queries**: Higher limit, safe to poll frequently
- **Concurrent tasks**: Varies by plan

Contact support for specific rate limit details for your account.

## Output URLs

- **Validity**: 24 hours from generation
- **Format**: MP4 video files
- **CDN delivery**: High-speed download
- **Audio**: Synchronized audio included by default (voice, sound effects, background music)

## Best Practices

### Prompt Writing
- Be specific and descriptive
- Include visual details (colors, lighting, movement)
- Avoid realistic human faces
- Use cinematic language for better results

### Performance Optimization  
- Start with 480p for testing
- Use shorter durations for faster generation
- Provide clear, high-quality reference images
- Batch similar requests to optimize costs

### Error Resilience
- Always handle all error codes
- Provide user-friendly error messages with action links
- Implement exponential backoff for rate limits
- Set reasonable timeouts for polling