# NEAR Multi-Account Manager

An OpenClaw skill for securely managing multiple NEAR Protocol accounts.

## Features

- 🔐 **Secure Storage** - Account credentials are encrypted and stored locally
- 🔄 **Easy Switching** - Quickly switch between active accounts
- 💰 **Balance Checking** - View balances for all accounts
- 💸 **Transfers** - Transfer NEAR between accounts
- 📊 **Summaries** - Get a comprehensive overview of all accounts
- 📜 **Transaction Tracking** - View account transaction history

## Installation

```bash
cd C:\Users\Shai\.openclaw\skills\near-multi-account-manager
npm install
```

## Usage

### Add an Account

Add a NEAR account to the manager:

```javascript
await add_account({
  accountId: "your-account.near",
  privateKey: "ed25519:...",
  name: "My Main Account"  // optional
});
```

### List All Accounts

List all managed accounts:

```javascript
await list_accounts();
```

### Set Active Account

Set the active account for operations:

```javascript
await set_active_account({
  accountId: "your-account.near"
});
```

### Get Account Balance

Get balance for a specific or active account:

```javascript
// Get active account balance
await get_balance();

// Get specific account balance
await get_balance({ accountId: "your-account.near" });
```

### Get All Balances

Get balances for all managed accounts:

```javascript
await get_all_balances();
```

### Transfer NEAR

Transfer NEAR between accounts:

```javascript
await transfer({
  from: "sender.near",        // optional, uses active if not specified
  to: "receiver.near",
  amount: "1.5",              // in NEAR
  note: "Payment"             // optional
});
```

### Get Transactions

View transaction information for an account:

```javascript
await get_transactions({ accountId: "your-account.near" });
```

### Account Summary

Get a comprehensive summary of all accounts:

```javascript
await account_summary();
```

### Remove Account

Remove an account from the manager:

```javascript
await remove_account({
  accountId: "your-account.near",
  confirm: "your-account.near"  // must match accountId
});
```

### Export Accounts

Export account information (without private keys):

```javascript
await export_accounts();
```

### Import Account

Import an account (requires adding private key separately):

```javascript
await import_account({
  accountId: "your-account.near",
  name: "Imported Account"
});
```

## Security

- Private keys are encrypted using AES-256-CBC
- Encryption key can be set via `NEAR_SKILL_KEY` environment variable
- Never share your private keys
- Backup your encrypted account file regularly

## Environment Variables

- `NEAR_SKILL_KEY` - Custom encryption key (defaults to a built-in key)
- `OPENCLAW_HOME` - OpenClaw home directory (for data storage)

## Data Storage

Account data is stored in:
```
~/.openclaw/skills/near-multi-account-manager/
├── accounts.enc          # Encrypted account storage
└── active_account.txt    # Current active account
```

## Network

Currently operates on NEAR mainnet. Testnet support can be added by modifying the `NETWORK_ID` constant.

## License

MIT
