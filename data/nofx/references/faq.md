# NOFX Frequently Asked Questions (FAQ)

## Installation & Deployment

### Q: What to do if installation fails?

**Checklist:**
1. Is Docker installed and running?
2. Is port 3000 occupied?
3. Can network access GitHub?

**Solutions:**
```bash
# Check Docker
docker --version

# Check port
lsof -i :3000

# Manually pull image
docker pull nofxai/nofx:latest
```

### Q: How to update to latest version?

```bash
# Re-run installation script
curl -fsSL https://raw.githubusercontent.com/NoFxAiOS/nofx/main/install.sh | bash
```

### Q: Will data be lost?

No. Data is stored in Docker volume, updates don't affect data.

---

## API Issues

### Q: API returns 403 Forbidden?

**Reasons:**
1. API Key invalid or expired
2. Request rate exceeded (>30/s)
3. IP temporarily banned

**Solutions:**
1. Check if API Key is correct
2. Reduce request frequency
3. Wait a few minutes then retry

### Q: Where to get API Key?

Visit https://nofxos.ai/api-docs, displayed at top of page.

### Q: API request timeout?

1. Check network connection
2. Use proxy (if necessary)
3. Increase timeout duration

---

## Exchange Configuration

### Q: Error after configuring API Key?

**Check:**
1. Are API Key and Secret copied completely
2. Are permissions enabled (read + trade)
3. Is IP whitelist configured
4. OKX requires additional Passphrase

### Q: Why "Insufficient Balance" error?

1. Account balance insufficient
2. Margin insufficient
3. Position limit exceeded

### Q: Does it support demo trading?

Some exchanges support it:
- Binance: Need to apply for testnet API
- Bybit: Supports demo trading mode
- OKX: Supports demo trading

---

## Strategy Issues

### Q: Strategy doesn't trigger trades?

**Check:**
1. Is Trader started?
2. Is strategy activated?
3. Are market conditions met?
4. Check AI decision logs

### Q: How to optimize strategy?

1. Backtest different parameters
2. Analyze historical trades
3. Adjust risk control parameters
4. Reference AI suggestions

### Q: What to do if strategy loses money?

1. Check strategy logic
2. Analyze loss reasons
3. Reduce position/leverage
4. Consider pausing trading

---

## Trader Issues

### Q: Trader fails to start?

**Common reasons:**
1. Exchange API configuration error
2. AI model API Key invalid
3. Strategy configuration issues

**Troubleshooting steps:**
1. Check Trader logs
2. Verify exchange connection
3. Test AI model response

### Q: Trader doesn't place orders?

1. Check account balance
2. Check AI decision logs
3. Confirm market conditions
4. Check risk control limits

### Q: How to view Trader logs?

Dashboard → Select Trader → View AI Decision Logs

---

## Grid Trading

### Q: Grid profit not ideal?

1. Check price range settings
2. Adjust grid quantity
3. Consider if market suits grid

### Q: What if price breaks boundaries?

1. System auto stop-loss (if configured)
2. Manually adjust boundaries
3. Consider pausing grid

### Q: Do grid and AI strategy conflict?

No conflict. Can run simultaneously:
- Grid strategy for ranging
- AI strategy for trending

---

## Security Issues

### Q: Is funding safe?

1. NOFX doesn't custody funds
2. Funds always remain at exchange
3. Recommend disabling withdrawal permissions
4. Use IP whitelist

### Q: How to protect API Key?

1. Don't share API Key
2. Enable IP whitelist
3. Regularly change Key
4. Use sub-accounts

### Q: Discovered abnormal trades?

1. Immediately stop Trader
2. Check exchange account
3. Change API Key
4. Check server security

---

## Performance Issues

### Q: System is slow?

1. Check server resources
2. Reduce concurrent Traders
3. Clear historical logs
4. Consider upgrading configuration

**Recommended configuration:**
- CPU: 2 cores+
- Memory: 4GB+
- Storage: 20GB+

### Q: High latency?

1. Choose server close to exchange
2. Use low-latency network
3. Reduce unnecessary data requests

---

## Other Issues

### Q: How to join community?

- Telegram: https://t.me/nofx_dev_community
- Twitter: https://x.com/nofx_official
- GitHub: https://github.com/NoFxAiOS/nofx

### Q: How to report bugs?

GitHub Issues: https://github.com/NoFxAiOS/nofx/issues

### Q: Are there tutorial videos?

Check pinned messages in official Twitter and Telegram groups.

### Q: Is it free?

NOFX is completely open source and free.
- Exchange fees are your responsibility
- AI API costs are your responsibility
- Server costs are your responsibility