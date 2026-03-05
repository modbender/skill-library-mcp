# Climate Configuration

## Setup climate.md

Create `~/garden/climate.md` with your garden's climate profile:

```markdown
# Climate Profile

## Location
- **USDA Zone:** 9b
- **Latitude:** 37.7749° N
- **Elevation:** 50m

## Frost Dates
- **Last spring frost:** March 15 (average)
- **First fall frost:** November 15 (average)
- **Growing season:** ~245 days

## Temperature Ranges
- **Record low:** -7°C (rare, 1-2 times per decade)
- **Typical winter low:** 2-5°C
- **Summer high:** 30-35°C (July-August peaks)

## Precipitation
- **Annual:** 500mm
- **Dry season:** June-September (minimal rain)
- **Wet season:** November-March
- **Irrigation needed:** May-October

## Microclimate Notes
- South-facing garden, good sun exposure
- North fence creates wind shelter
- Low corner (bed-3) collects cold air = frost pocket
- Stone wall retains heat, extends season for tender plants

## Alert Thresholds
- **Frost alert:** Forecast below 2°C
- **Heat alert:** Forecast above 35°C
- **Wind alert:** Gusts above 50 km/h
```

## Seasonal Planting Windows

Based on frost dates, calculate:

| Category | Start After | End Before |
|----------|-------------|------------|
| Tender annuals (tomato, pepper) | Last frost + 2 weeks | First frost |
| Hardy annuals (lettuce, peas) | 4 weeks before last frost | 6 weeks before first frost |
| Cool season crops | Fall: 8 weeks before first frost | Spring: 6 weeks after last frost |

## Climate-Aware Recommendations

When user asks "what can I plant now?":

1. Check current date against frost dates
2. Calculate weeks until/since frost events
3. Filter plant suggestions by timing
4. Note microclimate exceptions ("bed-3 runs cold, wait extra week")

## Alert Triggers

When user reports weather:

**"Frost tonight"**
1. List tender plants currently in ground
2. Suggest protection methods:
   - Cover with frost cloth
   - Harvest mature produce
   - Move containers indoors
3. Note affected zones (especially frost pockets)

**"Heat wave coming"**
1. Increase watering schedule
2. Consider shade cloth for sensitive plants
3. Harvest cool-season crops before bolting
4. Early morning watering preferred

**"Storm warning"**
1. Stake/secure tall plants
2. Harvest ripe produce
3. Check drainage in problem areas
4. Secure garden structures

## Zone-Specific Climate

Link microclimate data to zones:

```markdown
# zones/bed-3.md
...
## Microclimate
- **Frost risk:** HIGH (cold air pocket)
- **Adjustment:** Plant 1 week later than general date
- **Best for:** Cold-hardy crops, late-season extension
```

## Tracking Weather Impact

Log significant weather in monthly log:

```
## 2026-06-15
- 🌡️ Heat wave day 3 (38°C recorded)
- 💧 Emergency watering at 6pm
- 💀 Lost lettuce to bolt
- 📝 Note: move lettuce to shaded bed next year
```

This builds historical data for better predictions.
