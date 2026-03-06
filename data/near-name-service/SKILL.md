---
name: near-name-service
description: Manage NEAR Name Service (.near domains) - check availability, register, resolve, and manage names.
---

# NEAR Name Service Skill

Manage .near domain names with ease.

## Description

This skill provides a CLI interface to interact with NEAR Name Service (.near domains). Check availability, register names, resolve names to accounts, and manage your owned .near domains.

## Features

- Check .near name availability
- Register a .near domain
- Resolve .near domain to account ID
- List owned .near domains
- Simple command-line interface

## Commands

### `near-name check <name>`
Check if a .near domain is available.

**Parameters:**
- `name` - The domain name (without .near suffix)

**Example:**
```bash
near-name check mydomain
```

### `near-name register <name> [account_id]`
Register a .near domain.

**Parameters:**
- `name` - The domain name (without .near suffix)
- `account_id` - Account to register to (optional, uses default)

**Example:**
```bash
near-name register mydomain myaccount.near
```

### `near-name resolve <name>`
Resolve a .near domain to its account ID.

**Parameters:**
- `name` - The domain name to resolve

**Example:**
```bash
near-name resolve mydomain.near
```

### `near-name list [account_id]`
List all .near domains owned by an account.

**Parameters:**
- `account_id` - Account to list domains for (optional, uses default)

## Configuration

Set your default account:
```bash
export NEAR_ACCOUNT="myaccount.near"
```

## Pricing

- Registration: ~5-10 NEAR (varies by name length)
- Annual renewal: ~0.1 NEAR
- Shorter names (<4 chars) cost more

## References

- NEAR Name Service: https://near.org/names/
- Naming Registry Contract: naming.near
- NEAR CLI: https://docs.near.org/tools/near-cli
