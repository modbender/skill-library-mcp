# Lyrion Music Server API Reference

## Überblick

Lyrion Music Server (LMS) bietet eine JSON-RPC API über HTTP.

- **Endpoint:** `http://<host>:9000/jsonrpc.js`
- **Methode:** POST
- **Content-Type:** `application/json`

## Request Format

```json
{
  "id": 1,
  "method": "slim.request",
  "params": [
    "<player_id>",
    ["<befehl>", "<param1>", "<param2>", ...]
  ]
}
```

Für globale Befehle (ohne Player): `""` als player_id verwenden.

## Wichtige Befehle

### Player

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `players` | `count`, `start` | Liste aller Player |
| `status` | `-`, `tags:...` | Aktueller Status |
| `power` | `0`, `1`, `?` | Ein/Aus/Status |
| `display` | `<line1>`, `<line2>`, `<duration>` | Display-Text |

### Wiedergabe

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `play` | - | Wiedergabe starten |
| `pause` | `0`, `1`, `?` | Pause an/aus/Status |
| `stop` | - | Stoppen |
| `mode` | `?` | Aktueller Modus |

### Lautstärke

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `mixer` | `volume`, `<0-100|+|-|%>` | Lautstärke |
| `mixer` | `muting`, `0`, `1`, `?` | Stummschaltung |

### Playlist

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `playlist` | `play`, `<uri>` | URI abspielen |
| `playlist` | `add`, `<uri>` | Zur Playlist hinzufügen |
| `playlist` | `insert`, `<uri>` | Als nächstes einfügen |
| `playlist` | `delete`, `<index>` | Eintrag löschen |
| `playlist` | `clear` | Playlist leeren |
| `playlist` | `index`, `<index>` | Zu Index springen |
| `playlist` | `tracks`, `-`, `tags:...` | Playlist-Inhalt |

### Datenbank

| Befehl | Parameter | Beschreibung |
|--------|-----------|--------------|
| `artists` | -, `tags:...` | Künstler auflisten |
| `albums` | -, `artist_id:...`, `tags:...` | Alben auflisten |
| `titles` | -, `album_id:...`, `tags:...` | Titel auflisten |
| `genres` | - | Genres auflisten |
| `search` | `term:<query>` | Globale Suche |

## Antwort Format

```json
{
  "id": 1,
  "result": {
    "_count": 10,
    "players_loop": [
      {
        "playerid": "aa:bb:cc:dd:ee:ff",
        "name": "Wohnzimmer",
        "model": "squeezelite",
        "power": 1,
        "isplaying": 1
      }
    ]
  }
}
```

## CLI über HTTP

Alternative: Direkte CLI-Befehle über GET:

```
http://<host>:9000/status.json?p0=playlist&p1=play&player=<player_id>
```

## Weitere Dokumentation

- Offizielle CLI-Doku: https://lyrion.org/reference/cli/
- LMS GitHub: https://github.com/LMS-Community/slimserver
