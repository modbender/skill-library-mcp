# Contributing to Claude Code Mastery

Thank you for your interest in contributing! This skill helps Clawdbot users master Claude Code.

## How to Contribute

### Reporting Issues

- Open an issue on GitHub
- Include steps to reproduce
- Include your OS and Claude Code version

### Suggesting Features

- Open an issue with the "enhancement" label
- Describe the use case
- Explain why it would benefit users

### Pull Requests

**⚠️ Branch Protection: `main` branch is protected.**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test your changes locally
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request against `main`

### PR Requirements

- [ ] Changes tested locally
- [ ] SKILL.md updated if adding features
- [ ] Scripts are executable (`chmod +x`)
- [ ] No large binary files (use .gitignore)
- [ ] Clear commit message

## Code Style

### Shell Scripts
- Use `set -e` for error handling
- Add comments for complex logic
- Check dependencies before using them
- Support `--help` flag

### Markdown
- Use headers for sections
- Include code examples
- Keep lines under 100 chars when possible

## What We Accept

✅ Bug fixes
✅ Documentation improvements
✅ New subagent templates
✅ Script improvements
✅ Compatibility fixes

## What We Don't Accept

❌ Large binary files
❌ Credentials or secrets
❌ Breaking changes without discussion
❌ Features that require non-standard dependencies

## Questions?

Open an issue or reach out to the maintainers.

---

*Thank you for helping improve Claude Code Mastery!*
