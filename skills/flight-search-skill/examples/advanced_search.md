# Advanced Flight Search Examples

## Multi-City Trips

```
"Search flights GRU to LIS, then LIS to CDG, then CDG to GRU"
```

**Note:** Currently requires separate searches for each leg. Future versions may support multi-city in one query.

---

## Flexible Date Range

```
"Find cheapest flights to Thailand between December 2026 and January 2027"
```

**What happens:**
- Searches multiple dates
- Finds best prices across date range
- Returns optimal departure/return dates

---

## With Constraints

```
"Flights JFK to BKK December 15 to January 10, minimum 20 days, maximum 2 stops"
```

**Parameters:**
- **Minimum stay:** 20 days
- **Maximum stops:** 2
- **Date range:** Dec 15 - Jan 10

---

## Filter by Airline

```
"Search United Airlines flights to Asia"
```

**What happens:**
- Filters results by United Airlines
- Shows only United and partners
- Useful for loyalty programs

---

## Filter by Class

```
"Business class flights to Europe"
```

**Available Classes:**
- ECONOMY
- PREMIUM_ECONOMY
- BUSINESS
- FIRST

---

## Price Range

```
"Flights to Orlando under $500"
```

**What happens:**
- Searches all dates
- Filters results under $500
- Returns only affordable options

---

## Long-Term Planning

```
"Best time to fly to Japan in 2027"
```

**What happens:**
- Searches across multiple months
- Compares seasonal prices
- Returns cheapest periods

---

## Specific Route Optimization

```
"Best route from Belo Horizonte to Bangkok with connection via Europe"
```

**What happens:**
- Searches CNF → BKK
- Filters for European connections
- Compares routes via:
  - Lisbon (TAP)
  - Frankfurt (Lufthansa)
  - Istanbul (Turkish)

---

## Using Scripts Directly

### Search Flights
```bash
./scripts/search_flights.sh CNF BKK 2026-12-15 2027-01-10
```

### With Custom Currency
```bash
python3 lib/amadeus_client.py \
  --origin CNF \
  --destination BKK \
  --departure 2026-12-15 \
  --return 2027-01-10 \
  --currency USD \
  --max 10
```

### Maximum Stops
```bash
python3 lib/amadeus_client.py \
  --origin JFK \
  --destination BKK \
  --departure 2026-12-15 \
  --max-stops 1
```

### Business Class
```bash
python3 lib/amadeus_client.py \
  --origin GRU \
  --destination CDG \
  --departure 2026-06-15 \
  --class BUSINESS
```

---

## Complex Queries

### Example 1: Marco's Thailand Trip

```
"Search flights CNF to BKK December 2026 to January 2027,
minimum 20 days, maximum 2 stops, prefer United or Turkish Airlines"
```

**Breaking it down:**
1. **Origin:** CNF (Confins, Belo Horizonte)
2. **Destination:** BKK (Bangkok)
3. **Period:** Dec 2026 - Jan 2027
4. **Duration:** 20+ days
5. **Stops:** Maximum 2
6. **Airlines:** United, Turkish (good connections via USA/Japan or Istanbul)

---

### Example 2: Family Trip to Orlando

```
"Flights GRU to MCO July 2027 for 4 adults, 2 children, under R$4000 per person"
```

**Parameters:**
- **Route:** GRU → MCO (Orlando)
- **Month:** July 2027
- **Passengers:** 4 adults + 2 children
- **Budget:** R$4000/person (R$24000 total)

---

### Example 3: Multi-Destination Europe

```
"Best route: GRU → LIS (7 days) → CDG (5 days) → FCO (4 days) → GRU"
```

**Strategy:**
1. Search GRU → LIS
2. Search LIS → CDG
3. Search CDG → FCO
4. Search FCO → GRU
5. Calculate total cost
6. Compare with open-jaw tickets

---

## Performance Tips

### Reduce API Calls
- Search specific dates instead of ranges
- Use max results parameter
- Cache results for repeated searches

### Better Results
- Search Tuesday-Thursday
- Avoid holidays and events
- Book 2-3 months in advance
- Use flexible dates

### Rate Limits
- Amadeus: 2,000 requests/month (free tier)
- AviationStack: 100 requests/month (free tier)
- Space out flexible date searches

---

## Troubleshooting Advanced Searches

### "Too many API calls"
- Reduce date range
- Increase days between searches
- Use cached results

### "No results with filters"
- Relax constraints (more stops, different dates)
- Try different airlines
- Check if route exists

### "Prices inconsistent"
- Sandbox mode uses test data
- Prices update frequently
- Currency conversion varies
