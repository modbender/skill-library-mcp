# TheSportsDB API Documentation

## Overview

TheSportsDB is a free sports data API providing information about teams, players, events, and game results. Perfect for resolving sports-related oracle queries.

## Base URL

```
https://www.thesportsdb.com/api/v1/json
```

## Authentication

- **Free API Key**: `123` (for testing)
- **Premium API Key**: Get from your user profile
- **Location**: API key goes in the URL path: `/{API_KEY}/`

### Example
```
https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=Arsenal
```

## Rate Limits

- **Free**: 30 requests per minute
- **Premium**: 100 requests per minute
- **Business**: 120 requests per minute

## Common Endpoints

### 1. Search Teams

**Endpoint**: `/{API_KEY}/searchteams.php`

**Parameters**:
- `t` (required): Team name (e.g., "Arsenal")

**Example**:
```
GET /api/v1/json/123/searchteams.php?t=Arsenal
```

**Response**: Returns team details including `idTeam` which can be used for faster lookups.

---

### 2. Search Events

**Endpoint**: `/{API_KEY}/searchevents.php`

**Parameters**:
- `e` (required): Event name (e.g., "Arsenal_vs_Chelsea")
- `d` (optional): Date in format YYYY-MM-DD (e.g., "2026-02-03")
- `s` (optional): Season (e.g., "2016-2017")
- `f` (optional): Filename format

**Examples**:
```
GET /api/v1/json/123/searchevents.php?e=Arsenal_vs_Chelsea
GET /api/v1/json/123/searchevents.php?e=Arsenal_vs_Chelsea&d=2026-02-03
GET /api/v1/json/123/searchevents.php?e=Arsenal_vs_Chelsea&s=2016-2017
```

**Use Case**: Find specific games/matches by name and optionally by date.

---

### 3. Lookup Event

**Endpoint**: `/{API_KEY}/lookupevent.php`

**Parameters**:
- `id` (required): Event ID (get from search results)

**Example**:
```
GET /api/v1/json/123/lookupevent.php?id=441613
```

**Response**: Full event details including scores, teams, date, and result.

---

### 4. Lookup Event Results

**Endpoint**: `/{API_KEY}/eventresults.php`

**Parameters**:
- `id` (required): Event ID

**Example**:
```
GET /api/v1/json/123/eventresults.php?id=652890
```

**Response**: Detailed results including scores, goals, cards, etc.

---

### 5. Search Players

**Endpoint**: `/{API_KEY}/searchplayers.php`

**Parameters**:
- `p` (required): Player name (e.g., "Danny_Welbeck")

**Example**:
```
GET /api/v1/json/123/searchplayers.php?p=Danny_Welbeck
```

---

### 6. Lookup League

**Endpoint**: `/{API_KEY}/lookupleague.php`

**Parameters**:
- `id` (required): League ID (e.g., 4328 for Premier League)

**Example**:
```
GET /api/v1/json/123/lookupleague.php?id=4328
```

---

### 7. Lookup League Table

**Endpoint**: `/{API_KEY}/lookuptable.php`

**Parameters**:
- `l` (required): League ID
- `s` (optional): Season (e.g., "2020-2021")

**Example**:
```
GET /api/v1/json/123/lookuptable.php?l=4328&s=2020-2021
```

**Note**: Limited to featured soccer leagues only.

---

### 8. Events by Date

**Endpoint**: `/{API_KEY}/eventsday.php`

**Parameters**:
- `d` (required): Date in format YYYY-MM-DD (e.g., "2026-02-03")
- `s` (optional): Sport name
- `l` (optional): League name

**Example**:
```
GET /api/v1/json/123/eventsday.php?d=2026-02-03
GET /api/v1/json/123/eventsday.php?d=2026-02-03&s=Soccer
```

**Use Case**: Get all events on a specific date.

---

## Response Format

All endpoints return JSON with the following structure:

```json
{
  "teams": [...],      // For team searches
  "events": [...],      // For event searches
  "event": [...],       // For single event lookup
  "players": [...],     // For player searches
  "leagues": [...]      // For league lookups
}
```

## Common Query Patterns

### Pattern 1: "Who won [Team A] vs [Team B] on [Date]?"

1. Search for event: `searchevents.php?e=TeamA_vs_TeamB&d=YYYY-MM-DD`
2. Get event ID from results
3. Lookup event: `lookupevent.php?id={eventId}`
4. Extract winner from event result or use `eventresults.php` for detailed scores

### Pattern 2: "What was the score of [Team A] vs [Team B]?"

1. Search for event: `searchevents.php?e=TeamA_vs_TeamB`
2. Get event ID
3. Lookup event results: `eventresults.php?id={eventId}`
4. Extract scores from response

### Pattern 3: "Who won the [League] game on [Date]?"

1. Get league ID (Premier League = 4328)
2. Get events by date: `eventsday.php?d=YYYY-MM-DD&l={leagueId}`
3. Find relevant event
4. Lookup event results

## Important Notes

1. **Team Names**: Use underscores for spaces (e.g., "Arsenal_vs_Chelsea")
2. **Date Format**: Always use YYYY-MM-DD
3. **Event IDs**: Once you have an event ID, use lookup endpoints for faster access
4. **Free Tier**: Limited to 30 requests/minute - be mindful of rate limits
5. **Error Handling**: If no results found, response will have empty arrays

## Example Usage in Code

```javascript
const axios = require('axios');
const API_KEY = process.env.SPORTSDB_API_KEY || '123';
const BASE_URL = 'https://www.thesportsdb.com/api/v1/json';

// Search for event
async function searchEvent(teamA, teamB, date) {
  const eventName = `${teamA}_vs_${teamB}`;
  const url = `${BASE_URL}/${API_KEY}/searchevents.php?e=${eventName}&d=${date}`;
  const response = await axios.get(url);
  return response.data.event || [];
}

// Get event results
async function getEventResult(eventId) {
  const url = `${BASE_URL}/${API_KEY}/eventresults.php?id=${eventId}`;
  const response = await axios.get(url);
  return response.data;
}
```

## Query Parsing Tips

When extracting information from natural language queries:

- **Teams**: Look for team names, common abbreviations (e.g., "Lakers", "Arsenal", "Man Utd")
- **Dates**: Extract dates in various formats and convert to YYYY-MM-DD
- **Event Type**: Determine if it's a game, match, or tournament
- **Question Type**: "Who won?" = need winner, "What was the score?" = need scores

## Support

- **Documentation**: http://thesportsdb.com/documentation
- **Free API Key**: Use `123` for testing
- **Premium**: Upgrade for higher limits and V2 API access
