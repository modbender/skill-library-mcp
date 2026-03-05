# Basic Flight Search Examples

## Simple One-Way Search

```
"Search flights from JFK to LHR"
```

**What happens:**
- Searches for flights JFK → LHR
- Returns results for next available dates
- Shows cheapest options first

---

## Round-Trip with Dates

```
"Flights JFK to LAX December 15 to January 10"
```

**What happens:**
- Searches JFK → LAX departing Dec 15
- Returning Jan 10
- Compares round-trip prices

---

## Specific Month

```
"Find flights to Paris in March"
```

**What happens:**
- Searches all dates in March
- Finds cheapest days to fly
- Returns best prices for the month

---

## With Number of Passengers

```
"Search flights GRU to MIA for 2 adults"
```

**What happens:**
- Searches with 2 adult passengers
- Calculates total price
- Returns availability for group

---

## From Brazilian Airports

```
"Passagens CNF para LIS dezembro"
```

**What happens:**
- Searches CNF (Confins) → LIS (Lisbon)
- For December
- Returns prices in BRL (if configured)

---

## Quick Price Check

```
"How much to fly to Tokyo?"
```

**What happens:**
- Asks for departure airport if needed
- Searches for best prices to Tokyo
- Shows cheapest options across airlines

---

## Using Airport Codes

```
"Search flights GRU to CDG"
```

**Airport Codes Reference:**

| City | IATA Code |
|------|-----------|
| São Paulo (Guarulhos) | GRU |
| São Paulo (Congonhas) | CGH |
| Belo Horizonte (Confins) | CNF |
| Rio de Janeiro (Galeão) | GIG |
| Rio de Janeiro (Santos Dumont) | SDU |
| New York (JFK) | JFK |
| London (Heathrow) | LHR |
| Paris (Charles de Gaulle) | CDG |
| Bangkok | BKK |
| Tokyo (Haneda) | HND |
| Tokyo (Narita) | NRT |

---

## Tips for Better Results

✅ **Use IATA codes** (3 letters) for accuracy
✅ **Specify dates** for exact pricing
✅ **Be flexible** with dates for better prices
✅ **Include return date** for round-trip deals
✅ **Mention passengers** if more than 1

---

## Common Mistakes

❌ "Flights to Paris" (no origin)
❌ "Flights tomorrow" (no destination)
❌ "Flights December" (no year)
❌ "Flights JFK-LHR" (use spaces, not dashes)
