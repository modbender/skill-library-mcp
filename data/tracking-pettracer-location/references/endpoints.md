# PetTracer portal API endpoints (quick reference)

> These endpoints are derived from reverse engineering the PetTracer web portal and public community clients.
> Treat them as **unofficial** and be respectful with request frequency.

## Base URLs

- REST base: `https://portal.pettracer.com/api`
- WebSocket base (SockJS): `wss://pt.pettracer.com/sc`

## Authentication

### Login
`POST /user/login`

JSON body:
```json
{ "login": "you@example.com", "password": "••••••••" }
```

Response includes an `access_token` (bearer token).

### Auth header for all other requests
```
Authorization: Bearer <access_token>
```

## Devices

### List collars (and their latest fix)
`GET /map/getccs`

Returns a JSON list. Each item typically includes:
- `id`
- `details.name`
- `bat` (battery, millivolts)
- `lastContact`
- `lastPos` (lat/lon/time/accuracy/etc)

### Get single device info (optional)
`POST /map/getccinfo`

JSON body:
```json
{ "devId": 12345 }
```

## Location history

### Get position records for a time window
`POST /map/getccpositions`

JSON body:
```json
{ "devId": 12345, "filterTime": 1767152926491, "toTime": 1767174526491 }
```

- `filterTime` and `toTime` are **Unix epoch milliseconds**.
- Response is typically a JSON list of position objects (similar to `lastPos`).

## HomeStations (optional)

### List HomeStations
`GET /user/gethomestations`

HomeStations are not required for collar tracking, but some accounts include them.
