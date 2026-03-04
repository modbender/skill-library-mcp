# Flux API Reference

**Base URL:** `https://api.flux-universe.com` (or `http://localhost:3000` for local instances)

---

## Event Ingestion

### POST /api/events

Publish single event to Flux.

**Request:**
```json
{
  "stream": "sensors",
  "source": "agent-01",
  "timestamp": 1739290200000,
  "payload": {
    "entity_id": "temp-sensor-01",
    "properties": {
      "temperature": 22.5,
      "unit": "celsius"
    }
  }
}
```

**Optional Fields:**
- `eventId` - Auto-generated UUIDv7 if omitted
- `timestamp` - Required. Unix epoch milliseconds
  (e.g. `date +%s000` in bash, `int(time.time()*1000)` in Python).
  flux.sh generates this automatically.
- `key` - Optional ordering/grouping hint
- `schema` - Optional schema metadata

**Response:**
```json
{
  "eventId": "019c4da0-3e28-75c3-991b-ae7b2576485a",
  "stream": "sensors"
}
```

---

### POST /api/events/batch

Publish multiple events at once.

**Request:**
```json
{
  "events": [
    {
      "stream": "sensors",
      "source": "agent-01",
      "payload": {
        "entity_id": "sensor-01",
        "properties": {"temp": 22}
      }
    },
    {
      "stream": "sensors",
      "source": "agent-01",
      "payload": {
        "entity_id": "sensor-02",
        "properties": {"temp": 23}
      }
    }
  ]
}
```

**Response:**
```json
{
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "eventId": "019c4da0-...",
      "stream": "sensors"
    },
    {
      "eventId": "019c4da1-...",
      "stream": "sensors"
    }
  ]
}
```

---

## State Query

### GET /api/state/entities

List all entities in current world state.

**Response:**
```json
[
  {
    "id": "temp-sensor-01",
    "properties": {
      "temperature": 22.5,
      "unit": "celsius"
    },
    "lastUpdated": "2026-02-11T16:54:33.260296395+00:00"
  },
  {
    "id": "temp-sensor-02",
    "properties": {
      "temperature": 23.8,
      "unit": "celsius"
    },
    "lastUpdated": "2026-02-11T16:55:12.123456789+00:00"
  }
]
```

---

### GET /api/state/entities/:id

Get specific entity by ID.

**Response (200 OK):**
```json
{
  "id": "temp-sensor-01",
  "properties": {
    "temperature": 22.5,
    "unit": "celsius",
    "location": "lab-A"
  },
  "lastUpdated": "2026-02-11T16:54:33.260296395+00:00"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Entity not found"
}
```

---

## State Derivation Model

### How Events Become State

1. **Event Published:**
   ```json
   {
     "stream": "sensors",
     "payload": {
       "entity_id": "sensor-01",
       "properties": {"temperature": 22.5}
     }
   }
   ```

2. **Flux Processes Event:**
   - Validates envelope
   - Persists to NATS JetStream
   - State engine consumes event

3. **State Derived:**
   - Entity `sensor-01` created/updated
   - Property `temperature` set to `22.5`
   - `lastUpdated` timestamp recorded

4. **Query Returns Current State:**
   ```json
   {
     "id": "sensor-01",
     "properties": {"temperature": 22.5},
     "lastUpdated": "2026-02-11T..."
   }
   ```

### Property Updates

Properties merge on updates (last write wins per property):

```bash
# Event 1: Set temperature and unit
{"entity_id": "sensor-01", "properties": {"temperature": 22.5, "unit": "celsius"}}

# Event 2: Update temperature only
{"entity_id": "sensor-01", "properties": {"temperature": 23.0}}

# Result: Both properties preserved
{"temperature": 23.0, "unit": "celsius"}
```

---

## WebSocket Subscription

Real-time state updates via WebSocket (use wscat or a WebSocket client — not included in flux.sh):

**Endpoint:** `wss://api.flux-universe.com/api/ws` (or `ws://localhost:3000/api/ws` for local instances)

**Subscribe Message:**
```json
{
  "type": "subscribe",
  "entity_id": "temp-sensor-01"
}
```

**Update Notification:**
```json
{
  "type": "state_update",
  "entity_id": "temp-sensor-01",
  "property": "temperature",
  "value": 24.0,
  "timestamp": "2026-02-11T16:54:33.260296395+00:00"
}
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "error": "stream is required"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Failed to publish event to NATS"
}
```

---

## Architecture Notes

**Event Flow:**
```
Agent → POST /api/events → Validation → NATS JetStream → State Engine → In-Memory State (DashMap)
                                                                               ↓
Agent ← GET /api/state/entities ← Query API ← In-Memory State
```

**Key Characteristics:**
- Events are immutable (never modified)
- State is derived (not directly written)
- NATS provides durability (events persist)
- State engine rebuilds from events on restart
- Multiple agents observe same canonical state
