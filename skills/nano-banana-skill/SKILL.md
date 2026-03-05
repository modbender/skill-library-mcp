---
name: nano-banana-skill
description: Nano Banana, Nano Banana Pro, Nano Banana 2 - Google AI image generation models for AI agents. Ultra-high character consistency, 1K-4K resolution, up to 14 reference images, extreme aspect ratios up to 21:9 and 8:1.
metadata:
  openclaw:
    requires:
      env:
        - MONET_API_KEY # Required: API key from monet.vision
      bins: []
---

# Nano Banana Skill

Nano Banana is Google's cutting-edge AI image generation model series designed for AI agents. Part of the Monet AI unified API platform.

## When to Use

Use this skill when:

- **Character Consistent Image Series**: Create images with consistent characters using reference images
  - nano-banana-1: Up to 5 reference images for character consistency
  - nano-banana-1-pro: Up to 14 reference images with 1K-4K resolution
  - nano-banana-2: Latest Gemini model with extreme aspect ratio support
- **High-Resolution Output**: Generate professional-grade images with 1K, 2K, or 4K resolution
- **Ultra-Wide Formats**: Create panoramic images with extreme aspect ratios (21:9, 8:1)
- **Style Transfer**: Use multiple reference images to guide style and character

## Getting API Key

1. Visit https://monet.vision to register an account
2. After login, go to https://monet.vision/skills/keys to create an API Key
3. Configure the API Key in environment variables or code

If you don't have an API Key, ask your owner to apply at monet.vision.

## Quick Start

### Create an Image Generation Task

```bash
curl -X POST https://monet.vision/api/v1/tasks/async \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -d '{
    "type": "image",
    "input": {
      "model": "nano-banana-1",
      "prompt": "A cute cat in a garden",
      "aspect_ratio": "16:9"
    },
    "idempotency_key": "unique-key-123"
  }'
```

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation if the request is retried.

Response:

```json
{
  "id": "task_abc123",
  "status": "pending",
  "type": "image",
  "created_at": "2026-02-27T10:00:00Z"
}
```

### Get Task Status and Result

Task processing is asynchronous. You need to poll the task status until it becomes `success` or `failed`. **Recommended polling interval: 5 seconds**.

```bash
curl https://monet.vision/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer $MONET_API_KEY"
```

Response when completed:

```json
{
  "id": "task_abc123",
  "status": "success",
  "type": "image",
  "outputs": [
    {
      "model": "nano-banana-1",
      "status": "success",
      "progress": 100,
      "url": "https://files.monet.vision/..."
    }
  ],
  "created_at": "2026-02-27T10:00:00Z",
  "updated_at": "2026-02-27T10:01:30Z"
}
```

**Example: Poll until completion**

```typescript
const TASK_ID = "task_abc123";
const MONET_API_KEY = process.env.MONET_API_KEY;

async function pollTask() {
  while (true) {
    const response = await fetch(
      `https://monet.vision/api/v1/tasks/${TASK_ID}`,
      {
        headers: {
          Authorization: `Bearer ${MONET_API_KEY}`,
        },
      },
    );

    const data = await response.json();
    const status = data.status;

    if (status === "success") {
      console.log("Task completed successfully!");
      console.log(JSON.stringify(data, null, 2));
      break;
    } else if (status === "failed") {
      console.log("Task failed!");
      console.log(JSON.stringify(data, null, 2));
      break;
    } else {
      console.log(`Task status: ${status}, waiting...`);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
}

pollTask();
```

## Supported Models

### nano-banana-1

**nano-banana-1** - Google Nano Banana

_Ultra-high character consistency_

- 🎯 **Use Cases**: Image series requiring consistent character appearance
- 📐 **Max Reference Images**: 5

```typescript
{
  model: "nano-banana-1",
  prompt: string,                // Required
  images?: string[],             // Optional: Up to 5 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "16:9" | "9:16"
}
```

### nano-banana-1-pro

**nano-banana-1-pro** - Nano Banana Pro

_Google flagship generation model_

- 🎯 **Use Cases**: Professional-grade high-quality image generation
- 📐 **Max Reference Images**: 14
- 🖥️ **Resolution**: 1K, 2K, 4K

```typescript
{
  model: "nano-banana-1-pro",
  prompt: string,                // Required
  images?: string[],             // Optional: Up to 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "4:5" | "5:4" | "16:9" | "9:16" | "21:9",
  resolution?: "1K" | "2K" | "4K"
}
```

### nano-banana-2

**nano-banana-2** - Nano Banana 2

_Google Gemini latest model_

- 🎯 **Use Cases**: Latest technology for high-quality image generation
- 📐 **Max Reference Images**: 14
- 🖥️ **Resolution**: 1K, 2K, 4K
- 🌍 **Special**: Ultra-wide aspect ratios including 8:1

```typescript
{
  model: "nano-banana-2",
  prompt: string,                // Required
  images?: string[],             // Optional: Up to 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "4:5" | "5:4" | "16:9" | "9:16" | "21:9" | "4:1" | "1:4" | "8:1" | "1:8",
  resolution?: "1K" | "2K" | "4K"
}
```

## API Reference

### Create Task (Async)

POST `/api/v1/tasks/async` - Create an async task. Returns immediately with task ID.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/tasks/async \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -d '{
    "type": "image",
    "input": {
      "model": "nano-banana-1",
      "prompt": "A cute cat"
    },
    "idempotency_key": "unique-key-123"
  }'
```

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation if the request is retried.

**Response:**

```json
{
  "id": "task_abc123",
  "status": "pending",
  "type": "image",
  "created_at": "2026-02-27T10:00:00Z"
}
```

### Create Task (Streaming)

POST `/api/v1/tasks/sync` - Create a task with SSE streaming. Waits for completion and streams progress.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/tasks/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -N \
  -d '{
    "type": "image",
    "input": {
      "model": "nano-banana-1",
      "prompt": "A cute cat"
    },
    "idempotency_key": "unique-key-123"
  }'
```

### Get Task

GET `/api/v1/tasks/{taskId}` - Get task status and result.

**Request:**

```bash
curl https://monet.vision/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer $MONET_API_KEY"
```

**Response:**

```json
{
  "id": "task_abc123",
  "status": "success",
  "type": "image",
  "outputs": [
    {
      "model": "nano-banana-1",
      "status": "success",
      "progress": 100,
      "url": "https://files.monet.vision/..."
    }
  ],
  "created_at": "2026-02-27T10:00:00Z",
  "updated_at": "2026-02-27T10:01:30Z"
}
```

### List Tasks

GET `/api/v1/tasks/list` - List tasks with pagination.

**Request:**

```bash
curl "https://monet.vision/api/v1/tasks/list?page=1&pageSize=20" \
  -H "Authorization: Bearer $MONET_API_KEY"
```

**Response:**

```json
{
  "tasks": [
    {
      "id": "task_abc123",
      "status": "success",
      "type": "image",
      "outputs": [
        {
          "model": "nano-banana-1",
          "status": "success",
          "progress": 100,
          "url": "https://files.monet.vision/..."
        }
      ],
      "created_at": "2026-02-27T10:00:00Z",
      "updated_at": "2026-02-27T10:01:30Z"
    }
  ],
  "page": 1,
  "pageSize": 20,
  "total": 100
}
```

### Upload File

POST `/api/v1/files` - Upload a file to get an online access URL.

> 📁 **File Storage**: Uploaded files are stored for **24 hours** and will be automatically deleted after expiration.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/files \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -F "file=@/path/to/your/image.jpg" \
  -v
```

**Response:**

```json
{
  "id": "file_xyz789",
  "url": "...",
  "filename": "image.jpg",
  "size": 1048576,
  "content_type": "image/jpeg",
  "created_at": "2026-02-27T10:00:00Z"
}
```

## Configuration

### Environment Variables

```bash
export MONET_API_KEY="monet_xxx"
```

### Authentication

All API requests require authentication via the `Authorization` header:

```
Authorization: Bearer monet_xxx
```
