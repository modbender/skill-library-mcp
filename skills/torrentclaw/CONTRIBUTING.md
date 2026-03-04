# Contributing to torrentclaw-skill

Thanks for your interest in contributing! Here's how you can help.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-user>/torrentclaw-skill.git`
3. Install dev tools and git hooks:
   ```bash
   make install-tools
   make hooks
   ```
4. Create a branch: `git checkout -b feat/my-feature`
5. Make your changes
6. Lint locally: `make lint`
7. Commit with a clear message (see below) — the commit-msg hook will validate the format
8. Push and open a Pull Request

## Requirements

- Bash 4+
- [shellcheck](https://github.com/koalaman/shellcheck) (installed via your package manager)
- [lefthook](https://github.com/evilmartians/lefthook) (installed via your package manager)

## Commit Messages

Commits are validated automatically by a git hook. We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope][!]: <description>
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

Examples:

```
feat: add qBittorrent client detection
fix(detect): correct aria2 daemon check on macOS
docs: update API reference with new endpoints
chore: update shellcheck to latest version
feat!: redesign install guide output format
```

## Code Style

- All shell scripts must pass `shellcheck`
- Use `#!/usr/bin/env bash` as the shebang
- Use `set -euo pipefail` at the top of every script
- Keep functions focused and small
- Add comments only where the logic isn't self-evident

## Reporting Bugs

Open an issue with:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Your OS and bash version

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
