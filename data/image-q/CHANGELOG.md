# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-02-26

### Fixed
- **SDXL endpoint**: Updated from deprecated `fal-ai/lightning-models/sdxl-lightning-4step` (404 Not Found) to `fal-ai/fast-sdxl`. All 8 models now pass integration tests.

### Added
- **image-gen-proxy**: New Vercel serverless proxy at `services/image-gen-proxy/`. Users can generate images without any API keys (50 free fal.ai / 20 free Midjourney generations per IP).
  - `POST /api/generate` — fal.ai models (Flux, SDXL, Ideogram, Recraft, Nano Banana)
  - `POST /api/midjourney` — Midjourney via Legnext.ai (imagine, upscale, variation, poll)
  - `GET /api/health` — Health check and model registry
- **generate.js proxy mode**: Added `--proxy` flag and `IMAGE_GEN_PROXY_URL` env var support. When set, the script routes requests through the proxy instead of calling APIs directly.

---

## [1.3.0] - 2026-02-25

### Added
- **Non-blocking async mode for Midjourney** (`--async` flag). Submit a job and return immediately with `job_id`, without waiting for completion. This prevents the bot from being blocked while waiting for image generation.
- **Status poll mode** (`--poll --job-id <id>`). Check job status once and return immediately — no waiting. Returns `status: "completed"`, `"pending"`, `"processing"`, or `"failed"`.
- Updated SKILL.md with mandatory async workflow documentation. All Midjourney requests should now use `--async` + periodic `--poll` to avoid blocking the bot.

### Changed
- `--async` flag is supported for all Midjourney actions: `imagine`, `upscale`, `variation`, `reroll`.

---

## [1.2.0] - 2026-02-25

### Changed
- **Midjourney Turbo mode enabled by default.** The `--turbo` flag is now automatically appended to all Midjourney prompts, reducing generation time from ~30-60s to ~10-20s (requires Midjourney Pro or Mega subscription).
- Added `--mode` parameter: `turbo` (default), `fast`, `relax`.

---

## [1.1.0] - 2026-02-25

### Changed
- **Midjourney provider switched from TTAPI to Legnext.ai** for faster generation speed and higher stability.
- Environment variable renamed from `TTAPI_KEY` to `LEGNEXT_KEY`. Please update your OpenClaw config.
- Upscale now supports `--upscale-type` parameter: `0` = Subtle (default), `1` = Creative.
- Variation now supports `--variation-type` parameter: `0` = Subtle (default), `1` = Strong.
- Added `--action reroll` support for Midjourney.
- Added `--action describe` support for Midjourney.
- Response now includes `imageUrls` array (4 individual image URLs) in addition to the grid `imageUrl`.

### Migration Guide
If you were using `TTAPI_KEY`, please:
1. Register at [legnext.ai](https://legnext.ai) and get your API key.
2. Update `~/.openclaw/openclaw.json`: rename `TTAPI_KEY` to `LEGNEXT_KEY` and set your new key.

---

## [1.0.0] - 2026-02-25

### Added
- Initial release of the unified image generation skill.
- **Midjourney** support via TTAPI (imagine, upscale U1-U4, variation V1-V4, reroll, zoom, pan).
- **Flux 1.1 Pro** support via fal.ai (`fal-ai/flux-pro/v1.1`).
- **Flux Dev** support via fal.ai (`fal-ai/flux/dev`).
- **Flux Schnell** support via fal.ai (`fal-ai/flux/schnell`).
- **SDXL Lightning** support via fal.ai (`fal-ai/lightning-models/sdxl-lightning-4step`).
- **Nano Banana Pro** (Gemini-powered) support via fal.ai (`fal-ai/nano-banana-pro`).
- **Ideogram v3** support via fal.ai (`fal-ai/ideogram/v3`).
- **Recraft v3** support via fal.ai (`fal-ai/recraft-v3`).
- Aspect ratio support: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `21:9`.
- Multi-image generation support (1-4 images per request).
- Negative prompt support for fal.ai models.
- Seed parameter support for reproducible results.
- Automatic job polling for Midjourney tasks (up to 5 minutes).
- Published to ClawHub as `wells1137/image-gen@1.0.0`.
