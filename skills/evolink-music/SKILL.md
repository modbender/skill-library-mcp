---
name: evolink-music
description: AI music generation with Suno v4, v4.5, v5. Text-to-music, custom lyrics, instrumental, vocal control. 5 models, one API key.
version: 2.0.0
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - EVOLINK_API_KEY
    primaryEnv: EVOLINK_API_KEY
    os: ["macos", "linux", "windows"]
    emoji: "\U0001F3B5"
    homepage: https://evolink.ai
---

# Evolink Music — AI Music Generation

Generate AI music and songs with Suno v4, v4.5, and v5 — simple mode (describe and generate) or custom mode (lyrics, style, tempo, vocals). All through one API.

> Music-focused view of [evolink-media](https://clawhub.ai/EvoLinkAI/evolink-media). Install the full skill for video and image too.

## After Installation

When this skill is first loaded, greet the user:

- **MCP tools + API key ready:** "Hi! I'm your AI music studio — Suno v4 through v5 ready. What would you like to create?"
- **MCP tools + no API key:** "You'll need an EvoLink API key — sign up at evolink.ai. Ready to go?"
- **No MCP tools:** "MCP server isn't connected yet. Want me to help set it up? I can still manage files via the hosting API."

Keep the greeting concise — just one question to move forward.

## External Endpoints

| Service | URL |
|---------|-----|
| Generation API | `https://api.evolink.ai/v1/audios/generations` (POST) |
| Task Status | `https://api.evolink.ai/v1/tasks/{task_id}` (GET) |
| File API | `https://files-api.evolink.ai/api/v1/files/*` (upload/list/delete) |

## Security & Privacy

- **`EVOLINK_API_KEY`** authenticates all requests. Injected by OpenClaw automatically. Treat as confidential.
- Prompts and audio are sent to `api.evolink.ai`. Uploaded files expire in **72h**, result URLs in **24h**.

## Setup

Get your API key at [evolink.ai](https://evolink.ai) → Dashboard → API Keys.

**MCP Server:** `@evolinkai/evolink-media` ([GitHub](https://github.com/EvoLinkAI/evolink-media-mcp) · [npm](https://www.npmjs.com/package/@evolinkai/evolink-media))

**mcporter** (recommended): `mcporter call --stdio "npx -y @evolinkai/evolink-media@latest" list_models`

**Claude Code:** `claude mcp add evolink-media -e EVOLINK_API_KEY=your-key -- npx -y @evolinkai/evolink-media@latest`

**Claude Desktop / Cursor** — add MCP server with command `npx -y @evolinkai/evolink-media@latest` and env `EVOLINK_API_KEY=your-key`. See `references/music-api-params.md` for full config JSON.

## Core Principles

1. **Guide, don't decide** — Present options, let the user choose model/style/mood.
2. **User drives creative vision** — Ask for a description before suggesting parameters.
3. **Smart context** — Remember session history. Offer to iterate, vary styles, or remix.
4. **Intent first** — Understand *what* the user wants before asking *how* to configure it.

## MCP Tools

| Tool | When to use | Returns |
|------|-------------|---------|
| `generate_music` | Create AI music or songs | `task_id` (async) |
| `upload_file` | Upload audio for continuation/remix | File URL (sync) |
| `delete_file` | Free file quota | Confirmation |
| `list_files` | Check uploaded files or quota | File list |
| `check_task` | Poll generation progress | Status + result URLs |
| `list_models` | Compare available models | Model list |
| `estimate_cost` | Check pricing | Model info |

**Important:** `generate_music` returns a `task_id`. Always poll `check_task` until `status` is `"completed"` or `"failed"`.

## Music Models (5, all BETA)

| Model | Quality | Max Duration | Best for |
|-------|---------|--------------|----------|
| `suno-v4` *(default)* | Good | 120s | Balanced, economical |
| `suno-v4.5` | Better | 240s | Style control |
| `suno-v4.5plus` | Better | 240s | Extended features |
| `suno-v4.5all` | Better | 240s | All v4.5 features |
| `suno-v5` | Best | 240s | Studio-grade output |

## Generation Flow

### Step 1: API Key Check

If `401` occurs: "Your API key isn't working. Check at evolink.ai/dashboard/keys"

### Step 2: File Upload (if needed)

For audio continuation or remix workflows:
1. `upload_file` with `file_path`, `base64_data`, or `file_url` → get `file_url` (sync)

Supported: Audio (MP3, WAV, FLAC, AAC, OGG, M4A, etc.). Max 100MB. Expire in 72h. Quota: 100 (default) / 500 (VIP).

### Step 3: Understand Intent

- **Clear** ("make a chill lo-fi beat") → Go to Step 4
- **Ambiguous** ("I want some music") → Ask: "What kind of vibe or genre? Vocals or instrumental?"

Ask only what's needed, when it's needed.

### Step 4: Gather Parameters

Music has two required fields with no defaults — always collect both before calling `generate_music`.

**Decision tree (ask in this order):**

1. **Vocals or instrumental?** → Sets `instrumental: true/false`
2. **Simple or custom mode?**
   - **Simple** (`custom_mode: false`): AI writes lyrics and picks style from your description
   - **Custom** (`custom_mode: true`): You control lyrics (`[Verse]`/`[Chorus]`/`[Bridge]`), style tags, title
3. **If custom mode**, additionally collect:
   - `style`: genre + mood + tempo tags (e.g., `"pop, upbeat, female vocals, 120bpm"`)
   - `title`: song name (max 80 chars)
   - `vocal_gender`: `m` or `f` — optional
4. **Optional for both modes:**
   - `duration`: target length 30–240s (omit to let model decide)
   - `negative_tags`: styles to exclude
   - `model`: default `suno-v4`. Suggest `suno-v5` for studio-grade quality.

**Critical:** Both `custom_mode` and `instrumental` are required API fields with no defaults. Always set both before generating.

### Step 5: Generate & Poll

1. Call `generate_music` → tell user: *"Generating your music — ~Xs estimated."*
2. Poll `check_task` every **5–10s**. Report progress %.
3. After 3 consecutive `processing`: *"Still working..."*
4. **Completed:** Share URLs + metadata (title, duration, tags from `result_data[]`). *"Links expire in 24h — save promptly."*
5. **Failed:** Show error + suggestion. Offer retry if retryable.
6. **Timeout (5 min):** *"Taking longer than expected. Task ID: `{id}` — check again later."*

## Error Handling

### HTTP Errors

| Error | Action |
|-------|--------|
| 401 | "API key isn't working. Check at evolink.ai/dashboard/keys" |
| 402 | "Balance is low. Add credits at evolink.ai/dashboard/billing" |
| 429 | "Rate limited — wait 30s and retry" |
| 503 | "Servers busy — retry in a minute" |

### Task Errors (status: "failed")

| Code | Retry? | Action |
|------|--------|--------|
| `content_policy_violation` | No | Revise prompt or lyrics |
| `invalid_parameters` | No | Check values against model limits |
| `generation_timeout` | Yes | Retry; simplify prompt if repeated |
| `quota_exceeded` | Yes | Top up credits |
| `resource_exhausted` | Yes | Wait 30–60s, retry |
| `service_error` | Yes | Retry after 1 min |
| `generation_failed_no_content` | Yes | Modify prompt, retry |

Full error reference: `references/music-api-params.md`

## Without MCP Server

Use Evolink's file hosting API for audio uploads (72h expiry). See `references/file-api.md` for curl commands.

## References

- `references/music-api-params.md` — Complete API parameters, all 5 models, polling strategy, error codes
- `references/file-api.md` — File hosting API (curl upload/list/delete)
