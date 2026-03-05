#!/bin/bash

# Lyrion Music Server Control Script
# JSON-RPC API Client

HOST="${LYRION_HOST:-192.168.20.10}"
PORT="${LYRION_PORT:-9000}"
URL="http://${HOST}:${PORT}/jsonrpc.js"

# Hilfe anzeigen
show_help() {
    cat << 'EOF'
Lyrion Music Server Steuerung

Verwendung: lyrion.sh <befehl> [parameter]

Player:
  players                    - Liste aller Player
  status [player_id]         - Status eines Players

Wiedergabe:
  play [player_id]           - Wiedergabe starten
  pause [player_id]          - Pause umschalten
  stop [player_id]           - Stoppen
  power [player_id] [on|off|?] - Ein/Aus/Status
  next [player_id]           - Nächster Titel
  prev [player_id]           - Vorheriger Titel

Lautstärke:
  volume [player_id] [0-100|+|-] - Lautstärke setzen/ändern
  mute [player_id]           - Stummschalten umschalten

Playlist:
  playlist [player_id]       - Aktuelle Playlist anzeigen
  clear [player_id]          - Playlist leeren
  add [player_id] <uri>      - Zur Playlist hinzufügen
  insert [player_id] <uri>   - Als nächstes einfügen
  playuri [player_id] <uri>  - URI direkt abspielen

Datenbank:
  artists                    - Künstler auflisten
  albums [artist_id]         - Alben auflisten
  songs [album_id]           - Titel auflisten
  search <begriff>           - Suche in der Datenbank

Beispiele:
  lyrion.sh players
  lyrion.sh play aa:bb:cc:dd:ee:ff
  lyrion.sh volume aa:bb:cc:dd:ee:ff 50
  lyrion.sh search "Queen"
EOF
}

# JSON-RPC Request senden
# $1 = player_id (oder "" für global)
# $2+ = Befehl und Parameter
send_request() {
    local player_id="$1"
    shift
    
    # Parameter als JSON-Array aufbauen
    local params=""
    for param in "$@"; do
        if [ -z "$params" ]; then
            params="\"$param\""
        else
            params="$params, \"$param\""
        fi
    done
    
    local json="{\"id\":1,\"method\":\"slim.request\",\"params\":[\"$player_id\",[$params]]}"
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$json" \
        "$URL"
}

# Player-Liste abrufen
cmd_players() {
    send_request "" "players" "0" "100" | python3 -m json.tool 2>/dev/null || send_request "" "players" "0" "100"
}

# Player-Status
cmd_status() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        echo "Verwendung: status <player_id>"
        exit 1
    fi
    send_request "$player_id" "status" "-" "1" "tags:aAlKtTn" | python3 -m json.tool 2>/dev/null || send_request "$player_id" "status" "-" "1" "tags:aAlKtTn"
}

# Wiedergabe starten
cmd_play() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        echo "Verwendung: play <player_id>"
        exit 1
    fi
    send_request "$player_id" "play"
}

# Pause umschalten
cmd_pause() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        echo "Verwendung: pause <player_id>"
        exit 1
    fi
    send_request "$player_id" "pause"
}

# Stoppen
cmd_stop() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        echo "Verwendung: stop <player_id>"
        exit 1
    fi
    send_request "$player_id" "stop"
}

# Power ein/aus
cmd_power() {
    local player_id="${1:-}"
    local state="${2:-?}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        echo "Verwendung: power <player_id> [on|off|?]"
        exit 1
    fi
    case "$state" in
        on|1) state="1" ;;
        off|0) state="0" ;;
        *) state="?" ;;
    esac
    send_request "$player_id" "power" "$state"
}

# Nächster Titel
cmd_next() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        exit 1
    fi
    send_request "$player_id" "playlist" "index" "+1"
}

# Vorheriger Titel
cmd_prev() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        exit 1
    fi
    send_request "$player_id" "playlist" "index" "-1"
}

# Lautstärke
cmd_volume() {
    local player_id="${1:-}"
    local vol="${2:-}"
    if [ -z "$player_id" ] || [ -z "$vol" ]; then
        echo "Fehler: player_id und Volume erforderlich"
        echo "Verwendung: volume <player_id> <0-100|+|-%>"
        exit 1
    fi
    send_request "$player_id" "mixer" "volume" "$vol"
}

# Stummschalten
cmd_mute() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        exit 1
    fi
    send_request "$player_id" "mixer" "muting"
}

# Playlist anzeigen
cmd_playlist() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        exit 1
    fi
    send_request "$player_id" "status" "0" "100" "tags:aAlKtTn" | python3 -m json.tool 2>/dev/null || send_request "$player_id" "status" "0" "100" "tags:aAlKtTn"
}

# Playlist leeren
cmd_clear() {
    local player_id="${1:-}"
    if [ -z "$player_id" ]; then
        echo "Fehler: player_id erforderlich"
        exit 1
    fi
    send_request "$player_id" "playlist" "clear"
}

# Zur Playlist hinzufügen
cmd_add() {
    local player_id="${1:-}"
    local uri="${2:-}"
    if [ -z "$player_id" ] || [ -z "$uri" ]; then
        echo "Fehler: player_id und URI erforderlich"
        echo "Verwendung: add <player_id> <uri>"
        exit 1
    fi
    send_request "$player_id" "playlist" "add" "$uri"
}

# Als nächstes einfügen
cmd_insert() {
    local player_id="${1:-}"
    local uri="${2:-}"
    if [ -z "$player_id" ] || [ -z "$uri" ]; then
        echo "Fehler: player_id und URI erforderlich"
        echo "Verwendung: insert <player_id> <uri>"
        exit 1
    fi
    send_request "$player_id" "playlist" "insert" "$uri"
}

# URI direkt abspielen
cmd_playuri() {
    local player_id="${1:-}"
    local uri="${2:-}"
    if [ -z "$player_id" ] || [ -z "$uri" ]; then
        echo "Fehler: player_id und URI erforderlich"
        echo "Verwendung: playuri <player_id> <uri>"
        exit 1
    fi
    send_request "$player_id" "playlist" "play" "$uri"
}

# Künstler auflisten
cmd_artists() {
    send_request "" "artists" "0" "1000" | python3 -m json.tool 2>/dev/null || send_request "" "artists" "0" "1000"
}

# Alben auflisten
cmd_albums() {
    local artist_id="${1:-}"
    if [ -n "$artist_id" ]; then
        send_request "" "albums" "0" "1000" "artist_id:$artist_id" | python3 -m json.tool 2>/dev/null || send_request "" "albums" "0" "1000" "artist_id:$artist_id"
    else
        send_request "" "albums" "0" "1000" | python3 -m json.tool 2>/dev/null || send_request "" "albums" "0" "1000"
    fi
}

# Titel auflisten
cmd_songs() {
    local album_id="${1:-}"
    if [ -n "$album_id" ]; then
        send_request "" "titles" "0" "1000" "album_id:$album_id" "tags:aAlKtTn" | python3 -m json.tool 2>/dev/null || send_request "" "titles" "0" "1000" "album_id:$album_id" "tags:aAlKtTn"
    else
        send_request "" "titles" "0" "1000" "tags:aAlKtTn" | python3 -m json.tool 2>/dev/null || send_request "" "titles" "0" "1000" "tags:aAlKtTn"
    fi
}

# Suche
cmd_search() {
    local term="${1:-}"
    if [ -z "$term" ]; then
        echo "Fehler: Suchbegriff erforderlich"
        echo "Verwendung: search <begriff>"
        exit 1
    fi
    send_request "" "search" "0" "100" "term:$term" | python3 -m json.tool 2>/dev/null || send_request "" "search" "0" "100" "term:$term"
}

# Hauptprogramm
main() {
    local cmd="${1:-help}"
    shift || true
    
    case "$cmd" in
        help|--help|-h)
            show_help
            ;;
        players)
            cmd_players
            ;;
        status)
            cmd_status "$@"
            ;;
        play)
            cmd_play "$@"
            ;;
        pause)
            cmd_pause "$@"
            ;;
        stop)
            cmd_stop "$@"
            ;;
        power)
            cmd_power "$@"
            ;;
        next)
            cmd_next "$@"
            ;;
        prev)
            cmd_prev "$@"
            ;;
        volume)
            cmd_volume "$@"
            ;;
        mute)
            cmd_mute "$@"
            ;;
        playlist)
            cmd_playlist "$@"
            ;;
        clear)
            cmd_clear "$@"
            ;;
        add)
            cmd_add "$@"
            ;;
        insert)
            cmd_insert "$@"
            ;;
        playuri)
            cmd_playuri "$@"
            ;;
        artists)
            cmd_artists
            ;;
        albums)
            cmd_albums "$@"
            ;;
        songs)
            cmd_songs "$@"
            ;;
        search)
            cmd_search "$@"
            ;;
        *)
            echo "Unbekannter Befehl: $cmd"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
