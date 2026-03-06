# Changelog

## [1.9.0] - 2026-02-18
### Changed
- Default OpenRouter model changed from `openai/gpt-5-image-mini` to `google/gemini-3-pro-image-preview` — better fallback when GLM API not present
- Margin guard relaxed: no longer mandates exact 80%/10% constraints; gives the model flexibility on dimensions while keeping comfortable margins
- Vertical layout recommended but not forced — long content benefits from tall format

## [1.8.0] - 2026-02-18
### Changed
- OpenRouter margin guard strengthened: from "5% margin / 50px" to "center 80% constraint with 10% empty border on all four sides" — more explicit instruction to prevent edge clipping on gpt-5-image-mini

## [1.7.0] - 2026-02-18
### Fixed
- OpenRouter: append margin guard instruction to every prompt — prevents content clipping at canvas edges (gpt-5-image-mini places labels/text flush against the edge with no padding)

## [1.6.0] - 2026-02-18
### Fixed
- OpenRouter response parsing: image URL was at `images[0]["image_url"]["url"]` (snake_case), not `imageUrl` (camelCase) — was crashing with KeyError on every generation
- Cost extraction: moved to `usage.cost` from main response body (immediate, no extra API call); generation endpoint kept as fallback only

## [1.5.0] - 2026-02-18
### Added
- Cost display at end of every run:
  - GLM: shows ¥ and ~$ from known pricing (¥0.10 standard / ¥0.20 HD) with console link
  - OpenRouter: fetches actual USD cost from `/api/v1/generation?id=<id>` endpoint; falls back to activity link
### Changed
- Default OpenRouter model: `google/gemini-2.5-flash-image-preview` → `openai/gpt-5-image-mini`
  (better text rendering for scrapbook-style prompts)

## [1.4.0] - 2026-02-18
### Added
- OpenRouter provider support: `--provider openrouter` uses `/api/v1/chat/completions`
  with `modalities: ["image"]`; returns base64 image decoded and saved locally
- `--provider` flag: auto-detects from available keys (GLM preferred); explicit override available
- `--model` flag: choose OpenRouter image model (default: google/gemini-2.5-flash-image-preview)
- `OPENROUTER_API_KEY` lookup in env, config.json (`openrouter_api_key`), and .env
- Setup section updated: two-provider docs with key registration links
- Step 0 now checks for either key; tells user both setup options if neither found

## [1.3.0] - 2026-02-18
### Added
- Setup section: documents all 4 key lookup locations with examples (env var, config.json, .env)
- Step 0 in Usage: agent checks for KEY_MISSING before proceeding, then tells user exactly how to configure in plain language (3 options with code examples)

## [1.2.0] - 2026-02-18
### Added
- Explicit language selection: `--language` flag (required) on `generate.py`
- Supported languages: zh, en, ja, ko, fr, de, es
- SKILL.md mandates asking the user for language choice before every generation — no defaulting, no inferring
- Language label printed in script output

## [1.1.0] - 2026-02-17
### Added
- skill.yml with display_name, attribution, triggers, permissions
- README.md
- Configuration section (GLM_API_KEY via TOOLS.md)
- Agent owner declaration
- Success criteria and edge cases
- Attribution to original author ViffyGwaanl
### Fixed
- Script now also checks ~/.openclaw/config.json for API key

## [1.0.0] - 2026-02-01
### Added
- Initial release by ViffyGwaanl
- generate.py with full GLM-Image API support
