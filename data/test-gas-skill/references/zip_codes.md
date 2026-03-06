# Columbus, OH Area ZIP Codes

## Downtown & Central
- 43085 - Downtown Columbus
- 43201 - Columbus (Downtown)
- 43202 - Columbus (Downtown/OSU area)
- 43203 - Columbus (Victorian Village)
- 43204 - Columbus (German Village)
- 43205 - Columbus (Olde Towne East)
- 43206 - Columbus (Bexley area)
- 43209 - Columbus (Eastgate)
- 43210 - Columbus (Campus area)
- 43211 - Columbus (Northland)
- 43212 - Columbus (Morse Rd area)
- 43213 - Columbus (Eastland area)
- 43214 - Columbus (Hilltop)
- 43215 - Columbus (South Columbus)
- 43216 - Columbus (Hilltop area)
- 43217 - Columbus (Westland)
- 43218 - Columbus (Linden)
- 43219 - Columbus (Morse Rd)
- 43220 - Columbus (Airport area)
- 43221 - Columbus (Reynoldsburg)
- 43222 - Columbus (Eastmoor)
- 43223 - Columbus (Obetz area)
- 43224 - Columbus (Southfield)
- 43225 - Columbus (Gahanna area)
- 43226 - Columbus (Westgate)
- 43227 - Columbus (Whitehall area)
- 43228 - Columbus (Hilliard)
- 43229 - Columbus (Groveport)
- 43230 - Columbus (Brice area)
- 43231 - Columbus (Pickerington area)
- 43232 - Columbus (Canal Winchester)
- 43235 - Columbus (Southeast)
- 43601 - Toledo (for reference)
- 45039 - Grove City

## Coordinates for ZIP Centers

For accurate geocoding, use ZIP + city + state:
- "43215, Columbus, OH" - South Columbus
- "43213, Columbus, OH" - Morse Rd area
- "43228, Columbus, OH" - Hilliard

## How to Geocode ZIP Codes

Using Nominatim (OpenStreetMap):
```python
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='gas-finder')
location = geolocator.geocode('43215, Columbus, OH')
```

Using Google Geocoding API (requires API key):
```python
import googlemaps
gmaps = googlemaps.Client(key='YOUR_API_KEY')
geocode_result = gmaps.geocode('43215')
```

Note: OpenStreetMap's Nominatim is free but has rate limits and may not be as accurate for ZIP-only searches. Always include city and state for best results.
