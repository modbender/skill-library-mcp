# TTP (Travelling Tourist Problem)

> ⚠️ **All TTP endpoints are deprecated.**

The TTP (Travelling Tourist Problem) API provides endpoints for solving a variant of the travelling salesman problem. Given both a sorted list A and set B of locations, it inserts the locations from set B into A in the optimal order while keeping all elements of A in their same relative order.

**Base URL:** `https://api.tripgo.com/v1/`

**Authentication:** Requires `X-TripGo-Key` header.

---

## Endpoints

### 1. Create Travelling Tourist Problem (Deprecated)

**POST** `/ttp/`

Creates a new instance of a travelling tourist problem. Returns an ID which can be used to fetch the solution.

#### Request Body (application/json)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string (date) | Yes | Date used to determine available services |
| `modes` | array of strings | Yes | Mode identifiers (e.g., `["pt_pub","ps_tax","wa_wal","cy_bic-s"]`) |
| `insert` | array of objects | No | Locations to insert (CoordinateWithID) |
| `insertInto` | array of objects | Yes | Fixed route locations (CoordinateWithID), requires at least 2 elements defining start and end |

#### Response 200 (application/json)

```json
{
  "id": "string"
}
```

---

### 2. Delete Travelling Tourist Problem (Deprecated)

**DELETE** `/ttp/{id}`

Deletes the problem of the provided ID. This is optional as problems expire automatically.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | ID of the problem to delete |

#### Responses

- `200` - Successful deletion
- `404` - Problem not found
- `410` - Problem already deleted

---

### 3. Get Solution to Travelling Tourist Problem (Deprecated)

**GET** `/ttp/{id}/solution`

> ⚠️ **Note:** The documentation title incorrectly shows "Delete travelling tourist problem" but the actual endpoint and URL (`/ttp/{id}/solution`) correctly indicate this retrieves the solution.

Retrieves the solution for the problem of the provided ID. The solution may take time to be created. Use the `hashCode` query parameter to check if the solution has changed.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | ID of the problem |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hashCode` | integer | No | Content hash code of previously fetched solution |

#### Responses

- `200` - Successful response with solution
- `299` - Solution not yet available (still processing)
- `304` - Solution not changed (when using hashCode)
- `404` - Problem not found
- `410` - Problem expired

#### Response 200 Body (application/json)

```json
{
  "id": "string",
  "hashCode": 0,
  "items": [
    {
      "locationId": "string",
      "tripOptions": [...]
    }
  ]
}
```

---

## Notes

- The TTP is a variant of the [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
- If `insert` (set B) is empty, this behaves similarly to `waypoint.json` but returns alternatives for going from one location to the next
- Solutions can change due to data changes (including real-time data)
