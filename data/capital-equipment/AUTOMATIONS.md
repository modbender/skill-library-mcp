# Capital Equipment - Proactive Automations

These automations run on OpenClaw's heartbeat/cron system to deliver proactive value without the researcher asking.

## Automations

### Equipment Scout (Every 6 hours)
Monitors marketplace and database for new equipment matching saved searches.

```yaml
name: equipment-scout
schedule: "0 */6 * * *"
description: "Check for new equipment matching your saved interests"
```

**Prompt for OpenClaw agent:**
```
Check the Capital Equipment platform for new listings matching my saved equipment interests.
Use the search_equipment tool with my saved search criteria.
Compare results against what I've seen before (check memory for previous scout results).
If there are new listings I haven't seen, send me a brief summary via my preferred channel.
Format: Equipment name, location, key specs, and price if available.
Only notify me if there are genuinely new or notable listings.
```

### Morning Lab Briefing (Daily at 7 AM)
Daily summary of equipment-related updates.

```yaml
name: morning-briefing  
schedule: "0 7 * * 1-5"
description: "Daily briefing on equipment bookings, marketplace deals, and network activity"
```

**Prompt for OpenClaw agent:**
```
Generate my morning lab equipment briefing:

1. UPCOMING BOOKINGS: Check if I have any equipment bookings in the next 48 hours. Remind me of facility name, time, and any prep needed.

2. MARKETPLACE DEALS: Use search_marketplace to check for any equipment in my interest areas that was listed in the last 24 hours or had a price drop.

3. EXPIRING OPPORTUNITIES: Check for any marketplace listings about to close or go to auction.

Send a concise briefing - no more than 10 lines. Only include sections with actual updates.
```

### Booking Reminder (2 hours before)
Triggered when a booking is approaching.

```yaml
name: booking-reminder
trigger: "2 hours before any equipment booking"
description: "Remind me before upcoming equipment sessions"
```

**Prompt for OpenClaw agent:**
```
I have an equipment booking coming up:
- Equipment: {equipment_name}
- Facility: {facility_name}  
- Time: {start_time}
- Duration: {duration}

Send me a reminder with:
1. The booking time and location
2. Any facility-specific prep requirements (if you can find them)
3. The facility contact info in case I need to reach them

Keep it brief and actionable.
```

### Price Alert (Every 12 hours)
Monitors equipment prices for significant changes.

```yaml
name: price-alert
schedule: "0 */12 * * *"
description: "Alert on significant price changes for watched equipment"
```

**Prompt for OpenClaw agent:**
```
Check the Capital Equipment marketplace for price changes on equipment I'm watching.
Use search_marketplace for each item in my watchlist.
Only alert me if:
- Price dropped more than 15%
- New listing is 30%+ below typical market price (use get_pricing for fair market value)
- An item I was watching is about to be removed/sold

Format each alert as: Equipment | Old Price → New Price | % Change | Location
```

### Network Activity Monitor (Daily)
Tracks relevant activity from followed researchers.

```yaml
name: network-monitor
schedule: "0 18 * * *"
description: "Evening digest of network activity relevant to my research"
```

**Prompt for OpenClaw agent:**
```
Check for relevant network activity on the Capital Equipment platform:
1. Use search_papers to check for new publications from researchers I follow or in my equipment interest areas (last 24 hours)
2. Any new equipment listings at institutions in my network
3. New researchers in my area of expertise who joined the platform

Only send a digest if there's something genuinely relevant. Skip if nothing notable happened.
```

## Configuration

Users should set their preferences:

```
Tell my Capital Equipment skill:
- My research interests: [e.g., "cryo-EM, structural biology, protein crystallography"]
- My institution: [e.g., "MIT"]  
- Equipment I'm watching: [e.g., "Thermo Fisher Krios, Bruker Avance 600MHz"]
- Preferred notification channel: [e.g., "WhatsApp", "Slack", "Discord"]
- Briefing time: [e.g., "7 AM EST"]
- Alert threshold: [e.g., "only deals >20% below market"]
```

These preferences are stored in OpenClaw's persistent memory and used by all automations.
