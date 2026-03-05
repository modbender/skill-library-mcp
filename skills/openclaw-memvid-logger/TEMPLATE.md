# GitHub Repository Template

This is a template repository for creating OpenClaw skills with GitHub integration.

## Quick Setup

1. **Click "Use this template"** on GitHub to create your own repo
2. **Update package.json** with your GitHub username
3. **Customize** README.md, SKILL.md for your skill
4. **Commit and push**
5. **Install** in OpenClaw

## Repository Structure

```
.
├── .github/
│   ├── workflows/ci.yml       # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md
├── tools/
│   └── log.py                 # Main skill code
├── tests/
│   └── test_log.py           # Unit tests
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md                  # GitHub-facing docs
├── SKILL.md                   # OpenClaw skill docs
├── install.sh                 # Installation script
└── package.json               # NPM + OpenClaw metadata
```

## Files to Customize

| File | What to Change |
|------|----------------|
| `package.json` | Update repository URL, author |
| `README.md` | Update description, examples |
| `SKILL.md` | Skill-specific documentation |
| `LICENSE` | Update copyright if needed |
| `install.sh` | Update default paths |

## CI/CD

The included GitHub Actions workflow:
- Validates Python syntax
- Checks shell scripts
- Validates JSON files
- Verifies file structure

## Publishing

1. Tag a release: `git tag v1.0.0`
2. Push tags: `git push --tags`
3. GitHub will create a release archive

## Installing from GitHub

Users can install your skill:

```bash
# Download latest release
curl -L https://github.com/YOUR_USERNAME/unified-logger/archive/refs/tags/v1.0.0.tar.gz | tar -xz

# Copy to OpenClaw
cp -r unified-logger-1.0.0 ~/.openclaw/workspace/skills/unified-logger
```

## Next Steps

- [ ] Publish to [ClawHub](https://clawhub.com) for discoverability
- [ ] Add more tests
- [ ] Write tutorials/examples
- [ ] Get feedback from OpenClaw community
