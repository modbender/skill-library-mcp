---
name: near-dca
description: Dollar-cost averaging for NEAR tokens with flexible scheduling, performance tracking, and cancellation support.
---
# NEAR DCA Skill

Dollar-Cost Averaging implementation for NEAR tokens.

## Description

This skill provides DCA functionality with flexible scheduling and performance tracking. Set up recurring NEAR token purchases and track performance over time.

## Features

- Create DCA plans
- Cancel DCA plans
- List all DCA plans
- Track DCA performance
- Flexible scheduling (daily, weekly, etc.)

## Commands

### `near-dca create <token> <amount> <schedule> [account]`
Create a new DCA plan.

**Parameters:**
- `token` - Token to buy (e.g., NEAR, USDT)
- `amount` - Amount per purchase
- `schedule` - Schedule: daily, weekly, biweekly, monthly
- `account` - Account ID (optional, uses default)

**Example:**
```bash
near-dca create USDT 10 daily myaccount.near
```

### `near-dca list [account]`
List all DCA plans for an account.

### `near-dca cancel <plan_id>`
Cancel a DCA plan.

### `near-dca performance <plan_id>`
Show performance for a DCA plan.

### `near-dca history <plan_id>`
Show purchase history for a plan.

## Configuration

DCA plans are stored in `~/.near-dca/plans.json`.

## Notes

- DCA execution requires integration with a DEX (e.g., Ref Finance)
- Scheduling requires cron or a job scheduler
- Track performance vs lump-sum investment

## References

- NEAR DeFi: https://near.org/defi/
- Ref Finance: https://ref.finance/
