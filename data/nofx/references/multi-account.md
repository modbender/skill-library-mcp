# NOFX Multi-Account Management

## Multi-Account Scenarios

1. **Risk Isolation** - Different strategies use different accounts
2. **Multiple Exchanges** - Use multiple exchanges simultaneously
3. **Capital Allocation** - Spread risk
4. **Test Environment** - Main account + test account

## Configuration Methods

### Multi-Accounts on Same Exchange

Add multiple exchange configurations in Config page, distinguished by different names:

```
binance-main       → Main account
binance-test       → Test account
binance-grid       → Grid trading dedicated
```

### Multiple Exchanges

```
binance   → Primary trading
bybit     → Backup
okx       → Arbitrage
gate      → Altcoins
```

## Account Naming Suggestions

| Naming Pattern | Example | Purpose |
|----------------|---------|---------|
| `{exchange}-{purpose}` | binance-main | Distinguish purpose |
| `{exchange}-{strategy}` | binance-grid | Distinguish strategy |
| `{exchange}-{capital}` | binance-10k | Distinguish capital amount |

## Trader & Account Binding

Select corresponding account when creating Trader:

```
Trader: eth-hunter
├── AI Model: Claude
├── Exchange: binance-main    ← Select account
└── Strategy: ai500 strategy
```

## Capital Allocation Recommendations

| Account Type | Capital Ratio | Risk Level |
|--------------|---------------|-------------|
| Main Account | 50-60% | Low risk strategy |
| Aggressive Account | 20-30% | High return strategy |
| Test Account | 10-20% | New strategy testing |

## Risk Management

### Single Account Limits

- Max position: 50% of account capital
- Max single coin: 20% of account capital
- Daily loss limit: 10% of account capital

### Multi-Account Total Limits

- Total exposure: 70% of total capital
- Correlation: Avoid all accounts holding highly correlated positions
- Monitoring: View all accounts P&L in aggregate

## Dashboard Switching

Switch Trader/account in dropdown menu at top of Dashboard page:

```javascript
// Browser automation to switch account
browser.act({kind: "click", ref: "traderSelector"})
browser.act({kind: "click", ref: "targetTrader"})
```

## Multi-Account API

When calling APIs for different accounts, use corresponding API Keys:

```bash
# Account A
curl -H "Authorization: Bearer $KEY_A" ...

# Account B
curl -H "Authorization: Bearer $KEY_B" ...
```

## Sub-Account Features (Exchange)

### Binance Sub-Accounts

1. User Center → Sub-Accounts
2. Create sub-account
3. Transfer funds
4. Generate sub-account API

### OKX Sub-Accounts

1. User Center → Sub-Account Management
2. Create trading sub-account
3. Set permissions and limits

## Security Recommendations

1. **Different IP Whitelist** - Each account uses different server
2. **Independent 2FA** - Each account has independent verification
3. **Minimal Permissions** - Only enable necessary permissions
4. **Regular Auditing** - Check for abnormal trades