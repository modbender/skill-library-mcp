# Price Monitoring Examples

## Basic Monitoring

### Start Monitoring

```
"Monitor prices JFK to LHR December"
```

**What happens:**
1. Adds route to monitoring list
2. Records current best price
3. Checks periodically (every 6 hours)
4. Alerts if price drops >5%

---

### Monitor with Specific Dates

```
"Monitor flights CNF to BKK December 15 to January 10"
```

**What happens:**
- Monitors exact dates
- Tracks price changes
- Alerts on significant drops

---

### View Monitored Flights

```
"Show my monitored flights"
```

**Returns:**
- List of all monitored routes
- Current prices
- Price history
- Last check time

---

## How Monitoring Works

### Check Frequency

| Type | Frequency | Notes |
|------|-----------|-------|
| **Heartbeat** | Every 6 hours | Automatic background check |
| **Manual** | On demand | "Check flight prices now" |
| **Alert** | Immediate | When price drops detected |

---

### Price Drop Threshold

- **Default:** 5% drop triggers alert
- **Configurable:** Can be changed in config.json
- **Example:** R$5000 → R$4750 = 5% drop = Alert

---

## Using Monitor Script

### Start Monitoring

```bash
./scripts/monitor_price.sh CNF BKK 2026-12-15 2027-01-10
```

**Output:**
```
🔍 Checking current prices...
💰 Current best price: 4850.00 BRL
✅ Added to monitoring: CNF-BKK-2026-12-15-2027-01-10
📊 Monitoring 1 flights total

🔔 Monitoring active!
   • Check HEARTBEAT.md for periodic checks
   • Alert threshold: 5% price drop
   • View all: cat .monitored_flights.json
```

---

### View Monitored Flights

```bash
cat .monitored_flights.json
```

**Example:**
```json
{
  "monitored_flights": [
    {
      "id": "CNF-BKK-2026-12-15-2027-01-10",
      "origin": "CNF",
      "destination": "BKK",
      "departure_date": "2026-12-15",
      "return_date": "2027-01-10",
      "initial_price": 4850.00,
      "last_price": 4720.00,
      "currency": "BRL",
      "threshold_percent": 5,
      "created_at": "2026-03-01T10:30:00",
      "last_check": "2026-03-01T16:30:00",
      "check_count": 2,
      "alerts_sent": 0
    }
  ]
}
```

---

## HEARTBEAT Integration

Add to your `HEARTBEAT.md`:

```markdown
## Flight Price Monitoring

### Every 6 hours:
- [ ] Check prices for monitored routes
- [ ] If price drops >5%, send alert
- [ ] Update last known prices

### Configuration:
```json
{
  "monitored_routes": [
    {
      "id": "cnf-bkk-2026",
      "origin": "CNF",
      "destination": "BKK",
      "departure_range": ["2026-12-01", "2026-12-20"],
      "return_range": ["2027-01-05", "2027-01-15"],
      "min_duration_days": 20,
      "last_price": 4850,
      "threshold_percent": 5,
      "created_at": "2026-02-28"
    }
  ]
}
```
```

---

## Alert Example

### When Price Drops

```
🔔 PRICE ALERT!

📍 Route: CNF → BKK
📅 Dates: Dec 15, 2026 - Jan 10, 2027

📉 PRICE DROPPED!
- Before: R$ 4,850.00
- Now: R$ 4,420.00
- Savings: R$ 430.00 (-8.9%)

✈️ Turkish Airlines
- Outbound: Dec 15, 18:15 (1 stop: IST)
- Return: Jan 10, 22:00 (1 stop: IST)

🔗 Book now: [link]

⚠️ Valid for: 48h
```

---

## Monitoring Strategies

### Strategy 1: Single Date Monitoring

**Best for:** Fixed travel dates

```
"Monitor flights CNF to BKK December 15 to January 10"
```

- Monitors exact dates
- Alerts on any price drop
- Good for firm plans

---

### Strategy 2: Flexible Date Monitoring

**Best for:** Flexible travel dates

```
"Monitor flights CNF to BKK December 2026 to January 2027"
```

- Monitors entire month
- Finds cheapest dates
- Alerts on best opportunities

---

### Strategy 3: Multi-Route Monitoring

**Best for:** Comparing destinations

```
"Monitor flights to Asia: Bangkok, Tokyo, Singapore"
```

- Monitors multiple destinations
- Compares prices
- Alerts on best deal

---

## Stopping Monitoring

### Remove Single Route

```
"Stop monitoring CNF to BKK"
```

### Remove All

```
"Clear all monitored flights"
```

### Using Script

```bash
# Edit .monitored_flights.json manually
# Remove the route from the array
```

---

## Best Practices

### ✅ Do

- Monitor 2-3 months before travel
- Set realistic thresholds (5-10%)
- Check alerts promptly
- Book when price is right
- Monitor multiple dates

### ❌ Don't

- Monitor too many routes (API limits)
- Set threshold too low (1-2%)
- Wait too long to book
- Ignore alerts
- Monitor more than 6 months ahead

---

## Rate Limit Considerations

| Monitoring Type | API Calls | Monthly Impact |
|-----------------|-----------|----------------|
| **1 route, 6h checks** | ~120/month | 6% of Amadeus limit |
| **3 routes, 6h checks** | ~360/month | 18% of Amadeus limit |
| **10 routes, 6h checks** | ~1200/month | 60% of Amadeus limit |

**Recommendation:** Monitor max 3-5 routes simultaneously on free tier.

---

## Advanced Monitoring

### Conditional Alerts

```
"Alert me when CNF to BKK drops below R$4500"
```

### Multi-Person Monitoring

```
"Monitor flights for family trip: 4 adults, 2 children"
```

### Seasonal Monitoring

```
"Monitor Christmas flights to Europe, alert in September"
```

---

## Troubleshooting

### "Not receiving alerts"

**Check:**
- HEARTBEAT.md is configured
- Monitoring is active (check .monitored_flights.json)
- Price drops exceed threshold
- API quota not exceeded

### "Price increased but got alert"

**Explanation:**
- Alert based on initial price, not last price
- Once triggered, alert won't repeat for same route
- Manual re-monitor to reset baseline

### "Too many alerts"

**Solutions:**
- Increase threshold (e.g., 10% instead of 5%)
- Monitor specific dates instead of ranges
- Reduce number of monitored routes
