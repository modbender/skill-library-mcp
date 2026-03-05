---
name: swiss-geo
description: Schweizer Geodaten, POIs und Tourismus. Orte/Adressen suchen, Höhen abfragen, städtische POIs finden (Restaurants, Cafés, Sehenswürdigkeiten via OpenStreetMap), ÖV-Fahrplan, Kartenlinks. Nutze bei Fragen zu Schweizer Orten, Attraktionen, Ausflügen oder Koordinaten.
---

# Swiss Geo Skill

Zugriff auf Swisstopo-Geodaten für die Schweiz.

## Funktionen

### 1. Orts-/Adresssuche
```bash
curl -s "https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=SUCHTEXT&type=locations&sr=4326"
```
- Gibt lat/lon (WGS84), Label, Gemeinde zurück
- `type=locations` für Adressen/Orte, `type=layers` für Layer-Suche

### 2. Höhenabfrage
Zuerst Koordinaten via Suche holen, dann in LV95 umrechnen:
```bash
# Umrechnung WGS84 → LV95 (grobe Näherung für Schweiz):
# easting = 2600000 + (lon - 7.4) * 73000
# northing = 1200000 + (lat - 46.95) * 111000

curl -s "https://api3.geo.admin.ch/rest/services/height?easting=EASTING&northing=NORTHING&sr=2056"
```
Gibt Höhe in Metern über Meer zurück.

### 3. Feature-Identifikation (Gemeinde, Kanton, etc.)
```bash
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=0&layers=all:LAYER_ID&sr=4326"
```

Wichtige Layer-IDs:
- `ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill` — Gemeindegrenzen
- `ch.swisstopo.swissboundaries3d-kanton-flaeche.fill` — Kantonsgrenzen
- `ch.bafu.bundesinventare-flachmoore` — Flachmoore
- `ch.bafu.schutzgebiete-paerke_nationaler_bedeutung` — Naturpärke

### 4. Kartenlink generieren
```
https://map.geo.admin.ch/?lang=de&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&E=LON&N=LAT&zoom=ZOOM
```
- `zoom`: 0-13 (13 = max Detail)
- `E`/`N`: WGS84 Koordinaten
- `layers`: Komma-getrennte Layer-IDs zum Einblenden

## Beispiel-Workflow: "Wo liegt Matterhorn und wie hoch ist es?"

1. **Suchen:**
```bash
curl -s "https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText=Matterhorn&type=locations&sr=4326"
```
→ lat=45.9766, lon=7.6586

2. **Höhe abfragen (LV95):**
```bash
# easting ≈ 2600000 + (7.6586-7.4)*73000 = 2618878
# northing ≈ 1200000 + (45.9766-46.95)*111000 = 1091893
curl -s "https://api3.geo.admin.ch/rest/services/height?easting=2618878&northing=1091893&sr=2056"
```
→ 4477.5m

3. **Kartenlink:**
```
https://map.geo.admin.ch/?lang=de&E=7.6586&N=45.9766&zoom=10
```

### 5. Wanderwege abfragen
```bash
# Wanderwege in einem Gebiet finden (bbox = west,south,east,north)
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.swisstopo.swisstlm3d-wanderwege&searchText=ORTSNAME&searchField=name"

# Wanderwege an einem Punkt identifizieren
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=50&layers=all:ch.swisstopo.swisstlm3d-wanderwege&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"
```

**Wanderweg-Kategorien:**
- `wanderweg` — Gelb markiert (T1)
- `bergwanderweg` — Weiss-rot-weiss (T2-T3)
- `alpinwanderweg` — Weiss-blau-weiss (T4-T6)

**Kartenlink mit Wanderwegen:**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=10&layers=ch.swisstopo.swisstlm3d-wanderwege&bgLayer=ch.swisstopo.pixelkarte-farbe
```

### 6. Berghütten & Unterkünfte
```bash
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=5000&layers=all:ch.swisstopo.unterkuenfte-winter&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"
```

**Kartenlink mit Hütten:**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=11&layers=ch.swisstopo.unterkuenfte-winter&bgLayer=ch.swisstopo.pixelkarte-farbe
```

### 7. Bergbahnen & Seilbahnen
```bash
# Seilbahnen mit Bundeskonzession
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=2000&layers=all:ch.bav.seilbahnen-bundeskonzession&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"

# Alle Seilbahnen (swissTLM3D)
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=2000&layers=all:ch.swisstopo.swisstlm3d-uebrigerverkehr&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"
```

**Kartenlink mit Bergbahnen:**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=11&layers=ch.bav.seilbahnen-bundeskonzession&bgLayer=ch.swisstopo.pixelkarte-farbe
```

### 8. Naturgefahren
```bash
# Lawinengefahr
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=100&layers=all:ch.bafu.silvaprotect-lawinen&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"

# Sturzgefahr (Steinschlag, Felssturz)
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=100&layers=all:ch.bafu.silvaprotect-sturz&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"

# Hochwasser-Warnkarte (aktuell)
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=500&layers=all:ch.bafu.hydroweb-warnkarte_national&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"
```

**Gefahren-Layer:**
| Layer-ID | Beschreibung |
|----------|--------------|
| `ch.bafu.silvaprotect-lawinen` | Lawinengebiete |
| `ch.bafu.silvaprotect-sturz` | Sturzgebiete |
| `ch.bafu.hydroweb-warnkarte_national` | Hochwasser aktuell |
| `ch.bafu.gefahren-waldbrand_warnung` | Waldbrandgefahr |
| `ch.vbs.sperr-gefahrenzonenkarte` | Militärische Sperrzonen |

**Kartenlink mit Naturgefahren:**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=12&layers=ch.bafu.silvaprotect-lawinen,ch.bafu.silvaprotect-sturz&bgLayer=ch.swisstopo.pixelkarte-farbe
```

### 9. Wetter (Schweiz)

**Aktuelles Wetter (via wttr.in):**
```bash
curl -s "wttr.in/Zürich?format=%l:+%c+%t+%h+%w&lang=de"
# Zürich: ⛅️ +5°C 78% ↙12km/h
```

**MeteoSwiss Warnungen (Karte):**
```
https://map.geo.admin.ch/?lang=de&layers=ch.meteoschweiz.gefahren-warnungen
```

**Lawinenbulletin SLF:**
- Aktuell: https://www.slf.ch/de/lawinenbulletin-und-schneesituation.html
- API (experimentell): https://www.slf.ch/avalanche/mobile/bulletin_de.json

**Hochwasser BAFU (aktuelle Pegel):**
```
https://map.geo.admin.ch/?lang=de&layers=ch.bafu.hydroweb-messstationen_gefahren
```

### 10. ÖV-Fahrplan (transport.opendata.ch)

**Verbindung suchen:**
```bash
curl -s "https://transport.opendata.ch/v1/connections?from=Zürich&to=Bern&limit=3"
```

**Abfahrtstafel:**
```bash
curl -s "https://transport.opendata.ch/v1/stationboard?station=Zürich+HB&limit=5"
```

**Haltestelle suchen:**
```bash
curl -s "https://transport.opendata.ch/v1/locations?query=Paradeplatz"
```

**Beispiel-Output parsen:**
```bash
curl -s "https://transport.opendata.ch/v1/stationboard?station=Bern&limit=3" | python3 -c "
import sys,json
data = json.load(sys.stdin)
for s in data.get('stationboard', []):
    time = s.get('stop', {}).get('departure', '')[11:16]
    cat = s.get('category', '') + s.get('number', '')
    print(f\"{time} {cat} → {s.get('to', '')}\")"
```

**Parameter:**
| Parameter | Beschreibung |
|-----------|--------------|
| `from` / `to` | Start/Ziel (Name oder ID) |
| `station` | Haltestelle für Abfahrtstafel |
| `limit` | Max. Ergebnisse |
| `date` | Datum (YYYY-MM-DD) |
| `time` | Zeit (HH:MM) |
| `isArrivalTime` | 1 = Ankunftszeit statt Abfahrt |

### 11. Weitere nützliche Daten

**ÖV-Haltestellen:**
```bash
curl -s "https://api3.geo.admin.ch/rest/services/api/MapServer/identify?geometryType=esriGeometryPoint&geometry=LON,LAT&tolerance=500&layers=all:ch.bav.haltestellen-oev&sr=4326&imageDisplay=500,500,96&mapExtent=5.9,45.8,10.5,47.8"
```

**Skitouren & Schneeschuhrouten:**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=11&layers=ch.swisstopo-karto.skitouren,ch.swisstopo-karto.schneeschuhrouten&bgLayer=ch.swisstopo.pixelkarte-farbe
```

**Hangneigung (für Touren):**
```
https://map.geo.admin.ch/?lang=de&E=LON&N=LAT&zoom=13&layers=ch.swisstopo-karto.hangneigung&bgLayer=ch.swisstopo.pixelkarte-farbe
```

### 12. Städtische POIs via OpenStreetMap (Overpass API)

**Kostenlos, kein API-Key nötig.** Ideal für Restaurants, Cafés, Eisdielen, Museen, Sehenswürdigkeiten in Städten.

#### Basis-Query (Bounding Box)
```bash
# POIs in einem Gebiet suchen (south,west,north,east)
# Beispiel: Eisdielen in Zürich-Zentrum
curl -s "https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A10%5D%3Bnode%5B%22amenity%22%3D%22ice_cream%22%5D%2847.36%2C8.52%2C47.39%2C8.56%29%3Bout%3B"
```

#### Query mit Stadt-Area (empfohlen)
```bash
# Alle Eisdielen in der Stadt Zürich
curl -s "https://overpass-api.de/api/interpreter" --data-urlencode 'data=[out:json][timeout:15];
area["name"="Zürich"]["admin_level"="8"]->.city;
(
  node["amenity"="ice_cream"](area.city);
  node["shop"="ice_cream"](area.city);
);
out body;'
```

#### Wichtige POI-Tags

| Kategorie | OSM-Tag | Beispiel |
|-----------|---------|----------|
| 🍦 Eisdiele | `amenity=ice_cream` | Gelateria |
| 🍕 Restaurant | `amenity=restaurant` | + `cuisine=*` |
| ☕ Café | `amenity=cafe` | |
| 🍺 Bar/Pub | `amenity=bar` / `pub` | |
| 🏛️ Museum | `tourism=museum` | |
| 🎭 Theater | `amenity=theatre` | |
| ⛪ Kirche | `amenity=place_of_worship` | |
| 🏰 Sehenswürdigkeit | `tourism=attraction` | |
| 👁️ Aussichtspunkt | `tourism=viewpoint` | |
| 🎡 Freizeitpark | `leisure=amusement_arcade` | |
| 🏊 Schwimmbad | `leisure=swimming_pool` | + `access=yes` |
| 🎮 Spielplatz | `leisure=playground` | |
| 🌳 Park | `leisure=park` | |

#### Beispiel: Museen & Sehenswürdigkeiten in Zürich Altstadt
```bash
curl -s "https://overpass-api.de/api/interpreter" --data-urlencode 'data=[out:json][timeout:15];
(
  node["tourism"="museum"](47.366,8.538,47.378,8.548);
  node["tourism"="attraction"](47.366,8.538,47.378,8.548);
  node["historic"](47.366,8.538,47.378,8.548);
);
out body;'
```

#### Beispiel: Familienfreundliche Orte (Spielplätze, Parks)
```bash
curl -s "https://overpass-api.de/api/interpreter" --data-urlencode 'data=[out:json][timeout:15];
area["name"="Zürich"]["admin_level"="8"]->.city;
(
  node["leisure"="playground"](area.city);
  way["leisure"="playground"](area.city);
);
out center body;'
```

#### Response parsen (Python)
```bash
curl -s "https://overpass-api.de/api/interpreter?data=..." | python3 -c "
import sys, json
data = json.load(sys.stdin)
for el in data.get('elements', []):
    tags = el.get('tags', {})
    name = tags.get('name', 'Unbenannt')
    lat, lon = el.get('lat', el.get('center', {}).get('lat', '')), el.get('lon', el.get('center', {}).get('lon', ''))
    addr = tags.get('addr:street', '')
    website = tags.get('website', '')
    opening = tags.get('opening_hours', '')
    print(f'{name}')
    if addr: print(f'  📍 {addr} {tags.get(\"addr:housenumber\", \"\")}')
    if opening: print(f'  🕐 {opening}')
    if website: print(f'  🔗 {website}')
    print()
"
```

#### Koordinaten für Schweizer Städte (Bbox)

| Stadt | South | West | North | East |
|-------|-------|------|-------|------|
| Zürich Zentrum | 47.36 | 8.52 | 47.39 | 8.56 |
| Zürich Altstadt | 47.366 | 8.538 | 47.378 | 8.548 |
| Bern Zentrum | 46.94 | 7.43 | 46.96 | 7.46 |
| Basel Zentrum | 47.55 | 7.58 | 47.57 | 7.61 |
| Luzern Zentrum | 47.04 | 8.29 | 47.06 | 8.32 |
| Genf Zentrum | 46.19 | 6.13 | 46.21 | 6.16 |

### 13. Schweiz Tourismus API (MySwitzerland)

**⚠️ Benötigt API-Key** (Header: `x-api-key`)

**Hinweis:** Diese API ist primär für Outdoor-Tourismus (Wandern, Bergtouren, Regionen) geeignet. Für städtische POIs (Restaurants, Cafés, Museen) ist die Overpass API (Abschnitt 12) besser.

**Sehenswürdigkeiten suchen:**
```bash
curl -s "https://opendata.myswitzerland.io/v1/attractions/?lang=de&limit=5" \
  -H "x-api-key: $MYSWITZERLAND_API_KEY"
```

**Touren suchen:**
```bash
curl -s "https://opendata.myswitzerland.io/v1/tours/?lang=de&limit=5" \
  -H "x-api-key: $MYSWITZERLAND_API_KEY"
```

**Geodaten einer Tour (GeoJSON):**
```bash
curl -s "https://opendata.myswitzerland.io/v1/tours/TOUR_ID/geodata" \
  -H "x-api-key: $MYSWITZERLAND_API_KEY"
```

**Destinationen:**
```bash
curl -s "https://opendata.myswitzerland.io/v1/destinations/?lang=de" \
  -H "x-api-key: $MYSWITZERLAND_API_KEY"
```

**Response-Felder:**
- `name` — Name der Attraktion/Tour
- `abstract` — Kurzbeschreibung
- `geo.latitude`, `geo.longitude` — Koordinaten
- `classification` — Kategorien (Saison, Typ, etc.)

## Beispiel-Workflows

### "Wo kann ich mit Kindern in Zürich Eis essen und was gibt's in der Nähe?"
1. Eisdielen via Overpass API suchen (Abschnitt 12)
2. Sehenswürdigkeiten/Spielplätze in der Nähe finden
3. ÖV-Verbindung dorthin (Abschnitt 10)
4. Kartenlink generieren (Abschnitt 4)

### "Wanderung mit Bergbahn und Hütte im Engadin?"
1. Bergbahnen suchen (Abschnitt 7)
2. Wanderwege finden (Abschnitt 5)
3. Berghütten identifizieren (Abschnitt 6)
4. MySwitzerland Touren abfragen (Abschnitt 13)

## Tipps
- **Städtische POIs** → Overpass API (kostenlos, detailliert)
- **Outdoor-Tourismus** → MySwitzerland API (braucht Key)
- **Karten & Geodaten** → Swisstopo (kostenlos)
- **ÖV-Fahrplan** → transport.opendata.ch (kostenlos)
- Suchergebnisse enthalten `origin` (address, sn25, gg25, etc.) zur Kategorisierung
- Für genaue LV95-Koordinaten siehe [references/api.md](references/api.md)
- Kombiniere Swisstopo-Layer mit Komma: `layers=layer1,layer2,layer3`
