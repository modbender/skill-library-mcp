# ⚠️ IMPORTANT WARNINGS

## About API Keys and Data Accuracy

---

## 🎯 Critical Information

### **Amadeus API Environments**

| Environment | Cost | Data | Free Quota | Use Case |
|-------------|------|------|------------|----------|
| **Test/Sandbox** | ✅ FREE | ❌ **TEST DATA** | 2,000 searches/month | Development, testing |
| **Production** | ✅ FREE + 💰 Pay-as-you-go | ✅ **REAL DATA** | FREE quota + pay extra | Real searches, bookings |

---

## ✅ GREAT NEWS: Production has FREE Tier!

**Contrary to popular belief, Production is NOT €30/month!**

### **Production Environment Pricing:**
- ✅ **FREE request quota** every month
- 💰 **Pay-as-you-go** (only pay for calls beyond free quota)
- ✅ **Real prices** and availability
- ✅ **40 TPS** (vs 10 TPS in test)
- 💰 **90% discount** on search calls if you create bookings

---

## 📊 Actual Pricing Structure

### **Test/Sandbox Environment:**
- ✅ **FREE** - No credit card required
- ✅ 2,000 flight searches/month FREE
- ✅ 10 TPS (Transactions Per Second)
- ❌ Test data (prices are NOT real)
- ✅ Perfect for development

### **Production Environment:**
- ✅ **FREE tier** + pay-as-you-go
- ✅ FREE request quota every month (same as test!)
- 💰 Pay only for calls beyond free quota
- ✅ Real-time data (prices are REAL)
- ✅ 40 TPS (4x faster than test)
- 💰 90% discount if you create bookings
- ✅ Perfect for production use

---

## 💰 Cost Examples

### **Scenario 1: Personal Use (Light)**
- Monthly searches: ~100 flight searches
- **Test Environment:** FREE ✅
- **Production Environment:** FREE ✅
- **Your cost:** **$0/month**

### **Scenario 2: Personal Use (Moderate)**
- Monthly searches: ~500 flight searches
- **Test Environment:** FREE ✅
- **Production Environment:** FREE ✅ (within free quota)
- **Your cost:** **$0/month**

### **Scenario 3: Heavy Use**
- Monthly searches: ~5,000 flight searches
- **Test Environment:** FREE ✅ (but test data)
- **Production Environment:** FREE quota + small fee for extra ~3,000 calls
- **Your cost:** ~$5-15/month (only for extra calls)

### **Scenario 4: With Bookings**
- You create bookings via Flight Create Orders
- **Production Environment:** 90% discount on search calls!
- **Your cost:** **90% less** than normal pricing

---

## ⚠️ SANDBOX MODE LIMITATIONS

When using **Sandbox** (test environment):

### **What Works:**
- ✅ API structure and endpoints
- ✅ Response format
- ✅ Search functionality
- ✅ Skill integration
- ✅ Development and testing

### **What Doesn't Work:**
- ❌ **Prices are NOT real** (test data)
- ❌ **Availability may be inaccurate**
- ❌ **Routes may be limited**
- ❌ **Cannot actually book flights**

---

## ✅ PRODUCTION MODE BENEFITS

When using **Production** (real environment):

### **What You Get:**
- ✅ **FREE tier** (yes, it's free!)
- ✅ **Real prices** (actual market prices)
- ✅ **Real availability** (live data)
- ✅ **All routes available**
- ✅ **Can actually book** flights
- ✅ **40 TPS** (faster than test)
- ✅ **Full parallelization**
- 💰 **90% discount** with bookings

### **When You Pay:**
- 💰 Only when you EXCEED the free quota
- 💰 Pay-as-you-go (no monthly fees)
- 💰 Example: If free quota is 2,000 and you make 2,500 calls, you pay for 500 extra calls

---

## 🔧 How to Switch Environments

### **Sandbox → Production:**

1. **Get Production credentials:**
   - Login to developers.amadeus.com
   - Create **Production** app (not Test!)
   - NO credit card required for free tier
   - Get Production API Key + Secret

2. **Update config.json:**
   ```json
   {
     "apis": {
       "amadeus": {
         "api_key": "YOUR_PRODUCTION_KEY",
         "api_secret": "YOUR_PRODUCTION_SECRET",
         "sandbox_mode": false  // Changed to false!
       }
     }
   }
   ```

3. **Test with real search:**
   ```bash
   ./scripts/search_flights.sh CNF BKK 2026-12-15
   ```

4. **See REAL prices!** ✅

---

## 💡 Recommendations

### **For Development:**
1. ✅ Use **Sandbox** (free)
2. ✅ Test all features
3. ✅ Verify skill works
4. ✅ **Cost: $0**

### **For Personal Use:**
1. ✅ Use **Production** (FREE tier!)
2. ✅ Get **real prices**
3. ✅ Stay within free quota
4. ✅ **Cost: $0** (in most cases)

### **For Heavy Use:**
1. ✅ Use **Production**
2. 💰 Pay-as-you-go for extra calls
3. 💰 Consider creating bookings for 90% discount
4. 💰 **Cost: $5-30/month** (depending on usage)

### **For Publishing:**
1. ✅ Publish skill with **Sandbox configuration**
2. ✅ Document clearly in README
3. ✅ Let users choose their environment
4. ✅ **Your cost: $0** (users pay for their own APIs)

---

## 🚨 Common Mistakes

### **Mistake 1: Thinking Production costs €30/month**
- ❌ "I can't afford Production"
- ⚠️ **Reality:** Production has a FREE tier!
- ✅ **Fix:** Just try Production - it's free!

### **Mistake 2: Using Sandbox for real searches**
- ❌ "I found a flight for $200!"
- ⚠️ **Reality:** That's test data, not real price
- ✅ **Fix:** Switch to Production (also free!)

### **Mistake 3: Not reading documentation**
- ❌ "The skill is broken, prices are fake!"
- ⚠️ **Reality:** User didn't switch to Production
- ✅ **Fix:** Read this file and use Production

### **Mistake 4: Thinking you need to pay upfront**
- ❌ "I need to subscribe to use Production"
- ⚠️ **Reality:** No subscription needed for free tier
- ✅ **Fix:** Just create Production app and use it!

---

## 📊 Quick Comparison

| Feature | Sandbox | Production |
|---------|---------|------------|
| **Cost** | FREE | FREE + pay-as-you-go |
| **Free Quota** | ✅ 2,000/month | ✅ FREE quota/month |
| **Data** | ❌ Test | ✅ Real |
| **Prices** | ❌ Fake | ✅ Real |
| **Booking** | ❌ No | ✅ Yes |
| **Speed** | 10 TPS | 40 TPS |
| **Credit Card** | ❌ No | ❌ No (for free tier) |
| **Best For** | Development | Production use |

---

## 🎯 Summary

| Mode | Best For | Cost | Data | Recommendation |
|------|----------|------|------|----------------|
| **Sandbox** | Testing, development | FREE | Test | ✅ Use for testing skill |
| **Production** | Real searches, bookings | FREE + pay-as-you-go | Real | ✅ **Use for real prices!** |

**Choose Production for real prices - it's also FREE!**

---

## ❓ FAQ

**Q: Is Production really free?**
- A: YES! Production has a free tier with monthly quota. Only pay if you exceed it.

**Q: Do I need a credit card for Production?**
- A: NO! You can use the free tier without a credit card.

**Q: What happens if I exceed the free quota?**
- A: You pay only for the extra calls (pay-as-you-go). No monthly fees.

**Q: Can I use Sandbox for personal searches?**
- A: Yes, but prices will be inaccurate. For real prices, use Production (also free!).

**Q: Do I need Production to publish the skill?**
- A: No! Users configure their own API keys. You pay $0.

**Q: Is AviationStack also free?**
- A: Yes! AviationStack free tier provides real flight status data (but limited to 100 requests/month).

**Q: What if I can't afford extra calls?**
- A: Stay within the free quota! Most personal users never exceed it.

**Q: How do I get 90% discount?**
- A: Create bookings via Flight Create Orders API in Production. Amadeus gives 90% discount on search calls.

---

## 🔗 Useful Links

- **Amadeus Pricing:** https://developers.amadeus.com/pricing
- **Create App:** https://developers.amadeus.com/user/apps
- **Documentation:** https://developers.amadeus.com/self-service/apis-docs
- **FAQ:** https://developers.amadeus.com/support/faq

---

**Last Updated:** March 2026
**Author:** Marco Rabelo
**Based on:** Official Amadeus pricing page (March 2026)
