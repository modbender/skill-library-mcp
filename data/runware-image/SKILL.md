---
name: runware-image
version: 1.0.0
author: Shobhit Kumar Prabhakar
description: Generate high-quality images on-demand via the Runware.ai API. This skill is the default image generator. Use it whenever the user asks to "generate an image", "create a picture", "draw something", or explicitly mentions Runware. It handles text-to-image generation with comprehensive safety checks.
---

Runware Image Skill

Purpose

Provide a secure, documented, and testable integration for generating images via the Runware.ai Image Inference API.

IMPORTANT INSTRUCTIONS FOR AGENT:
1. **Do NOT ask the user for the RUNWARE_API_KEY.** The script automatically loads it from the `.env` file in the skill directory.
2. **Do NOT ask clarifying questions** (style, size, etc.) unless the user's prompt is extremely vague. For requests like "generate a man on the moon", use your best judgment for the prompt and run the script immediately.
3. **Execute the script directly.** Do not propose it.

What it does

- Send text-to-image tasks to Runware's task API (imageInference).
- Support synchronous (sync) responses returning base64 image data and asynchronous workflows (webhook/polling) if required.
- Save generated images to the user's Downloads folder by default.
- Validate prompts for common safety issues (e.g., minors) before sending requests.

Included files

- scripts/generate_image.py — Primary CLI script (Python 3.8+). Reads RUNWARE_API_KEY from environment, supports sync mode, size/format options, and output filename.
- skill-config.json — default parameters (no secrets). Contains default_size and default_format.
- SKILL.md — this metadata and usage file.

Security & secrets

- DO NOT commit API keys. This skill requires RUNWARE_API_KEY to be provided via the environment when executed (export RUNWARE_API_KEY=...) or via a secure secret manager.
- The packaged version uploaded to ClawHub must not include any API keys. Before publishing, confirm skill-config.json contains NO sensitive values.
- The script performs simple prompt filtering; users should still follow platform content policies.

Usage (CLI)

1. Install dependencies
   - pip install -r requirements.txt
   (The script uses requests and python-dotenv; keep requirements minimal.)

2. Set your Runware API key. You can create a `.env` file in the skill directory:
   `RUNWARE_API_KEY=your_key_here`
   Or set it in your environment:
   $env:RUNWARE_API_KEY = "<YOUR_KEY>"

3. Run the script (sync mode):
   python scripts/generate_image.py --prompt "A photorealistic adult portrait (age 25)" --sync --outfile "my_image.png"

4. For non-sync workflows, omit --sync and implement webhook handling or polling as described in the Runware docs.

Configuration

- skill-config.json fields:
  - default_size: e.g. "1024x1024"
  - default_format: e.g. "png"

Packaging & publishing (ClawHub)

Checklist before publishing:
- Remove any plaintext API keys from skill-config.json (already removed).
- Add a short one-line license (MIT recommended) in LICENSE file.
- Add a small tests/ directory with a smoke test that verifies parsing logic and saved file behavior using temporary directories. Tests may require RUNWARE_API_KEY for live integration or can be skipped in CI if secrets are not provided.
- Ensure SKILL.md frontmatter (name + description) is accurate and includes trigger phrases.
- Provide example prompts and recommended safety guidance in SKILL.md.

Suggested repository structure

runware-image/
├── SKILL.md
├── skill-config.json
├── scripts/
│   └── generate_image.py
├── requirements.txt
├── LICENSE
└── tests/
    └── test_generate_image.py

Tests and CI

- Include a minimal pytest-based test that stubs requests.post and verifies parsing logic and saved file behavior using temporary directories.
- Add GitHub Actions workflow (optional) that runs tests on push.

Contribution & support

- Include a short CONTRIBUTING.md describing how to run tests, where to report issues, and how to add features (e.g., support for ControlNet, LoRA, or custom models).
- Provide an examples/ folder with 2–3 example prompts and expected CLI commands.

Licensing

- Recommend MIT license for public sharing unless you prefer another OSI-approved license.

Privacy and usage notes

- Make it explicit that the skill does not collect or store user prompts or keys on the server. All generation is performed using the user's Runware account.
- Recommend users review Runware's terms and ensure they have rights to generate/host the requested imagery.
