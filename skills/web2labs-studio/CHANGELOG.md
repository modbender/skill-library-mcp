# Changelog

## Unreleased

## 1.0.1 - 2026-02-23

### Security
- Prevent leaking `WEB2LABS_API_KEY` to third-party artifact URLs by stripping auth headers on non-Web2Labs domains.
- Sanitize remote filenames to prevent path traversal and unsafe writes during `studio_download`.

### Fixed
- Align OpenClaw `skillKey` with setup writer so saved API key is correctly injected on future runs.
- Use deep merge for watch mode configuration overrides instead of shallow `Object.assign`.
- Collapse SKILL.md metadata to single-line JSON for OpenClaw parser compatibility.

### Added
- `studio_setup` tool for zero-touch onboarding (`send_magic_link`, `complete_setup`, `save_api_key`).
- Hardened auth-flow error handling (`invalid_code`, `key_already_exists`, rate-limit messaging).
- Revenue-aware tools: `studio_pricing`, `studio_estimate`, `studio_thumbnails`, and `studio_analytics`.
- `studio_rerender` for configuration-only rerenders of completed projects.
- Spend-policy enforcement for paid actions (`smart|explicit|auto`) with `confirm_spend` support.
- Checkout deep links (`ref=openclaw`) and recommendations in `studio_pricing` and `studio_credits` outputs.
- Preflight insufficient-credit detection with purchase-link hints for paid actions.
- `studio_brand` tool and API client support for `/api/v1/brand` (get/update brand kit settings).
- `studio_brand_import` tool and API client support for `/api/v1/brand/import` (preview/apply from YouTube/Twitch/X profile URLs).
- Upload webhook support (`webhook_url`, `webhook_secret`) for `project.completed` callbacks.
- `studio_assets` tool and API client support for `/api/v1/assets` (intro/outro/watermark list/upload/delete).
- `studio_watch` tool for monitoring YouTube/Twitch channels with auto-processing, retry tracking, and rate-limited uploads.
- `studio_referral` tool for referral code management and bonus credits.
- Contextual `next_steps` hints in tool responses for download, results, upload, credits, and setup.
- Dependency checks (Node.js version, yt-dlp availability) and trust/privacy block in `studio_setup` responses.
- Sandbox mode documentation in SKILL.md.

## 1.0.0 - 2026-02-21
- Initial OpenClaw Studio skill release.
- Added 9 core tools for upload, polling, results, download, credits, project management, and feedback.
- Added preset catalog and URL download support via yt-dlp.
