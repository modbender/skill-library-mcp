# Contributing to Unified Logger

Thank you for your interest in contributing! This project follows standard open source practices.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/unified-logger.git`
3. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

```bash
# Install dependencies
npm install -g @memvid/cli

# Set up test environment
export JSONL_LOG_PATH="/tmp/test_conversation.jsonl"
export MEMVID_PATH="/tmp/test_memory.mv2"

# Run tests (if available)
python3 -m pytest tests/
```

## Code Style

- Python: PEP 8 compliant
- Shell scripts: `shellcheck` clean
- Documentation: Clear, concise, example-driven

## Submitting Changes

1. Ensure your code works with OpenClaw >= 2026.2.12
2. Update README.md if adding features
3. Add examples for new functionality
4. Submit a pull request with a clear description

## Reporting Issues

When reporting bugs, please include:
- OpenClaw version
- Python version
- Memvid CLI version
- Steps to reproduce
- Expected vs actual behavior

## Questions?

- Open an issue for bugs/features
- Join [OpenClaw Discord](https://discord.com/invite/clawd) for discussions
