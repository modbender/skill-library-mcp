# runware-image

Runware Image Skill - a small CLI skill to generate images on-demand via the Runware.ai Image Inference API.

This repository contains an OpenClaw-style skill that provides a Python CLI script to submit text-to-image tasks to Runware, save generated images locally, and includes tests, examples, and CI configuration to make the skill production-ready for publishing to ClawHub (or GitHub first).

## Features

- Submit text-to-image tasks to Runware's task API (imageInference).
- Default synchronous generation (returns base64 image data) with support for async/webhook workflows.
- Safe-by-default prompt validation to reduce the risk of generating images of minors.
- Default output directory: `~/runware_images` (created automatically). The script remembers the last used output directory.
- Minimal dependencies. Tests can be configured to run in CI with secrets for integration or skipped when no RUNWARE_API_KEY is present.

## Contents

- `SKILL.md` - Skill metadata and usage guidance (required by OpenClaw skills).
- `skill-config.json` - Default settings (no secrets). Contains `default_size`, `default_format`, and `default_output_dir`.
- `scripts/generate_image.py` - Primary CLI script (Python 3.8+).
- `requirements.txt` - Minimal dependencies.
- `tests/test_generate_image.py` - Pytest unit test that mocks Runware responses.
- `examples/` - Example CLI commands.
- `.github/workflows/ci.yml` - GitHub Actions CI workflow to run tests.
- `LICENSE`, `CONTRIBUTING.md` - Project metadata.

## Quick Start (GitHub)

1. Clone the repository:

  git clone <repo-url>
  cd runware-image

2. Create a Python virtual environment and install deps:

  python -m venv .venv
  source .venv/bin/activate # or .\.venv\Scripts\activate on Windows
  pip install -r requirements.txt

3. Set your Runware API key.
   - Create a `.env` file in the root of the skill: `RUNWARE_API_KEY=your_key`
   - OR set it in the environment: `$env:RUNWARE_API_KEY = "<YOUR_KEY>"`

4. Generate an image (sync):

  python scripts/generate_image.py --prompt "A photorealistic portrait of an adult (age 28)" --sync --outfile "portrait.png"

By default, images are saved under `~/runware_images/` unless you provide an absolute path or a relative filename (the script will remember the last directory used).

## Configuration

`skill-config.json` contains defaults used by the CLI. Fields:

- `default_size` - default image size (e.g., "1024x1024").
- `default_format` - output format (png/jpg/webp).
- `default_output_dir` - default output directory (e.g., "~\\runware_images").
- `last_output_dir` - automatically updated by the script to remember the last save location.

Do NOT store API keys in this file. Use the `RUNWARE_API_KEY` environment variable or a secret manager.

## Safety

- The script implements a simple prompt filter to block prompts that reference minors (e.g., "teen", ages under 21). This is a lightweight safeguard but does not replace human judgment or platform policies.
- Users are responsible for ensuring they have legal rights to generate and host requested imagery and for following Runware's terms of service.

## Testing & CI

- Tests are in `tests/` and use pytest. The included test stubs/mocks `requests.post` so CI does not require real API keys.
- GitHub Actions workflow `.github/workflows/ci.yml` runs the tests on push and pull requests.

Run tests locally:

  pytest -q

## Examples

See `examples/README.md` for example prompts and usage patterns (sync vs async).

## Packaging & Publishing

Before publishing to ClawHub:

1. Ensure `skill-config.json` contains no secrets.
2. Run tests and fix any issues.
3. Optionally package the skill using the project packaging script (if available) or create a .zip that follows the skill layout.

I can assist with creating the .skill package and publishing to ClawHub when you’re ready.

## Contributing

See `CONTRIBUTING.md` for contribution guidelines. Keep changes small, include tests, and run CI locally.

## License

This project is licensed under the MIT License - see LICENSE.

## Contact / Support

Open an issue or a pull request on the repository. For Runware API specifics, consult: https://runware.ai/docs/getting-started/introduction
