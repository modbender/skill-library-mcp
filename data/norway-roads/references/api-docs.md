# Norway Roads API Reference

## Statens Vegvesen NVDB API

Base URL: `https://nvdbapiles-v3.atlas.vegvesen.no`

### Object Types (vegobjekttyper)

- **207** - Trafikkmelding (Traffic messages/road closures)
- **305** - Føreforhold (Road surface conditions)
- **540** - Vegarbeid (Road work)

### Key Endpoints

#### Road Closures & Traffic Messages
```
GET /vegobjekter/207
```

Query parameters:
- `inkluder=alle` - Include all properties
- `lat={lat}&lon={lon}&radius={meters}` - Location-based search
- `vegreferanse={road}` - Filter by road reference (E6, E16, etc.)

Headers required:
```
Accept: application/vnd.vegvesen.nvdb-v3-rev1+json
User-Agent: norway-roads-skill/1.0
```

### Response Properties (egenskaper)

Common fields for traffic messages (type 207):

| Norwegian | English | Description |
|-----------|---------|-------------|
| Vegidentitet | Road identity | Road number (E6, Rv7, etc.) |
| Beskrivelse | Description | Human-readable description |
| Status | Status | Open/Closed/Partial |
| Alvorlighetsgrad | Severity | Høy/High, Middels/Medium, Lav/Low |
| Gyldig fra | Valid from | Start time |
| Gyldig til | Valid to | End time |
| Årsak | Cause | Reason for closure |

### City Coordinates

Used for route-based searches:

| City | Latitude | Longitude |
|------|----------|-----------|
| Oslo | 59.9139 | 10.7522 |
| Bergen | 60.3913 | 5.3221 |
| Stavanger | 58.9700 | 5.7331 |
| Trondheim | 63.4305 | 10.3951 |
| Tromsø | 69.6492 | 18.9553 |
| Kristiansand | 58.1467 | 7.9956 |
| Ålesund | 62.4722 | 6.1495 |
| Bodø | 67.2804 | 14.4049 |
| Fredrikstad | 59.2105 | 10.9362 |
| Sandnes | 58.8524 | 5.7352 |

### Severity Levels

- **Høy / High** - Critical, road closed or severe conditions
- **Middels / Medium** - Warning, partial closure or difficult conditions
- **Lav / Low** - Information, minor issues

### Road Numbering

- **E** - European routes (E6, E16, E18, E39)
- **Rv** - National roads (Rv7, Rv3, Rv15)
- **Fv** - County roads (Fv50, Fv60)

### Common Issues

1. **Winter closures** - Mountain passes often closed November-April
2. **Weather alerts** - High wind, snow, ice warnings
3. **Construction** - Road work with temporary closures
4. **Accidents** - Temporary closures due to incidents

### Alternative Data Sources

- Vegvesen.no mobile app API
- Trafikknytt (traffic news) RSS feeds
- Weather stations along roads
