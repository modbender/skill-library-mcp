# 📦 ClawHub Skill Submission

## Skill Information

**Skill Name:** Crypto Transaction Analyzer  
**Skill ID:** crypto-scam-detector  
**Version:** 1.0.0  
**Team:** Trust Claw  
**Hackathon:** NeoClaw Hackathon 2026  

---

## Team Information

**Team Name:** trust-claw  
**Instance:** neoclaw-trustclaw  
**Instance IP:** 3.82.242.14  
**Team Member:** Prince Punniyadoss  

---

## Skill Description

Real-time cryptocurrency scam detection using multi-source verification. Protects OpenClaw users from phishing, honeypots, rug pulls, and ponzi schemes by analyzing crypto addresses, transactions, and smart contracts.

### Key Features:
- Multi-source verification (local DB + ChainAbuse API)
- Real-time scam detection
- Pattern analysis for unknown addresses
- Honeypot and rug pull detection
- Confidence scoring (0-100)
- Risk level assessment (low/medium/high/critical)

---

## Technical Details

**Type:** MCP Server  
**Language:** Python 3.8+  
**Framework:** FastAPI  
**Port:** 5000  
**Transport:** HTTP  

**MCP Endpoint:** `http://localhost:5000/mcp`  
**Health Check:** `http://localhost:5000/health`  

---

## Installation

### Requirements:
- Python 3.8 or higher
- pip
- Virtual environment support (python3-venv)

### Quick Install:
```bash
./install.sh
```

### Manual Install:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python mcp_server.py
```

---

## Configuration

### Required:
- None (works out of the box)

### Optional:
- `ETHERSCAN_API_KEY` - For enhanced transaction analysis
  - Get free at: https://etherscan.io/myapikey
  - 5 calls/sec, 100,000 calls/day on free tier

---

## Methods

### 1. analyze_address
Analyze cryptocurrency address for scam indicators

**Parameters:**
- `address` (string, required) - Address to check (0x...)
- `chain` (string, optional) - Blockchain (default: "ethereum")

**Returns:** Risk score, scam indicators, recommendations

### 2. analyze_transaction
Analyze transaction for suspicious activity

**Parameters:**
- `from` (string) - Sender address
- `to` (string) - Recipient address
- `value` (string) - Transaction value in wei

**Returns:** Risk assessment and recommendations

### 3. check_contract
Check smart contract for scam patterns

**Parameters:**
- `contract_address` (string, required) - Contract to check
- `chain` (string, optional) - Blockchain

**Returns:** Honeypot detection, risk factors

---

## Data Sources

1. **Local Database** - 6+ curated known scams
2. **ChainAbuse.com** - Community-reported scams (real-time)
3. **Pattern Analysis** - Algorithmic detection

**Optional:**
4. **Etherscan API** - Transaction history (with API key)

---

## Testing

### Health Check:
```bash
curl http://localhost:5000/health
```

Expected: `{"status":"healthy","database":{"addresses":6,"domains":7}}`

### Test Scam Detection:
```bash
curl -X POST http://localhost:5000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"analyze_address","params":{"address":"0x1234567890abcdef1234567890abcdef12345678"}}'
```

Expected: Risk score 100 (known phishing address)

### Test Via OpenClaw:
```
Ask: "Is 0x1234567890abcdef1234567890abcdef12345678 a scam?"
Expected: Critical risk warning with details
```

---

## Files Included

- `clawhub-manifest.json` - ClawHub metadata
- `package.json` - Package information
- `README.md` - Full documentation
- `LICENSE` - MIT License
- `requirements.txt` - Python dependencies
- `install.sh` - Installation script
- `mcp_server.py` - FastAPI MCP server
- `crypto_analyzer.py` - Core analysis logic
- `scam_database.py` - Known scam database
- `.gitignore` - Git exclusions
- `SUBMISSION.md` - This file

---

## Deployment Status

✅ **Currently Running:**
- Instance: neoclaw-trustclaw (3.82.242.14)
- Port: 5000
- Status: Active (systemd service)
- Uptime: Stable

✅ **Tested:**
- Health endpoint: Working
- MCP endpoint: Working
- All 3 methods: Working
- Real-time API: Working (ChainAbuse)

---

## Integration with OpenClaw

### Current Status:
- ✅ MCP server running and accessible
- ✅ All methods tested and working
- 📋 Ready for ClawHub registration

### For ClawHub Registration:

**Recommended Config:**
```json
{
  "mcp": {
    "servers": {
      "crypto-scam-detector": {
        "command": "/home/ubuntu/crypto-skill/venv/bin/python",
        "args": ["/home/ubuntu/crypto-skill/mcp_server.py"],
        "cwd": "/home/ubuntu/crypto-skill",
        "env": {
          "ETHERSCAN_API_KEY": "V6FR6FXRTZJ4W7YCZIDTYSBG1365TK243A"
        }
      }
    }
  }
}
```

---

## Use Cases

### For Users:
- Check addresses before sending funds
- Verify smart contracts before interacting
- Get real-time scam alerts
- Protect against phishing

### For DeFi:
- Wallet safety checks
- dApp integration
- Transaction validation
- Contract verification

### For Security:
- Scam tracking
- Pattern analysis
- Threat intelligence
- Community protection

---

## Demo Script

**Show:**
1. "What skills do you have?" → Lists crypto analyzer
2. "Is 0x1234... a scam?" → Shows CRITICAL warning
3. "Check 0x742d..." → Shows LOW risk
4. Explain multi-source verification

**Talk Points:**
- Real-time API integration (not static database)
- Multi-source verification for accuracy
- Pattern analysis for unknown addresses
- Production-ready architecture
- Expandable to more chains

---

## Future Enhancements

- [ ] Support for BSC, Polygon, Arbitrum
- [ ] More data sources (CryptoScamDB, Elliptic)
- [ ] Machine learning pattern detection
- [ ] Real-time blockchain monitoring
- [ ] User-submitted reports
- [ ] Webhook notifications

---

## License

MIT License - Open source and free to use

---

## Contact

**Team:** Trust Claw  
**Email:** team@trustclaw.dev  
**Instance:** neoclaw-trustclaw  
**Hackathon:** NeoClaw 2026  

---

## Acknowledgments

**Built with:**
- FastAPI - Modern Python framework
- httpx - Async HTTP client
- ChainAbuse API - Community scam reports
- Etherscan API - Blockchain data

**Thanks to:**
- NeoClaw Hackathon organizers
- Gen Digital's Agent Trust Hub team
- OpenClaw community

---

**✅ Ready for ClawHub Publication!**

