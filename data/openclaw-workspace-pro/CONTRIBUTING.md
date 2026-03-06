# Contributing to OpenClaw Workspace Pro

Thank you for considering contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and constructive. We're building tools for the OpenClaw community.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** - Someone might have already reported it
2. **Create a detailed issue** with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - OpenClaw version
   - Environment details (OS, Docker, etc.)

### Suggesting Features

1. **Search existing feature requests**
2. **Open a new issue** with:
   - Clear use case
   - Why it's valuable
   - Proposed implementation (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow existing code style
   - Add tests if applicable
   - Update documentation
4. **Commit with clear messages**: 
   - `feat: Add artifact validation`
   - `fix: Resolve .env overwrite issue`
   - `docs: Update memory compaction guide`
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/openclaw-workspace-pro.git
cd openclaw-workspace-pro

# Test installation
./install.sh

# Make changes
# ...

# Test your changes
./install.sh
```

## Guidelines

### Code Style
- Use clear, descriptive variable names
- Comment complex logic
- Keep functions focused and small
- Follow existing patterns

### Documentation
- Update README.md for user-facing changes
- Update SKILL.md for skill behavior changes
- Add inline comments for complex logic
- Update CHANGELOG.md

### Testing
- Test installation on clean workspace
- Test upgrades from previous versions
- Verify backups are created correctly
- Test on different OpenClaw versions (when possible)

## Project Structure

```
openclaw-workspace-pro/
├── SKILL.md              # Skill manifest + documentation
├── README.md             # GitHub homepage
├── install.sh            # Installation script
├── templates/            # Template files for installation
│   ├── gitignore
│   ├── env.example
│   ├── MEMORY-COMPACTION.md
│   ├── AGENTS-additions.md
│   └── TOOLS-additions.md
├── docs/                 # Detailed documentation (future)
├── LICENSE               # MIT License
├── CHANGELOG.md          # Version history
└── package.json          # ClawHub metadata
```

## Release Process

1. Update `CHANGELOG.md` with changes
2. Bump version in `SKILL.md`, `package.json`, `install.sh`
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. Create GitHub release
6. Publish to ClawHub (maintainers only)

## Questions?

- **GitHub Discussions:** https://github.com/Eugene9D/openclaw-workspace-pro/discussions
- **OpenClaw Discord:** https://discord.com/invite/clawd
- **Issues:** https://github.com/Eugene9D/openclaw-workspace-pro/issues

---

Thank you for contributing to OpenClaw Workspace Pro! 🚀
