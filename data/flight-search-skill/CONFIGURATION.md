# ⚙️ Configuration Guide

---

## 📋 config.json Structure

```json
{
  "apis": {
    "amadeus": {
      "enabled": true,
      "base_url_test": "https://test.api.amadeus.com",
      "base_url_production": "https://api.amadeus.com",
      "api_key": "YOUR_API_KEY_HERE",
      "api_secret": "YOUR_API_SECRET_HERE",
      "sandbox_mode": true
    },
    "aviationstack": {
      "enabled": false,
      "base_url": "https://api.aviationstack.com/v1",
      "api_key": "YOUR_API_KEY_HERE"
    }
  },
  "defaults": {
    "currency": "USD",
    "locale": "en-US",
    "max_results": 20,
    "max_stops": 2
  },
  "alerts": {
    "enabled": true,
    "check_interval_hours": 6,
    "price_drop_threshold_percent": 5
  }
}
```

---

## 🔧 Configuration Options

### **Amadeus API**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable/disable Amadeus API | `true` |
| `base_url_test` | string | Test/Sandbox API URL | `https://test.api.amadeus.com` |
| `base_url_production` | string | Production API URL | `https://api.amadeus.com` |
| `api_key` | string | Your Amadeus API Key | Required |
| `api_secret` | string | Your Amadeus API Secret | Required |
| `sandbox_mode` | boolean | Use test (true) or production (false) | `true` |

### **AviationStack API**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable/disable AviationStack | `false` |
| `base_url` | string | AviationStack API URL | `https://api.aviationstack.com/v1` |
| `api_key` | string | Your AviationStack API Key | Required if enabled |

### **Defaults**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `currency` | string | Default currency (BRL, USD, EUR) | `USD` |
| `locale` | string | Default locale | `en-US` |
| `max_results` | int | Maximum results per search | `20` |
| `max_stops` | int | Maximum stops (null = any) | `2` |

### **Alerts**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `enabled` | boolean | Enable price monitoring | `true` |
| `check_interval_hours` | int | Hours between checks | `6` |
| `price_drop_threshold_percent` | int | Alert threshold (%) | `5` |

---

## 🔄 Switching Environments

### **Test/Sandbox Mode (Default)**

```json
{
  "apis": {
    "amadeus": {
      "sandbox_mode": true,
      "api_key": "YOUR_SANDBOX_KEY",
      "api_secret": "YOUR_SANDBOX_SECRET"
    }
  }
}
```

**Use for:**
- ✅ Development
- ✅ Testing
- ✅ Learning the API

**Data:**
- ❌ Test data (prices are NOT real)

---

### **Production Mode**

```json
{
  "apis": {
    "amadeus": {
      "sandbox_mode": false,
      "api_key": "YOUR_PRODUCTION_KEY",
      "api_secret": "YOUR_PRODUCTION_SECRET"
    }
  }
}
```

**Use for:**
- ✅ Real flight searches
- ✅ Actual bookings
- ✅ Production apps

**Data:**
- ✅ Real data (prices are REAL)

**Cost:**
- ✅ FREE tier available
- 💰 Pay-as-you-go for extra calls

---

## 🌍 Currency Configuration

### **Supported Currencies:**

| Currency | Code | Example |
|----------|------|---------|
| Brazilian Real | `BRL` | R$ 1.234,56 |
| US Dollar | `USD` | $ 1,234.56 |
| Euro | `EUR` | € 1.234,56 |
| British Pound | `GBP` | £ 1,234.56 |
| Japanese Yen | `JPY` | ¥ 123,456 |

### **Change Default Currency:**

```json
{
  "defaults": {
    "currency": "USD"
  }
}
```

### **Override per Search:**

```bash
# Search in USD
python3 lib/amadeus_client.py --origin GRU --destination LHR --departure 2026-03-15 --currency USD
```

---

## ⚠️ Security Best Practices

### **DO:**
- ✅ Use environment variables for API keys
- ✅ Keep `config.json` out of git (use `.gitignore`)
- ✅ Use different keys for test and production
- ✅ Rotate keys periodically

### **DON'T:**
- ❌ Commit API keys to git
- ❌ Share keys publicly
- ❌ Use production keys for testing
- ❌ Hardcode keys in scripts

---

## 🔐 Using Environment Variables

### **Create .env file:**

```bash
# .env (add to .gitignore!)
AMADEUS_API_KEY=your_key_here
AMADEUS_API_SECRET=your_secret_here
AVIATIONSTACK_API_KEY=your_key_here
```

### **Load in Python:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_API_SECRET")
```

---

## 📝 Example Configurations

### **Minimal (Sandbox Only):**

```json
{
  "apis": {
    "amadeus": {
      "api_key": "YOUR_KEY",
      "api_secret": "YOUR_SECRET",
      "sandbox_mode": true
    }
  },
  "defaults": {
    "currency": "USD"
  }
}
```

### **Full (Both APIs):**

```json
{
  "apis": {
    "amadeus": {
      "enabled": true,
      "base_url_test": "https://test.api.amadeus.com",
      "base_url_production": "https://api.amadeus.com",
      "api_key": "YOUR_KEY",
      "api_secret": "YOUR_SECRET",
      "sandbox_mode": false
    },
    "aviationstack": {
      "enabled": true,
      "base_url": "https://api.aviationstack.com/v1",
      "api_key": "YOUR_KEY"
    }
  },
  "defaults": {
    "currency": "USD",
    "locale": "en-US",
    "max_results": 20,
    "max_stops": 2
  },
  "alerts": {
    "enabled": true,
    "check_interval_hours": 6,
    "price_drop_threshold_percent": 5
  }
}
```

---

## 🧪 Testing Configuration

### **Test Amadeus Connection:**

```bash
python3 lib/amadeus_client.py --origin GRU --destination LHR --departure 2026-03-15 --max 1
```

### **Test AviationStack Connection:**

```bash
python3 lib/aviationstack_client.py --flight AA100
```

### **Expected Output:**

```json
[
  {
    "api": "amadeus",
    "price": 2500.00,
    "currency": "USD",
    "airline": "TK"
  }
]
```

---

## ❓ FAQ

**Q: Do I need to change base_url?**
- A: No! The URLs are already configured. Just change `sandbox_mode`.

**Q: Can I use both Sandbox and Production?**
- A: Yes! Create two config files or change `sandbox_mode` as needed.

**Q: Which URL is used when sandbox_mode is true?**
- A: `base_url_test` (https://test.api.amadeus.com)

**Q: Which URL is used when sandbox_mode is false?**
- A: `base_url_production` (https://api.amadeus.com)

**Q: Do I need different API keys for test and production?**
- A: Yes! Create separate apps in Amadeus dashboard.

---

**Need help?** Check SKILL.md or create an issue on GitHub!
