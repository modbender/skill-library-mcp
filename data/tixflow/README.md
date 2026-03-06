# TixFlow - OpenClaw Skill 🎫🤖

AI-powered event assistant skill for OpenClaw agents.

## Installation

```bash
clawhub install tixflow
```

Or manually:

```bash
cd skill
npm install
```

## Environment Variables

Create a `.env` file:

```env
# Google Calendar (for event scheduling)
GOOGLE_CALENDAR_API_KEY=your_google_api_key

# Google Maps (for directions/routes)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# CrossMint (for cNFT ticket minting)
CROSSMINT_API_KEY=your_crossmint_api_key
CROSSMINT_COLLECTION_ID=your_collection_id
```

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Event Discovery** | Search events by type, location, date |
| 📅 **Calendar Sync** | Add events to Google Calendar |
| 🗺️ **Directions** | Get transport routes to venue |
| 🎟️ **cNFT Minting** | Mint real NFT tickets on Solana |
| 👻 **Wallet Detection** | Detect user wallet (Phantom, Solflare) |
| 💰 **Price Monitoring** | Compare prices across platforms |

## Functions

- `findEvents({type, location, date, budget})` - Search for events
- `getEventDetails(eventId)` - Get event information
- `purchaseTicket({eventId, quantity, walletAddress})` - Buy tickets (mints cNFT)
- `syncToCalendar({eventId})` - Generate Google Calendar link
- `getDirections({eventId, mode})` - Get transport directions (drive, transit, walk)
- `addToWaitlist({eventId, walletAddress})` - Join event waitlist
- `checkPrices(eventId)` - Compare prices across platforms

## Demo Mode

Set `demo_mode: true` in config to run without real API keys (mock data).

## Supported Platforms

- Telegram
- Discord  
- WhatsApp

## License

MIT

---

*Built for KYD Labs Solana Graveyard Hackathon*
