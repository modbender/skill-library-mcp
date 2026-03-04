# 📅 Luma Event Manager

A Clawdbot skill for managing [Luma](https://lu.ma) events as both host and attendee. Discover nearby events, view guest lists, and track your RSVPs — all via web scraping (no API key required).

## Features

### Public Access (No Auth)
- 🔍 Search events by topic, theme, or keyword
- 📍 Discover events near any location
- 📄 View event details (title, date, location, host)
- 🌍 Geographic search with radius filtering

### Authenticated Access (With Cookies)
- 📋 View your RSVP'd events
- 🎯 View events you're hosting
- 👥 Access guest lists for your events
- ✅ RSVP to events
- 📆 Sync events to Google Calendar (via `gog` CLI)

## Installation

### Via ClawdHub
```bash
npx clawdhub install luma
```

### Manual
```bash
cd ~/clawd/skills/luma
npm install
npm run build
```

## Usage

### Search by Topic
```
"luma search AI"
"luma search startup"
"luma search AI near San Francisco"
```

### Discover Events by Location
```
"luma events near San Francisco"
"luma events near Belmont this weekend"
"luma event ai-meetup-sf"
```

### Host Mode (Auth Required)
```
"luma host events"           # List your hosted events
"luma host guests <slug>"    # View guest list
```

### Attendee Mode (Auth Required)
```
"luma my events"             # Your RSVP'd events
"luma rsvp <slug> <response>"# RSVP yes/no/maybe/waitlist
```

### Utility Commands
```
"luma configure"             # Set up authentication
"luma status"                # Check connection
"luma help"                  # Show all commands
"luma add calendar <slug>"   # Add event to Google Calendar
```

## Setup

### Basic (Public Events Only)
No setup required! Just start using discover commands.

### Full Access (Your Events + Guest Lists)

1. Log into [lu.ma](https://lu.ma) in your browser
2. Open DevTools (F12) → Application → Cookies → lu.ma
3. Copy these cookie values:
   - `luma_session`
   - `luma_user_id`
4. Store in pass:
   ```bash
   pass insert luma/cookies
   # Enter: {"luma_session": "value", "luma_user_id": "value"}
   ```

### Calendar Sync (Optional)
Requires the `gog` CLI with an authorized Google account.

1. Add your account (if not already):
   ```bash
   gog auth add you@example.com
   ```
2. Create the calendar entry:
   ```
   "luma add calendar <slug>"
   ```
3. If you have multiple Google accounts, provide the account:
   ```
   "luma add calendar <slug> --account you@example.com"
   ```
4. (Optional) Target a specific calendar:
   ```
   "luma add calendar <slug> --calendar_id primary"
   ```

## Technical Details

### How It Works
- **Web Scraping**: Parses lu.ma HTML pages using Cheerio
- **Geocoding**: Uses Nominatim (OpenStreetMap) for location search — free, no API key
- **Auth**: Cookie-based authentication stored in `pass` (password manager)
- **Rate Limiting**: Exponential backoff with a 1 req/sec floor to respect lu.ma
- **Resilience**: Fallback selectors + Next.js JSON parsing with warnings when selectors fail

### Dependencies
- `cheerio` — HTML parsing
- `typescript` — Type safety
- `pass` — Cookie storage for authenticated features
- `gog` — Google Calendar sync (optional)

### Project Structure
```
luma/
├── SKILL.md           # Clawdbot skill documentation
├── README.md          # This file
├── package.json       # Dependencies
├── tsconfig.json      # TypeScript config
├── src/
│   ├── index.ts       # Main handler & tool definitions
│   ├── scraper.ts     # Web scraping logic
│   ├── utils.ts       # Geocoding, date formatting
│   └── skill-types.ts # Type definitions
└── dist/              # Compiled JavaScript
```

## Limitations

- **Scraping Changes**: Luma can change HTML structure; fallback selectors help but may still break
- **RSVP Variability**: RSVP endpoints can change; failures return actionable errors
- **Rate Limits**: Exponential backoff reduces risk, but heavy use may still trigger blocks
- **Calendar Sync**: Requires `gog` CLI and a configured Google account

## Roadmap

- [ ] v2.1: Check-in support for hosts
- [ ] v2.2: Event creation

## Contributing

1. Fork this repo
2. Make changes in `src/`
3. Run `npm run build`
4. Test locally
5. Submit PR

## License

MIT

---

Built for [Clawdbot](https://github.com/clawdbot/clawdbot) 🦞
