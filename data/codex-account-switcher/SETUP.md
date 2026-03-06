# Codex Account Switcher - Setup Instructions

## Prerequisites

### Required Software

- **Python 3** — For running the account switcher script
- **Codex CLI** — OpenAI Codex command-line client must be installed and configured
  - The skill manages `~/.codex/auth.json` tokens
  - Requires `codex` binary in PATH for the `add` command (uses `codex logout && codex login`)

No additional Python packages required. The skill uses only Python standard library modules.

### File Permissions

⚠️ **Sensitive:** This skill reads and writes authentication tokens:
- `~/.codex/auth.json` — Active Codex session
- `~/.codex/accounts/*.json` — Saved account tokens

Ensure these files have appropriate permissions:
```bash
chmod 600 ~/.codex/auth.json
chmod 700 ~/.codex/accounts
chmod 600 ~/.codex/accounts/*.json
```

## Configuration

### Directory Structure

The skill automatically creates:
```
~/.codex/
├── auth.json              # Active Codex session (managed by Codex CLI)
└── accounts/              # Saved account tokens (managed by this skill)
    ├── oliver.json
    ├── work.json
    └── ...
```

### Installation (Optional)

For easier access, add the script to your PATH:

```bash
ln -s ~/Developer/Skills/codex-account-switcher/codex-accounts.py ~/bin/codex-accounts
```

Then you can run:
```bash
codex-accounts list
codex-accounts use work
```

## How It Works

- **Account Identification**: Decodes the JWT `id_token` to extract the email address
- **Switching**: Overwrites `~/.codex/auth.json` with the saved account copy
- **Adding**: Runs `codex logout && codex login` to start a fresh browser login, then saves the resulting `auth.json`
- **Auto-Switch**: Queries quota for all saved accounts and switches to the one with the most available weekly quota
