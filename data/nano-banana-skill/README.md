# Nano Banana Skill

[![API](https://img.shields.io/badge/API-monet.vision-blue)](https://monet.vision)
[![Documentation](https://img.shields.io/badge/docs-latest-green)](https://monet.vision/skills/keys)

Nano Banana is Google's cutting-edge AI image generation model series designed for AI agents. It provides ultra-high character consistency, multiple resolution options, and support for complex reference image workflows. Part of the Monet AI unified API platform.

## ✨ Features

### 🌟 Google Nano Banana Series

- **nano-banana-1**: Ultra-high character consistency for image series
- **nano-banana-1-pro**: Flagship model with 1K-4K resolution support
- **nano-banana-2**: Latest Gemini-powered model with extreme aspect ratio support

### 🎯 Key Capabilities

- **Character Consistency**: Maintain consistent characters across multiple images
- **Reference Images**: Support up to 14 reference images for style guidance
- **Multiple Resolutions**: From standard to 4K output
- **Extreme Aspect Ratios**: From square to ultra-wide 21:9 and 8:1

## 🚀 Quick Start

### Get API Key

1. Visit [monet.vision](https://monet.vision) to register an account
2. After login, go to [API Keys page](https://monet.vision/skills/keys) to create an API Key
3. Configure the API Key in environment variables or code

### Setup

Set environment variable:

```bash
export MONET_API_KEY="monet_xxx"
```

### Your First Image Generation Task

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

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation on retries.

**Response Example:**

```json
{
  "id": "task_abc123",
  "status": "pending",
  "type": "image",
  "created_at": "2026-02-27T10:00:00Z"
}
```

### Query Task Status

Task processing is asynchronous. You need to poll the task status until it becomes `success` or `failed`. **Recommended polling interval: 5 seconds**.

```bash
curl https://monet.vision/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer $MONET_API_KEY"
```

**Response when completed:**

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

### Polling Example (TypeScript)

```typescript
const TASK_ID = 'task_abc123';
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

    if (status === 'success') {
      console.log('Task completed successfully!');
      console.log(JSON.stringify(data, null, 2));
      break;
    } else if (status === 'failed') {
      console.log('Task failed!');
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

## 📖 API Reference

### Create Task (Async)

**POST** `/api/v1/tasks/async`

Create an async task, returns task ID immediately.

### Create Task (Streaming)

**POST** `/api/v1/tasks/sync`

Create task with SSE streaming, waits for completion and streams progress.

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

**GET** `/api/v1/tasks/{taskId}`

Get task status and result.

### List Tasks

**GET** `/api/v1/tasks/list`

List tasks with pagination.

```bash
curl "https://monet.vision/api/v1/tasks/list?page=1&pageSize=20" \
  -H "Authorization: Bearer $MONET_API_KEY"
```

### Upload File

**POST** `/api/v1/files`

Upload a file to get an online access URL.

> 📁 **File Storage**: Uploaded files are stored for **24 hours** and will be automatically deleted after expiration.

```bash
curl -X POST https://monet.vision/api/v1/files \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -F "file=@/path/to/your/image.jpg" \
  -v
```

## 🎨 Supported Models

### nano-banana-1

_Google Nano Banana - Ultra-high character consistency_

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

_Nano Banana Pro - Google flagship generation model_

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

_Nano Banana 2 - Google Gemini latest model_

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

## 💡 Usage Examples

### Example 1: Basic Image Generation

```typescript
const response = await fetch('https://monet.vision/api/v1/tasks/async', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.MONET_API_KEY}`,
  },
  body: JSON.stringify({
    type: 'image',
    input: {
      model: 'nano-banana-1',
      prompt: 'A futuristic city with neon lights',
      aspect_ratio: '16:9',
    },
    idempotency_key: crypto.randomUUID(),
  }),
});

const task = await response.json();
console.log('Task created:', task.id);
```

### Example 2: Generate Image with Reference Images

```typescript
const response = await fetch('https://monet.vision/api/v1/tasks/async', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.MONET_API_KEY}`,
  },
  body: JSON.stringify({
    type: 'image',
    input: {
      model: 'nano-banana-1-pro',
      prompt: 'A character in a medieval armor',
      images: [
        'https://example.com/ref-character.jpg',
        'https://example.com/ref-style.jpg'
      ],
      aspect_ratio: '3:2',
      resolution: '2K',
    },
    idempotency_key: crypto.randomUUID(),
  }),
});

const task = await response.json();
console.log('Task created:', task.id);
```

### Example 3: Ultra-Wide Panorama with nano-banana-2

```typescript
const response = await fetch('https://monet.vision/api/v1/tasks/async', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.MONET_API_KEY}`,
  },
  body: JSON.stringify({
    type: 'image',
    input: {
      model: 'nano-banana-2',
      prompt: 'A breathtaking landscape of mountains at sunset',
      aspect_ratio: '21:9',
      resolution: '4K',
    },
    idempotency_key: crypto.randomUUID(),
  }),
});

const task = await response.json();
console.log('Task created:', task.id);
```

## 🔐 Authentication

All API requests require authentication via the `Authorization` header:

```
Authorization: Bearer monet_xxx
```

## 📋 Task Status

| Status       | Description                          |
| ------------ | ------------------------------------ |
| `pending`    | Task created, waiting for processing |
| `processing` | Task is being processed              |
| `success`    | Task completed successfully          |
| `failed`     | Task failed                          |

## 🌟 Best Practices

1. **Use Idempotency Keys**: Always provide a unique `idempotency_key` for tasks to prevent duplicate creation
2. **Character Consistency**: Use reference images to maintain character consistency across image series
3. **Resolution Selection**: Choose appropriate resolution based on your use case - higher resolution costs more
4. **Reference Image Limits**: nano-banana-1 supports up to 5, Pro/2 support up to 14 reference images
5. **Extreme Aspect Ratios**: Use nano-banana-2 for ultra-wide formats like 21:9 or 8:1

## 🤝 Support

- **Documentation**: [SKILL.md](SKILL.md)
- **Website**: [monet.vision](https://monet.vision)
- **API Keys**: [monet.vision/skills/keys](https://monet.vision/skills/keys)

## 📄 License

Please visit [monet.vision](https://monet.vision) for terms of service and usage license.

---

**Powered by Monet AI** - Comprehensive content generation platform built for AI agents
