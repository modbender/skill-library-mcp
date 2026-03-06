# Contributing

Thanks for your interest in improving the Web2Labs Studio skill. This document covers setup, testing, and pull request expectations.

## Prerequisites

- Node.js 18+
- npm
- Optional: `yt-dlp` (for URL-based workflows and watch mode)

## Setup

```bash
git clone https://github.com/web2labs/web2labs-studio-skill.git
cd web2labs-studio-skill
npm install
```

## Running Tests

```bash
# Unit tests (mocked, no network)
npm test

# Integration tests (mocked API flows)
npm run test:integration

# End-to-end tests (mocked full workflows)
npm run test:e2e

# All quality gates
npm run test:hardening
```

Unit tests use Node.js built-in test runner (`node --test`) with no external test framework.

## Code Style

- ES modules (`.mjs` extension).
- Classes with static methods for tools and utilities.
- No TypeScript — plain JavaScript with JSDoc where helpful.
- No comments that narrate what the code does. Comments explain non-obvious intent only.

## Pull Request Guidelines

1. **One concern per PR.** Security fixes, features, and refactors should be separate.
2. **Run `npm test` before submitting.** All tests must pass.
3. **Fill out the PR template.** The security checklist is mandatory for any PR that touches network, filesystem, or auth logic.
4. **Update CHANGELOG.md** under `## Unreleased` with a line describing your change.
5. **Do not commit secrets.** No API keys, tokens, or credentials in code or tests.

## Security Contributions

If your contribution involves security-sensitive changes (auth, network destinations, file paths, spend confirmations), call it out explicitly in the PR description and verify:

- Auth headers are not sent to non-Web2Labs domains.
- File paths from external sources are sanitized via `safeFilename()`.
- Paid actions go through spend policy enforcement.
- No secrets appear in logs or tool output.

For vulnerability reports, see [SECURITY.md](SECURITY.md).

## Versioning

This skill follows [semver](https://semver.org/). ClawHub expects versioned releases with changelogs.

- **Patch** (1.0.x): bug fixes, security patches, doc improvements.
- **Minor** (1.x.0): new tools, new features, non-breaking changes.
- **Major** (x.0.0): breaking changes to tool schemas or behavior.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
