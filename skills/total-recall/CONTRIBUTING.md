# Contributing

Thanks for your interest in contributing to OpenClaw Memory!

## How to Contribute

1. **Bug reports** — Open an issue describing what happened, what you expected, and your setup (OS, OpenClaw version, model used).

2. **Feature requests** — Open an issue describing what you'd like and why. Bonus points for describing your use case.

3. **Pull requests** — Fork the repo, make your changes, and submit a PR. Please:
   - Keep changes focused (one feature/fix per PR)
   - Test on a clean install if possible
   - Update docs if your change affects usage

## Code Style

- Bash scripts: use `set -eo pipefail`, quote variables, use `${VAR:-default}` for optional env vars
- Keep it simple — the whole point is zero dependencies beyond bash/jq/curl

## Questions?

Open an issue or find us in the [OpenClaw Discord](https://discord.com/invite/clawd).
