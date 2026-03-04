# GitHub Bounty Hunter

Autonomous GitHub bounty discovery and application system.

## Installation

```bash
openclaw skills install github-bounty-hunter
```

## Quick Start

```bash
cd ~/.openclaw-claw2/workspace/skills/github-bounty-hunter
python3 bounty_hunter.py
```

## Configuration

Edit `config.json`:

```json
{
  "skills": ["writing", "documentation", "python"],
  "min_reward": 10,
  "max_competition": 15,
  "check_interval": 30
}
```

## Features

- ✅ Auto-scan GitHub bounties
- ✅ Smart skill matching
- ✅ Auto-submit proposals
- ✅ Track earnings
- ✅ Wallet management

## Requirements

- Python 3.8+
- GitHub CLI (`gh`)
- GitHub token

## License

MIT
