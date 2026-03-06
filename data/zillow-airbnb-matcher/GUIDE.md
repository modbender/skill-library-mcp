# 🏠 Zillow × Airbnb Matcher — Setup Guide

## What This Does

Ask your bot to search any US ZIP code. It instantly finds properties for sale that already have active Airbnb listings nearby — and calculates the investment numbers (cap rate, cash flow, mortgage, etc).

**Cost: $0** (uses RapidAPI free tier — 100 Airbnb + 600 Zillow searches/month)

---

## Setup (5 minutes)

### Step 1: Get Your Free RapidAPI Key

1. Go to **https://rapidapi.com** → Sign up (free, no credit card needed)
2. Subscribe to these 2 APIs (click "Subscribe" → choose **Basic/Free** plan):
   - **Airbnb:** https://rapidapi.com/3b-data-3b-data-default/api/airbnb13
   - **Zillow:** https://rapidapi.com/SwongF/api/us-property-market1
3. Copy your API key (it's the same key for both — find it on any API page, top right under "X-RapidAPI-Key")

### Step 2: Install the Skill

Tell your bot:
```
install zillow-airbnb-matcher
```

Or install manually via CLI:
```bash
clawhub install zillow-airbnb-matcher
cd ~/clawd/skills/zillow-airbnb-matcher
npm install
```

### Step 3: Add Your API Key

Add your RapidAPI key to the skill's `.env` file:

```bash
echo "RAPIDAPI_KEY=your_key_here" > ~/clawd/skills/zillow-airbnb-matcher/.env
```

Or run the install script which does it for you:
```bash
bash ~/clawd/skills/zillow-airbnb-matcher/scripts/install.sh --rapidapi-key YOUR_KEY_HERE
```

Then restart OpenClaw:
```bash
openclaw gateway restart
```

### Step 4: Test It

Send your bot any of these messages:

- `airbnb demo` → Demo mode (no API needed)
- `search airbnb 78704` → Austin TX
- `search airbnb 33139` → Miami Beach
- `search airbnb Nashville TN` → Nashville

---

## What You'll See

Your bot will return a full investment report like this:

```
🏠 Property Match Report — ZIP 78704
📅 Feb 19, 2026

✅ Found 5 matches out of 41 listings
💰 3 positive cash flow | ⭐ 2 Grade A

-------------------------

🟢 #1 EXCELLENT — 1234 S Congress Ave
📍 Austin TX 78704 | Single Family
💰 $650,000 | 3bd/2ba | 1,800 sqft
📅 45 days on market | Built 2005

🌙 Airbnb: $4,200/mo avg | ⭐ 4.8 (92 reviews)
📊 Occupancy: 78% | Superhost | 24 months of history

📈 Cap Rate: 7.2% | CoC: 12.1% | GRM: 12.9x
💵 Cash Flow: +$1,180/mo | Annual: +$14,160/yr
🏦 Mortgage: $3,548/mo | Down: $130,000
🎯 Break-even occupancy: 62% (currently at 78%)

🔗 Zillow: https://www.zillow.com/...
🔗 Airbnb: https://www.airbnb.com/rooms/...
```

### Investment Grades
- 🟢 **A (Excellent)** — Cap ≥6%, Cash-on-Cash ≥10%, high occupancy
- 🟡 **B (Good)** — Solid returns, normal risk
- 🟠 **C (Fair)** — Works but thin margins
- 🔴 **D (Weak)** — Avoid unless value-add play

---

## How the Matching Works

The tool uses **GPS-based geo-matching**, NOT exact address matching:

1. Zillow API returns all for-sale properties in your ZIP with GPS coordinates
2. Airbnb API returns all active listings in the same area with GPS coordinates
3. The tool calculates the distance between every pair using the Haversine formula
4. Properties within 100m get a 92% match confidence, within 200m = 82%
5. Each Airbnb listing only matches with ONE Zillow property (best match wins)

**Important:** A matched Airbnb listing is NOT necessarily the same property that's for sale. It's a nearby property (within ~150 meters) that shows there's active short-term rental demand AND revenue data in that immediate area.

Think of it as: *"There's a property for sale HERE, and someone RIGHT NEXT DOOR is making $X/month on Airbnb."*

---

## Tips

- **Compare ZIP codes**: `78704` vs `78745` — prices and returns vary a lot within the same city
- **Check STR permits**: Always google "[city] short term rental rules" before buying
- **Revenue estimates** assume 70% occupancy — conservative but realistic
- **Geo-matching** finds Airbnbs within ~150m of the for-sale property — it may be a neighbor's, not the exact same house
- **Popular STR markets**: 78704 (Austin), 33139 (Miami Beach), 37203 (Nashville), 92109 (San Diego), 32819 (Orlando)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Dependencies not installed" | Run `npm install` in the skill folder |
| "RAPIDAPI_KEY not configured" | Add `RAPIDAPI_KEY=xxx` to the skill's `.env` file |
| "RapidAPI rate limit hit" | Free tier = 100 Airbnb + 600 Zillow/month. Wait for reset or upgrade ($10/mo) |
| "0 matches found" | Normal! Not every ZIP has overlapping for-sale + Airbnb. Try a popular STR market |
| Bot doesn't respond | Restart OpenClaw: `openclaw gateway restart` |

---

## Free Tier Limits

| API | Free Requests/Month | Cost to Upgrade |
|-----|---------------------|-----------------|
| Airbnb (airbnb13) | 100 | $10/mo for 1,000 |
| Zillow (us-property-market1) | 600 | $10/mo for 5,000 |

At 100 searches/month you can check ~3 ZIP codes per day. Plenty for research.

---

*Built by em8.io*
