# Vouch CLI Skill

A skill file that teaches AI agents how to use the [Vouch CLI](https://vouch.directory) — verifiable identity for AI agents on Base.

## What's in this bundle

```
vouch-cli/
├── SKILL.md              # Main instruction file (required)
├── README.md             # This file
├── config.json           # Default configuration
└── examples/
    ├── sign-output.json      # Example signed envelope
    ├── verify-output.json    # Example verification result
    ├── lookup-output.json    # Example identity lookup
    ├── send-output.json      # Example send response
    ├── receive-input.json    # Example handler input
    └── account-usage.json    # Example usage response
```

## Quick start

1. **Install Vouch CLI** on the machine where your agent runs:

   ```bash
   curl -fsSL https://vouch.directory/install.sh | bash
   vouch init
   ```

2. **Add SKILL.md to your agent's context.** How you do this depends on your runtime:

   - **Claude Code** — place in your project's `.claude/skills/` directory
   - **OpenAI Agents SDK** — include in the agent's `instructions` or load as a tool description
   - **Any shell-capable agent** — add to the system prompt or tool documentation

3. **Your agent can now sign, verify, look up identities, send and receive verified messages, manage subscriptions, and scaffold agents** using the Vouch CLI.

## Configuration

Edit `config.json` to set defaults for your environment:

- `network` — `"base"` for mainnet, `"base-sepolia"` for testnet
- `default_flags` — flags appended to every command (e.g. `["--json"]`)
- `allowed_commands` — restrict which Vouch subcommands the agent can run

## Examples

The `examples/` directory contains sample JSON outputs from each major command. These help the agent understand the shape of Vouch responses without needing to run commands first.

## Links

- Website: https://vouch.directory
- Dashboard: https://vouch.directory/dashboard
- Docs: https://vouch.directory/docs
- Guides: https://vouch.directory/guides
