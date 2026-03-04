---
name: seisoai
description: Unified media generation gateway for agents. Discover tools dynamically, choose API key or x402 auth, invoke image/video/audio/music/3D/training tools, and handle queue jobs reliably.
metadata: {"openclaw":{"homepage":"https://seisoai.com","emoji":"🎨"}}
version: 1.1.1
last_synced: 2026-02-09
---

# Seisoai

Base URL: `https://seisoai.com`
Primary endpoint: `POST /api/gateway/invoke/{toolId}` or `POST /api/gateway/invoke` with `toolId` in body.
Auth: `X-API-Key` or x402 payment (USDC on Base).

## Agent-First Workflow (Do This Every Session)

1. Discover live tools:
   - `GET /api/gateway/tools`
2. For selected tools, fetch exact schema:
   - `GET /api/gateway/tools/{toolId}`
3. Optionally pre-price inputs:
   - `GET /api/gateway/price/{toolId}`
4. Invoke with API key or x402.
5. If queue tool, poll job status/result URLs from response.

Do not rely on static tool lists when a live registry is available.

## Auth Strategy

Use this decision order:

1. If you have a project API key, use `X-API-Key`.
2. If you do not have a key, use x402 pay-per-request.
3. Do not send browser CSRF tokens for machine clients.

### API Key Example

```http
POST /api/gateway/invoke/image.generate.flux-2
X-API-Key: sk_live_xxx
Content-Type: application/json

{"prompt":"a sunset over mountains"}
```

### x402 Example (2-step)

1. Call without payment header.
2. Receive `402` with payment requirements.
3. Sign/pay on Base.
4. Retry same request with one of:
   - `payment-signature`
   - `x-payment`
   - `payment`

## High-Value Endpoints

- Discovery:
  - `GET /api/gateway/tools`
  - `GET /api/gateway/tools/{toolId}`
  - `GET /api/gateway/price/{toolId}`
  - `GET /api/gateway/mcp-manifest`
- Invoke:
  - `POST /api/gateway/invoke/{toolId}`
  - `POST /api/gateway/invoke`
- Jobs:
  - `GET /api/gateway/jobs/{jobId}?model=...`
  - `GET /api/gateway/jobs/{jobId}/result?model=...`
- Agent-scoped:
  - `GET /api/gateway/agents`
  - `GET /api/gateway/agent/{agentId}`
  - `POST /api/gateway/agent/{agentId}/invoke/{toolId?}`
  - `POST /api/gateway/agent/{agentId}/orchestrate`

## Agent-Scoped Safety Controls (Mandatory)

For normal media generation (images, video, audio, 3D), use **`/api/gateway/invoke`** and the discovery endpoints above; no extra checks. The rules below apply only when the user explicitly asks to run or orchestrate a **specific agent** (e.g. a named bot or workflow).

Default posture: **deny by default** for agent-scoped routes (`/api/gateway/agent/*`). Use agent-scoped endpoints only when all checks pass:

1. **Explicit task requirement**
   - Do not call `/agent/*` routes unless the current task explicitly requires operating a specific agent.
2. **Exact agent binding**
   - Resolve `agentId` from a trusted source (`GET /api/gateway/agents` or user-provided exact ID).
   - Never infer or guess agent IDs from names/prompts.
3. **Authorization boundary**
   - Use only the current caller credentials.
   - Never attempt to reuse, escalate, or proxy credentials to access other tenants/owners.
4. **Single-agent scope**
   - For one task, operate on one approved `agentId` unless the user explicitly requests multi-agent execution.
5. **Tool allowlist enforcement**
   - Before invoke/orchestrate, fetch `GET /api/gateway/agent/{agentId}` and only use tool IDs declared for that agent.
   - Reject tool IDs not listed in that agent definition.
6. **No recursive orchestration**
   - Do not create self-referential orchestrations, orchestration loops, or fan-out patterns across unknown agents.
7. **No broad discovery exfiltration**
   - Do not enumerate all agents unless needed for user task; prefer direct lookup when `agentId` is known.
8. **Audit trail requirement**
   - Log `agentId`, route, tool ID, and reason for each agent-scoped call in agent run notes.
9. **On mismatch or ambiguity: stop**
   - If ownership/scope/tool authorization is ambiguous, do not call `/agent/*`; fall back to `/api/gateway/invoke`.

## Tool Selection Cheatsheet (Verified IDs)

### Images
- Fast text->image: `image.generate.flux-2`
- Premium cinematic: `image.generate.kling-image-v3`
- Premium consistency: `image.generate.kling-image-o3`
- 360/panorama: `image.generate.nano-banana-pro`
- Prompted edit: `image.generate.flux-pro-kontext-edit`
- Face swap: `image.face-swap`
- Inpaint/outpaint: `image.inpaint`, `image.outpaint`
- Background removal/layer: `image.extract-layer`
- Upscale: `image.upscale`

### Video
- Text->video (Veo): `video.generate.veo3`
- Image->video (Veo): `video.generate.veo3-image-to-video`
- First/last frame: `video.generate.veo3-first-last-frame`
- Kling text: `video.generate.kling-3-pro-text`, `video.generate.kling-3-std-text`
- Kling image: `video.generate.kling-3-pro-image`, `video.generate.kling-3-std-image`
- Motion transfer: `video.generate.dreamactor-v2`

### Audio / Speech / Music
- Voice clone TTS: `audio.tts`
- TTS quality tiers: `audio.tts.minimax-hd`, `audio.tts.minimax-turbo`
- Lip sync: `audio.lip-sync`
- Transcription: `audio.transcribe`
- Music: `music.generate`
- Sound FX: `audio.sfx`
- Stem separation: `audio.stem-separation`

### 3D
- Image->3D standard: `3d.image-to-3d`
- Image->3D pro: `3d.image-to-3d.hunyuan-pro`
- Text->3D pro: `3d.text-to-3d.hunyuan-pro`
- Fast image->3D: `3d.image-to-3d.hunyuan-rapid`
- Mesh post-processing: `3d.smart-topology`, `3d.part-splitter`

## Minimal Payload Patterns

Text->image:
```json
{"prompt":"..."}
```

Image edit:
```json
{"prompt":"...","image_url":"https://..."}
```

Text->video:
```json
{"prompt":"...","duration":"6s"}
```

DreamActor motion transfer:
```json
{"source_image_url":"https://...","driving_video_url":"https://..."}
```

Voice clone TTS:
```json
{"text":"...","audio_url":"https://..."}
```

3D image->mesh:
```json
{"image_url":"https://...","output_format":"glb"}
```

## Queue Handling Contract

If `executionMode` is `queue`, response includes job metadata. Use:

1. `statusUrl` until completed/failed.
2. `resultUrl` when completed.

Treat queue submit success as billable success (x402 settlement/API-key credit deduction already handled server-side).

## Error Policy

- `400`: Schema/input mismatch. Re-fetch tool schema and correct fields.
- `402`: Missing/invalid payment or insufficient API key credits.
- `404`: Tool/agent not found. Refresh registry.
- `503`: Tool disabled. Select fallback in same category.
- `500`: Retry with backoff; then switch model/tool.

## Reliability Rules for Agents

1. Always discover live tools before planning multi-step flows.
2. Use exact schema from `GET /tools/{toolId}` for required fields.
3. Keep one tool call per request; chain in your agent.
4. Prefer explicit model/tool IDs over natural-language routing assumptions.
5. For retries, do not reuse stale x402 signatures.
6. Treat `/api/gateway/agent/*` as privileged routes and apply the mandatory safety controls above.

## Self-Maintenance

When this file is updated:
- Keep IDs aligned with `backend/services/toolRegistry.ts`.
- Update `last_synced` and `version`.
- Keep examples minimal and executable.

## Changelog

- [2026-02-09] v1.1.1 - Added mandatory safety controls for agent-scoped endpoints (deny-by-default, agent/tool scoping, anti-recursion, and audit requirements).
- [2026-02-09] v1.1.0 - Rewrote for agent discovery-first flow, corrected stale tool IDs/params, tightened auth/x402 guidance, and added queue/error reliability policy.
- [2026-02-08] v1.0.0 - Initial self-improvement protocol added.
