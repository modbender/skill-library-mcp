# Reservation Skill — Decisions & Open Questions

**Last updated:** 2026-03-01

---

## Decisions Made (locked)

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | **Never auto-book** | Reservations are real commitments with potential fees/penalties |
| D2 | **No raw CC in skill** | Browser handoff for all CC entry. Virtual card later if desired. |
| D3 | **Bib Gourmand + Plate ONLY from Michelin** | "No over-fanciness" — Yonatan's explicit preference |
| D4 | **Ontopo is primary for Israel** | Best coverage (~730–1000 restaurants), clean API |
| D5 | **Default credentials = Yonatan Hyatt** | Use unless request specifies otherwise |
| D6 | **Tabit temp reservation = availability signal** | Only way to get real-time Tabit availability without OTP; cleans up after ~15min |
| D7 | **Maps curated lists take priority** | Hand-curated = highest trust signal; Michelin/TimeOut supplement |
| D8 | **Israel = Maps + Time Out** | Michelin doesn't cover Israel (confirmed). אופטיקאי מדופלם is a strategy blog, not restaurant guide. |
| D9 | **TheFork = browser handoff** | DataDome makes direct API impossible without Playwright setup |
| D10 | **OTP for Tabit booking** | Required by platform. Flow: `request_otp()` → ask user → `verify_otp()` → `confirm_booking()` |

---

## Open Questions (Yonatan to address)

### Q1 — Tabit phone number 📞
**Status:** RESOLVED — read from RESERVATION_PHONE env var or passed at runtime

### Q2 — Google Maps API key 🗺️
**Status:** Not configured.  
**Impact:** `search_restaurants_maps()` falls back to search URL only (no live data).  
**Action:** Add `GOOGLE_MAPS_API_KEY` to environment for live Places search.  
**Cost:** Maps Places API = ~$17/1000 requests (very affordable).

### Q3 — Resy release timing for NYC 🗓️
**Status:** Unresolved.  
**Context:** Don Angie, Lilia, Carbone etc. open reservations 28 days in advance at midnight ET.  
**Question:** Should Kai set a cron alert for June 2026 trip? (e.g., alert May 24 at midnight ET for June 21 dinner)  
**Proposed:** Yes — create cron alerts for top-3 NYC restaurants, ~28 days before arrival.

### Q4 — TheFork Partner API 🤝
**Status:** Not applied.  
**URL:** https://www.thefork.com/business/restaurant-partners  
**Impact:** Would unlock real-time TheFork availability without DataDome issues.  
**Question:** Worth applying? Mostly useful for Europe cruise ports.  
**Note:** May require restaurant-side credentials (i.e., designed for restaurant managers, not diners).

### Q5 — Valletta / Mozrest integration 🇲🇹
**Status:** Not integrated as a platform.  
**Context:** Most Valletta Michelin picks use Mozrest (not TheFork).  
**Question:** Should I reverse-engineer Mozrest widget? Or link handoff is sufficient?  
**Proposed:** Link handoff is fine for one-off Valletta trip.

### Q6 — Ontopo OTP confirmation 🔐
**Status:** Unclear from live testing.  
**Context:** `availability_search_marketplace` → `checkout_id` → `s1.ontopo.com/checkout/<id>`.  
**Question:** Does the Ontopo checkout page require phone OTP, or is anonymous JWT sufficient?  
**Action:** Test with a real booking (low-risk restaurant with free cancellation).

### Q7 — Yonatan's Maps saved places 📌
**Status:** Not fetched yet (gog OAuth needed).  
**Context:** Using Google Maps "Want to Go" / starred places would give the highest-signal recs.  
**Action:** Run `gog` skill → fetch saved places → cross-reference with curated lists in maps.py.  
**One-time task:** Run once, cache results in `cache/maps_saved_places.json`.

### Q8 — Marseille/Genoa ship timing ⏰
**Status:** Unconfirmed.  
**Context:** Apr 4 (Marseille) and Apr 5 (Genoa) — need to know ship arrival/departure times to know if lunch or dinner is feasible.  
**Impact:** Affects recommended meal time and whether a restaurant reservation is needed at all.  
**Action:** Check MSC itinerary PDF or contact cruise line.

---

## Platform Reliability Matrix

| Platform | Discovery | Availability | Booking | Notes |
|----------|-----------|-------------|---------|-------|
| Ontopo | ✅ Direct API | ✅ Direct API | ⚠️ Needs live test | OTP unclear |
| Tabit | ✅ Direct API | ✅ Temp hold | ⚠️ Needs OTP | Phone required |
| TheFork | 🔗 URL only | 🔗 URL only | 🔗 Browser | DataDome |
| Resy | 🔗 URL only | 🔗 URL only | 🔗 Browser | Best for NYC |
| OpenTable | 🔗 URL only | 🔗 URL only | 🔗 Browser | 403 without session |
| Michelin | ✅ Algolia | N/A | N/A | Recs only |
| Time Out | ✅ Scraping | N/A | N/A | Recs only |
| CNT | ⚠️ Limited | N/A | N/A | Auth needed |
| Maps | ✅ Curated | N/A | N/A | Manual curation |
