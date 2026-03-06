# NEAR Subaccount Manager Skill

Create and manage NEAR subaccounts from the command line.

## Installation

The skill is installed in `~/.openclaw/skills/near-subaccount/`

## Usage

### Create a Subaccount

```bash
export NEAR_ACCOUNT="myaccount.near"
node scripts/subaccount.js create wallet
```

Creates: `wallet.myaccount.near`

### List Subaccounts

```bash
node scripts/subaccount.js list myaccount.near
```

### Delete a Subaccount

```bash
node scripts/subaccount.js delete wallet.myaccount.near myaccount.near
```

### Bulk Distribute NEAR

Create a `subaccounts.json` file:
```json
{
  "subaccounts": [
    "wallet1.myaccount.near",
    "wallet2.myaccount.near",
    "wallet3.myaccount.near"
  ]
}
```

Then distribute:
```bash
export NEAR_ACCOUNT="myaccount.near"
node scripts/subaccount.js distribute subaccounts.json 0.1
```

## Requirements

- NEAR CLI installed and configured
- Account with sufficient balance (~0.1 NEAR per subaccount)

## License

MIT
