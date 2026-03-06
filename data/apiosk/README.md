# Apiosk AgentSkill

**Keyless API access with USDC micropayments for OpenClaw agents.**

Pay-per-request for production APIs. No API keys. No accounts. Just pay and call.

---

## 🚀 Quick Start

```bash
# Install via ClawHub
clawhub install apiosk

# Or clone manually
git clone https://github.com/apiosk/apiosk-skill ~/.openclaw/skills/apiosk
cd ~/.openclaw/skills/apiosk

# Setup wallet (one-time)
./setup-wallet.sh

# Fund your wallet with USDC on Base mainnet
# https://bridge.base.org

# List available APIs
./list-apis.sh

# Call an API
./call-api.sh weather --params '{"city": "Amsterdam"}'
```

---

## 📚 Documentation

See [SKILL.md](./SKILL.md) for complete documentation:
- Configuration
- Available APIs
- Usage examples (Node.js, Python, bash)
- Helper scripts
- Troubleshooting

---

## 🔐 Security Notice

**Before using this skill:**

1. **Private key storage:** The wallet's private key is stored in plaintext in `~/.apiosk/wallet.json` (with chmod 600 permissions). This is suitable for testing but NOT for production with large amounts.

2. **Recommended for production:**
   - Use a hardware wallet (Ledger, Trezor)
   - Or use an external key management service
   - Only fund test wallet with small amounts ($1-10)

3. **Foundry installation:** This skill requires Foundry (cast command). Install it manually:
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

4. **Gateway verification:** All payments are verified on-chain by the gateway. Your private key is NEVER sent to the gateway.

5. **Test first:** Try with a small API call before funding with larger amounts.

---

## 🔧 Gateway Changes Needed

See [GATEWAY_CHANGES_NEEDED.md](./GATEWAY_CHANGES_NEEDED.md) for:
- Required API endpoints
- Database migrations
- Implementation guide

**TL;DR:** Gateway needs 3 new endpoints:
1. `GET /v1/apis` - List available APIs
2. `GET /v1/balance` - Check wallet balance
3. `GET /v1/usage` - Usage statistics

---

## 📦 Files

```
apiosk-skill/
├── SKILL.md                    # Main documentation
├── README.md                   # This file
├── GATEWAY_CHANGES_NEEDED.md   # Implementation guide
├── package.json                # NPM metadata
├── setup-wallet.sh             # Wallet setup (one-time)
├── list-apis.sh                # List available APIs
├── call-api.sh                 # Call any API
├── check-balance.sh            # Check USDC balance
├── usage-stats.sh              # View usage stats
├── apiosk-client.js            # Node.js wrapper
└── apiosk_client.py            # Python wrapper
```

---

## 🎯 What This Enables

**For Agents:**
- Access 9+ production APIs instantly
- Pay per request ($0.001-0.10)
- No API key management
- Automatic USDC micropayments

**For Developers:**
- Monetize any API via Apiosk
- 90-95% revenue share
- No payment processing
- Instant settlement

**Network effect:** More APIs → More agents → More revenue → More APIs

---

## 🌐 Links

- **Website:** https://apiosk.com
- **Dashboard:** https://dashboard.apiosk.com
- **Docs:** https://docs.apiosk.com
- **ClawHub:** https://clawhub.com/apiosk
- **Moltbook:** @ApioskAgent

---

## 🦞 About

Built by Apiosk for the agent economy.

**Mission:** Make every API instantly accessible to every agent.

---

## 📝 License

MIT
