# Beecli Command Reference

## Installation

```bash
npm i -g @beelabs/beetrade-cli
```

## Usage

```bash
beecli [command]
```

## Configuration

The CLI stores configuration in `~/.beecli/config.json`:

- `apiUrl` - API base URL (default: `https://api.prod.beetrade.com/api/v2`)
- `accessToken` - Authentication token
- `refreshToken` - Token refresh credential
- `email` - Logged in user email

## Commands

### Authentication

```bash
# Login with email and password
beecli auth login -e <email> -p <password>

# Logout and clear credentials
beecli auth logout

# Show authentication status
beecli auth status
```

### Bots

```bash
# List all bots
beecli bots list [--page 1] [--page-size 20] [--status <status>] [--type-id <id>]

# Get bot details
beecli bots get <id>

# Create a new bot
beecli bots create -t <type-id> -c '<json-config>'

# Update a bot
beecli bots update <id> [-n <name>] [-s <status>] [-c '<json-config>']

# Delete a bot
beecli bots delete <id>

# Get bot runtime status
beecli bots status <id>

# Start paper trading
beecli bots run paper <id> -b <brokerage-id> -c <cash>

# Start live trading
beecli bots run live <id> -a <brokerage-account-id>

# Run backtest
beecli bots backtest <id> -b <brokerage-id> -c <cash> --from <YYYY-MM-DD> --to <YYYY-MM-DD>

# List available bot types
beecli bots types
```

### Market Data

```bash
# List symbols for a brokerage
beecli market symbols -b <brokerage-id> [--page 1] [--per-page 50] [-n <name>] [--sort-by <field>] [--include-brokerage]

# Get OHLCV historical data
beecli market history -s <symbol> --from <iso-datetime> --to <iso-datetime> -i <interval>

# Intervals: 1m, 5m, 15m, 1h, 4h, 1d, 1w
beecli market history -s BTCUSDT --from 2024-01-01T00:00:00Z --to 2024-01-31T23:59:59Z -i 1h
```

### Portfolio

```bash
# Get portfolio summary
beecli portfolio summary -c <currency> [-p <provider>] [-t <trading-client-id>]

# Get portfolio analysis
beecli portfolio analysis

# Get total assets
beecli portfolio total-assets -c <currency>

# Get assets summary over time
beecli portfolio assets-summary -c <currency> -p <days> [--provider <provider>] [-t <trading-client-id>]
```

### Watchlists

```bash
# List all watchlists
beecli watchlists list [--page 1] [--page-size 20]

# Get watchlist details
beecli watchlists get <id>

# Create a new watchlist
beecli watchlists create -n <name>

# Delete a watchlist
beecli watchlists delete <id>

# Get items in a watchlist
beecli watchlists items <id>
```

### Trading

```bash
# Get live trade status
beecli trading status <strategy-id> [--paper]

# Get live trade details
beecli trading detail <strategy-id> [--paper]

# Stop a live trade
beecli trading stop <strategy-id> [--paper]
```

### Strategies

```bash
# List all strategies
beecli strategies list [--page 1] [--page-size 20] [-k <keyword>]

# Get strategy details
beecli strategies get <id>

# Create a new strategy
beecli strategies create -n <name> -d '<json-data>' [--description <description>]

# Update a strategy
beecli strategies update <id> [-n <name>] [-d '<json-data>'] [--description <description>]

# Delete a strategy
beecli strategies delete <id>

# Run strategy backtest
beecli strategies backtest <id> -b <brokerage-id> -c <cash> --from <YYYY-MM-DD> --to <YYYY-MM-DD>

# Start paper trading
beecli strategies paper <id> -b <brokerage-id> -c <cash>

# Start live trading
beecli strategies live <id> -a <brokerage-account-id>

# Schedule a strategy
beecli strategies schedule <id> -e '<cron-expression>'

# Get strategy schedule info
beecli strategies schedule-info <id>

# Delete a schedule
beecli strategies schedule-delete <schedule-id>

# List strategy alerts
beecli strategies alerts <id>

# Create strategy alert
beecli strategies create-alert <id> -c '<json-config>'

# Update strategy alert
beecli strategies update-alert <id> <alert-id> -c '<json-config>'

# Delete strategy alert
beecli strategies delete-alert <id> <alert-id>

# List strategy versions
beecli strategies versions <id> [--page 1] [--page-size 20]

# Rollback strategy to version
beecli strategies rollback <id> <version-id>

# Get strategy execution history
beecli strategies history <id> [--page 1] [--page-size 20] [--status <status>]

# Optimize strategy parameters using ML
beecli strategies optimize <id> -c '<json-config>'
```

### Alerts

```bash
# List all alerts
beecli alerts list [--page 1] [--page-size 20] [-k <keyword>] [--status <true/false>] [-b <brokerage-id>]

# Get alert details
beecli alerts get <id>

# Create a new alert
beecli alerts create -c '<json-config>'

# Update an alert
beecli alerts update <id> -c '<json-config>'

# Delete an alert
beecli alerts delete <id>

# Toggle alert status
beecli alerts toggle <id> --active <true/false>
```

### Brokerages

```bash
# List all brokerages
beecli brokerages list [--page 1] [--page-size 20] [--search <keyword>] [--all] [-l <lang>]

# Get brokerage by code
beecli brokerages get <code> [-l <lang>]

# Get brokerages available for live trading
beecli brokerages live-trade [-l <lang>]
```

### Accounts

```bash
# List all brokerage accounts
beecli accounts list [-t <trading-client-id>] [-l <lang>]

# Get accounts grouped by trading client
beecli accounts grouped [-l <lang>]

# Get brokerage account details
beecli accounts get <id> [-l <lang>]

# Create a new brokerage account
beecli accounts create <brokerage-id> [-l <lang>]

# Update brokerage account credentials
beecli accounts update <id> -c '<json-credentials>' [-l <lang>]

# Delete a brokerage account
beecli accounts delete <id> [-l <lang>]

# Get account balance
beecli accounts balance <id>
```

### Clients

```bash
# List all trading clients
beecli clients list [-l <lang>]

# Create a new trading client
beecli clients create -n <name> [-d <description>] [-l <lang>]

# Update a trading client
beecli clients update <id> [-n <name>] [-d <description>] [-l <lang>]

# Delete a trading client
beecli clients delete <id> [-l <lang>]
```

## Output Format

Command actions generally return JSON suitable for scripting. Note: help/usage/argument validation output from Commander may not be JSON.

```bash
beecli auth status
# {"authenticated": true, "email": "user@example.com", "apiUrl": "https://api.prod.beetrade.com/api/v2"}

beecli bots list
# {"data": [...], "page": 1, "pageSize": 20, "total": 100}
```
