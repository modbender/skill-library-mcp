# Flight Search Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ClawHub](https://img.shields.io/badge/ClawHub-Publish-green.svg)](https://clawhub.ai)

Search flights, compare prices, and monitor airfare using Amadeus API with price drop alerts.

---

## ✨ Features

- ✅ **Flight Search** - Search flights via Amadeus API
- ✅ **Price Comparison** - Compare prices across airlines
- ✅ **Flexible Dates** - Search across date ranges
- ✅ **Price Monitoring** - Track prices and get alerts
- ✅ **Flight Status** - Real-time flight tracking (AviationStack)
- ✅ **Multi-City Routes** - Support for complex itineraries
- ✅ **Filters** - Filter by stops, airline, duration, class
- ✅ **Currency Support** - Multiple currencies (BRL, USD, EUR, etc.)

---

## 🚀 Quick Start

### 1. Get API Keys

**Amadeus (Required):**
1. Visit: https://developers.amadeus.com
2. Create account (FREE)
3. Create new app
4. **Choose environment:**
   - **Test/Sandbox** (FREE) - ⚠️ Test data only (prices are not real)
   - **Production** (FREE tier + pay-as-you-go) - ✅ Real prices!
5. Copy API Key and API Secret

**✅ GREAT NEWS:** 
- **Both environments have FREE tiers!**
- **Test:** 2,000 flight searches/month FREE
- **Production:** FREE quota + pay only for extra calls
- **Production has REAL prices** (not test data)
- **Bonus:** 90% discount if you create bookings!

**⚠️ IMPORTANT:** 
- **Sandbox mode** uses test data - prices shown are **NOT real**
- For **real flight prices**, use **Production** (also has free tier!)
- AviationStack free tier (100 requests/month) provides real flight status data

**AviationStack (Optional - for flight status):**
1. Visit: https://aviationstack.com
2. Sign up for free tier (100 requests/month)
3. Copy API Key

### 2. Configure

**⚠️ SECURITY: Never commit API keys to git!**

```bash
# 1. Copy example config (DO NOT edit config.example.json directly!)
cp config.example.json config.json

# 2. Edit config.json with your API keys
nano config.json
```

Edit `config.json`:

```json
{
  "apis": {
    "amadeus": {
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    },
    "aviationstack": {
      "enabled": false,
      "api_key": "YOUR_API_KEY"
    }
  }
}
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions!**

### 3. Use

```bash
# Search flights
./scripts/search_flights.sh GRU LHR 2026-03-15

# Check flight status
./scripts/check_status.sh AA100

# Monitor prices
./scripts/monitor_price.sh CNF BKK 2026-12-15 2027-01-10
```

---

## 📖 Documentation

- **QUICKSTART.md** - 🚀 **START HERE** - Step-by-step setup guide
- **CONFIGURATION.md** - ⚙️ Configuration guide - How to configure APIs, currencies, environments
- **PRICING.md** - 💰 **MUST READ** - Amadeus pricing explained (Production is FREE too!)
- **WARNINGS.md** - ⚠️ **IMPORTANT** - API keys and data accuracy
- **SKILL.md** - Full documentation
- **SECURITY.md** - 🔒 Security audit and vulnerability fixes
- **examples/** - Usage examples
- **config.example.json** - Example configuration file

---

## 🔧 API Information

| API | Coverage | Free Tier | Best For | Security |
|-----|----------|-----------|----------|----------|
| **Amadeus** | Global | ✅ 2,000/month (Sandbox & Production!) | Flight search, prices | ✅ HTTPS |
| **AviationStack** | Global | 100/month ⚠️ | Flight status | ✅ HTTPS |

**✅ BONUS:** Amadeus Production also has FREE tier (not just Sandbox)!
**🔒 SECURITY:** All API communications use HTTPS encryption!

---

## 💡 Use Cases

- **Personal Travel** - Find best prices for your trips
- **Price Monitoring** - Track routes and get alerts on price drops
- **Flight Status** - Check real-time flight information
- **Trip Planning** - Compare routes, airlines, and schedules
- **Business Travel** - Optimize corporate travel costs

---

## 🌟 Why This Skill?

| Feature | This Skill | Others |
|---------|-----------|--------|
| **API** | Amadeus (official) | Google Flights (scraping) |
| **Price Monitoring** | ✅ Yes | ❌ No |
| **Flight Status** | ✅ Yes | ❌ No |
| **Documentation** | ✅ Complete | ⚠️ Basic |
| **Templates** | ✅ 3 templates | ❌ No |
| **Scripts** | ✅ 3 scripts | ❌ No |
| **Free Tier** | ✅ Yes (Production too!) | Varies |
| **Real Prices** | ✅ Yes (Production) | Varies |
| **Security** | ✅ Audited & Secure | ⚠️ Unknown |

---

## 📊 Examples

### Search Flights
```bash
./scripts/search_flights.sh JFK LHR 2026-03-15
```

### Round-Trip
```bash
./scripts/search_flights.sh CNF BKK 2026-12-15 2027-01-10
```

### Flight Status
```bash
./scripts/check_status.sh AA100
```

### Monitor Prices
```bash
./scripts/monitor_price.sh GRU CDG 2026-06-01 2026-06-15
```

---

## 🛠️ Technical Details

**Structure:**
```
flight-search-skill/
├── SKILL.md              # Documentation
├── LICENSE               # MIT License
├── config.json           # API configuration
├── scripts/              # Shell scripts
│   ├── search_flights.sh
│   ├── monitor_price.sh
│   └── check_status.sh
├── lib/                  # Python libraries
│   ├── amadeus_client.py
│   └── aviationstack_client.py
├── templates/            # Response templates
│   ├── results.md
│   ├── alert.md
│   └── status.md
└── examples/             # Usage examples
    ├── basic_search.md
    ├── advanced_search.md
    └── monitoring.md
```

**Requirements:**
- Python 3.7+
- `requests` library
- Amadeus API credentials

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- **Amadeus for Developers**: https://developers.amadeus.com
- **AviationStack**: https://aviationstack.com
- **Created by**: Marco Rabelo
- **ClawHub**: https://clawhub.ai

---

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/marco-rabelo/flight-search-skill/issues)
- **ClawHub**: https://clawhub.ai/skills/flight-search
- **Documentation**: See `SKILL.md`

---

**Made with ❤️ for the OpenClaw community**
