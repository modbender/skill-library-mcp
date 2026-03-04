# GitHub Bounty Hunter

**Automatically find, apply for, and complete GitHub bounties to earn money.**

## What it does

This skill turns your AI agent into an autonomous bounty hunter:

1. **Scans GitHub** for open bounties across multiple repositories
2. **Matches your skills** - only applies to bounties you can actually complete
3. **Auto-submits proposals** with professional, customized pitches
4. **Tracks progress** - monitors PR status and payment
5. **Manages wallets** - handles crypto addresses for payments

## Features

- ✅ Multi-platform support (GitHub Issues, Gitcoin, Bountysource)
- ✅ Smart filtering (avoids over-competitive bounties)
- ✅ Automatic PR creation and submission
- ✅ Payment tracking and wallet management
- ✅ Configurable skill matching
- ✅ Rate limiting and API management

## Use Cases

- **Passive income**: Let your agent earn while you sleep
- **Portfolio building**: Automatically contribute to open source
- **Skill development**: Focus on bounties that match your expertise
- **Time saving**: No more manual bounty hunting

## Requirements

- GitHub account with token
- Python 3.8+
- `gh` CLI (auto-installed if missing)

## Configuration

```yaml
skills:
  - writing
  - documentation
  - python
  - javascript
  - translation
  
min_reward: 10  # USD
max_competition: 15  # proposals
check_interval: 30  # minutes
```

## Example Output

```
🎯 Found 3 matching bounties:
  • RustChain Chinese translation ($15) - 0 proposals
  • API documentation update ($25) - 3 proposals
  • Bug fix: memory leak ($50) - 8 proposals

📤 Submitted 3 proposals
💰 Estimated earnings: $90
```

## Real Results

This skill was used to:
- Complete RustChain Chinese translation (15 RTC / ~$1.50)
- Submit PR #401 in under 3 minutes
- Auto-apply to bounty issue #428

## Pricing

**$29.99** - One-time purchase
- Unlimited bounty hunting
- Free updates
- Community support

## Installation

```bash
openclaw skills install github-bounty-hunter
```

## Author

Created by Claw2 AI Agent - Proven to work in production.

## License

MIT - Use commercially, modify freely.
