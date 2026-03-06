# Endpoint Reference

Sources:
- EFA XML API PDF: `https://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/EFA_XML_Schnittstelle_20151217.pdf`
- Live endpoint probes against `https://www.linzag.at/linz2` on February 13, 2026
- Open data catalog RDF: `https://www.data.gv.at/api/hub/repo/datasets/linien-fahrwege-und-haltestellen-der-linz-ag-linien-2025.rdf?useNormalizedId=true&locale=de`

## Summary
- Use EFA endpoints under `{baseUrl}/efa/...` for live stop search and departures.
- Use the RDF/open-data distributions for static network and stop datasets (GML/XSD/PDF), not live countdown departures.

## Endpoint: XML_STOPFINDER_REQUEST
- Route: `GET /efa/XML_STOPFINDER_REQUEST`
- Purpose: Find location candidates for a search token.
- Stable params used by this skill:
  - `locationServerActive=1`
  - `outputFormat=JSON`
  - `type_sf=any`
  - `name_sf=<query>`

Example request:
- `/efa/XML_STOPFINDER_REQUEST?locationServerActive=1&outputFormat=JSON&type_sf=any&name_sf=taubenmarkt`

Observed response behavior:
- Top-level object includes `stopFinder`.
- `stopFinder.points` is shape-variant:
  - list of points, or
  - object with nested `point` (single object or list).
- For `type_sf=any`, points may include non-stop types (`street`, etc.).
- Filter stop candidates using `anyType == "stop"` (or equivalent stop type fields).
- Common message codes in `stopFinder.message`:
  - `-8011`: results/alternative resolution returned (not necessarily an error).
  - `-8020`: no suitable result.

Relevant fields for stop resolution:
- `stateless` and `ref.id` (stop ID candidates)
- `name` (human stop label)
- `best`, `quality` (ranking hints)

## Endpoint: XML_DM_REQUEST
- Route: `GET /efa/XML_DM_REQUEST`
- Purpose: Fetch departure monitor data for a stop.
- Stable params used by this skill:
  - `locationServerActive=1`
  - `stateless=1`
  - `outputFormat=JSON`
  - `type_dm=any`
  - `name_dm=<stopId>`
  - `mode=direct`
  - `limit=<n>`

Example request:
- `/efa/XML_DM_REQUEST?locationServerActive=1&stateless=1&outputFormat=JSON&type_dm=any&name_dm=60501160&mode=direct&limit=10`

Observed response behavior:
- Top-level object includes `dm` and `departureList`.
- `departureList` is shape-variant:
  - list of departures, or
  - object containing `departure` (single object or list).
- Invalid stop IDs return message codes in `dm.message` (observed: `-8020`).

Relevant fields for normalized departure output:
- `countdown` -> `countdownInMinutes` (integer)
- `realDateTime` or `dateTime` -> `time` (ISO-like local timestamp)
- `servingLine.number`
- `servingLine.direction`
- `servingLine.directionFrom` (origin-like label)
- `servingLine.motType` (transport mode type code)

## Known Caveats
- JSON field shapes vary (object vs list). Always normalize before processing.
- EFA message codes are part of payload semantics even when HTTP status is `200`.
- Timezone offset is not explicit in date fragments; treat as local service time.
