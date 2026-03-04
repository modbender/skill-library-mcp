# Contributing to SonarQube Analyzer

Thank you for your interest in contributing to the SonarQube Analyzer skill! This document provides guidelines and instructions for contributing.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/FelipeOFF/sonarqube-analyzer.git
cd sonarqube-analyzer

# Install dependencies
npm install

# Run tests
npm test

# Run linter
npm run lint
```

## Adding New Rules

To add support for a new SonarQube rule:

1. Edit `src/rules.js`
2. Add entry to `RULE_SOLUTIONS` object:

```javascript
'rule-key': {
  title: 'Human-readable title',
  description: 'Detailed explanation',
  autoFixable: true | false,
  solution: (issue) => `Solution for ${issue.component}:${issue.line}`,
  example: `
// ❌ Before:
bad code

// ✅ After:
good code
  `
}
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add tests if applicable
5. Run `npm test` and `npm run lint`
6. Commit with clear messages
7. Push to your fork
8. Open a PR against `main`

## Code Style

- Use ESLint configuration
- Follow existing code patterns
- Add JSDoc comments for functions
- Keep functions small and focused

## Reporting Issues

When reporting issues, please include:
- Node.js version
- SonarQube version
- Error messages
- Steps to reproduce

## License

By contributing, you agree that your contributions will be licensed under the MIT License.