# Locations API

The Locations API provides endpoints for retrieving Points of Interest (POIs) and location details.

## Base URL
```
https://api.tripgo.com/v1/
```

## Authentication
All requests require the `X-TripGo-Key` header with your API key.

---

## Endpoints

### 1. POIs for a Circular Region

**GET** `/locations.json`

Gets points of interest for a provided circular region (coordinate + radius). Which POIs are included depends on the enabled modes (by default all modes). For public transport, transit stops are displayed; for driving, car parks; for bike share, bike share pods; for car share, car share locations; etc.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | number | Yes | Latitude |
| `lng` | number | Yes | Longitude |
| `radius` | number | Yes | Radius in metres. When using a radius of 5km or more, only major locations are returned that should be displayed when zoomed out, such as public transport parent stations. |
| `modes` | string[] | No | Mode identifiers for which to include POIs. |
| `strictModeMatch` | boolean | No | Should `modes` be treated strictly? Default: `true`. If `false`, you might request on-street parking, but also get off-street parking, or results for different car or bike share providers than those requested. |
| `limit` | integer | No | Maximum number of locations to return |
| `includeChildren` | boolean | No | Should "parent" public transport location (e.g., large station) include the details for each child stops (e.g., individual platforms)? Default: `false` |
| `includeRoutes` | boolean | No | Set to include `routes` information for public transport locations. Default: `false` |
| `includeDropOffOnly` | boolean | No | Set to include `drop-off-only` stops for public transport locations. Default: `false` |
| `sortedByProximity` | boolean | No | If enabled the results are sorted using the distance to the center as measure. Nearest results should be at the beginning of the list. Default: `false` |

#### Response
Returns `groups` array with POI data.

---

### 2. POIs for Map Region (using cell IDs)

**POST** `/locations.json`

Gets points of interest for a provided map region. Which POIs are included depends on the enabled modes (by default public transport only).

This variant using cell IDs is recommended if the client wants to cache locations locally, while frequently calling this endpoint to make sure the local data is updated without requiring a lot of data overhead (and having most of the logic on the server).

For an explanation of cell IDs and hash codes, please see the [FAQ](https://developer.tripgo.com/faq/#locations-cell-ids-and-hash-codes).

#### Request Body

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region` | string | Yes | Region code from `regions.json`. Example: `"AU_NSW_Sydney"` |
| `levels` | integer[] | No | Levels to include in the output. '1' means major locations displayed when zoomed out, '2' means minor locations displayed when zoomed in. Default: `[1]` |
| `cellIDs` | string[] | No* | Cell IDs for the region (required if `level` isn't 1 and `cellIDHashCodes` not provided). Example: `["-2540#11340","-2540#11341"]` |
| `cellIDHashCodes` | object | No* | Hash codes for cell IDs (required if `level` isn't 1 and `cellIDs` not provided) |
| `cellsPerDegree` | integer | No | Default: `75` |
| `modes` | string[] | No | Mode identifiers for which to include POIs. |
| `strictModeMatch` | boolean | No | Should `modes` be treated strictly? Default: `true` |
| `includeChildren` | boolean | No | Include child stops for parent stations? Default: `false` |
| `includeRoutes` | boolean | No | Include routes for public transport locations? Default: `false` |
| `includeDropOffOnly` | boolean | No | Include drop-off-only stops? Default: `false` |

*Either `cellIDs` or `cellIDHashCodes` is required when level isn't 1.

#### Example Request Body
```json
{
  "region": "AU_NSW_Sydney",
  "level": 2,
  "cellIDs": [
    "-2540#11340",
    "-2540#11341",
    "-2540#11342",
    "-2541#11340",
    "-2541#11341",
    "-2541#11342"
  ]
}
```

#### Response
Returns `groups` array with POI data.

---

### 3. Additional Details for a Coordinate

**GET** `/locationInfo.json`

Gets details, including real-time information, for the provided location (either identified by a coordinate or a unique identifier). Returns what3words information and, if available, a nearby transit stop and car park.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | number | No* | Latitude |
| `lng` | number | No* | Longitude |
| `identifier` | string | No* | Unique identifier for this location |
| `region` | string | No** | Region code from `regions.json` |

*Either `lat`/`lng` or `identifier` is required.
**Required if `identifier` is provided instead of `lat` and `lng`.

#### Response

Returns location details including:

| Field | Type | Description |
|-------|------|-------------|
| `lat` | number | Latitude (required) |
| `lng` | number | Longitude (required) |
| `details` | object | Contains `w3w` (what3words) and `w3wInfoURL` |
| `alerts` | array | Real-time alerts |
| `stop` | object | Nearby transit stop (StopLocationParent) |
| `bikePod` | object | Nearby bike share pod (BikePodInfo) |
| `carPark` | object | Nearby car park (CarParkInfo) |
| `carPod` | object | Car share location (CarPodInfo) |
| `carRental` | object | Car rental location (CarRentalInfo) |

---

## See Also
- [TripGo FAQ - Locations, cell IDs and hash codes](https://developer.tripgo.com/faq/#locations-cell-ids-and-hash-codes)
- [Regions API](./regions.md)
