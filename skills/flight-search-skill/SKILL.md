---
name: flight-search
description: Search flights, compare prices, and monitor airfare using Amadeus API
author: marco-rabelo
version: 1.0.2
triggers:
  - "search flights"
  - "find flights"
  - "flight prices"
  - "airfare"
  - "plane tickets"
  - "book flights"
  - "flight status"
credentials:
  required:
    - name: AMADEUS_API_KEY
      description: Amadeus API key for flight search
      how_to_get: Visit developers.amadeus.com, create account, and create an app
    - name: AMADEUS_API_SECRET
      description: Amadeus API secret for authentication
      how_to_get: Provided when you create an app on developers.amadeus.com
  optional:
    - name: AVIATIONSTACK_API_KEY
      description: AviationStack API key for flight status (optional)
      how_to_get: Visit aviationstack.com and sign up for free tier (100 requests/month)
---

# Flight Search

Search flights, compare prices across airlines, and monitor airfare drops. Supports flexible dates, price alerts, and flight status tracking.

## ⚠️ Required Credentials

**This skill requires API credentials to function:**

### **Required (Amadeus):**
- `AMADEUS_API_KEY` - Get from [developers.amadeus.com](https://developers.amadeus.com)
- `AMADEUS_API_SECRET` - Provided when you create an app

**Free Tier:** 2,000 searches/month (sandbox) or production free tier with real prices

### **Optional (AviationStack):**
- `AVIATIONSTACK_API_KEY` - Get from [aviationstack.com](https://aviationstack.com)

**Free Tier:** 100 requests/month (very limited, only for flight status)

## Configuration

After installing, copy `config.example.json` to `config.json` and add your credentials:

```json
{
  "apis": {
    "amadeus": {
      "api_key": "YOUR_AMADEUS_API_KEY",
      "api_secret": "YOUR_AMADEUS_API_SECRET",
      "sandbox_mode": true
    },
    "aviationstack": {
      "enabled": false,
      "api_key": "YOUR_AVIATIONSTACK_API_KEY"
    }
  }
}
```

**🔒 Security:** 
- `config.json` is in `.gitignore` by default
- Never commit API keys to version control
- Use environment variables or secure config files
- Rotate keys if accidentally exposed

## What it does

Searches flights using Amadeus API, compares prices, finds the best routes, and can monitor prices over time to alert you when they drop. Optional AviationStack integration for real-time flight status.

## Prerequisites

1. **Get API Keys:**
   - **Amadeus (Required):** developers.amadeus.com
     - **Test/Sandbox (FREE):** 2,000 flight searches/month - ⚠️ **TEST DATA ONLY**
     - **Production (FREE + pay-as-you-go):** FREE quota + pay only for extra calls - ✅ **REAL PRICES**
     - Sign up and create an app
     - Get API Key and API Secret
   
   **✅ GREAT NEWS:**
   - **Both environments have FREE tiers!**
   - **Test:** 2,000 requests/month FREE (test data)
   - **Production:** FREE quota + pay-as-you-go (real data)
   - **Production gives REAL prices** for free (within quota)
   - **Bonus:** 90% discount on search calls if you create bookings!
   
   **⚠️ CRITICAL:**
   - **Sandbox = Test data** (prices are NOT real)
   - **Production = Real data** (actual prices, availability)
   - **Production is NOT €30/month** - it has a FREE tier!
   - Only pay if you exceed the free quota
   
   - **AviationStack (Optional):** aviationstack.com
     - Free tier: 100 requests/month ⚠️ **VERY LIMITED**
     - For flight status tracking only
     - Consider paid plan ($49.99+) for production
   
2. **Configure the skill:**
   Edit `config.json` with your API keys:
   ```json
   {
     "apis": {
       "amadeus": {
         "api_key": "YOUR_KEY",
         "api_secret": "YOUR_SECRET",
         "sandbox_mode": true  // false for Production (real prices, also FREE tier!)
       }
     }
   }
   ```

**Recommendation:** 
- Start with **Sandbox** (free) to test the skill functionality
- Switch to **Production** (also FREE tier!) for **real prices**
- Only pay if you exceed the free quota (pay-as-you-go)

**Recommendation:** Start with Amadeus only. Add AviationStack only if you need flight status tracking and have budget for paid plan.

## Usage

### Basic Search
```
"Search flights from JFK to LHR"
"Find flights São Paulo to Lisbon in March"
"How much to fly to Thailand in December?"
```

### With Dates
```
"Flights JFK to LAX December 15 to January 10"
"Flights 01/03 to 15/03 GRU to MIA"
"Search tickets to Paris departing in January"
```

### Flexible Dates
```
"Cheapest time to fly to Europe?"
"Best prices to Thailand next 3 months"
"When is it cheapest to visit Paris?"
```

### Monitor Prices
```
"Monitor prices JFK to LHR"
"Alert me when flights to Rome drop"
"Set up price alert for Paris"
```

### Flight Status (Limited)
```
"Check status of flight AA123"
"Is flight LA1234 on time?"
"Track flight G3 4567"
```

**Note:** Flight status requires AviationStack API. Free tier is extremely limited (100 requests/month). Consider:
- Use sparingly for important flights only
- Upgrade to paid plan ($49.99+/month) for regular use
- Alternative: Use airline's official app/website

### Compare Airlines
```
"Compare airlines flying to Asia"
"Which airline is cheapest?"
"Best route to Thailand"
```

## Features

- ✅ Flight search via Amadeus API
- ✅ Price comparison across airlines
- ✅ Flexible date search
- ✅ Price monitoring and alerts
- ✅ Multi-city routes
- ✅ Filter by stops, airline, duration
- ✅ Currency conversion
- ✅ Flight status tracking (AviationStack)
- ✅ International airport support

## API Information

| API | Coverage | Best For | Free Tier | Paid Plans |
|-----|----------|----------|-----------|------------|
| **Amadeus** | Global | Flight search, prices, routes | 2,000/month | From €30/month |
| **AviationStack** | Global | Flight status, tracking | 100/month ⚠️ | From $49.99/month |

**Recommendation:** Start with Amadeus only. Add AviationStack only if flight status tracking is critical for your use case and you're willing to upgrade to paid plan.

## Tips

- Use airport codes (JFK, LHR, BKK) for accuracy
- Specify flexible dates for best prices
- Set up monitoring for long-term planning
- Book Tuesday-Thursday for lower prices
- Book 2-3 months in advance for international flights
- Check flight status before heading to airport

## Examples

See `examples/` folder for:
- Basic searches
- Multi-city trips
- Price monitoring setup
- Advanced filtering
- Route optimization
- Flight status tracking

## Troubleshooting

### "No flights found"
- Verify airport codes (use IATA codes)
- Try broader date ranges
- Check API key configuration
- Verify API quota not exceeded

### "API error"
- Verify API keys are valid
- Check API rate limits
- Ensure API is enabled in config
- Check network connectivity

### "Prices seem wrong"
- Prices update frequently
- Try refreshing search
- Sandbox mode uses test data
- Check currency settings

### "Flight status unavailable"
- Enable AviationStack in config
- Verify flight number format (e.g., AA123)
- Check if flight exists for date
- Try without date for current status

## API Rate Limits

| API | Free Tier | Rate Limit | Notes |
|-----|-----------|------------|-------|
| **Amadeus** | 2,000/month | ~10/second | Sandbox mode only |
| **AviationStack** | 100/month | Varies | ⚠️ Very limited free tier |

**Important Notes:**
- **Amadeus** sandbox mode provides test data suitable for development. For production use with real prices, upgrade to production API.
- **AviationStack** free tier is extremely limited (100 requests/month). For production use, consider:
  - Paid plans start at $49.99/month (Basic plan: 5,000 requests)
  - Professional plan: $149.99/month (50,000 requests)
  - Enterprise: Custom pricing
- **Alternative:** If you need flight status, consider using Amadeus's limited flight status endpoints or airline-specific APIs.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

- Amadeus for Developers: developers.amadeus.com
- AviationStack: aviationstack.com
