# NEAR Name Service Skill

Manage .near domain names from the command line.

## Installation

The skill is installed in `~/.openclaw/skills/near-name-service/`

## Usage

### Check Availability

```bash
node scripts/nameservice.js check mydomain
```

### Register a Domain

```bash
export NEAR_ACCOUNT="myaccount.near"
node scripts/nameservice.js register mydomain
```

Or specify account directly:
```bash
node scripts/nameservice.js register mydomain myaccount.near
```

### Resolve a Domain

```bash
node scripts/nameservice.js resolve mydomain.near
```

## Requirements

- NEAR CLI installed and configured
- Account with sufficient balance for registration (~5-10 NEAR)

## Pricing

- Registration: ~5-10 NEAR (varies by name length)
- Annual renewal: ~0.1 NEAR

## License

MIT
