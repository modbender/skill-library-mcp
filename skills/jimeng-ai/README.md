# Jimeng AI - Text to Image & Video

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A TypeScript CLI tool for generating images and videos from text prompts using ByteDance's VolcEngine Jimeng AI API.

## Features

- **Text-to-image generation**: Jimeng AI image generation (v3.0 / v3.1 / v4.0)
- **Text-to-video generation**: Jimeng AI video generation (v3.0 1080P)
- **Task persistence**: Tasks are stored using MD5 hash of the prompt as folder name
- **Async query**: Resume and query existing tasks without re-submission
- **Base64 image handling**: Images saved directly from API response
- Configurable aspect ratios, image count, and custom dimensions
- AWS Signature V4 compatible authentication
- Supports both permanent credentials (AK/SK) and temporary credentials (STS Token)
- Structured JSON output for easy integration

## Tech Stack

- **TypeScript** + **Node.js**
- **axios** — HTTP client
- **crypto** (Node.js built-in) — AWS Signature V4 signing
- **ts-node** — Direct TypeScript execution

## Quick Start

### 1. Install dependencies

```bash
npm install
```

### 2. Configure credentials

| Variable | Required | Description |
|----------|----------|-------------|
| `VOLCENGINE_AK` | **Required** | VolcEngine Access Key |
| `VOLCENGINE_SK` | Conditional | VolcEngine Secret Key (required for permanent credentials) |
| `VOLCENGINE_TOKEN` | Optional | Security Token (required for temporary STS credentials) |

> **Note**: When using temporary credentials (starting with AKTP), you can use AK + Token without SK.

```bash
export VOLCENGINE_AK="your-access-key"
export VOLCENGINE_SK="your-secret-key"

# Optional: for temporary credentials (STS)
export VOLCENGINE_TOKEN="your-security-token"
```

Get your credentials from [VolcEngine Console](https://console.volcengine.com/) → Access Control → Key Management.

### 3. Run

**Text-to-Image:**

```bash
npx ts-node scripts/text2image.ts "a cute cat"
```

**Text-to-Video:**

```bash
npx ts-node scripts/text2video.ts "a cute cat running on grass"
```

## Text-to-Image Usage

```bash
npx ts-node scripts/text2image.ts "prompt" [options]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `prompt` | Image generation prompt (required) | - |
| `--version` | API version: `v30`, `v31`, `v40` | `v31` |
| `--ratio` | Aspect ratio: `1:1`, `9:16`, `16:9`, `3:4`, `4:3`, `2:3`, `3:2`, `1:2`, `2:1` | `16:9` |
| `--count` | Number of images (1–4) | `1` |
| `--width` | Custom width (optional) | - |
| `--height` | Custom height (optional) | - |
| `--size` | Custom area (optional, e.g. `4194304` = 2048×2048) | - |
| `--seed` | Random seed (optional) | - |
| `--output` | Image output directory | `./output` |
| `--debug` | Enable debug mode | `false` |
| `--no-download` | Do not download images, only return URLs | `false` |

## Text-to-Image Workflow

### First Execution (New Task)

When you run with a new prompt, the script will:
1. Submit the task to the API
2. Create a folder using `md5(prompt)` as the name
3. Save `param.json`, `response.json`, and `taskId.txt`
4. Output: `"Task submitted, TaskId: xxx"`

```bash
$ npx ts-node scripts/text2image.ts "a cute cat"
Task submitted, TaskId: 1234567890
```

### Subsequent Executions (Async Query)

Running with the same prompt will query the existing task:
1. If images exist → returns image paths immediately
2. If task is incomplete → outputs: `"Task incomplete, TaskId: xxx"`
3. If task is complete → downloads images and returns paths

```bash
$ npx ts-node scripts/text2image.ts "a cute cat"
Task incomplete, TaskId: 1234567890

# Or when complete:
$ npx ts-node scripts/text2image.ts "a cute cat"
Task completed, images saved:
  - ./output/<md5_hash>/1.jpg
  - ./output/<md5_hash>/2.jpg
```

## Examples

### Landscape painting (16:9)

```bash
npx ts-node scripts/text2image.ts "mountain landscape, ink wash painting style" --version v40 --ratio 16:9
```

### Sci-fi city, multiple images

```bash
npx ts-node scripts/text2image.ts "futuristic sci-fi city, neon lights, cyberpunk style" --version v40 --ratio 16:9 --count 2
```

### Custom dimensions

```bash
npx ts-node scripts/text2image.ts "abstract art" --width 2048 --height 1152
```

### Custom output directory

```bash
npx ts-node scripts/text2image.ts "a cute cat" --output ~/Pictures/jimeng
```

## Output Format

### Task Submitted (First Run)

```json
{
  "success": true,
  "submitted": true,
  "prompt": "a cute cat",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "folder": "./output/<md5_hash>",
  "message": "Task submitted, query later with the same prompt"
}
```

### Task Completed

```json
{
  "success": true,
  "prompt": "a cute cat",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "images": [
    "./output/<md5_hash>/1.jpg",
    "./output/<md5_hash>/2.jpg"
  ],
  "outputDir": "./output/<md5_hash>"
}
```

### Task Incomplete

```json
{
  "success": true,
  "prompt": "a cute cat",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "folder": "./output/<md5_hash>",
  "message": "Task incomplete, query later with the same prompt"
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "MISSING_CREDENTIALS",
    "message": "Please set environment variables VOLCENGINE_AK and VOLCENGINE_SK"
  }
}
```

## Folder Structure

### Text-to-Image Output

```
output/
└── <md5(prompt)>/           # MD5 hash as folder name
    ├── param.json           # Request parameters
    ├── response.json        # API submit response
    ├── taskId.txt           # Task ID
    └── 1.jpg, 2.jpg, ...    # Generated images
```

### Text-to-Video Output

```
output/video/
└── <md5(prompt)>/           # MD5 hash as folder name
    ├── param.json           # Request parameters
    ├── response.json        # API submit response
    ├── taskId.txt           # Task ID
    └── video.mp4            # Generated video
```

## Text-to-Video Usage

```bash
npx ts-node scripts/text2video.ts "prompt" [options]
```

### Video Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `prompt` | Video generation prompt (required) | - |
| `--ratio` | Aspect ratio: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9` | `9:16` |
| `--duration` | Video duration: `5` or `10` seconds | `5` |
| `--fps` | Frame rate: `24` or `30` | `24` |
| `--output` | Video output directory | `./output/video` |
| `--wait` | Wait for task completion | `false` |
| `--debug` | Enable debug mode | `false` |
| `--no-download` | Do not download video, only return URL | `false` |

### Video Examples

```bash
# Basic usage
npx ts-node scripts/text2video.ts "a cute cat running on grass"

# Custom aspect ratio and duration
npx ts-node scripts/text2video.ts "futuristic city" --ratio 16:9 --duration 10

# Wait for completion
npx ts-node scripts/text2video.ts "ocean waves" --wait
```

### Video Output Format

#### Task Submitted

```json
{
  "success": true,
  "submitted": true,
  "prompt": "a cute cat running",
  "ratio": "9:16",
  "duration": 5,
  "fps": 24,
  "taskId": "1234567890",
  "folder": "./output/video/<md5_hash>",
  "message": "Task submitted, query later with the same prompt"
}
```

#### Task Completed

```json
{
  "success": true,
  "prompt": "a cute cat running",
  "ratio": "9:16",
  "duration": 5,
  "fps": 24,
  "taskId": "1234567890",
  "videoUrl": "https://...",
  "videoPath": "./output/video/<md5_hash>/video.mp4",
  "outputDir": "./output/video/<md5_hash>"
}
```

## Project Structure

```
jimeng/
├── scripts/
│   ├── common.ts          # Shared utilities: API signing, HTTP requests, credentials
│   ├── text2image.ts      # Text-to-image CLI entry point
│   ├── text2video.ts      # Text-to-video CLI entry point
│   └── debug-sign.ts      # Signature debugging tool
├── dist/                  # Compiled JavaScript output
├── check_key.sh           # Credential verification script
├── verify_auth.py         # Python auth verification helper
├── package.json
├── tsconfig.json
├── skill.yaml             # Skill configuration
├── SKILL.md               # Usage guide (Chinese)
└── README.md
```

## Supported Models

### Image Generation

| Version | Model | Description |
|---------|-------|-------------|
| `v30` | `jimeng_t2i_v30` | Jimeng 3.0 — baseline |
| `v31` | `jimeng_t2i_v31` | Jimeng 3.1 — improved |
| `v40` | `jimeng_t2i_v40` | Jimeng 4.0 — latest (recommended) |

### Video Generation

| Version | Model | Description |
|---------|-------|-------------|
| `v30` | `jimeng_t2v_v30` | Jimeng 3.0 1080P video generation |

## Development

```bash
# Build TypeScript
npm run build

# Run text-to-image
npx ts-node scripts/text2image.ts "prompt"

# Run text-to-video
npx ts-node scripts/text2video.ts "prompt"
```

## License

[MIT](https://opensource.org/licenses/MIT)

## Reference

- [VolcEngine Jimeng AI Text-to-Image Documentation](https://www.volcengine.com/docs/85621/1820192)
- [VolcEngine Jimeng AI Text-to-Video Documentation](https://www.volcengine.com/docs/85621/1792702)
