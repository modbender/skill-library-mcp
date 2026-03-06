###### WIP Computer
# wip-grok

xAI Grok API. Search the web, search X, generate images, generate video. All from one module.

**Sensor:** search_web, search_x ... turns questions into knowledge.
**Actuator:** generate_image, edit_image, generate_video ... turns prompts into media.

Zero dependencies. Four interfaces: CLI, Module, MCP Server, Skill.

## Install

Open your AI coding tool and say:

```
Clone wipcomputer/wip-grok and read the README and SKILL.md.
Then explain to me:
1. What is this tool?
2. What does it do?
3. What would it change or fix in our current system?

Then ask me if I have more questions, or if I want you to integrate it into our system.
```

Your agent will read the repo, explain the tool, and walk you through integration interactively.

### API Key

Get your xAI API key from https://console.x.ai/

The tool resolves your key automatically:

1. **1Password** (preferred) ... `op://Agent Secrets/X API/api key`. No env vars needed.
2. **Environment variable** ... `export XAI_API_KEY="your-key"` as a fallback.

## Usage

### CLI

```bash
# Search (sensor)
wip-grok search-web "latest AI regulation developments"
wip-grok search-x "what people are saying about OpenAI"
wip-grok search-x "AI thoughts" --handles=elonmusk,kaboré --from=2026-01-01

# Image generation (actuator)
wip-grok imagine "a cat in space, photorealistic" --output=cat.png
wip-grok imagine "minimalist logo" --aspect=16:9 --n=4

# Image editing (actuator)
wip-grok edit "make the sky purple" --image=photo.jpg --output=edited.jpg

# Video generation (actuator)
wip-grok video "a sunset timelapse over the ocean" --duration=10 --resolution=720p --wait
wip-grok video "animate this image" --image=photo.jpg --output=animated.mp4

# Check video status
wip-grok video-status abc123
```

### As a Module

```javascript
import { search_web, search_x, generate_image, generate_video, wait_for_video } from '@wipcomputer/wip-grok';

// Sensor: search
const web = await search_web({ query: "UN climate summit" });
console.log(web.content);
console.log(web.citations);

const x = await search_x({
  query: "AI regulation",
  allowed_x_handles: ["elonmusk"],
  from_date: "2026-01-01",
});

// Actuator: generate
const img = await generate_image({ prompt: "a red cube on white", aspect_ratio: "1:1" });
console.log(img.images[0].url);

const vid = await generate_video({ prompt: "spinning globe", duration: 5 });
const result = await wait_for_video({ request_id: vid.request_id });
console.log(result.url);
```

### MCP Server

Add to your `.mcp.json`:

```json
{
  "wip-grok": {
    "command": "node",
    "args": ["/path/to/wip-grok/mcp-server.mjs"]
  }
}
```

Exposes 6 tools: grok_search_web, grok_search_x, grok_imagine, grok_edit_image, grok_generate_video, grok_poll_video.

## Functions

### Sensor (Search)

| Function | What | Endpoint |
|----------|------|----------|
| `search_web` | Web search via Grok | POST /v1/responses (web_search tool) |
| `search_x` | X/Twitter search via Grok | POST /v1/responses (x_search tool) |

### Actuator (Generate)

| Function | What | Endpoint | Cost |
|----------|------|----------|------|
| `generate_image` | Text to image | POST /v1/images/generations | $0.02/image |
| `edit_image` | Edit image with text | POST /v1/images/edits | $0.022/image |
| `generate_video` | Text/image to video | POST /v1/video/generations | $0.05-0.07/sec |
| `poll_video` | Check video status | GET /v1/video/generations/:id | free |
| `wait_for_video` | Poll until complete | (convenience wrapper) | free |

## Attribution

Search functions ported from [castanley/grok v1.0.3](https://clawhub.ai/castanley/grok) by Christopher Stanley on [ClawHub](https://clawhub.ai).

---

## License

MIT

Built by Parker Todd Brooks, with Claude Code and Lēsa (OpenClaw).
