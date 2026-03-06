# QuiverAI API Reference

## Overview

QuiverAI provides a REST API for programmatic SVG generation.

**Base URL**: `https://api.quiver.ai`

## Authentication

Include your API key in the request header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Create SVG (Text to SVG)

**POST** `/v1/svgs`

**Request Body**:
```json
{
  "prompt": "A minimalist geometric lion logo",
  "reference_images": ["https://example.com/ref.jpg"],
  "format": "svg"
}
```

**Response**:
```json
{
  "id": "svg_abc123",
  "status": "processing",
  "svg_url": "https://cdn.quiver.ai/svgs/abc123.svg"
}
```

### Create SVG (Image to SVG)

**POST** `/v1/svgs/image-to-svg`

**Request Body**:
```json
{
  "image_url": "https://example.com/input.png",
  "style": "minimalist"
}
```

### Get SVG Status

**GET** `/v1/svgs/{id}`

**Response**:
```json
{
  "id": "svg_abc123",
  "status": "completed",
  "svg_url": "https://cdn.quiver.ai/svgs/abc123.svg",
  "preview_url": "https://cdn.quiver.ai/previews/abc123.png"
}
```

## Streaming

For real-time generation, use Server-Sent Events:
```
GET /v1/svgs/{id}/stream
```

## Rate Limits

| Plan | Requests/min |
|------|--------------|
| Free | 10 |
| Basic | 30 |
| Pro | 60 |
| Enterprise | Custom |

## Error Codes

- `400`: Invalid request
- `401`: Invalid API key
- `429`: Rate limit exceeded
- `500`: Server error
