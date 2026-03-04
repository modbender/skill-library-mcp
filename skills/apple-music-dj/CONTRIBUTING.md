# Contributing to Apple Music DJ

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

1. Fork the repo and clone your fork
2. Copy `.env.example` to `.env` and fill in your Apple Music tokens
3. Verify setup: `scripts/verify_setup.sh`

## Development

### Prerequisites

- macOS or Linux
- `curl`, `jq`, `python3` installed
- Apple Developer Program membership (for MusicKit tokens)
- Active Apple Music subscription (for testing)

### Project Structure

- `SKILL.md` — Skill definition (frontmatter + workflows). This is what OpenClaw reads.
- `scripts/` — All executable scripts (Bash + Python)
- `references/` — Deep reference docs for auth, API, and strategies
- `assets/` — Skill icon and visual assets

### Code Style

**Bash:**

- Use `set -euo pipefail` at the top of every script
- Quote all variables: `"$var"` not `$var`
- Use `[[ ]]` for conditionals
- Functions use `snake_case`

**Python:**

- Python 3.9+ (compatible with 3.9, 3.11, and 3.13)
- No pip dependencies for core scripts (stdlib only)
- `PyJWT` is the only exception (for token generation)
- Functions use `snake_case`, classes use `PascalCase`
- Run tests before submitting: `python3 -m pytest tests/ -v`

### Testing Changes

```bash
# Verify all scripts compile/parse cleanly
for f in scripts/*.py; do python3 -c "import py_compile; py_compile.compile('$f', doraise=True)"; done
for f in scripts/*.sh; do bash -n "$f"; done

# Verify API connectivity
scripts/apple_music_api.sh verify

# Run a taste profile (uses real API)
python3 scripts/taste_profiler.py --cache /tmp/test_profile.json
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-change`
2. Make your changes
3. Run syntax checks (see above)
4. Test with a real Apple Music account if possible
5. Update `CHANGELOG.md` under `[Unreleased]`
6. Update `SKILL.md` if you add triggers, commands, or scripts
7. Submit a pull request

## Adding a New Feature

If you're adding a new engagement feature or playlist strategy:

1. Create the script in `scripts/`
2. Add the feature section to `SKILL.md` (triggers, run command, description)
3. Add the script to the Scripts table in `SKILL.md`
4. Add a Quick Commands entry in `SKILL.md`
5. Add an Example Interaction in `SKILL.md`
6. Update `README.md` features list, file structure, and examples
7. If it's a playlist strategy, add the algorithm to `references/playlist-strategies.md`
8. Update `CHANGELOG.md`

## Reporting Issues

- Include your OS, Python version, and OpenClaw version
- Include the full error output
- Redact your tokens! Never paste `APPLE_MUSIC_DEV_TOKEN` or `APPLE_MUSIC_USER_TOKEN`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
