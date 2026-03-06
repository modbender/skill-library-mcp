# Contributing to OpenClaw Skills

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](../../issues)
- Include a clear description of the bug
- Provide steps to reproduce
- Include error messages and stack traces
- Specify your environment (OS, Node.js version, etc.)

### Suggesting Features

- Check if the feature has already been suggested in [Issues](../../issues)
- Describe the feature and its use case
- Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass: `npm test`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/openclawskills.git
cd openclawskills

# Install dependencies
npm install

# Run tests
npm test

# Build
npm run build
```

## Code Style

- Use TypeScript for type safety
- Follow existing code formatting
- Add JSDoc comments for public methods
- Keep functions focused and modular

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests where appropriate

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
