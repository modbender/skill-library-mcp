# 🚀 Quick Start Guide

---

## ⚠️ IMPORTANT: Setup Steps

### **Step 1: Create Your Config File**

**NEVER commit API keys to git!** Follow these steps:

```bash
# 1. Copy the example config
cp config.example.json config.json

# 2. Edit with your API keys
nano config.json  # or your favorite editor

# 3. Verify config.json is in .gitignore (it should be!)
git status
# config.json should NOT appear in tracked files
```

---

## 📋 Getting API Keys

### **Amadeus (Required)**

1. Visit: https://developers.amadeus.com
2. Create FREE account
3. Create new app
4. **Choose environment:**
   - **Test/Sandbox** (FREE) - Test data only
   - **Production** (FREE tier + pay-as-you-go) - Real prices!
5. Copy API Key and API Secret
6. Paste in `config.json`

### **AviationStack (Optional)**

1. Visit: https://aviationstack.com
2. Sign up for FREE tier (100 requests/month)
3. Copy API Key
4. Paste in `config.json`
5. Set `"enabled": true`

---

## 🔧 Editing config.json

**Minimal Config (Sandbox/Test):**

```json
{
  "apis": {
    "amadeus": {
      "api_key": "YOUR_SANDBOX_KEY",
      "api_secret": "YOUR_SANDBOX_SECRET",
      "sandbox_mode": true
    }
  }
}
```

**Full Config (Production + Flight Status):**

```json
{
  "apis": {
    "amadeus": {
      "api_key": "YOUR_PRODUCTION_KEY",
      "api_secret": "YOUR_PRODUCTION_SECRET",
      "sandbox_mode": false
    },
    "aviationstack": {
      "enabled": true,
      "api_key": "YOUR_AVIATIONSTACK_KEY"
    }
  },
  "defaults": {
    "currency": "USD"
  },
  "alerts": {
    "price_drop_threshold_percent": 10
  }
}
```

---

## 🧪 Testing Your Setup

### **Test Amadeus:**

```bash
./scripts/search_flights.sh JFK LHR 2026-03-15
```

**Expected:**
- ✅ Returns flight results (test data in sandbox, real in production)
- ✅ No authentication errors

### **Test AviationStack:**

```bash
./scripts/check_status.sh AA100
```

**Expected:**
- ✅ Returns flight status (if enabled)
- ✅ No API key errors

### **Test Monitoring:**

```bash
./scripts/monitor_price.sh JFK LHR 2026-03-15
```

**Expected:**
- ✅ Shows "Monitoring active!"
- ✅ Uses threshold from config.json

---

## 🔒 Security Best Practices

### **✅ DO:**
- ✅ Copy `config.example.json` to `config.json`
- ✅ Edit `config.json` with your API keys
- ✅ Verify `config.json` is in `.gitignore`
- ✅ Use environment variables if possible
- ✅ Use different keys for test and production
- ✅ Rotate keys periodically

### **❌ DON'T:**
- ❌ Commit `config.json` to git
- ❌ Share API keys publicly
- ❌ Use production keys for testing
- ❌ Hardcode keys in scripts
- ❌ Push to public repositories with keys

---

## 🚨 Common Mistakes

### **Mistake #1: Editing config.example.json**

```bash
# ❌ WRONG! This file is tracked in git
nano config.example.json

# ✅ CORRECT! Copy first, then edit
cp config.example.json config.json
nano config.json
```

### **Mistake #2: Committing config.json**

```bash
# ❌ DANGER! API keys will be in git history
git add config.json
git commit -m "Add my config"

# ✅ CHECK FIRST! Should be in .gitignore
git status
# config.json should NOT appear

# If it appears, add to .gitignore:
echo "config.json" >> .gitignore
```

### **Mistake #3: Using Sandbox for Real Searches**

```json
{
  "apis": {
    "amadeus": {
      "sandbox_mode": true  // ← Test data!
    }
  }
}
```

**Result:** Prices are fake!

**Fix:** Set `"sandbox_mode": false` for real prices

---

## 📚 Next Steps

1. ✅ Create `config.json` from example
2. ✅ Add your API keys
3. ✅ Test with simple search
4. ✅ Read [SKILL.md](SKILL.md) for advanced usage
5. ✅ Check [CONFIGURATION.md](CONFIGURATION.md) for all options

---

## ❓ FAQ

**Q: Why do I need to copy config.example.json?**
- A: `config.json` is in `.gitignore` to prevent accidental commits of API keys. The example file is a template.

**Q: Can I commit config.json if I remove API keys first?**
- A: NO! It's too easy to make a mistake. Keep `config.json` out of git entirely.

**Q: What if I accidentally committed config.json?**
- A: 
  1. Remove from git: `git rm --cached config.json`
  2. Add to `.gitignore`
  3. Commit: `git commit -m "Remove config from git"`
  4. **ROTATE YOUR API KEYS IMMEDIATELY!**

**Q: Can I use environment variables instead?**
- A: Yes! See [CONFIGURATION.md](CONFIGURATION.md) for details.

---

## 🔗 Helpful Links

- **Amadeus Dashboard:** https://developers.amadeus.com/user/apps
- **AviationStack Dashboard:** https://aviationstack.com/dashboard
- **Config Guide:** [CONFIGURATION.md](CONFIGURATION.md)
- **Full Docs:** [SKILL.md](SKILL.md)

---

**Remember:** 🔒 **NEVER commit `config.json` to git!** 🔒
