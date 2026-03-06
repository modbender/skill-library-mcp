# Public Transport API

The Public Transport API provides endpoints to retrieve information about transit operators, routes, services, departure timetables, real-time information, and alerts.

## Base URL
```
https://api.tripgo.com/v1/
```

## Authentication
All requests require an API key in the header:
```
X-TripGo-Key: YOUR_API_KEY
```

## Endpoints

### 1. Operators for a Region or Group of Regions
**POST** `/info/operators.json`

Retrieves detailed information about covered transport service providers for a specified region.

**Request Body:**
```json
{
  "regions": ["US_CA_LosAngeles", "US_CA_Ventura"],
  "modes": ["pt_pub_tram", "pt_pub_bus"],
  "operatorIDs": [],
  "operatorNames": [],
  "onlyRealTime": false,
  "full": true
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regions | array of strings | Yes | Region names/codes from `regions.json` |
| modes | array of strings | No | Public transit modes (e.g., `pt_pub_tram`, `pt_pub_bus`). If absent, all modes are included |
| operatorIDs | array of strings | No | Operator IDs to retrieve. Use either this or `operatorNames` |
| operatorNames | array of strings | No | Operator names to retrieve. Use either this or `operatorIDs` |
| onlyRealTime | boolean | No | Filter only operators with real-time support (default: false) |
| full | boolean | No | Include full information or just IDs (default: false) |

**Response (200):**
```json
[
  {
    "id": "LACMTA",
    "name": "Metro - Los Angeles",
    "feedId": "string",
    "regions": ["string"],
    "hasStableID": false,
    "modes": [...]
  }
]
```

---

### 2. Routes for a Region or Operator
**POST** `/info/routes.json`

Retrieves detailed information about routes for either all operators in a region, or a specified operator.

**Request Body:**
```json
{
  "regions": ["US_CA_LosAngeles"],
  "query": "string",
  "operatorID": "LACMTA_Rail",
  "modes": ["pt_pub_tram"],
  "routesIDs": [],
  "routesNames": [],
  "onlyRealTime": false,
  "full": true
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regions | array of strings | Yes | Region names/codes from `regions.json` |
| query | string | No | Search string to filter routes by short name (complete) or name (partial) |
| operatorID | string | No | Operator ID from `info/operators.json` to filter by operator |
| modes | array of strings | No | Public transit modes (e.g., `pt_pub_tram`) |
| routesIDs | array of strings | No | Route IDs to retrieve. Use either this or `routesNames` |
| routesNames | array of strings | No | Route names to retrieve. Use either this or `routesIDs` |
| onlyRealTime | boolean | No | Filter only routes with real-time support (default: false) |
| full | boolean | No | Include full information or just IDs (default: false) |

**Response (200):**
```json
[
  {
    "region": "string",
    "id": "string",
    "operatorId": "string",
    "operatorName": "string",
    "routeName": "string",
    "shortName": "string",
    "mode": "string",
    "modeInfo": {...},
    "routeColor": {...},
    "numberOfServices": 0,
    "stops": ["string"],
    "realTime": {...}
  }
]
```

---

### 3. Details of a Route
**POST** `/info/routeInfo.json`

Retrieves detailed information about a route and its stops.

**Request Body:**
```json
{
  "regions": ["US_CA_LosAngeles"],
  "operatorID": "LACMTA_Rail",
  "routeID": "806"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regions | array of strings | Yes | Region names/codes from `regions.json` |
| operatorID | string | Yes | Operator ID from `info/routes.json` or `info/operators.json` |
| routeID | string | Yes | Route ID from `info/routes.json` |

**Response (200):**
```json
{
  "region": "string",
  "id": "string",
  "operatorId": "string",
  "operatorName": "string",
  "routeName": "string",
  "shortName": "string",
  "mode": "string",
  "modeInfo": {...},
  "routeColor": {...},
  "directions": [...]
}
```

---

### 4. Services for a Route
**POST** `/info/services.json`

Retrieves detailed information about services for a specified route.

**Request Body:**
```json
{
  "regions": ["US_CA_LosAngeles"],
  "operatorID": "LACMTA_Rail",
  "routeID": "806",
  "serviceTripIDs": [40358027],
  "onlyRealTime": false,
  "full": true
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| regions | array of strings | Yes | Region names/codes from `regions.json` |
| operatorID | string | Yes | Operator ID from `info/routes.json` or `info/operators.json` |
| routeID | string | Yes | Route ID from `info/routes.json` |
| serviceTripIDs | array of strings | No | Specific service trip IDs to retrieve |
| onlyRealTime | boolean | No | Filter only services with real-time support (default: false) |
| full | boolean | No | Include full information or just IDs (default: false) |

**Response (200):**
```json
[
  {
    "id": "string",
    "stops": ["string"],
    "realTime": {...}
  }
]
```

---

### 5. Departure Timetable for a Stop
**POST** `/departures.json`

Gets the departure timetable for a provided list of transit stops. Returns the next `limit` departures after `timeStamp`.

**Request Body:**
```json
{
  "region": "AU_NSW_Sydney",
  "embarkationStops": ["2035143"],
  "disembarkationRegion": "string",
  "disembarkationStops": [],
  "timeStamp": 0,
  "limit": 10,
  "includeStops": false,
  "filters": []
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Region code from `regions.json` |
| embarkationStops | array of strings | Yes | Stop codes for departure |
| disembarkationRegion | string | No | Region code for disembarkation stops (when different from embarkation) |
| disembarkationStops | array of strings | No | Stop codes for destination (filters services to those covering the journey) |
| timeStamp | integer | No | Seconds since 1970 for earliest time (default: current time) |
| limit | integer | No | Number of services to return |
| includeStops | boolean | No | Whether to include stops related to the service |
| filters | array of objects | No | Optional filters (treated as OR condition) |

**Response (200):**
```json
{
  "embarkationStops": [
    {
      "stopCode": "string",
      "services": [...],
      "wheelchairAccessible": true
    }
  ],
  "parentInfo": {...},
  "alerts": [...]
}
```

---

### 6. Real-time Information for a Service
**POST** `/latest.json`

Retrieves real-time information for specified services.

**Request Body:**
```json
{
  "region": "AU_NSW_Sydney",
  "services": [
    {
      "operator": "Sydney Buses",
      "serviceTripID": "766415652016030700000",
      "startStopCode": "2035143",
      "endStopCode": "string",
      "startTime": 0
    }
  ]
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Region code from `regions.json` |
| services | array of objects | Yes | Array of service objects |
| services[].operator | string | Yes | ID or name of the service's operator |
| services[].serviceTripID | string | Yes | ID of the service |
| services[].startStopCode | string | No | Only return real-time for this stop |
| services[].endStopCode | string | No | Include arrival time at this stop |
| services[].startTime | integer | No | Departure time in seconds since 1970 (highly recommended) |

**Response (200):**
```json
{
  "services": [
    {
      "serviceTripID": "string",
      "alerts": [...],
      "realtimeVehicle": {...},
      "realtimeAlternativeVehicle": [...],
      "startStopCode": "string",
      "startTime": 0,
      "endStopCode": "string",
      "endTime": 0,
      "lastUpdate": 0,
      "stops": {...}
    }
  ]
}
```

---

### 7. Get Details of a Service
**GET** `/service.json`

Gets the details of a transit service from the traveller's perspective. Can include multiple shapes if the vehicle continues as a different service.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Region identifier from `regions.json` |
| serviceTripID | string | Yes | Identifier of service from other servlets |
| operator | string | No | Operator of service (recommended if ID might match multiple operators) |
| embarkationDate | integer | Yes | Departure time in seconds since 1970 |
| encode | boolean | Yes | Set to `true` to receive waypoints as encoded polyline |
| startStopCode | string | No | Stop code of embarkation (first stop to be "travelled") |
| endStopCode | string | No | Stop code of disembarkation (last stop to be "travelled") |

**Example Request:**
```
GET /service.json?region=AU_NSW_Sydney&serviceTripID=142496466201603080e21&operator=Sydney%20Buses&embarkationDate=1457740800&encode=true
```

**Response (200):**
```json
{
  "shapes": [...],
  "modeInfo": {...},
  "realTimeStatus": "IS_REAL_TIME",
  "realtimeVehicle": {...},
  "realtimeAlternativeVehicle": [...],
  "alerts": [...]
}
```

---

### 8. Get Real-time Alerts
**GET** `/alerts/transit.json`

Retrieves real-time alerts for a region.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Region code from `regions.json` |

**Example Request:**
```
GET /alerts/transit.json?region=AU_NSW_Sydney
```

**Response (200):**
```json
{
  "alerts": [
    {
      "alert": {
        "title": "string",
        "hashCode": 0,
        "severity": "alert",
        "text": "string",
        "type": "string",
        "externalId": "string",
        "url": "string",
        "remoteIcon": "string",
        "location": {...},
        "action": {...}
      },
      "operators": ["string"],
      "stopCodes": ["string"],
      "routeIDs": ["string"],
      "serviceTripIDs": ["string"]
    }
  ]
}
```

---

## Common Response Codes
- **200** - Successful response
- **400** - Bad request (invalid parameters)
