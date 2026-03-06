---
name: trip-calendar
description: Add trip itineraries, flights, hotel check-ins, and activities to Google Calendar using gog CLI. Handles "add to calendar" and boarding pass parsing.
metadata: { "openclaw": { "requires": { "bins": ["gog"] } } }
---

# Trip Calendar

## When to activate
- User says "add to calendar", "put this on my calendar"
- User forwards a boarding pass screenshot
- After itinerary is finalized and user confirms

## Adding itinerary to calendar
When user confirms "add to calendar":
1. Create events for key milestones using gog:
   - ✈️ Flights (with terminal, timing)
   - 🏨 Hotel check-in / check-out (with address)
   - 🥾 Major activities (treks, tours)
   - 🚕 Major transport

2. Command format:
   gog calendar create primary --summary "✈️ DEL→KLU 6E-2041" --from "2026-03-14T06:00:00+05:30" --to "2026-03-14T07:30:00+05:30" --location "DEL Terminal 1" --description "Reach airport by 4:30 AM"

3. Use emojis in titles: ✈️ flights, 🏨 hotels, 🥾 treks, 🚕 transport
4. Include location and useful details in description

## Boarding pass parsing
When user sends boarding pass image:
1. Extract: flight number, date, time, origin, destination, gate/terminal
2. Confirm with user
3. On confirmation, create calendar event

## Response
✓ Added 4 events to your Google Calendar:
  ✈️ DEL→KLU flight (Mar 14, 6 AM)
  🏨 Check-in: Parvati Riverside (Mar 14, 1 PM)
  🥾 Kheerganga Trek (Mar 15, full day)
  ✈️ KLU→DEL return (Mar 16, 3:30 PM)

## Rules
- Never add without explicit user confirmation
- Always use IST timezone (+05:30)
- Don't create events for every small activity — key milestones only
- If gog is not available, tell user: "Calendar integration isn't set up yet. Here's your itinerary to add manually."
