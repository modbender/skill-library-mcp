---
name: near-subaccount
description: Create, list, delete, and manage NEAR subaccounts with bulk distribution operations.
---

# NEAR Subaccount Manager Skill

Create and manage NEAR subaccounts easily.

## Description

This skill provides tools to create, list, and delete NEAR subaccounts. Also includes bulk operations for distributing NEAR tokens to multiple subaccounts.

## Features

- Create subaccounts
- List all subaccounts under an account
- Delete subaccounts
- Bulk distribute NEAR to multiple subaccounts
- Clean command-line interface

## Commands

### `near-subaccount create <subaccount_name> [master_account]`
Create a new subaccount.

**Parameters:**
- `subaccount_name` - Name of the subaccount (without .master.account)
- `master_account` - Master account (optional, uses default)

**Example:**
```bash
near-subaccount create wallet myaccount.near
# Creates: wallet.myaccount.near
```

### `near-subaccount list [account_id]`
List all subaccounts under an account.

**Parameters:**
- `account_id` - Account to list subaccounts for (optional, uses default)

**Example:**
```bash
near-subaccount list myaccount.near
```

### `near-subaccount delete <subaccount_id> [master_account]`
Delete a subaccount.

**Parameters:**
- `subaccount_id` - Full subaccount ID to delete
- `master_account` - Master account (optional, uses default)

### `near-subaccount distribute <file.json> [amount]`
Bulk distribute NEAR from master account to subaccounts listed in a JSON file.

**Parameters:**
- `file.json` - JSON file with subaccount list
- `amount` - NEAR amount to send each (default: 0.1)

**JSON format:**
```json
{
  "subaccounts": [
    "wallet1.myaccount.near",
    "wallet2.myaccount.near",
    "wallet3.myaccount.near"
  ]
}
```

## Configuration

Set your default account:
```bash
export NEAR_ACCOUNT="myaccount.near"
```

## Requirements

- NEAR CLI installed and configured
- Master account with sufficient balance for creating subaccounts (~0.1 NEAR each)

## References

- NEAR CLI: https://docs.near.org/tools/near-cli
- Subaccount docs: https://docs.near.org/concepts/account/subaccounts
