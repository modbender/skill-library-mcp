**English** | **[中文](README_CN.md)**

# Seedance 2.0 API Guide

API integration examples for the Seedance 2.0 all-in-one model. Access ByteDance's next-generation AI video generation model through the [Xskill AI](https://www.xskill.ai/#/v2/models?model=st-ai%2Fsuper-seed2) platform.

## Model Overview

**Model ID:** `st-ai/super-seed2`

Seedance 2.0 is ByteDance's next-generation AI video generation model with the following core capabilities:

- **Multi-modal Mixed Input** — Supports mixed input of images/videos/audio (up to 9 images + 3 videos + 3 audio clips)
- **@ Reference Syntax** — Precisely control each asset's role using `@image_file_1`, `@video_file_1`, `@audio_file_1` (backward compatible with `@图片1`, `@视频1`)
- **Two Function Modes** — Omni Reference (multi-modal mixing) and First/Last Frames (image-to-video)
- **Native Audio-Visual Sync** — Phoneme-level lip sync support (8+ languages)
- **Multi-shot Narrative** — Generate multi-shot coherent narratives from a single prompt
- **Cinema-grade Quality** — Up to 2K resolution output, 4-15 seconds duration, ~60 seconds to generate

## Pricing

| Mode | Price |
|------|-------|
| Base price | 40 credits/completion |
| Fast 5s (text-to-video) | 50 credits |
| Fast 5s (with video input) | 100 credits |
| Standard 5s (with video input) | 200 credits |

> Billed per second: Fast without video 10/sec, with video 20/sec; Standard without video 20/sec, with video 40/sec (4-15 sec)

## Prerequisites

1. Register an account at [Xskill AI](https://www.xskill.ai)
2. Create an API Key on the [API Key page](https://www.xskill.ai/#/v2/api-key)
3. Obtain credits for API calls

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v3/tasks/create` | POST | Create a task, returns task_id |
| `/api/v3/tasks/query` | POST | Query task status and results |

**Base URL:** `https://api.xskill.ai`

### Authentication

Add the API Key to the request header:

```
Authorization: Bearer sk-your-api-key
```

### Function Modes

Seedance 2.0 supports two function modes:

| Mode | Description | Asset Parameters |
|------|-------------|-----------------|
| `omni_reference` | **Omni Reference (default)** — Multi-modal mixing with separate image/video/audio arrays | `image_files`, `video_files`, `audio_files` |
| `first_last_frames` | **First/Last Frames** — Text-to-video or image-to-video with first/last frame control | `filePaths` |

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID, fixed as `st-ai/super-seed2` |
| `params.model` | string | No | Speed mode: `seedance_2.0_fast` (fast, default) / `seedance_2.0` (standard) |
| `params.prompt` | string | Yes | Prompt text. Supports `@image_file_1`, `@video_file_1`, `@audio_file_1` to reference assets (also compatible with `@图片1`, `@视频1`, `@音频1`) |
| `params.functionMode` | string | No | Function mode: `omni_reference` (default) / `first_last_frames` |
| `params.ratio` | string | No | Aspect ratio: `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `params.duration` | integer | No | Video duration (seconds), 4-15 integer. Default `5` |
| `params.image_files` | array | No | Reference image URL array (omni_reference mode, max 9). Array element N corresponds to `@image_file_N` |
| `params.video_files` | array | No | Reference video URL array (omni_reference mode, max 3, total ≤ 15s). Array element N corresponds to `@video_file_N` |
| `params.audio_files` | array | No | Reference audio URL array (omni_reference mode, max 3). Array element N corresponds to `@audio_file_N` |
| `params.filePaths` | array | No | Image URL array (first_last_frames mode). 0 items: text-to-video; 1 item: first frame; 2 items: first + last frame |

### cURL Example

```bash
# Example 1: Omni Reference mode (image + video)
curl -X POST "https://api.xskill.ai/api/v3/tasks/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "st-ai/super-seed2",
    "params": {
      "model": "seedance_2.0_fast",
      "prompt": "@image_file_1 character performs following @video_file_1 motion and camera style, cinematic lighting",
      "functionMode": "omni_reference",
      "image_files": [
        "https://your-character-image.png"
      ],
      "video_files": [
        "https://your-reference-video.mp4"
      ],
      "ratio": "16:9",
      "duration": 5
    }
  }'

# Example 2: First/Last Frames mode
curl -X POST "https://api.xskill.ai/api/v3/tasks/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "st-ai/super-seed2",
    "params": {
      "model": "seedance_2.0_fast",
      "prompt": "Smooth cinematic transition from first frame to last frame, elegant lighting",
      "functionMode": "first_last_frames",
      "filePaths": [
        "https://your-first-frame.png",
        "https://your-last-frame.png"
      ],
      "ratio": "16:9",
      "duration": 5
    }
  }'

# Query task result (using the returned task_id)
curl -X POST "https://api.xskill.ai/api/v3/tasks/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{"task_id": "your-task-id"}'
```

### Python Example

```python
import requests
import time

url = "https://api.xskill.ai/api/v3/tasks/create"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-your-api-key"
}

# Omni Reference mode: image + video
payload = {
    "model": "st-ai/super-seed2",
    "params": {
        "model": "seedance_2.0_fast",
        "prompt": "@image_file_1 character performs following @video_file_1 motion and camera style, cinematic lighting",
        "functionMode": "omni_reference",
        "image_files": [
            "https://your-character-image.png"
        ],
        "video_files": [
            "https://your-reference-video.mp4"
        ],
        "ratio": "16:9",
        "duration": 5
    }
}

# Create task
response = requests.post(url, json=payload, headers=headers)
result = response.json()
print("Task created:", result)

# Get task_id
task_id = result["data"]["task_id"]

# Poll for task result
query_url = "https://api.xskill.ai/api/v3/tasks/query"
while True:
    query_response = requests.post(query_url, json={"task_id": task_id}, headers=headers)
    query_result = query_response.json()
    status = query_result["data"]["status"]
    print(f"Task status: {status}")

    if status == "completed":
        video_url = query_result["data"]["result"]["output"]["images"][0]
        print(f"Video URL: {video_url}")
        break
    elif status == "failed":
        print("Task failed")
        break

    time.sleep(5)  # Poll every 5 seconds
```

### JavaScript Example

```javascript
const API_KEY = "sk-your-api-key";
const BASE_URL = "https://api.xskill.ai";

// Create task (Omni Reference mode)
async function createTask() {
  const response = await fetch(`${BASE_URL}/api/v3/tasks/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      model: "st-ai/super-seed2",
      params: {
        model: "seedance_2.0_fast",
        prompt: "@image_file_1 character performs following @video_file_1 motion and camera style, cinematic lighting",
        functionMode: "omni_reference",
        image_files: [
          "https://your-character-image.png"
        ],
        video_files: [
          "https://your-reference-video.mp4"
        ],
        ratio: "16:9",
        duration: 5
      }
    })
  });

  const result = await response.json();
  console.log("Task created:", result);
  return result.data.task_id;
}

// Query task result
async function queryTask(taskId) {
  const response = await fetch(`${BASE_URL}/api/v3/tasks/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify({ task_id: taskId })
  });

  return await response.json();
}

// Main flow: create and poll
async function main() {
  const taskId = await createTask();

  while (true) {
    const result = await queryTask(taskId);
    const status = result.data.status;
    console.log(`Task status: ${status}`);

    if (status === "completed") {
      console.log("Video URL:", result.data.result.output.images[0]);
      break;
    } else if (status === "failed") {
      console.log("Task failed");
      break;
    }

    await new Promise(resolve => setTimeout(resolve, 5000)); // Poll every 5 seconds
  }
}

main();
```

### Response Format

**Task created successfully:**

```json
{
  "code": 200,
  "data": {
    "task_id": "task_xxx",
    "price": 10
  }
}
```

**Task query result:**

```json
{
  "code": 200,
  "data": {
    "status": "completed",
    "result": {
      "output": {
        "images": [
          "https://your-video-output-url.mp4"
        ]
      }
    }
  }
}
```

> **Status values:** `pending` (queued), `processing` (in progress), `completed` (done), `failed` (error)

---

## MCP Integration

Seedance 2.0 supports invocation via MCP (Model Context Protocol) directly in AI editors, without writing API code manually.

### Option 1: One-click Install

Copy and run the command below in your terminal to automatically configure the MCP environment:

**Mac / Linux:**

```bash
curl -fsSL https://api.xskill.ai/install-mcp.sh | bash -s -- YOUR_API_KEY
```

**Windows (PowerShell):**

```powershell
irm https://api.xskill.ai/install-mcp.ps1 | iex
```

### Option 2: Manual Editor Configuration

#### Cursor Configuration

1. Open Cursor Settings (`Cmd/Ctrl + ,`)
2. Search for "MCP" and enable the MCP feature
3. Create a `.cursor/mcp.json` file in the project root
4. Paste the following configuration:

```json
{
  "mcpServers": {
    "xskill-ai": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-client",
        "https://api.xskill.ai/api/v3/mcp-http"
      ],
      "env": {
        "XSKILL_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

#### Claude Desktop Configuration

Add the same MCP server configuration in Claude Desktop settings.

### MCP HTTP Endpoint

To call the MCP HTTP endpoint directly:

```
GET https://api.xskill.ai/api/v3/mcp-http
Authorization: Bearer YOUR_API_KEY
```

### MCP Usage

Once configured, simply chat in the AI editor to use it:

> **User:** Generate a video using st-ai/super-seed2
>
> **Agent:** Sure, I'll call st-ai/super-seed2 to generate the video...

**Tips:**
- MCP automatically identifies model capabilities and calls the corresponding tools
- No need to manually pass parameters — the Agent extracts them intelligently
- Supports multi-turn conversations for iterative refinement

---

## MCP + Cursor Skills: AI-Powered Storyboard Creation

Beyond calling the API directly via MCP, you can install **Cursor Skills** to let the AI Agent automate the entire workflow from idea to finished video — no manual coding or parameters required.

### What are Cursor Skills?

Cursor Skills are reusable AI workflow templates for the Cursor editor. Once installed, the AI Agent automatically recognizes your intent and guides you through a professional storyboarding process:

```
Your Idea → Info Gathering → Storyboard Design → Generate Reference Images → Build Prompt → Submit Video Task → Poll Results → Return Video
```

### Install the Skill

**Option 1: One-command install via skills.sh (recommended)**

Run in your **project root** directory. The skill will be installed to `.cursor/skills/seedance2-api/` automatically:

```bash
npx skills add hexiaochun/seedance2-api
```

The CLI will prompt you to select target agents (Cursor, Claude Code, Windsurf, etc.). Use `--yes` to skip prompts:

```bash
npx skills add hexiaochun/seedance2-api --yes
```

> Browse on skills.sh: [hexiaochun/seedance2-api](https://skills.sh/hexiaochun/seedance2-api/seedance2-api)

**Option 2: One-command install via agentskill.sh**

Type in your Cursor / Claude Code chat:

```
/learn @hexiaochun/seedance2-api
```

> Browse on agentskill.sh: search [seedance2-api](https://agentskill.sh/q/seedance2-api)

**Option 3: Clone the repository**

```bash
# Clone this repo
git clone https://github.com/hexiaochun/seedance2-api.git

# Copy the skill to your project
cp -r seedance2-api/.cursor/skills/seedance2-api/ your-project/.cursor/skills/seedance2-api/
```

**Option 4: Manual setup**

Create a `.cursor/skills/seedance2-api/` directory in your project and copy `SKILL.md`, `reference.md`, and `scripts/` from this repo into it.

> **Prerequisites:** Cursor editor installed, MCP configured (see "MCP Integration" section above) or set `XSKILL_API_KEY` env var for script fallback mode. Xskill AI account with sufficient credits.

### How to Use

Once configured, simply describe your creative idea in natural language within Cursor:

```
User: Create a 15-second sci-fi clip of an astronaut walking on Mars

Agent automatically:
1. Gathers info (duration, aspect ratio, style, available assets)
2. Generates astronaut and Mars landscape reference images with Seedream 4.5
3. Builds professional storyboard prompts (timeline + camera language + sound design)
4. Submits Seedance 2.0 video generation task
5. Polls and returns the generated video
```

### Full Workflow

| Step | Description | Model/Tool |
|------|-------------|------------|
| Info Gathering | Collect duration, aspect ratio, style, assets | Agent conversation |
| Reference Image Generation | Generate character, scene, first/last frame images | Seedream 4.5 (text-to-image / image editing) |
| Storyboard Construction | Write professional shot list with timeline | Built-in storyboard templates |
| Video Generation | Submit final prompt and assets | Seedance 2.0 |
| Result Retrieval | Auto-poll task status | MCP get_task |

### Conversation Example

```
User: Make a 15-second high-end coffee brand commercial

Agent: Sure! Let me confirm a few details:
  - Aspect ratio: 16:9 recommended for landscape ads
  - Do you have existing product photos?
  - Brand name and slogan?

User: 16:9, no existing photos, brand is Lucky Coffee

Agent:
  1. Generating coffee cup close-up and brand scene images with Seedream 4.5...
  2. Images ready. Building storyboard:
     0-3s: Macro close-up, coffee slowly pouring into cup, steam rising
     3-6s: Medium orbit shot, hand holding coffee cup, sunlight on table
     6-10s: Push into coffee beans, a single bean falling from above
     10-12s: Black screen transition
     12-15s: Brand text fades in "Lucky Coffee"
  3. Submitting Seedance 2.0 video task...
  4. Video generating, estimated 10 minutes...
  5. Video complete! [Video URL]
```

### Supported Creative Scenarios

| Scenario | Description | Example |
|----------|-------------|---------|
| Narrative Story | Emotional shorts, micro-films | "A heartwarming story of a man coming home" |
| Product Commercial | Brand promotion, e-commerce video | "15-second coffee brand ad" |
| Character Action | Martial arts, sci-fi, dance | "Wuxia-style sword duel" |
| Scenic Travel | Nature, cityscape, travel vlog | "Sunset beach walk" |
| Video Extension | Continue from an existing video | "Extend this video by 10 seconds" |
| Plot Twist | Modify an existing video's story | "Change the ending to a plot twist" |
| Creative Transition | Multi-scene traversal | "Sci-fi world portal transitions" |
| First/Last Frames | Control start and end frames | "Sunrise to sunset time-lapse" |

> **Tip:** The Skill includes rich storyboard templates (narrative, product, action, scenic, etc.) and a camera movement glossary. The Agent automatically selects the best-fitting template for your needs.

---

## Use Cases

### Case 1: Character Motion Transfer (Omni Reference — Image + Video)

Make the character in an image perform actions following a reference video's motion and camera style.

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 character performs following @video_file_1 motion and camera style, cinematic lighting",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "video_files": ["https://your-reference-video.mp4"],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### Case 2: Single Image to Video (Omni Reference)

Generate a dynamic video from a single image.

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 character walks slowly through a forest, sunlight filters through leaves casting dappled shadows, breeze gently moves hair",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "ratio": "9:16",
    "duration": 8
  }
}
```

### Case 3: First/Last Frame Video

Generate a video that transitions from a first frame image to a last frame image.

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "Smooth cinematic transition, elegant camera movement, natural lighting changes",
    "functionMode": "first_last_frames",
    "filePaths": [
      "https://your-first-frame.png",
      "https://your-last-frame.png"
    ],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### Case 4: Audio-driven Lip Sync (Omni Reference — Image + Audio)

```json
{
  "model": "st-ai/super-seed2",
  "params": {
    "prompt": "@image_file_1 character speaks naturally, matching @audio_file_1 content with expressive lip sync",
    "functionMode": "omni_reference",
    "image_files": ["https://your-character-image.png"],
    "audio_files": ["https://your-audio-file.mp3"],
    "ratio": "16:9",
    "duration": 5
  }
}
```

### More Examples

| Scenario | Prompt Example | Function Mode | Input Assets |
|----------|---------------|---------------|--------------|
| Motion transfer | `@image_file_1 character performs following @video_file_1 actions` | omni_reference | image_files + video_files |
| Single image animation | `@image_file_1 character slowly turns head and smiles, breeze moves hair` | omni_reference | image_files |
| Multi-character interaction | `@image_file_1 and @image_file_2 two characters talking face to face` | omni_reference | image_files |
| Audio-driven lip sync | `@image_file_1 character speaks, matching @audio_file_1 content` | omni_reference | image_files + audio_files |
| Scene transition | `Smooth transition from @image_file_1 scene to @image_file_2 scene` | omni_reference | image_files |
| First/last frame | `Cinematic transition from start to end` | first_last_frames | filePaths |
| Text-to-video | `A sunset over the ocean, waves gently crashing` | first_last_frames | (none) |

---

## Links

- [Xskill AI Website](https://www.xskill.ai)
- [Seedance 2.0 Model Page](https://www.xskill.ai/#/v2/models?model=st-ai%2Fsuper-seed2)
- [API Key Management](https://www.xskill.ai/#/v2/api-key)
- [Task List](https://www.xskill.ai/#/v2/tasks)

## License

MIT
