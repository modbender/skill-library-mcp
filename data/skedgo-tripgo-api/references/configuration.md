# Configuration Section - TripGo API

## Section Overview
- **Section Name:** Configuration
- **Root URL:** https://developer.tripgo.com/#/configuration
- **Base API URL:** https://api.tripgo.com/v1/
- **Timestamp:** 2026-02-27
- **Skill Name:** skedgo-tripgo-api

---

## Endpoint List

### 1. Available Regions
| Field | Value |
|-------|-------|
| **Title** | Available regions |
| **URL** | https://developer.tripgo.com/#/configuration/paths/~1regions.json/post |
| **Method** | POST |
| **Path** | /regions.json |
| **Description** | Lists available regions and available transport modes. Provide optional hash code to only return output if the data has changed. |
| **Script Filename** | `scripts/configuration-available-regions.sh` |
| **Deprecated** | No |

#### Parameters
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| v | integer | Yes | Version number | 2 |
| hashCode | integer | No | Hash code of your last response. If supplied, response might only contain hashCode if data hasn't changed. | - |
| cityPolygons | boolean | No | Add city boundaries in the response (default: false) | false |

#### Headers
| Name | Value |
|------|-------|
| X-TripGo-Key | API key (required) |
| Content-Type | application/json |

#### Curl Example
```bash
curl -X POST "https://api.tripgo.com/v1/regions.json" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $TRIPGO_API_KEY" \
  -d '{ "v": 2 }'
```

#### Response Structure
```json
{
  "hashCode": 0,
  "regions": [
    {
      "name": "DE_BV_Nuremberg",
      "polygon": "SDf9723rhkjFKHAFB",
      "cities": [
        {
          "title": "Nuremberg",
          "lat": 1.1,
          "lng": 14.2,
          "timezone": "Europe/Berlin"
        }
      ],
      "modes": ["pt_pub", "me_car", "me_mot", "cy_bic", "wa_wal"],
      "urls": ["nuremberg-bv-de.hadron.buzzhives.com"]
    }
  ],
  "modes": {
    "$modeIdentifier": { ... }
  }
}
```

#### Notes
- Use the hashCode parameter to reduce bandwidth by only getting new data when it has changed.
- The response includes region codes needed for other API calls.

---

### 2. TSPs per Region
| Field | Value |
|-------|-------|
| **Title** | TSPs per region |
| **URL** | https://developer.tripgo.com/#/configuration/paths/~1regioninfo.json/post |
| **Method** | POST |
| **Path** | /regionInfo.json |
| **Description** | Retrieves basic information about covered transport service providers for the specified regions. |
| **Script Filename** | `scripts/configuration-tsps-per-region.sh` |
| **Deprecated** | No |

#### Parameters
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| region | string | Yes | Region name/code from regions.json | "DE_HH_Hamburg" |

#### Headers
| Name | Value |
|------|-------|
| X-TripGo-Key | API key (required) |
| Content-Type | application/json |

#### Curl Example
```bash
curl -X POST "https://api.tripgo.com/v1/regionInfo.json" \
  -H "Content-Type: application/json" \
  -H "X-TripGo-Key: $TRIPGO_API_KEY" \
  -d '{ "region": "DE_HH_Hamburg" }'
```

#### Response Structure
```json
{
  "regions": [
    {
      "code": "DE_HH_Hamburg",
      "streetBicyclePaths": true,
      "streetWheelchairAccessibility": false,
      "transitBicycleAccessibility": false,
      "transitConcessionPricing": false,
      "transitWheelchairAccessibility": true,
      "transitModes": [
        {
          "identifier": "pt_pub_ferry",
          "alt": "ferry",
          "localIcon": "ferry",
          "remoteIcon": "ferry-germany-hamburg",
          "color": { "red": 0, "blue": 211, "green": 157 }
        }
      ],
      "operators": [
        {
          "modes": ["pt_pub_train", "pt_pub_tram", "pt_pub_subway", "pt_pub_bus"],
          "name": "VGN",
          "numberOfServices": 50056,
          "realTimeStatus": "INCAPABLE",
          "types": [...]
        }
      ],
      "modes": { ... }
    }
  ]
}
```

#### Notes
- TSP = Transport Service Provider
- Returns detailed information about operators, transit modes, and accessibility features.

---

### 3. POIs for a Transport Mode
| Field | Value |
|-------|-------|
| **Title** | POIs for a transport mode |
| **URL** | https://developer.tripgo.com/#/configuration/paths/~1regions~1{code}~1locations/get |
| **Method** | GET |
| **Path** | /regions/{code}/locations |
| **Description** | Bulk fetch of all locations for the provided mode in a region. |
| **Script Filename** | `scripts/configuration-pois-for-a-transport-mode.sh` |
| **Deprecated** | No |

#### Parameters
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| code | string | Yes (path) | Region code from regions.json | DE_HH_Hamburg |
| mode | string | Yes (query) | Mode identifier for which to include POIs | pt_pub |
| includeChildren | boolean | No | Should parent station include child stop details (default: true) | true |
| includeRoutes | boolean | No | Include routes (default: false) | false |

 information for public transport#### Headers
| Name | Value |
|------|-------|
| X-TripGo-Key | API key (required) |

#### Curl Example
```bash
curl -X GET "https://api.tripgo.com/v1/regions/DE_HH_Hamburg/locations?mode=pt_pub&includeChildren=true&includeRoutes=false" \
  -H "X-TripGo-Key: $TRIPGO_API_KEY"
```

#### Response Structure
```json
{
  "groups": [
    {
      // Array of location group objects with 8 properties
    }
  ]
}
```

#### Notes
- POI = Points of Interest
- Use this endpoint to get all stations/stops for a specific transport mode in a region.
- Set includeChildren=false to only get parent stations.
- Set includeRoutes=true to get route information for public transport.

---

## Authentication
All endpoints require the `X-TripGo-Key` header with a valid API key.

## Common Transport Mode Identifiers
- `pt_pub` - Public transport
- `me_car` - Car
- `me_car-s` - Car share
- `me_car-r` - Car rental
- `me_car-p` - Carpooling
- `cy_bic` - Bicycle
- `cy_bic-s` - Bike share
- `wa_wal` - Walk
- `ps_tax` - Taxi
- `ps_tnc` - Ride share/TNC
