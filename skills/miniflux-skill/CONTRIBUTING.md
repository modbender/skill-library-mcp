# Contributing to Miniflux Skill

Thank you for your interest in contributing to the Miniflux skill for OpenClaw!

## Development Workflow

### For Public Repository

All changes to this repository must go through **Pull Requests**. This ensures code quality and proper versioning.

## Semantic Releases

This project uses [semantic releases](https://www.conventionalcommits.org/) and [release-please-action](https://github.com/googleapis/release-please-action) for automated versioning.

### Commit Message Format

Your commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `ci`: Changes to CI configuration files and scripts

#### Examples:

```bash
feat(feeds): add support for OPML import/export
fix(auth): handle missing MINIFLUX_TOKEN gracefully
docs(readme): update installation instructions
test: add tests for feed creation endpoint
```

### Release Process

1. Developer creates a PR with conventional commits
2. CI/CD runs tests
3. PR is merged to `master` branch
4. `release.yaml` workflow runs automatically
5. Release is created with version based on commit types
6. CHANGELOG.md is automatically updated
7. Skill is published to ClawHub (if configured)

#### Version Bumps:

- `feat:` → Minor version bump (0.1.0 → 0.2.0)
- `fix:` → Patch version bump (0.1.0 → 0.1.1)
- `feat!` or `fix!:**` or `BREAKING CHANGE:` → Major version bump (0.1.0 → 1.0.0)

## Testing

Before creating a PR, run tests locally:

```bash
# Install dependencies
make install

# Run tests
make test

# Run all checks
make check
```

## Pull Request Process

1. Fork the repository
2. Create a new branch: `git checkout -b feat/my-new-feature`
3. Make your changes with conventional commits
4. Run tests: `make check`
5. Commit your changes
6. Push to your fork
7. Create a Pull Request to `master` branch

## Code Style

- All documentation must be in English
- Keep SKILL.md and README.md updated
- Add tests for new features
- Update CHANGELOG.md for unreleased changes manually if needed

## Questions?

Open an issue or discussion for questions or suggestions!
