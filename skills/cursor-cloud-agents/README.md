# Cursor Cloud Agents Skill for OpenClaw

[![Tests](https://github.com/Parcosta/cursor-cloud-agents/actions/workflows/test.yml/badge.svg)](https://github.com/Parcosta/cursor-cloud-agents/actions/workflows/test.yml)
[![Security](https://github.com/Parcosta/cursor-cloud-agents/actions/workflows/security.yml/badge.svg)](https://github.com/Parcosta/cursor-cloud-agents/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An [OpenClaw](https://openclaw.dev) skill that wraps the Cursor Cloud Agents HTTP API, enabling OpenClaw to dispatch coding tasks to Cursor's cloud agents, monitor their progress, and incorporate results.

## Features

- 🚀 **Launch agents** on any GitHub repository
- 📊 **Monitor progress** with real-time status updates
- 💬 **Full conversation history** retrieval
- 📝 **Follow-up instructions** for iterative refinement
- 🚦 **Rate limiting** (1 req/sec) to respect API limits
- 💾 **Response caching** (60s TTL) for better performance
- 🔐 **Secure** input sanitization and safe temp file handling
- ✅ **Comprehensive tests** with bats-core

## Quick Start

```bash
# Install the skill
clawhub install cursor-cloud-agents

# Set your Cursor API key
export CURSOR_API_KEY="your_cursor_api_key_here"

# List your agents
cursor-cloud-agents list

# Launch an agent
./scripts/cursor-api.sh launch \
  --repo owner/repo \
  --prompt "Add comprehensive tests for the auth module"

# Check status
./scripts/cursor-api.sh status <agent-id>

# Get conversation
./scripts/cursor-api.sh conversation <agent-id>
```

### Short Commands (cca aliases)

For faster daily usage, enable short commands:

```bash
# Source the aliases in your shell
source scripts/cca-aliases.sh

# Now use 'cca' instead of 'cursor-api.sh'
cca list                              # List agents
cca launch --repo owner/repo ...      # Launch agent
cca status <agent-id>                 # Check status
cca conversation <agent-id>           # Get conversation
cca followup <agent-id> --prompt "..." # Send followup
cca delete <agent-id>                 # Delete agent
```

Add to your `~/.bashrc` or `~/.zshrc` to enable permanently:
```bash
source ~/.openclaw/workspace/projects/cursor-cloud-agents/scripts/cca-aliases.sh
```

## Installation

### As an OpenClaw Skill

1. Install from clawhub:
   ```bash
   clawhub install cursor-cloud-agents
   ```

2. Add your Cursor API key to `~/.openclaw/.env`:
   ```bash
   echo "CURSOR_API_KEY=your_cursor_api_key_here" >> ~/.openclaw/.env
   ```

3. OpenClaw will automatically discover the skill and use `SKILL.md` for guidance.

### Manual Installation (Not Recommended)

If you need to install manually (e.g., for development):
```bash
git clone https://github.com/Parcosta/cursor-cloud-agents.git ~/.openclaw/skills/cursor-cloud-agents
```

### Standalone Usage

After installation, use the skill directly:

```bash
cursor-cloud-agents --help
```

### Short Commands (Optional)

For faster daily usage, enable short-form `cca` aliases by sourcing the aliases file:

```bash
# One-time setup: Add to your ~/.bashrc or ~/.zshrc
echo 'source ~/.openclaw/workspace/projects/cursor-cloud-agents/scripts/cca-aliases.sh' >> ~/.bashrc

# Or source manually for current session
source ~/.openclaw/workspace/projects/cursor-cloud-agents/scripts/cca-aliases.sh
```

Then use short commands:

```bash
cca list              # List all agents
cca ls                # Short for 'list'
cca launch --repo owner/repo --prompt "Add tests"
cca status <agent-id>
cca conv <agent-id>   # Short for 'conversation'
cca fu <agent-id> --prompt "..." # Short for 'followup'
cca rm <agent-id>     # Short for 'delete'
```

All standard commands work with `cca` prefix, plus these extra-short aliases:
- `cca ls` → `cca list`
- `cca conv` → `cca conversation`
- `cca fu` → `cca followup`
- `cca rm` → `cca delete`

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all agents |
| `launch` | Launch a new agent on a repository |
| `status <id>` | Get agent status |
| `conversation <id>` | Get full conversation history |
| `followup <id>` | Send follow-up message to agent |
| `stop <id>` | Stop a running agent |
| `delete <id>` | Delete an agent |
| `models` | List available models |
| `me` | Get account information |
| `verify <repo>` | Verify repository access |
| `usage` | Get usage and quota information |
| `clear-cache` | Clear response cache |

See [SKILL.md](SKILL.md) for detailed usage instructions and workflow patterns.

## API Reference

See [references/api-reference.md](references/api-reference.md) for complete API documentation.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CURSOR_API_KEY` | Your Cursor API key (required) | - |
| `CURSOR_CACHE_TTL` | Cache TTL in seconds | 60 |

### Global Options

| Option | Description |
|--------|-------------|
| `--no-cache` | Disable response caching |
| `--verbose` | Enable verbose output |
| `--help` | Show help message |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | API error |
| 2 | Authentication missing |
| 3 | Rate limited |
| 4 | Repository not accessible |
| 5 | Invalid arguments |

## Development

### Running Tests

```bash
# Run all tests
bats tests/

# Run with coverage
./tests/run-tests.sh --coverage

# Run integration tests (requires API key)
CURSOR_API_KEY=xxx bats tests/integration.bats
```

### Project Structure

```
cursor-cloud-agents/
├── scripts/
│   └── cursor-api.sh          # Main API wrapper script
├── references/
│   └── api-reference.md       # API documentation
├── tests/
│   ├── test_cursor_api.bats   # Unit tests
│   ├── integration.bats       # Integration tests
│   └── run-tests.sh           # Test runner
├── .github/
│   └── workflows/
│       ├── test.yml           # Test CI workflow
│       ├── security.yml       # Security scan workflow
│       └── lint.yml           # Linting workflow
├── SKILL.md                   # OpenClaw skill documentation
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Requirements

- bash 4.0+
- curl
- jq
- base64

## Contributing

1. Fork the repository on GitHub
2. Clone your fork for development:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cursor-cloud-agents.git
   cd cursor-cloud-agents
   ```
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please ensure:
- All tests pass (`bats tests/`)
- ShellCheck is clean (`shellcheck scripts/cursor-api.sh`)
- Code follows the existing style

## Security

This skill follows security best practices:

- No secrets in code
- Input sanitization prevents command injection
- Safe temporary file handling
- All code passes shellcheck
- Regular security scans via GitHub Actions

See [SECURITY.md](SECURITY.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Cursor](https://cursor.com) for the Cloud Agents API
- [OpenClaw](https://openclaw.dev) for the skill framework
- [bats-core](https://github.com/bats-core/bats-core) for testing

## Support

- 📖 [Documentation](SKILL.md)
- 🐛 [Issue Tracker](https://github.com/Parcosta/cursor-cloud-agents/issues)
- 💬 [Discussions](https://github.com/Parcosta/cursor-cloud-agents/discussions)
