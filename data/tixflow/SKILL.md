---
name: tixflow
description: AI-powered event assistant for discovering, booking, and coordinating event tickets. Integrates with KYD Labs protocol and Google Calendar.
metadata:
  openclaw:
    requires:
      env: ["GOOGLE_CALENDAR_API_KEY", "KYD_API_KEY"]
    install:
      - id: npm
        kind: npm
        package: googleapis
        label: Install Google Calendar API
---

# 🎫 TixFlow - AI Event Assistant

> Your personal AI agent for event discovery, booking, and coordination

## What TixFlow Does

- 🔍 **Event Discovery** - Search events by artist, location, date, or genre
- 🎫 **Smart Booking** - Purchase tickets across platforms
- 📅 **Calendar Sync** - Sync events to Google Calendar with reminders
- ⏰ **Waitlist Management** - Get notified when sold-out events have availability
- 🤖 **AI Agent Power** - Let your agent handle everything automatically

## Installation

```bash
clawhub install tixflow
```

## Environment Variables

- `GOOGLE_CALENDAR_API_KEY` - Google Calendar API key (for calendar sync)
- `KYD_API_KEY` - KYD Labs API key (optional, for real ticketing)

## Functions

| Function | Status | Description |
|----------|--------|-------------|
| `findEvents()` | ✅ Ready | Search events by criteria |
| `getEventDetails()` | ✅ Ready | Get event information |
| `purchaseTicket()` | 🔄 Demo | Purchase ticket (demo mode) |
| `syncToCalendar()` | 🔄 Ready | Sync to Google Calendar |
| `addToWaitlist()` | ✅ Ready | Join event waitlist |
| `checkPrices()` | ✅ Ready | Compare prices across platforms |

## Usage

```javascript
const { findEvents, syncToCalendar, purchaseTicket } = require('./scripts/tixflow.js');

// Find events
const events = await findEvents({
  type: 'concert',
  location: 'London',
  date: '2026-03'
});

// Sync to calendar
await syncToCalendar({
  eventId: '123',
  userEmail: 'user@example.com'
});

// Purchase ticket
await purchaseTicket({
  eventId: '123',
  quantity: 2,
  walletAddress: '...'
});
```

## Demo Mode

Without API keys, the skill runs in demo mode with mock event data. This is perfect for:
- Prototyping
- Hackathons
- User demos

## Built For

- KYD Labs Ticketing Track
- Solana Graveyard Hackathon
- OpenClaw Agents
