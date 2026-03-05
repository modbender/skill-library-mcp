# Soundside — OpenClaw Skill

Connect your OpenClaw agent to Soundside's 12 MCP tools for AI media generation, editing, and analysis.

## Setup

Add to your `openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "soundside": {
        "enabled": true,
        "env": {
          "SOUNDSIDE_API_KEY": "mcp_your_key_here"
        }
      }
    }
  },
  "mcpServers": {
    "soundside": {
      "transport": "streamable-http",
      "url": "https://mcp.soundside.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${SOUNDSIDE_API_KEY}"
      }
    }
  }
}
```

Then restart: `openclaw gateway restart`

## What You Get

Once connected, your agent has access to:

### Generation (6 tools)
- `create_image` — Text-to-image across 5 providers (Vertex AI, Grok, Runway, MiniMax, Luma)
- `create_video` — Text/image-to-video across 5 providers (Vertex Veo 3.1, Runway, MiniMax, Luma, Grok)
- `create_audio` — TTS, transcription, voice cloning (MiniMax, Vertex AI)
- `create_music` — Music from lyrics + style prompt (MiniMax)
- `create_text` — LLM completions with structured output (Vertex Gemini, Grok, MiniMax)
- `create_artifact` — Charts, presentations, documents, diagrams

### Editing & Analysis (2 tools)
- `edit_video` — 21 editing actions: trim, concat, Ken Burns, mix audio, text overlays, color grading, film grain, split screen, and more
- `analyze_media` — Technical analysis + AI vision QA scoring

### Library (3 tools)
- `lib_list` — Browse projects, collections, resources
- `lib_manage` — Create/update/delete library entities
- `lib_share` — Share projects by email

## Durable Resource Pattern

Every generation returns a `resource_id` that persists across sessions:

1. Generate media → receive `resource_id`
2. Chain into editing: `edit_video(resource_id=..., action="add_text", ...)`
3. Organize: `lib_manage(entity_type="project", operation="create", ...)`
4. Check status: `lib_list(entity_type="resources", resource_id=...)`
5. Download only for final delivery

This keeps workflow state durable without local storage.

## Example Workflows

**Generate and edit an image:**
```
"Create an image of a sunset over the ocean using Vertex AI,
 then add the text 'Golden Hour' as a title overlay"
```

**Produce a narrated video:**
```
"Generate a video of waves crashing using Luma,
 create TTS narration saying 'The ocean calls to those who listen',
 then mix the narration into the video"
```

**Build a presentation:**
```
"Create a pitch deck with 5 slides covering our Q1 metrics,
 include a revenue chart showing growth from $100K to $600K"
```

## Pricing

Live pricing: `GET https://mcp.soundside.ai/api/x402/status`

Soundside charges near-cost on provider pass-through (~10% margin). Editing and analysis are $0.01/call. A typical video pipeline (image → video → edit → analyze) costs $0.50-3.00 depending on provider.

## Docs

- [Getting Started](https://github.com/soundside-design/soundside-docs/blob/main/guides/getting-started.md)
- [Tool Reference](https://github.com/soundside-design/soundside-docs/blob/main/guides/tools.md)
- [x402 Pay-Per-Call](https://github.com/soundside-design/soundside-docs/blob/main/guides/x402.md)
