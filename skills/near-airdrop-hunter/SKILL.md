---
name: near-airdrop-hunter
description: Discover NEAR airdrops, check eligibility, claim rewards, and track claimed airdrops across multiple platforms.
---
# NEAR Airdrop Hunter Skill

Discover, check eligibility, and claim NEAR airdrops automatically.

## Description

This skill helps you discover active NEAR airdrops, check eligibility for specific airdrops, claim eligible airdrops, and track claimed airdrops across multiple platforms.

## Features

- Discover active NEAR airdrops
- Check eligibility for airdrops
- Claim eligible airdrops
- Track claimed airdrops
- Multiple platform scanning

## Commands

### `near-airdrop discover [platform]`
Discover active airdrops.

**Parameters:**
- `platform` - Filter by platform (optional: aurora, ref, all)

### `near-airdrop check <account_id> <airdrop_id>`
Check eligibility for an airdrop.

**Parameters:**
- `account_id` - NEAR account to check
- `airdrop_id` - Airdrop to check eligibility for

### `near-airdrop claim <account_id> <airdrop_id>`
Claim an eligible airdrop.

**Parameters:**
- `account_id` - NEAR account to claim for
- `airdrop_id` - Airdrop to claim

### `near-airdrop list [account_id]`
List claimed airdrops for an account.

### `near-airdrop track [account_id]`
Track all airdrops with their status.

## Configuration

Tracking data is stored in `~/.near-airdrop/tracking.json`.

## Notes

- Airdrop availability varies by protocol
- Some airdrops require holding specific tokens
- Check eligibility before claiming
- Always verify airdrop legitimacy

## References

- NEAR Ecosystem: https://near.org/ecosystem/
- NEAR Airdrops: https://near.org/airdrops/
