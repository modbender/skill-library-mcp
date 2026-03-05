# Simulated Road Trip

Let your Clawbot go on a GPS-grounded road trip through the real world. Pick a route, choose a theme, and Turai generates narrated stops using real Google Maps data. Your agent posts updates as it "travels."

## Concept

Your agent picks a starting point and destination, and the Turai Road Trip API plans a real route with actual stops along the way. Each stop includes:

- **Real location data** — GPS coordinates, place names, distances from Google Maps
- **Themed narration** — Written from the perspective of someone actually traveling there
- **Atmosphere details** — What you'd see, hear, smell, eat at each stop

The agent can drip-feed these stops over time — one per hour, one per day — creating an ongoing travel narrative in chat, on Moltbook, or any messaging channel.

## Themes

| Theme | Focus |
|-------|-------|
| `history` | Historical landmarks, battlefields, monuments |
| `foodie` | Local restaurants, street food, regional specialties |
| `haunted` | Ghost stories, abandoned places, local legends |
| `weird` | Roadside attractions, oddities, world's largest things |
| `nature` | National parks, scenic overlooks, wildlife |
| `art` | Galleries, murals, public art installations |
| `architecture` | Notable buildings, bridges, urban design |
| `music` | Venues, birthplaces of musicians, music history |
| `literary` | Bookstores, author homes, fictional settings |
| `film` | Filming locations, movie landmarks |
| `spiritual` | Temples, churches, sacred sites |
| `adventure` | Extreme sports, hiking, off-the-beaten-path |

## Setup

1. Get a Turai API key from [turai.org](https://turai.org)
2. Set the environment variable:
   ```bash
   export TURAI_API_KEY="your-key-here"
   ```

## Usage

### From the command line

```bash
# Basic road trip — NYC to LA, 5 stops, foodie theme
node skills/simulated-roadtrip/scripts/roadtrip.mjs \
  --from "New York City" \
  --to "Los Angeles" \
  --theme foodie \
  --stops 5

# Haunted road trip through New England
node skills/simulated-roadtrip/scripts/roadtrip.mjs \
  --from "Salem, MA" \
  --to "Sleepy Hollow, NY" \
  --theme haunted \
  --stops 4

# Drip-feed mode — post one stop every 2 hours
node skills/simulated-roadtrip/scripts/roadtrip.mjs \
  --from "Nashville, TN" \
  --to "New Orleans, LA" \
  --theme music \
  --stops 6 \
  --drip 2h

# Save trip data to JSON for later use
node skills/simulated-roadtrip/scripts/roadtrip.mjs \
  --from "Tokyo" \
  --to "Kyoto" \
  --theme art \
  --stops 4 \
  --output trip.json
```

### Drip-feed intervals

- `1h`, `2h`, `4h` — hours between posts
- `1d` — one stop per day
- `30m` — every 30 minutes (for impatient travelers)

### From your agent

> "Take a road trip from Chicago to Austin, music theme, 5 stops"

The agent should run the script, then post each stop as a chat message or social update.

## API Reference

**Endpoint:** `POST https://turai.org/api/agent/roadtrip`

**Headers:**
- `x-api-key`: Your Turai API key
- `Content-Type`: `application/json`

**Body:**
```json
{
  "from": "New York City",
  "to": "Los Angeles",
  "theme": "foodie",
  "stops": 5
}
```

**Response:** JSON with array of stops, each containing location data and narration.

## Files

- `SKILL.md` — This file
- `scripts/roadtrip.mjs` — Main script
