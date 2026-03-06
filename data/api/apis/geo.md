# Index

| API | Line |
|-----|------|
| OpenWeather | 2 |
| Mapbox | 61 |
| Google Maps Platform | 124 |

---

# OpenWeather

Weather data API for current conditions, forecasts, and historical data.

## Base URL
```
https://api.openweathermap.org/data/2.5
```

One Call API 3.0: `https://api.openweathermap.org/data/3.0`

## Authentication
API key as query parameter (`appid`).

```bash
curl -X GET "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
```

## Core Endpoints

### Current Weather
```bash
curl -X GET "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY&units=metric"
```

### 5-Day Forecast
```bash
curl -X GET "https://api.openweathermap.org/data/2.5/forecast?lat=51.5&lon=-0.12&appid=YOUR_API_KEY&units=metric"
```

### One Call API 3.0 (All-in-one)
```bash
curl -X GET "https://api.openweathermap.org/data/3.0/onecall?lat=51.5&lon=-0.12&appid=YOUR_API_KEY&units=metric"
```

### Geocoding (City to Coords)
```bash
curl -X GET "https://api.openweathermap.org/geo/1.0/direct?q=London&limit=1&appid=YOUR_API_KEY"
```

## Rate Limits
- Free: 60 calls/minute, 1,000,000 calls/month
- 429 response when exceeded
- Pro plans have higher limits

## Gotchas
- New API key activation takes up to 2 hours
- Use coordinates (`lat`, `lon`) for most accurate results
- `units=metric` for Celsius, `units=imperial` for Fahrenheit
- Don't call more than once per 10 minutes per location (data update freq)
- One Call API 3.0 requires separate subscription
- City names can be ambiguous - prefer coordinates
- Free plan data may have delays

## Links
- [Docs](https://openweathermap.org/api)
- [One Call API 3.0](https://openweathermap.org/api/one-call-3)
- [Geocoding API](https://openweathermap.org/api/geocoding-api)
- [Pricing](https://openweathermap.org/price)
# Mapbox

Maps, geocoding, directions, and location services API.

## Base URL
```
https://api.mapbox.com
```

## Authentication
Access token as query parameter.

```bash
curl -X GET "https://api.mapbox.com/geocoding/v5/mapbox.places/Los%20Angeles.json?access_token=YOUR_ACCESS_TOKEN"
```

## Core Endpoints

### Forward Geocoding
```bash
curl -X GET "https://api.mapbox.com/search/geocode/v6/forward?q=1600%20Pennsylvania%20Ave&access_token=YOUR_ACCESS_TOKEN"
```

### Reverse Geocoding
```bash
curl -X GET "https://api.mapbox.com/search/geocode/v6/reverse?longitude=-77.0365&latitude=38.8977&access_token=YOUR_ACCESS_TOKEN"
```

### Directions
```bash
curl -X GET "https://api.mapbox.com/directions/v5/mapbox/driving/-122.42,37.78;-77.03,38.91?access_token=YOUR_ACCESS_TOKEN"
```

### Static Map Image
```bash
curl -X GET "https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/-122.4194,37.7749,12,0/600x400?access_token=YOUR_ACCESS_TOKEN"
```

### Isochrone (Travel Time)
```bash
curl -X GET "https://api.mapbox.com/isochrone/v1/mapbox/driving/-122.4194,37.7749?contours_minutes=15&access_token=YOUR_ACCESS_TOKEN"
```

## Rate Limits
- Varies by API and plan
- Geocoding: 600 requests/minute (free)
- Directions: 300 requests/minute (free)
- Headers indicate remaining quota

## Gotchas
- Geocoding v6 is latest (v5 still available)
- Coordinates format: `longitude,latitude` (not lat,lon!)
- `permanent=true` required for storing/caching results
- Access tokens can be scoped to specific APIs
- Temporary geocoding results can't be cached
- Search text max 20 words, 256 characters
- SDK available for web/mobile (often easier than raw API)

## Links
- [Docs](https://docs.mapbox.com/api/)
- [Geocoding](https://docs.mapbox.com/api/search/geocoding/)
- [Directions](https://docs.mapbox.com/api/navigation/directions/)
- [Playground](https://docs.mapbox.com/playground/)
# Google Maps Platform

Maps, geocoding, places, directions, and location services.

## Base URL
```
https://maps.googleapis.com/maps/api
```

## Authentication
API key as query parameter.

```bash
curl -X GET "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway&key=YOUR_API_KEY"
```

## Core Endpoints

### Geocoding
```bash
curl -X GET "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY"
```

### Reverse Geocoding
```bash
curl -X GET "https://maps.googleapis.com/maps/api/geocode/json?latlng=37.4224764,-122.0842499&key=YOUR_API_KEY"
```

### Directions
```bash
curl -X GET "https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=YOUR_API_KEY"
```

### Places Search
```bash
curl -X GET "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.7749,-122.4194&radius=500&type=restaurant&key=YOUR_API_KEY"
```

### Distance Matrix
```bash
curl -X GET "https://maps.googleapis.com/maps/api/distancematrix/json?origins=Seattle&destinations=San+Francisco&key=YOUR_API_KEY"
```

### Static Map
```bash
curl -X GET "https://maps.googleapis.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York&zoom=13&size=600x300&key=YOUR_API_KEY"
```

## Rate Limits
- Varies by API
- Geocoding: 50 requests/second
- Most APIs have per-day quotas
- Pay-as-you-go with free tier ($200/month credit)

## Gotchas
- Must enable each API individually in Cloud Console
- Billing account required even for free tier
- API key restrictions recommended (HTTP referrers, IP)
- `components` parameter helps disambiguate geocoding
- Places API returns place_id, not full details (need second call)
- `region` and `bounds` parameters bias results
- Caching allowed for geocoding, places have restrictions

## Links
- [Docs](https://developers.google.com/maps/documentation)
- [Geocoding](https://developers.google.com/maps/documentation/geocoding)
- [Places](https://developers.google.com/maps/documentation/places)
- [Directions](https://developers.google.com/maps/documentation/directions)
- [Pricing](https://mapsplatform.google.com/pricing/)
