# Changelog

All notable changes to the ProductAI skill will be documented in this file.

## [1.2.0] - 2026-02-24

### Updated
- **API Reference Documentation** — Complete rewrite of `references/API.md` with official ProductAI API endpoints
- Added detailed documentation for `/api/generate` endpoint with all parameters
- Added `/api/job/:jobId` polling endpoint documentation
- Added `/api/upscale` endpoint details
- Added `/api/generate-custom-model` endpoint for custom model support
- Added `/api/key-check` endpoint for API key validation
- Documented new models: `kontext-max`, updated pricing table
- Added `aspect_ratio` parameter support with extended ratio options for nanobanana/nanobananapro
- Added `resolution` parameter documentation (1K/2K/4K) for nanobanana models
- Improved error handling documentation with specific error codes
- Added best practices section for async workflows and rate limiting

### Technical Details
- Models now include: `gpt-low`, `gpt-medium`, `gpt-high`, `kontext-pro`, `kontext-max`, `nanobanana`, `nanobananapro`, `seedream`
- Rate limit: 15 requests per minute per IP
- Multi-image support: up to 2 images with `nanobanana`, `nanobananapro`, `seedream`
- Output formats: PNG (default), JPG/JPEG
- Aspect ratios: Standard (SQUARE/LANDSCAPE/PORTRAIT) + extended ratios for nano models

## [1.1.0] - 2026-02-23

### Added
- Initial release with core functionality
- Image generation with multiple model support
- Image upscaling support
- Multi-image compositing (up to 2 images)
- Async job polling
- Setup wizard for API key configuration
- Comprehensive documentation and examples

### Features
- `generate_photo.py` — Generate AI product photos
- `upscale_image.py` — Upscale images with Magnific AI
- `batch_generate.py` — Batch processing support
- `setup.py` — Interactive setup wizard
