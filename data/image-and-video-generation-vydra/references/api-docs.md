# Vydra API Documentation

Complete reference for Vydra.ai API integration.

## Base URL
```
https://vydra.ai/api/v1
```

## Authentication
All API requests require an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

## Core Endpoints

### 1. List Available Models
```http
GET /models
```

**Query Parameters:**
- `provider` (optional): Filter by provider (e.g., "kie-ai", "xai", "fal-ai", "elevenlabs")
- `isActive` (optional): Filter active models only (`true`/`false`)

**Response:**
```json
{
  "data": [
    {
      "slug": "veo3",
      "name": "Google Veo 3 — Video Generation",
      "provider": "kie-ai",
      "creditsPerUnit": 175,
      "pricingUnit": "video",
      "description": "Generate high-quality videos from text prompts",
      "inputSchema": {...},
      "isActive": true
    }
  ],
  "count": 12
}
```

### 2. Generate Video/Image (Model-Specific)
```http
POST /models/{model-slug}
```

#### Veo 3 Text-to-Video
```http
POST /models/veo3
```
**Body:**
```json
{
  "prompt": "A serene lake at sunset",
  "aspect_ratio": "9:16" // "16:9", "9:16", "1:1"
}
```

#### Grok Imagine
```http
POST /models/grok-imagine
```
**Body:**
```json
{
  "prompt": "Creative description",
  "model": "text-to-image", // "text-to-image", "text-to-video", "image-to-video"
  "aspect_ratio": "16:9", // optional
  "duration": 10 // for video models only
}
```

#### Kling Motion Control
```http
POST /models/kling-motion-control
```
**Body:**
```json
{
  "image_url": "https://...",
  "video_url": "https://...", 
  "prompt": "Optional description",
  "keep_original_sound": true
}
```

#### ASMR Generator
```http
POST /models/asmr-generator
```
**Body:**
```json
{
  "theme": "kinetic_sand" // or customPrompt for custom text
}
```

**Success Response (202 Accepted):**
```json
{
  "jobId": "job_abc123",
  "status": "pending",
  "message": "Job created. Poll /jobs/{jobId} for status.",
  "creditsCharged": 350,
  "externalJobId": "ext_xyz789"
}
```

### 3. Check Job Status
```http
GET /jobs/{jobId}
```

**Response (Pending/Running):**
```json
{
  "id": "job_abc123",
  "status": "running", // "pending", "running", "completed", "failed", "cancelled"
  "progress": 45,
  "workflow": "kling",
  "creditsCharged": 350,
  "createdAt": "2024-01-15T10:30:00Z",
  "startedAt": "2024-01-15T10:30:15Z"
}
```

**Response (Completed):**
```json
{
  "id": "job_abc123", 
  "status": "completed",
  "output": {
    "videoUrl": "https://vydra-cdn.com/videos/xyz.mp4",
    "duration": 8,
    "resolution": "1080p"
  },
  "creditsCharged": 350,
  "createdAt": "2024-01-15T10:30:00Z",
  "completedAt": "2024-01-15T10:32:45Z"
}
```

**Response (Failed):**
```json
{
  "id": "job_abc123",
  "status": "failed", 
  "error": {
    "message": "Content moderation failed",
    "code": "CONTENT_VIOLATION"
  },
  "creditsRefunded": 350,
  "refundStatus": "refunded"
}
```

### 4. Cancel Job
```http
DELETE /jobs/{jobId}
```

**Response:**
```json
{
  "success": true,
  "message": "Job cancelled",
  "refund": {
    "creditsRefunded": 350,
    "alreadyRefunded": false
  }
}
```

### 5. Check Credit Balance  
```http
GET /organization
```

**Response:**
```json
{
  "id": "org_123",
  "name": "My Organization",
  "creditsRemaining": 2750,
  "plan": "creator", // "free", "creator", "pro", "enterprise"
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Invalid API key"
}
```

### 402 Insufficient Credits
```json
{
  "error": "Insufficient credits",
  "creditsRequired": 350,
  "creditsRemaining": 150
}
```

### 400 Bad Request
```json
{
  "error": "Missing required field: prompt (string)"
}
```

### 404 Not Found
```json
{
  "error": "Job not found"
}
```

### 429 Rate Limited
```json
{
  "error": "Rate limit exceeded. Try again in 60 seconds."
}
```

## Rate Limits

- **Generation requests**: 10 per minute
- **Status checks**: 100 per minute  
- **Model listing**: 50 per minute

## Credit Pricing

| Model | Credits | Approx. Cost | Notes |
|-------|---------|-------------|-------|
| Veo 3 | 175 | ~$0.51 | Text-to-video |
| Kling Motion Control | 350 | ~$1.02 | Motion transfer |
| Grok Imagine (Image) | 8 | ~$0.02 | Text-to-image |
| Grok Imagine (Video) | 150 | ~$0.44 | Text/image-to-video |
| ASMR Generator | 175 | ~$0.51 | Themed videos |
| ElevenLabs TTS | 5 | ~$0.01 | Per request |
| ElevenLabs STS | 10 | ~$0.03 | Voice conversion |
| Whisper | 3 | ~$0.01 | Per minute |
| Video utilities | 2-5 | ~$0.01 | Trim/compose/extract |
| Nano Banana | 8 | ~$0.02 | Image gen/edit |

*Pricing based on Creator plan rates (1 credit ≈ $0.003)*

## Best Practices

1. **Poll Efficiently**: Check status every 10-30 seconds, not continuously
2. **Handle Errors**: Always check for 402 (insufficient credits) and 400 (validation)
3. **Cache Models**: Model list changes infrequently, cache for 1+ hours
4. **Validate Inputs**: Check file URLs are accessible before submitting
5. **Monitor Credits**: Alert users when balance drops below 500 credits

## SDKs & Integration

The official CLI tools (`scripts/`) provide high-level wrappers around these APIs with:
- Automatic retry logic
- Progress tracking
- Error handling
- Credit warnings
- File management

See individual script files for implementation details.