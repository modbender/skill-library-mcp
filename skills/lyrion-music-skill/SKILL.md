---
name: lyrion-music
description: Steuere Lyrion Music Server (LMS) über die JSON-RPC API. Nutze diesen Skill für Wiedergabe-Steuerung (Play/Pause/Stop), Lautstärke, Playlist-Verwaltung, Player-Auswahl und Musikdatenbank-Abfragen. Erfordert LMS auf Port 9000.
---

# Lyrion Music Server Skill

Steuerung des Lyrion Music Servers (ehemals Logitech Media Server) über JSON-RPC API.

## Konfiguration

Standard-Host: `192.168.20.40:9000` (konfigurierbar über LYRION_HOST Umgebungsvariable)

## Verwendung

Nutze das Skript `scripts/lyrion.sh` für alle Operationen:

```bash
./skills/lyrion-music/scripts/lyrion.sh <befehl> [parameter]
```

### Befehle

**Player-Verwaltung:**
- `players` - Liste aller Player
- `status [player_id]` - Aktueller Status eines Players

**Wiedergabe-Steuerung:**
- `play [player_id]` - Wiedergabe starten
- `pause [player_id]` - Pause umschalten
- `stop [player_id]` - Stoppen
- `power [player_id] [on|off]` - Player ein/ausschalten

**Lautstärke:**
- `volume [player_id] [0-100|+|-]` - Lautstärke setzen/ändern
- `mute [player_id]` - Stummschalten

**Playlist:**
- `playlist [player_id]` - Aktuelle Playlist anzeigen
- `clear [player_id]` - Playlist leeren
- `add [player_id] <url/pfad>` - Titel zur Playlist hinzufügen
- `playtrack [player_id] <index>` - Bestimmten Titel abspielen

**Datenbank:**
- `artists` - Künstler auflisten
- `albums [artist_id]` - Alben auflisten
- `songs [album_id]` - Titel auflisten
- `search <suchbegriff>` - Globale Suche

## API Referenz

Siehe [references/api.md](references/api.md) für vollständige API-Dokumentation.

## Beispiele

```bash
# Alle Player anzeigen
./skills/lyrion-music/scripts/lyrion.sh players

# Wiedergabe im Wohnzimmer starten (Player ID erforderlich)
./skills/lyrion-music/scripts/lyrion.sh play aa:bb:cc:dd:ee:ff

# Lautstärke auf 50% setzen
./skills/lyrion-music/scripts/lyrion.sh volume aa:bb:cc:dd:ee:ff 50

# Playlist leeren und Album abspielen
./skills/lyrion-music/scripts/lyrion.sh clear aa:bb:cc:dd:ee:ff
./skills/lyrion-music/scripts/lyrion.sh add aa:bb:cc:dd:ee:ff "db:album.id=123"
./skills/lyrion-music/scripts/lyrion.sh play aa:bb:cc:dd:ee:ff
```
