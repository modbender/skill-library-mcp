# StandX CLI Skill

Crypto trading CLI skill for OpenClaw - StandX exchange integration.

## Quick Install

```bash
clawhub install standx-cli
```

## Documentation

- [SKILL.md](SKILL.md) - Full usage documentation
- [references/api-docs.md](references/api-docs.md) - API reference
- [references/examples.md](references/examples.md) - Command examples
- [references/troubleshooting.md](references/troubleshooting.md) - Troubleshooting guide

## Security

This skill requires authentication credentials. See [SKILL.md#authentication](SKILL.md#authentication) for secure configuration.

Required environment variables:
- `STANDX_JWT` - JWT token for API access
- `STANDX_PRIVATE_KEY` - Ed25519 private key for trading (optional for read-only)

## License

MIT
