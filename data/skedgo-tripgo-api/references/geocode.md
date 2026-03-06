# Geocode API

The Geocode API provides search and autocompletion functionality for transit stops and other points of interest (POIs).

## Base URL

```
https://api.tripgo.com/v1/
```

## Authentication

All requests require an API key passed via the `X-TripGo-Key` header:

```
X-TripGo-Key: YOUR_API_KEY
```

---

## Endpoint: Search and Autocompletion

```
GET /geocode.json
```

Gets the transit stops and other POIs matching a provided search string. Optionally does auto completion.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search term |
| `near` | string | Yes | - | Nearby coordinate as `(lat,lng)` string |
| `a` | boolean | No | `false` | Set to `true` when results are used for autocompletion. Note that not all POI sources may be used when this is enabled. |
| `allowGoogle` | boolean | No | `false` | Set to `true` to enable Google Places API calls for geocoding (requires credentials). Will be set to `false` if `a=true`. |
| `allowW3W` | boolean | No | `false` | Set to `true` to enable What3Words API calls for geocoding (requires credentials). |
| `allowYelp` | boolean | No | `false` | Set to `true` to enable Yelp API calls for geocoding (requires credentials). Will be set to `false` if `a=true`. |
| `allowFoursquare` | boolean | No | `false` | Set to `true` to enable Foursquare API calls for geocoding (requires credentials). Will be set to `false` if `a=true`. |
| `limit` | integer | No | `25` | Limits the amount of results for each search term. Any negative value means all results. |

### Example Request

```bash
curl -X GET "https://api.tripgo.com/v1/geocode.json?q=Central+Station&near=(-33.8688,151.2093)" \
  -H "Accept: application/json" \
  -H "X-TripGo-Key: YOUR_API_KEY"
```

### Response (200)

```json
{
  "query": "string",
  "choices": [
    {
      // Location object or StopLocation
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Search term as provided in input |
| `choices` | array of objects | Matching results. May be of type `Location` or `StopLocation`. |

---

## Optional Providers

To enable third-party geocoding providers, you need to configure credentials. See [Unlocking Geocoding Providers](https://developer.tripgo.com/extensions/#unlocking_geocoding_providers) for details.

- **Google Places**: Enable with `allowGoogle=true`
- **What3Words**: Enable with `allowW3W=true`
- **Yelp**: Enable with `allowYelp=true`
- **Foursquare**: Enable with `allowFoursquare=true`

Note: These providers are automatically disabled when using autocompletion mode (`a=true`).
