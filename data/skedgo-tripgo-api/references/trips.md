# Trips API

The Trips section provides endpoints for managing computed trips, including retrieval, saving, real-time updates, and tracking.

## Base URL

```
https://api.tripgo.com/v1/
```

## Authentication

All requests require the `X-TripGo-Key` header with your API key.

## Endpoints

### 1. Retrieve Previously Computed Trip

**GET** `/trip/{id}`

Retrieves a previously computed trip by its ID.

**URL:** `https://api.tripgo.com/v1/trip/{id}`

**Parameters:**
- `id` (path): The trip identifier

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** Returns the trip details in JSON format.

**Notes:**
- The temporaryURL allows access to the trip for a short-term period (maximum of 7 days from the time of creation)
- The trip is stored on the server that computed it originally

---

### 2. Save Trip for Later Use

**GET** `/trip/save/{id}`

Saves a trip for later use, making it persistent beyond the typical user session.

**URL:** `https://api.tripgo.com/v1/trip/save/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the saveURL)

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** Returns the saved trip with new unique ID, shareURL (for web access) and appURL (for app/json access).

**Notes:**
- This feature needs to be enabled on 3scale with "Keep Trips" value set to true
- Saving the trip will create a new unique ID
- The trip saved could change when reconstructing it from the database if there's newer real-time data available

---

### 3. Update Trip with Real-Time Data

**GET** `/trip/update/{id}`

Updates a trip with real-time data by pulling from the server.

**URL:** `https://api.tripgo.com/v1/trip/update/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the updateURL)

**Query Parameters:**
- `hash` (optional): A hash code to check if anything has changed since last fetch

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** 
- Returns the updated trip if changes exist
- Returns an empty response if there is no change
- Returns new updateURL for subsequent requests if trip was updated

**Notes:**
- Only available if the trip has real-time information sources
- After two hours of not getting any update, the trip is discarded from memory
- If the trip involves a booking (e.g., Uber), on the status of the ride

---

 it will get updates### 4. Get Hooked URLs

**GET** `/trip/hook/{id}`

Gets the status of a hook (to confirm whether there is a hook already registered).

**URL:** `https://api.tripgo.com/v1/trip/hook/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the hookURL)

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** Returns the current hook configuration if one exists.

---

### 5. Hook a Trip to Real-Time Updates

**POST** `/trip/hook/{id}`

Registers a webhook callback to receive real-time updates when the trip changes.

**URL:** `https://api.tripgo.com/v1/trip/hook/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the hookURL)

**Headers:**
- `X-TripGo-Key`: Your API key

**Body (JSON):**
```json
{
  "url": "https://your-webhook-url.com/callback",
  "headers": {
    "x-custom-header": "value"
  }
}
```

**Response:** Returns 204 No Content on success.

**Notes:**
- Only one webhook per trip can be registered
- Multiple calls to register different webhooks will override existing ones
- Our platform will POST the tripID and tripURL to your registered URL when updates occur
- After two hours of not getting any update, the trip is discarded from memory

---

### 6. Remove a Hook from a Trip

**DELETE** `/trip/hook/{id}`

Removes a previously registered webhook from a trip.

**URL:** `https://api.tripgo.com/v1/trip/hook/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the hookURL)

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** Returns 204 No Content on success.

---

### 7. Mark Trip as Planned by a User

**POST** `/trip/planned/{id}`

Marks a trip as planned by a user for analytics purposes.

**URL:** `https://api.tripgo.com/v1/trip/planned/{id}`

**Parameters:**
- `id` (path): The trip identifier (from the plannedURL)

**Headers:**
- `X-TripGo-Key`: Your API key

**Response:** Returns confirmation of the planned trip.

**Notes:**
- The plannedURL is meant to be used for analytics purposes
- Used to keep track of which returned trips the user actually took

---

## Trip URLs Overview

When a trip is computed, it returns a list of URLs:

| URL Type | Description |
|----------|-------------|
| temporaryURL | Temporary URL for short-term access (max 7 days) |
| saveURL | URL to make the trip persistent |
| updateURL | URL to pull real-time updates |
| hookURL | URL to register for push notifications |
| progressURL | URL to report user progress (analytics) |
| plannedURL | URL for marking trip as planned (analytics) |
| logURL | URL to log trip in user account |
| shareURL | Persistent URL for web access |
| appURL | Persistent URL for app/json access |

## Real-Time Updates

Two methods are available for real-time updates:

1. **Pulling (updateURL):** Client periodically checks for changes using a hash code
2. **Pushing (hookURL):** Client registers a webhook to receive notifications

Both support the same goal of updating the trip with real-time information.

## Feature Requirements

- "Keep Trips" must be enabled on 3scale (disabled by default)
- Real-time updates are optional and only available for trips where the platform has real-time information sources

---

## Related Documentation

- [Trip URLs (Enterprise)](https://developer.tripgo.com/enterprise/tripurls/)
- [TripGo API Main Documentation](https://developer.tripgo.com/)
