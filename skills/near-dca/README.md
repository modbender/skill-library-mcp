# NEAR DCA Skill

Automated Dollar Cost Averaging (DCA) for NEAR token purchases.

## Features

- 📊 **Multiple DCA Strategies** - Create and manage multiple DCA strategies with different parameters
- ⏰ **Flexible Scheduling** - Support for hourly, daily, weekly, and monthly purchase intervals
- 💱 **Multiple Exchanges** - Integration with Ref Finance, Jumbo, Bancor, and on-chain swaps
- 📈 **Cost Basis Tracking** - Automatic calculation of average cost basis across all purchases
- 📜 **Full History** - Complete execution history for audit and analysis
- 🔔 **Alerts** - Configurable notifications on successful and failed executions
- ⏯️ **Pause/Resume** - Temporary halt strategies without deleting them

## Installation

```bash
cd C:\Users\Shai\.openclaw\skills\near-dca
npm install
```

## Configuration

The skill uses the following configuration options (set in your OpenClaw config):

```yaml
near-dca:
  network: mainnet
  default_exchange: ref-finance
  account_id: your-account.near
  private_key: your-private-key  # Or use secure credential storage
  storage_path: ./data/dca_state.json
```

## Usage

### Create a DCA Strategy

```javascript
{
  "action": "create-strategy",
  "params": {
    "name": "Weekly NEAR Buy",
    "amount": 50,
    "frequency": "weekly",
    "exchange": "ref-finance",
    "start_date": "2024-02-01",
    "end_date": "2024-12-31"
  }
}
```

**Frequency Options:**
- `hourly` - Execute every hour
- `daily` - Execute once per day
- `weekly` - Execute once per week
- `monthly` - Execute once per month

**Exchange Options:**
- `ref-finance` - Ref Finance DEX
- `jumbo` - Jumbo Exchange
- `bancor` - Bancor Network
- `on-chain` - Direct on-chain swaps

### List All Strategies

```javascript
{
  "action": "list-strategies",
  "params": {}
}
```

### Get Strategy Details

```javascript
{
  "action": "get-strategy",
  "params": {
    "strategy_id": "uuid-here"
  }
}
```

### Execute a Manual Purchase

```javascript
{
  "action": "execute-purchase",
  "params": {
    "strategy_id": "uuid-here"
  }
}
```

### Pause a Strategy

```javascript
{
  "action": "pause-strategy",
  "params": {
    "strategy_id": "uuid-here"
  }
}
```

### Resume a Strategy

```javascript
{
  "action": "resume-strategy",
  "params": {
    "strategy_id": "uuid-here"
  }
}
```

### Delete a Strategy

```javascript
{
  "action": "delete-strategy",
  "params": {
    "strategy_id": "uuid-here"
  }
}
```

### Get Execution History

```javascript
{
  "action": "get-history",
  "params": {
    "strategy_id": "uuid-here",  // Optional - filters by strategy
    "limit": 50
  }
}
```

### Calculate Cost Basis

```javascript
{
  "action": "calculate-cost-basis",
  "params": {
    "strategy_id": "uuid-here"  // Optional - calculates for all if omitted
  }
}
```

**Response Example:**
```json
{
  "strategyId": "uuid-here",
  "strategyName": "Weekly NEAR Buy",
  "totalInvested": 500.00,
  "totalNear": 75.1234,
  "averagePrice": 6.6543,
  "purchaseCount": 10,
  "currentPrice": 6.5200
}
```

### Configure Alerts

```javascript
{
  "action": "configure-alerts",
  "params": {
    "strategy_id": "uuid-here",  // Optional - applies to all if omitted
    "enabled": true,
    "channels": ["discord", "telegram"],
    "on_success": true,
    "on_failure": true
  }
}
```

**Available Channels:**
- `discord` - Send to Discord channel
- `telegram` - Send to Telegram chat
- `email` - Send via email

## Automatic Execution

The skill includes a scheduled trigger that automatically executes due purchases:

```yaml
triggers:
  - type: schedule
    name: dca-executor
    schedule: "*/5 * * * *"  # Check every 5 minutes
    action: execute-scheduled-purchases
```

The trigger runs every 5 minutes and executes any strategies whose next execution time has arrived.

## Data Storage

All strategy data and execution history is stored in a JSON file at `./data/dca_state.json`. This includes:

- Active strategies with their configuration
- Execution history (limited to 1000 entries)
- Alert configurations

## Security Notes

⚠️ **Important:** Store private keys securely using OpenClaw's credential management rather than in plain text configuration.

## Cost Basis Calculation

The skill calculates the true average cost basis:

```
Average Price = Total USD Invested / Total NEAR Accumulated

Example:
- 10 purchases of $50 each = $500 total invested
- 75.1234 NEAR accumulated
- Average Price = $500 / 75.1234 = $6.6543
```

This accounts for:
- Actual execution prices at purchase time
- All transaction fees
- Slippage from DEX operations

## Error Handling

The skill gracefully handles:

- Network failures
- Price feed issues
- Insufficient balance
- Exchange downtime
- Transaction failures

All errors are logged in the execution history and trigger failure alerts if configured.

## Testing

Run the test suite:

```bash
npm test
```

## License

MIT

## Support

For issues and questions, contact the skill maintainer or file an issue on the repository.
