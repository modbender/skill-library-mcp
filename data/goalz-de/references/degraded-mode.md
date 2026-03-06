# Degradierter Modus

Den degradierten Modus nutzen, wenn die verfuegbare MCP-Tool-Flaeche kleiner als erwartet ist oder Tool-Antworten unklar bleiben.

## Fehlende Bootstrap-Tools

### `whoami` fehlt

- Authentifizierungsstatus als unbekannt behandeln.
- Keine Writes ausfuehren.
- Den Nutzer bitten, das Goalz-MCP-Setup zu pruefen.

### Registrierung blockiert

- Wenn `register` oder `confirm_registration` technisch nicht erfolgreich nutzbar sind, den Blocker kurz berichten.
- Keine halbfertigen Accounts weiterverwenden, wenn der Auth-Status unklar ist.
- Sobald die technische Blockade geloest ist, den Bootstrap erneut autonom versuchen.

### `list_teams` fehlt

- Nur mit globalen Reads weitermachen.
- Keine teamgebundenen Writes ausfuehren.
- Wenn moeglich vorhandenen Standardkontext weiterverwenden und den Nutzer nur informativ darauf hinweisen.

## Fehlende Policy-Tools

Wenn `*_with_policy`-Kommunikationstools fehlen:
- bei Kommunikation draft-first bleiben
- wenn Ton und Kontext klar genug sind, rohes Senden eigenstaendig abwaegen
- nur optional `beratung_optional` nutzen

## Fehlende Kontext-Tools

Wenn Such- oder Historien-Tools fehlen:
- nur auf Live-Reads bauen
- erwaehnen, dass historischer Kontext begrenzt ist

Wenn Community-Kontext-Tools fehlen:
- Entwuerfe kuerzer und vorsichtiger halten
- keine uebertrieben selbstsicheren Ton-Matching-Aussagen machen

## Unbekannte oder inkonsistente Antwortstruktur

Wenn einer Tool-Antwort erwartete Status- oder Datenfelder fehlen:
- keine Schreibaktionen auf dieser Antwort aufbauen
- zusammenfassen, was trotzdem bekannt ist
- einen direkten Lese-Folgeaufruf bevorzugen oder sicher stoppen

## Fehlende Workflow-Tools

Wenn Workflow-Tools wie `run_daily_manager_routine` fehlen:
- die kleineren Lese-Tools direkt nutzen
- das Fehlen nicht automatisch als Fehler behandeln

## Unsicherheit bei Tools mit hoher Wirkung

Wenn ein Tool mit hoher Wirkung existiert, sein Verhalten aber unklar ist:
- es nicht nutzen
- erklaeren, dass das Tool vorhanden ist, aber fuer diese konkrete Aktion nicht ausreichend verifiziert ist
