# Platforms & Data Sources

## Primary Platforms

| Platform | Best For | Watch Out |
|----------|----------|-----------|
| **Booking.com** | Hotels, last-minute, free cancellation | Prices sometimes beat Airbnb after fees |
| **Airbnb** | Apartments, kitchen access, monthly stays | Fees can add 20-40% to listed price |
| **Hotels.com** | Loyalty rewards, business travel | Collect 10 nights → 1 free night |
| **Hostelworld** | Hostels, backpackers | Book direct on hostel site often 10-15% cheaper |
| **VRBO** | Family vacation rentals | US-focused, less international |

## Long-Stay Platforms (Nomads)

| Platform | Region | Notes |
|----------|--------|-------|
| **HousingAnywhere** | Europe | Verified, medium-term rentals |
| **Spotahome** | Europe | Video tours, no in-person viewing needed |
| **Flatio** | Europe | Deposit-free, furnished |
| **Idealista** | Spain/Portugal/Italy | Local prices, requires local language often |
| **Immobilienscout24** | Germany | Standard for German rentals |
| **Badi** | Spain | Room rentals, flatshares |
| **Facebook Groups** | Everywhere | "Digital Nomads [City]", "Apartments [City]" |

## Budget/Hostel Direct Booking

Many hostels offer 10-15% cheaper rates on their own website vs Hostelworld.

**Strategy:**
1. Find hostel on Hostelworld
2. Google "[hostel name] direct booking"
3. Compare prices
4. Book whichever is cheaper

## Price Comparison Flow

```
1. Search user criteria on Booking.com (baseline)
2. Same search on Airbnb (compare total, not nightly)
3. For hostels: check direct website
4. For long stays: check local platforms
5. Present winner with reasoning
```

## API/Scraping Notes

**Live data priority:**
- Never recommend based on training data prices
- Use web_fetch or browser to check current availability
- If unable to verify live: state "prices may have changed, verify before booking"

## Loyalty Program Considerations

**Business travelers:**
- Ask about existing status (Marriott Bonvoy, Hilton Honors, etc.)
- Calculate value of points earned
- Sometimes slightly more expensive chain hotel > cheap independent (status progress)

**Casual travelers:**
- Hotels.com 10-night reward is accessible to anyone
- Booking.com Genius levels unlock discounts
