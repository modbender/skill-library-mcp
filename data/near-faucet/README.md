# NEAR Testnet Faucet Skill

Request NEAR testnet tokens easily with this OpenClaw skill.

## Installation

The skill is installed in `~/.openclaw/skills/near-faucet/`

## Usage

### Request Testnet Tokens

```bash
node scripts/faucet.js request youraccount.testnet
```

### Check Balance

```bash
node scripts/faucet.js balance youraccount.testnet
```

## Rate Limits

- 1 request per account per 24 hours
- Maximum 10 NEAR per request

## Notes

- Tokens typically arrive within 1-5 minutes
- Only works on NEAR testnet
- You can also use the web faucet at https://wallet.testnet.near.org/

## License

MIT
