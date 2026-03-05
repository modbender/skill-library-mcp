# Navifare Flight Validator - Usage Examples

Real conversation examples showing how to use this skill effectively.

---

## Example 1: User Found Price on Skyscanner

### Conversation

**User**: I found a flight from New York to London on Skyscanner for $450. It's BA553 departing June 15 at 6 PM.

**Assistant** (activates skill):
I'd love to help you check if that's the best price! However, Navifare currently only supports **round-trip** flight searches.

Do you have a return flight as well? If so, share the return flight details (airline, flight number, date, and times) and I'll compare prices across multiple booking sites for the full round trip.

---

## Example 2: Screenshot Upload from Kayak

### Conversation

**User**: *[Uploads screenshot of Kayak search showing Milan to Barcelona for €299]*

**Assistant** (activates skill):
I can see your flight search. Let me extract the details and find the best price for you.

*[Extracts flight details from screenshot]*

Extracted from your screenshot:
- Route: MXP (Milan Malpensa) → BCN (Barcelona)
- Date: June 20, 2025
- Return: June 27, 2025
- Airline: Vueling
- Passengers: 1 adult
- Class: Economy
- Reference price: €299 on Kayak

*[Calls mcp__navifare-mcp__flight_pricecheck with extracted data]*

Searching multiple booking sites...

*[Results come back]*

✅ **Price verified!**

Your reference: €299 on Kayak
Navifare best price: **€295 on Kiwi.com**
📊 Difference: €4 (1.3%)

Your price is very competitive! The best available is nearly identical.

**Top 5 Options:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Kiwi.com | €295 | Standard | [Book Now](https://kiwi.com/...) |
| 2 | Kayak | €299 | Standard | [Book Now](https://kayak.com/...) |
| 3 | Momondo | €305 | Standard | [Book Now](https://momondo.com/...) |
| 4 | Skyscanner | €310 | Standard | [Book Now](https://skyscanner.com/...) |
| 5 | eDreams | €315 | Special Fare | [Book Now](https://edreams.com/...) |

All prices checked: 2025-02-11 16:45 UTC

The price you found is excellent. I'd recommend booking soon as prices for June travel tend to increase closer to departure.

---

## Example 3: Multi-Segment Connection Flight

### Conversation

**User**: Google Flights shows $890 for LAX to Tokyo via Seattle on July 10. Alaska AS338 to Seattle, then ANA NH178 to Tokyo. Should I book it?

**Assistant** (activates skill):
Let me verify that's the best price for your itinerary with the connection in Seattle.

*[Extracts details]*
- Segment 1: AS338, LAX → SEA, July 10
- Segment 2: NH178, SEA → NRT, July 10
- Need departure/arrival times for accurate search

**Question**: What are the departure and arrival times for each segment?
- AS338 LAX → SEA: Departure time?
- NH178 SEA → NRT: Departure time?

**User**: AS338 departs 10 AM arrives 12:30 PM. NH178 departs 2:30 PM arrives 5 PM next day.

**Assistant**:
Perfect! Searching now...

*[Calls search with both segments]*

⚠️ **Prices have changed**

Your reference: $890 on Google Flights
Current best price: **$925 on Kiwi.com**
📈 Increase: $35 (3.9%)

Prices for this route have gone up slightly since you checked.

**Top 3 Options:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Kiwi.com | $925 | Standard | [Book Now](https://kiwi.com/...) |
| 2 | Momondo | $945 | Standard | [Book Now](https://momondo.com/...) |
| 3 | Google Flights | $890* | Standard | [Book Now](https://google.com/flights/...) |

*Note: The $890 price on Google Flights may no longer be available. Verify on their site.*

All prices checked: 2025-02-11 17:00 UTC

**Recommendation**: If the $890 price is still available on Google Flights when you check, that's your best option. Otherwise, Kiwi.com at $925 is the next best choice.

---

## Example 4: Round-Trip Validation Before Booking

### Conversation

**User**: I'm about to book this flight to Athens. Can you check if it's a good price first?

**Details:**
- London Gatwick to Athens, June 10-17
- British Airways outbound, Aegean return
- £380 total on Skyscanner

**Assistant** (activates skill):
Absolutely! Let me verify that's the best price before you commit.

I need a few more details for an accurate search:
- Outbound: BA flight number and departure time?
- Return: Aegean (A3) flight number and departure time?
- Travel class (Economy, Business)?

**User**:
- Outbound: BA632, departs 7:30 AM, arrives 1:15 PM
- Return: A3605, departs 9:00 AM, arrives 11:30 AM
- Economy class

**Assistant**:
Thank you! Searching now...

*[Builds round-trip search with both flights]*

✅ **I found savings!**

Your reference: £380 on Skyscanner
Best price found: **£365 on Momondo**
💰 You save: £15 (3.9%)

**Top 5 Options:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Momondo | £365 | Standard | [Book Now](https://momondo.com/...) |
| 2 | Kiwi.com | £370 | Standard | [Book Now](https://kiwi.com/...) |
| 3 | Kayak | £375 | Standard | [Book Now](https://kayak.com/...) |
| 4 | Skyscanner | £380 | Standard | [Book Now](https://skyscanner.com/...) |
| 5 | eDreams | £395 | Special Fare | [Book Now](https://edreams.com/...) |

All prices checked: 2025-02-11 17:15 UTC

I recommend booking with Momondo to save £15. However, verify that both flights (BA632 and A3605) are included in their quote before purchasing.

---

## Example 5: Missing Information Handling

### Conversation

**User**: Found a flight to Paris for $600. Is that good?

**Assistant** (activates skill):
I'd be happy to check if that's the best price! To search accurately, I need more details:

**Missing information:**
❌ Departure city/airport
❌ Travel dates
❌ Airline and flight number
❌ Departure/arrival times
❌ Travel class

Could you provide:
1. **Where are you flying from?** (e.g., "New York JFK")
2. **What date?** (e.g., "June 15, 2025")
3. **Which airline and flight?** (e.g., "Air France AF007")
4. **What time does it depart?** (e.g., "6:00 PM")
5. **Economy or Business class?**

**User**: Oh right! Flying from Boston to Paris CDG on June 8. Air France AF334 leaving at 8:30 PM, arriving 9:45 AM next day. Economy.

**Assistant**:
Perfect! Now I can search properly.

*[Extracts details]*
- BOS → CDG
- AF334
- June 8, 2025
- 20:30 → 09:45 (+1 day)
- Economy
- 1 adult
- Reference: $600

Searching across multiple booking sites...

*[Results]*

✅ **Better prices available!**

Your reference: $600 on [unknown site]
Best price found: **$565 on Kiwi.com**
💰 You save: $35 (5.8%)

**Top 3 Options:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Kiwi.com | $565 | Standard | [Book Now](https://kiwi.com/...) |
| 2 | Momondo | $580 | Standard | [Book Now](https://momondo.com/...) |
| 3 | Google Flights | $595 | Standard | [Book Now](https://google.com/flights/...) |

All prices checked: 2025-02-11 17:30 UTC

---

## Example 6: No Better Price Found

### Conversation

**User**: Kayak shows €450 for Zurich to Rome on LX1612, March 15. Can you beat it?

**Assistant** (activates skill):
Let me check what other booking sites have for that flight.

*[Needs more info]*

**Question**: What time does LX1612 depart and arrive on March 15?

**User**: Departs 10:40 AM, arrives 12:25 PM.

**Assistant**:
Searching...

*[Results show higher prices]*

✅ **Your price is the best available!**

Your reference: €450 on Kayak
Navifare best price: €450 on Kayak
📊 Match: €0 (0%)

**All available prices:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Kayak | €450 | Standard | [Book Now](https://kayak.com/...) |
| 2 | Skyscanner | €450 | Standard | [Book Now](https://skyscanner.com/...) |
| 3 | Momondo | €465 | Standard | [Book Now](https://momondo.com/...) |
| 4 | Kiwi.com | €475 | Standard | [Book Now](https://kiwi.com/...) |
| 5 | eDreams | €490 | Special Fare | [Book Now](https://edreams.com/...) |

All prices checked: 2025-02-11 17:45 UTC

The €450 price you found is the best current rate. I recommend booking it through Kayak or Skyscanner (both offer the same price).

**Note**: Swiss International Air Lines (LX) is a reputable carrier. This is a direct flight with good timing, making it excellent value.

---

## Example 7: Price Alert - High Demand Route

### Conversation

**User**: Is $1,200 good for Miami to London on December 20? American Airlines.

**Assistant** (activates skill):
Let me check current prices for that route and date.

*[Extracts details, asks for flight number and times]*

**User**: AA38, departs 9:15 PM, arrives 10:30 AM next day.

**Assistant**:
Searching...

⚠️ **Peak season alert**

Your reference: $1,200
Current best price: **$1,150 on Momondo**
💰 Savings: $50 (4.2%)

**Top 3 Options:**

| # | Website | Price | Fare Type | Booking Link |
|---|---------|-------|-----------|--------------|
| 1 | Momondo | $1,150 | Standard | [Book Now](https://momondo.com/...) |
| 2 | Kayak | $1,195 | Standard | [Book Now](https://kayak.com/...) |
| 3 | Google Flights | $1,200 | Standard | [Book Now](https://google.com/flights/...) |

All prices checked: 2025-02-11 18:00 UTC

**Important context:**
- December 20 is peak Christmas travel
- Transatlantic flights are in very high demand
- Prices typically increase significantly closer to departure
- $1,150-$1,200 is actually reasonable for this route/date

**Recommendation**: If you need to travel on December 20 specifically, I'd suggest booking the $1,150 Momondo option soon. If you have flexibility, flying a few days earlier (Dec 17-19) or later (Dec 21-23) could save $300-500.

Would you like me to check alternative dates?

---

## Example 8: Error Handling - No Results

### Conversation

**User**: Can you check if £250 is good for Manchester to Ibiza on June 30? Flight ZZ1234.

**Assistant** (activates skill):
Let me search for that flight.

*[Searches but gets no results]*

❌ **No results found**

Navifare couldn't find current prices for this exact itinerary.

**Possible issues:**
1. **Airline code "ZZ"** is not recognized in our database
2. **Flight number 1234** may be incorrect or the flight may not exist
3. The route may not be currently scheduled for June 30

**Can you help me verify:**
- Which airline operates this flight? (Ryanair, easyJet, Jet2?)
- Are you sure about the flight number ZZ1234?
- Is this a direct flight or with connections?

**Alternative approach:**
If you're flexible on the exact flight, I can search for:
- "Manchester to Ibiza on June 30, Economy, 1 adult"
- And find the best prices across all airlines

Would you like me to do that instead?

**User**: Oh sorry, it's Jet2 flight LS449, not ZZ1234!

**Assistant**:
No problem! Let me search for Jet2 LS449 now.

*[Searches with correct airline/flight]*

✅ **Found better prices!**
... [continues with normal results]

---

## Key Patterns from Examples

### What Triggers the Skill
1. ✅ "I found a flight for $X on [site]"
2. ✅ "Is this a good price?"
3. ✅ "Can you beat this deal?"
4. ✅ Screenshot of booking site
5. ✅ "I'm about to book..."
6. ✅ "Should I book this flight?"

### What Information to Extract
- **Route**: Departure and arrival airports (IATA codes)
- **Date(s)**: Departure date, return date if applicable
- **Flight(s)**: Airline code + flight number(s)
- **Times**: Departure and arrival times (24-hour format)
- **Class**: Economy, Premium Economy, Business, First
- **Passengers**: Adults, children, infants
- **Reference Price**: Amount user saw + currency

### How to Handle Missing Data
1. **Ask specific questions** - don't guess
2. **Reference documentation** - check AIRPORTS.md, AIRLINES.md
3. **Provide examples** - show format you need
4. **Be patient** - walk user through each missing field

### How to Present Results
1. **Clear comparison** - reference price vs best found
2. **Savings calculation** - amount and percentage
3. **Top 3-5 options** - formatted table
4. **Clickable links** - make booking easy
5. **Timestamp** - show when prices were checked
6. **Context** - explain price trends, seasonality
7. **Recommendations** - guide user to best choice

### Edge Cases to Handle
- ❌ No results: Verify flight details, suggest alternatives
- ⚠️ Price increased: Warn user, explain demand
- ✅ Price matched: Validate user's research
- 💰 Price decreased: Celebrate savings!
- ⏱️ Timeout: Show partial results, explain delay
- ❓ Unclear airports: Clarify multi-airport cities
- 🔄 Codeshares: Use operating carrier
- 📅 Past dates: Ask for correct year/date

---

These examples demonstrate the full workflow from user inquiry to actionable booking recommendations. Always prioritize clarity, accuracy, and helpfulness in your responses.
