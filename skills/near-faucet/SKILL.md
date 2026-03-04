---
name: near-faucet
description: OpenClaw skill for requesting NEAR testnet tokens via faucet. Provides faucet requests, status checking, and balance queries with rate limiting.
---

# NEAR Testnet Faucet Skill

Simple faucet integration for NEAR testnet tokens.

## Description

This skill provides easy access to NEAR testnet tokens via faucet requests. Includes rate limiting to prevent abuse.

## Features

- Request NEAR testnet tokens
- Check faucet request status
- Rate limiting per address
- Simple CLI commands

## Commands

### `near-faucet request [account_id]`
Request testnet NEAR tokens for an account.

**Parameters:**
- `account_id` - NEAR account ID (optional, uses default if configured)

**Example:**
```bash
near-faucet request myaccount.testnet
```

### `near-faucet status [request_id]`
Check the status of a faucet request.

**Parameters:**
- `request_id` - Request ID to check (optional, shows latest if omitted)

### `near-faucet balance [account_id]`
Check testnet balance for an account.

## Configuration

Set your default account via environment variable or config:
```bash
export NEAR_ACCOUNT="myaccount.testnet"
```

## Installation

The skill is automatically installed in your OpenClaw skills directory.

## Rate Limits

- 1 request per account per 24 hours
- Maximum 10 NEAR per request
- Request queue processing time: ~1-5 minutes

## References

- NEAR Testnet Faucet: https://wallet.testnet.near.org/
- NEAR CLI: https://docs.near.org/tools/near-cli
