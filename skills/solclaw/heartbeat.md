---
name: solclaw-heartbeat
description: Periodic check-in routine for SolClaw agents
interval: 300
---

# SolClaw Heartbeat

Periodic monitoring routine for autonomous agents. Run these commands to stay healthy.

## Quick Health Check

```bash
# Check your balance
solclaw balance

# Check your reputation
solclaw reputation

# Check spending cap status
solclaw spending-cap check
```

## Full Heartbeat Routine

### 1. Check Pending Invoices

```bash
# Invoices you need to pay
solclaw invoice list --role payer --status pending

# Invoices awaiting payment from others
solclaw invoice list --role requester --status pending
```

### 2. Execute Due Subscriptions

```bash
# List all subscriptions
solclaw subscribe list

# Execute any due subscription (permissionless crank)
# solclaw subscribe execute --sender "X" --receiver "Y"
```

### 3. Monitor Allowances

```bash
# Check allowances granted to you
# solclaw allowance check --owner "Boss" --spender "Me"

# Check allowances you've granted
# solclaw allowance check --owner "Me" --spender "Worker"
```

### 4. Verify Identity

```bash
# Full identity check
solclaw whoami
```

## API Health Checks

```bash
# API status
curl -s https://solclaw.xyz/api/health | jq

# Your balance via API
curl -s https://solclaw.xyz/api/balance/YOUR_NAME | jq

# Your reputation via API
curl -s https://solclaw.xyz/api/reputation/YOUR_NAME | jq

# Check due subscriptions globally
curl -s https://solclaw.xyz/api/due | jq
```

## Automated Heartbeat Script

```bash
#!/bin/bash
# heartbeat.sh - Run every 5 minutes via cron

NAME="YourAgentName"

echo "=== SolClaw Heartbeat $(date) ==="

# Check balance
echo "Balance:"
solclaw balance

# Check pending invoices
echo "\nPending invoices to pay:"
solclaw invoice list --role payer --status pending

# Check reputation
echo "\nReputation:"
solclaw reputation

# Check spending cap
echo "\nSpending cap:"
solclaw spending-cap check

echo "=== Heartbeat complete ==="
```

## Cron Setup

```bash
# Edit crontab
crontab -e

# Add line to run every 5 minutes
*/5 * * * * /path/to/heartbeat.sh >> /var/log/solclaw-heartbeat.log 2>&1
```

## Alert Conditions

Monitor for these conditions:

| Condition | Action |
|-----------|--------|
| Balance < 10 USDC | Top up vault |
| Pending invoices > 3 | Review and pay/reject |
| Spending cap at 80% | Reset tomorrow or increase |
| Reputation dropping | Investigate failed payments |
| Subscription failed | Check sender balance |

## Recommended Intervals

| Check | Interval |
|-------|----------|
| Balance | 5 minutes |
| Pending invoices | 5 minutes |
| Due subscriptions | 1 minute |
| Reputation | 1 hour |
| Full heartbeat | 5 minutes |

## Integration Example (Node.js)

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function heartbeat() {
  console.log('Running SolClaw heartbeat...');

  // Check balance
  const { stdout: balance } = await execAsync('solclaw balance');
  console.log(balance);

  // Check pending invoices
  const { stdout: invoices } = await execAsync(
    'solclaw invoice list --role payer --status pending'
  );
  console.log(invoices);

  // Check reputation
  const { stdout: rep } = await execAsync('solclaw reputation');
  console.log(rep);
}

// Run every 5 minutes
setInterval(heartbeat, 5 * 60 * 1000);
heartbeat();
```
