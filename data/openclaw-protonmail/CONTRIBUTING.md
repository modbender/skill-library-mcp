# Contributing to ProtonMail Skill for OpenClaw

Thank you for considering contributing! This skill is built for the OpenClaw community, and contributions are welcome.

## How to Contribute

### Reporting Bugs

If you find a bug:

1. Check [existing issues](https://github.com/rvacyber/openclaw-protonmail-skill/issues) first
2. If it's new, open an issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Node version, Bridge version)

### Suggesting Features

Feature requests are welcome! Open an issue with:

- Use case description
- Why it would benefit the community
- Proposed implementation (if you have ideas)

### Pull Requests

1. **Fork the repo** and create a feature branch
2. **Make your changes:**
   - Follow existing code style (TypeScript, ESLint)
   - Add tests if applicable
   - Update documentation (README, SKILL.md) if needed
3. **Test your changes:**
   ```bash
   npm test
   npm run lint
   npm run build
   ```
4. **Commit with clear messages:**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
   - Example: `feat: add support for HTML email sending`
5. **Push to your fork** and open a PR
6. **Describe your changes** in the PR description

### Code Style

- **TypeScript** for all source files
- **ESLint** rules enforced (run `npm run lint`)
- **Descriptive variable names** (no single letters except loop indices)
- **JSDoc comments** for public APIs
- **Error handling** — always handle errors gracefully

### Security

- **Never commit credentials** — use `.env` or config examples only
- **Review dependencies** — only add packages from reputable sources
- **Report security issues privately** — email jim@rvacyber.com instead of opening a public issue

### Testing

- Write tests for new features (`test/` directory)
- Ensure existing tests pass before submitting PR
- Integration tests should use mock IMAP/SMTP, not real accounts

### Documentation

- Update README.md for user-facing changes
- Update SKILL.md for tool definitions or setup changes
- Add inline comments for complex logic
- Update examples/ if config format changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/rvacyber/openclaw-protonmail-skill.git
cd openclaw-protonmail-skill

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Link to OpenClaw for local testing
npm run install-skill
```

## Community Guidelines

- Be respectful and constructive
- Focus on the code and ideas, not the person
- Welcome newcomers and help them learn
- Give credit where it's due

## Questions?

- **GitHub Discussions:** https://github.com/openclaw/openclaw/discussions
- **OpenClaw Discord:** https://discord.com/invite/clawd
- **Email:** jim@rvacyber.com

---

Thank you for helping improve ProtonMail integration for OpenClaw! 🔐
