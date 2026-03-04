---
name: golf-tee-times
description: "Search for golf tee times and deals near any location. Find cheapest rounds, compare prices across platforms, and get discount tips. Use when asked about golf, tee times, courses, or booking a round."
metadata:
  openclaw:
    emoji: "⛳"
    requires:
      bins: ["curl", "python3"]
---

# Golf Tee Time Finder ⛳

Find and compare golf tee times using the GolfNow API (reverse-engineered). Works for any location.

## When to Use
- User asks to find tee times, book golf, or play a round
- Looking for cheap/discounted golf or hot deals
- Comparing courses in an area
- Checking availability for a specific date
- Finding credit-bookable (trade offer) tee times

## GolfNow API (Primary Method)

The GolfNow website uses a POST API to fetch tee times. This is the **only reliable method** — web_fetch returns empty shells (JS-rendered SPA).

### API Endpoint
```
POST https://www.golfnow.com/api/tee-times/tee-time-results
Content-Type: application/json
Accept: application/json
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
Origin: https://www.golfnow.com
```

### Facility-Specific Search (SearchType: 1) — WORKS ✅
Requires a `FacilityId`. Returns all tee times for that course on a given date.

```json
{
  "Radius": 50,
  "Latitude": 26.1224,
  "Longitude": -80.1373,
  "PageSize": 50,
  "PageNumber": 0,
  "SearchType": 1,
  "SortBy": "Date",
  "SortDirection": 0,
  "Date": "Feb 16 2026",
  "BestDealsOnly": false,
  "PriceMin": "0",
  "PriceMax": "10000",
  "Players": "2",
  "Holes": "3",
  "FacilityType": 0,
  "RateType": "all",
  "TimeMin": "10",
  "TimeMax": "42",
  "FacilityId": 5744,
  "SortByRollup": "Date.MinDate",
  "View": "Grouping",
  "ExcludeFeaturedFacilities": true,
  "TeeTimeCount": 50,
  "PromotedCampaignsOnly": "false",
  "CurrentClientDate": "2026-02-16T05:00:00.000Z"
}
```

### Area Search (SearchType: 0) — DOES NOT WORK ❌
Returns 0 results without a FacilityId. The API requires facility-specific queries.

### Key Parameters
| Param | Values | Notes |
|-------|--------|-------|
| `Players` | "1"-"4" | String, not int |
| `Holes` | "1"=9h, "2"=18h, "3"=any | String |
| `TimeMin`/`TimeMax` | 10-42 | Maps to time ranges. 10=5AM, 42=9PM+ |
| `Date` | "Feb 16 2026" | Human-readable format |
| `FacilityType` | 0=any, 1=course, 2=simulator | |
| `BestDealsOnly` | true/false | Hot deals filter (but returns 0 for area search) |
| `SearchType` | 1 | Must be 1 (facility). 0/2/3 don't work |

### Response Structure
```
ttResults.teeTimes[] → array of tee time groups
  ├── formattedTime: "7:18"
  ├── formattedTimeMeridian: "AM"
  ├── time: "2026-02-16T07:18:00"  (ISO timestamp)
  ├── displayRate: 35.0  (price per player)
  ├── multipleHolesRate: 18  (hole count)
  ├── maxPriceTransactionFee: 2.99
  ├── facility.name, facility.address.city, facility.averageRating, facility.reviewCount
  ├── facility.seoFriendlyName  (for building URLs)
  ├── facility.latitude, facility.longitude
  └── teeTimeRates[] → rate options for this time slot
       ├── rateName: "Prepaid - Online Rate" / "Hot Deal" / "Twilight" / etc.
       ├── isHotDeal: true/false  🔥
       ├── isTradeOffer: true/false  💳 (credit-bookable)
       ├── isCartIncluded: true/false
       ├── singlePlayerPrice.greensFees.value: 35.0
       └── rateSetTypeId: 1=prepaid, other=pay at course
```

### Building Course URLs
```
https://www.golfnow.com/tee-times/facility/{seoFriendlyName}/search
```
Example: `https://www.golfnow.com/tee-times/facility/5744-colony-west-golf-club-glades-course/search`

## Helper Script

Use `skills/golf-tee-times/golfnow-search.py` for batch queries. See script for usage.

## Finding Facility IDs

Since area search doesn't work, you need FacilityIds. Methods:

1. **Use the known course database** (see below)
2. **Web search:** `site:golfnow.com/tee-times/facility {city} {state}` — URL contains the ID
3. **Browser intercept:** Load a course page, intercept the POST to `/api/tee-times/tee-time-results`, read the FacilityId from the payload

## Telegram Output Format

Use this clean format for presenting tee times:

```
🏌️ *Tee Times · {Day} {Date} · {Players} Players*

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

🔥 *DEALS*

🔥 *[Course Name](url)*
City · X mi · ⭐ X.X · N reviews
▸ Time · *$XX* · 18 holes · cart 🔥

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

*[Course Name](url)*
City · X mi · ⭐ X.X · N reviews
▸ Time range · $XX
▸ Time range · $XX twilight

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

_All prices per player · cart included · via GolfNow_
```

Key formatting rules:
- Use `▸` for time slot lines
- Bold the course name as a markdown link
- Show deals section first (🔥 hot deals, 💳 credit/trade offers)
- Group times by price tier within each course
- Include distance, rating, review count
- Add `← AM slots` or similar callouts for notable availability
- Footer: _All prices per player · cart included · via GolfNow_
- Do NOT use backtick code blocks for time listings (looks bad on mobile)

## Discount Tips

1. 🔥 **GolfNow Hot Deals** — `isHotDeal: true` in API. Unsold inventory at deep discounts.
2. 💳 **Trade Offers** — `isTradeOffer: true`. Bookable with GolfNow credits.
3. 🚶 **Walk don't ride** — saves $20-50 on cart fees
4. 🌅 **Twilight rates** — after 2-3 PM, prices drop significantly (look for `rateName: "Twilight"`)
5. 🏠 **FL resident rate** — show ID for local discount at public courses
6. ⏰ **Last-minute deals** — day-of prices drop; hot deals appear closer to tee time
7. 📞 **Call pro shop** — phone-only rates sometimes cheaper than online
8. 🗓️ **Weekday > Weekend** — Monday-Thursday is always cheaper
9. 🌧️ **Rain forecast** — prices drop when weather looks iffy

## Seasonal Notes (your area)
- **Peak season** (Dec-Apr): Highest prices, book 3-7 days ahead. Morning sells out fast.
- **Summer** (May-Sep): 40-60% cheaper, but hot/humid. Early AM or twilight.
- **Hurricane season** (Jun-Nov): Rain discounts common
- **Best value month**: September (cheapest + least crowded)

## Booking Flow## Booking Flow (GolfNow via Browser)

### ⚠️ CRITICAL: Always send a screenshot of the final checkout page to the user BEFORE clicking "Make Your Reservation". Wait for explicit approval.

### Steps
1. **Navigate** to `https://www.golfnow.com/tee-times/facility/{facilityId}/tee-time/{teeTimeId}`
2. **Select golfer count** — click radio button, dispatch `change` event, verify green fees total updates
3. **Click "Continue to Book"** (`.btnBook`) — redirects to login if not authenticated
4. **Login** — GolfID iframe (`my.golfid.io`): use `frame=[src*=golfid]` to access email/password fields
   - Creds: `scripts/vault.sh get golfnow`
5. **Checkout page** (URL: `.../checkout/players/{count}`):
   - **Apply rewards**: Click `#applyRewardsBtn` → checkboxes by code ID (e.g. `#MEMBERSAVE`)
     - Note: Rewards marked "Cannot Be Combined" won't stack on Hot Deals
   - **Apply GolfPass Points**: Click `#btn-apply-loyalty-points` (these DO work on Hot Deals)
   - **Decline Tee Time Protection**: Click `input[name=rdlTeeTimeProtection][value=false]`
   - **Decline charity roundup**: Click "No Thanks" if desired
   - **Payment**: Pre-filled from saved cards (default: AMEX 1004)
6. **📸 SCREENSHOT & SEND TO USER** — Send checkout screenshot via Telegram before proceeding
7. **Wait for approval**
8. **Accept terms**: Check `#agree-terms-top`
9. **Click reservation**: `#reservation-button-top`
10. **Confirmation**: Remove Truist ad overlay (`[class*=rokt], [class*=bold]`), screenshot confirmation page

### the user's Booking Preferences
- Always apply points/rewards to minimize cost
- Decline Tee Time Protection (save $3-4)
- Default payment: AMEX ending 1004
- Send confirmation screenshot after booking
