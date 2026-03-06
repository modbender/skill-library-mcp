#!/usr/bin/env bash
# apple_music_api.sh — Complete Apple Music API wrapper
# Every endpoint referenced in SKILL.md is implemented here.
set -euo pipefail

BASE="https://api.music.apple.com"

# ── Token check ───────────────────────────────────────────────────
require_dev_token() {
  if [[ -z "${APPLE_MUSIC_DEV_TOKEN:-}" ]]; then
    echo "ERROR: APPLE_MUSIC_DEV_TOKEN not set. See references/auth-setup.md" >&2; exit 1
  fi
}
require_user_token() {
  require_dev_token
  if [[ -z "${APPLE_MUSIC_USER_TOKEN:-}" ]]; then
    echo "ERROR: APPLE_MUSIC_USER_TOKEN not set. See references/auth-setup.md" >&2; exit 1
  fi
}

# ── HTTP helpers ──────────────────────────────────────────────────
_retry() {
  # Retry a curl command with exponential backoff on 429 responses.
  # Usage: _retry curl_args...
  local max_retries=3
  local delay=1
  local attempt=0
  local tmpfile=""
  tmpfile=$(mktemp "${TMPDIR:-/tmp}/am_api_XXXXXX")
  # Only use RETURN trap — EXIT persists globally and outlives the local var
  trap 'rm -f "$tmpfile"' RETURN

  while (( attempt <= max_retries )); do
    local http_code
    local curl_exit=0
    http_code=$(curl -sS -o "$tmpfile" -w '%{http_code}' "$@") || curl_exit=$?
    if [[ $curl_exit -ne 0 && "$http_code" != "429" ]]; then
      echo "ERROR: curl failed (exit $curl_exit). Check network connectivity." >&2
      return 1
    fi
    if [[ "$http_code" == "429" && attempt -lt max_retries ]]; then
      (( attempt++ ))
      echo "WARN: Rate limited (429). Retrying in ${delay}s (attempt ${attempt}/${max_retries})..." >&2
      sleep "$delay"
      (( delay *= 2 ))
    else
      cat "$tmpfile"
      if [[ "$http_code" =~ ^[45] ]]; then
        return 1
      fi
      return 0
    fi
  done
}

_make_auth_config() {
  # Write tokens to a curl config file so they don't appear in ps output.
  local cfgfile
  cfgfile=$(mktemp "${TMPDIR:-/tmp}/am_auth_XXXXXX")
  chmod 600 "$cfgfile"
  if [[ -n "${2:-}" ]]; then
    printf -- '-H "Authorization: Bearer %s"\n-H "Music-User-Token: %s"\n' "$1" "$2" > "$cfgfile"
  else
    printf -- '-H "Authorization: Bearer %s"\n' "$1" > "$cfgfile"
  fi
  echo "$cfgfile"
}

_get() {
  # Personalized request (both tokens)
  require_user_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN" "$APPLE_MUSIC_USER_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -K "$_cfg" "${BASE}${1}"
}

_get_catalog() {
  # Catalog-only request (dev token only)
  require_dev_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -K "$_cfg" "${BASE}${1}"
}

_post() {
  require_user_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN" "$APPLE_MUSIC_USER_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -X POST -K "$_cfg" \
    -H "Content-Type: application/json" \
    -d "${2}" \
    "${BASE}${1}"
}

_post_file() {
  require_user_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN" "$APPLE_MUSIC_USER_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -X POST -K "$_cfg" \
    -H "Content-Type: application/json" \
    -d @"${2}" \
    "${BASE}${1}"
}

_delete() {
  # DELETE request with JSON body (both tokens)
  require_user_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN" "$APPLE_MUSIC_USER_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -X DELETE -K "$_cfg" \
    -H "Content-Type: application/json" \
    -d @"${2}" \
    "${BASE}${1}"
}

_delete_no_body() {
  # DELETE request without body (both tokens)
  require_user_token
  local _cfg
  _cfg=$(_make_auth_config "$APPLE_MUSIC_DEV_TOKEN" "$APPLE_MUSIC_USER_TOKEN")
  trap 'rm -f "$_cfg"' RETURN INT TERM
  _retry -X DELETE -K "$_cfg" "${BASE}${1}"
}

_urlencode() {
  jq -sRr @uri <<< "$1"
}

# ── Commands ──────────────────────────────────────────────────────

cmd_verify() {
  require_user_token
  echo "Verifying developer token..." >&2
  if _get_catalog "/v1/storefronts/us" | jq -e '.data[0].id' >/dev/null 2>&1; then
    echo "  ✅ Developer token valid" >&2
  else
    echo "  ❌ Developer token failed — regenerate JWT" >&2; exit 1
  fi
  echo "Verifying user token..." >&2
  if _get "/v1/me/recent/played/tracks?limit=1" | jq -e '.data' >/dev/null 2>&1; then
    echo "  ✅ Music User Token valid" >&2
  else
    echo "  ❌ Music User Token failed (expired? re-authorize)" >&2; exit 1
  fi
  echo "Both tokens verified. 🎧" >&2
}

cmd_user_storefront() {
  # Detect storefront from the user's account
  require_user_token
  local resp
  resp=$(_get "/v1/me/storefront" 2>/dev/null) || true
  local sf
  sf=$(echo "$resp" | jq -r '.data[0].id // empty' 2>/dev/null)
  if [[ -n "$sf" ]]; then
    echo "$sf"
  else
    echo "us"  # fallback
    echo "WARN: Could not detect storefront, defaulting to 'us'" >&2
  fi
}

cmd_recent_tracks() {
  # Paginate through all 50 available recent tracks
  require_user_token
  local all="[]"
  for offset in 0 10 20 30 40; do
    local page
    page=$(_get "/v1/me/recent/played/tracks?types=songs&limit=10&offset=${offset}" 2>/dev/null) || break
    local data
    data=$(echo "$page" | jq -c '.data // []')
    [[ "$data" == "[]" ]] && break
    all=$(echo "$all" "$data" | jq -s '.[0] + .[1]')
  done
  echo "$all" | jq .
}

cmd_recent_played() {
  _get "/v1/me/recent/played?limit=10" | jq .
}

cmd_heavy_rotation() {
  _get "/v1/me/history/heavy-rotation?limit=10" | jq .
}

cmd_ratings() {
  local rtype="${1:-songs}"  # songs, albums, playlists, music-videos
  case "$rtype" in
    songs|albums|playlists|music-videos) ;;
    *) echo "ERROR: Invalid rating type: $rtype (allowed: songs, albums, playlists, music-videos)" >&2; return 1 ;;
  esac
  _get "/v1/me/ratings/${rtype}?limit=100" | jq .
}

cmd_library_artists() {
  local limit="${1:-25}"
  [[ "$limit" =~ ^[0-9]+$ ]] || { echo "ERROR: limit must be a number" >&2; return 1; }
  local all="[]"
  local offset=0
  while true; do
    local page
    page=$(_get "/v1/me/library/artists?limit=${limit}&offset=${offset}" 2>/dev/null) || break
    local data
    data=$(echo "$page" | jq -c '.data // []')
    [[ "$data" == "[]" ]] && break
    all=$(echo "$all" "$data" | jq -s '.[0] + .[1]')
    local count
    count=$(echo "$data" | jq 'length')
    [[ "$count" -lt "$limit" ]] && break
    offset=$((offset + limit))
    [[ $offset -ge 500 ]] && break  # safety cap
  done
  echo "$all" | jq '{"data": .}'
}

cmd_library_songs() {
  local limit="${1:-25}"
  [[ "$limit" =~ ^[0-9]+$ ]] || { echo "ERROR: limit must be a number" >&2; return 1; }
  local all="[]"
  local offset=0
  while true; do
    local page
    page=$(_get "/v1/me/library/songs?limit=${limit}&offset=${offset}&include=catalog" 2>/dev/null) || break
    local data
    data=$(echo "$page" | jq -c '.data // []')
    [[ "$data" == "[]" ]] && break
    all=$(echo "$all" "$data" | jq -s '.[0] + .[1]')
    local count
    count=$(echo "$data" | jq 'length')
    [[ "$count" -lt "$limit" ]] && break
    offset=$((offset + limit))
    [[ $offset -ge 500 ]] && break  # safety cap
  done
  echo "$all" | jq '{"data": .}'
}

cmd_recommendations() {
  _get "/v1/me/recommendations?limit=10" | jq .
}

cmd_replay_summary() {
  local year="${1:-}"
  local endpoint="/v1/me/music-summaries"
  [[ -n "$year" ]] && endpoint="${endpoint}?filter[year]=${year}"
  _get "$endpoint" | jq .
}

cmd_replay_milestones() {
  local year="${1:-}"
  local endpoint="/v1/me/music-summaries/milestones"
  [[ -n "$year" ]] && endpoint="${endpoint}?filter[year]=${year}"
  _get "$endpoint" | jq .
}

cmd_search() {
  local sf="${1:?Usage: search <storefront> <query> [types]}"
  local query="${2:?Usage: search <storefront> <query> [types]}"
  local types="${3:-songs,artists,albums}"
  [[ "$sf" =~ ^[a-z]{2}$ ]] || { echo "ERROR: Invalid storefront code: $sf" >&2; return 1; }
  local encoded
  encoded=$(_urlencode "$query")
  _get_catalog "/v1/catalog/${sf}/search?term=${encoded}&types=${types}&limit=25" | jq .
}

cmd_charts() {
  local sf="${1:?Usage: charts <storefront> [genre_id]}"
  local genre=""
  [[ -n "${2:-}" ]] && genre="&genre=${2}"
  _get_catalog "/v1/catalog/${sf}/charts?types=songs,albums&limit=25${genre}" | jq .
}

cmd_artist_albums() {
  local sf="${1:?Usage: artist-albums <storefront> <artist_id>}"
  local id="${2:?Usage: artist-albums <storefront> <artist_id>}"
  _get_catalog "/v1/catalog/${sf}/artists/${id}/albums?limit=25" | jq .
}

cmd_artist_top() {
  local sf="${1:?Usage: artist-top <storefront> <artist_id>}"
  local id="${2:?Usage: artist-top <storefront> <artist_id>}"
  _get_catalog "/v1/catalog/${sf}/artists/${id}?views=top-songs" | jq .
}

cmd_artist_detail() {
  local sf="${1:?Usage: artist-detail <storefront> <artist_id>}"
  local id="${2:?Usage: artist-detail <storefront> <artist_id>}"
  _get_catalog "/v1/catalog/${sf}/artists/${id}?include=albums,genres" | jq .
}

cmd_album_tracks() {
  local sf="${1:?Usage: album-tracks <storefront> <album_id>}"
  local id="${2:?Usage: album-tracks <storefront> <album_id>}"
  _get_catalog "/v1/catalog/${sf}/albums/${id}?include=tracks" | jq .
}

cmd_song_detail() {
  local sf="${1:?Usage: song-detail <storefront> <song_id>}"
  local id="${2:?Usage: song-detail <storefront> <song_id>}"
  _get_catalog "/v1/catalog/${sf}/songs/${id}?include=artists,albums" | jq .
}

cmd_genres() {
  local sf="${1:?Usage: genres <storefront>}"
  [[ "$sf" =~ ^[a-z]{2}$ ]] || { echo "ERROR: Invalid storefront code: $sf" >&2; return 1; }
  _get_catalog "/v1/catalog/${sf}/genres" | jq .
}

cmd_library_playlists() {
  local limit="${1:-25}"
  _get "/v1/me/library/playlists?limit=${limit}" | jq .
}

cmd_playlist_tracks() {
  local pid="${1:?Usage: playlist-tracks <playlist_library_id>}"
  _get "/v1/me/library/playlists/${pid}/tracks?limit=100" | jq .
}

cmd_create_playlist() {
  local json_file="${1:?Usage: create-playlist <json_file>}"
  [[ ! -f "$json_file" ]] && { echo "ERROR: File not found: ${json_file}" >&2; exit 1; }
  echo "Creating playlist..." >&2
  local resp
  resp=$(_post_file "/v1/me/library/playlists" "$json_file")
  echo "$resp" | jq .
  local name
  name=$(echo "$resp" | jq -r '.data[0].attributes.name // "Unknown"')
  echo "✅ Playlist '${name}' created in Apple Music!" >&2
}

cmd_add_to_playlist() {
  local pid="${1:?Usage: add-to-playlist <playlist_id> <json_file>}"
  local json_file="${2:?Usage: add-to-playlist <playlist_id> <json_file>}"
  [[ ! -f "$json_file" ]] && { echo "ERROR: File not found: ${json_file}" >&2; exit 1; }
  echo "Adding tracks to playlist ${pid}..." >&2
  _post_file "/v1/me/library/playlists/${pid}/tracks" "$json_file"
  echo "✅ Tracks added." >&2
}

cmd_remove_from_playlist() {
  local pid="${1:?Usage: remove-from-playlist <playlist_id> <json_file>}"
  local json_file="${2:?Usage: remove-from-playlist <playlist_id> <json_file>}"
  [[ ! -f "$json_file" ]] && { echo "ERROR: File not found: ${json_file}" >&2; exit 1; }
  echo "Removing tracks from playlist ${pid}..." >&2
  _delete "/v1/me/library/playlists/${pid}/tracks" "$json_file"
  echo "✅ Tracks removed." >&2
}

# ── Dispatch ──────────────────────────────────────────────────────
cmd="${1:-help}"; shift 2>/dev/null || true

case "$cmd" in
  verify)            cmd_verify ;;
  user-storefront)   cmd_user_storefront ;;
  recent-tracks)     cmd_recent_tracks ;;
  recent-played)     cmd_recent_played ;;
  heavy-rotation)    cmd_heavy_rotation ;;
  ratings)           cmd_ratings "$@" ;;
  library-artists)   cmd_library_artists "$@" ;;
  library-songs)     cmd_library_songs "$@" ;;
  recommendations)   cmd_recommendations ;;
  replay-summary)    cmd_replay_summary "$@" ;;
  replay-milestones) cmd_replay_milestones "$@" ;;
  search)            cmd_search "$@" ;;
  charts)            cmd_charts "$@" ;;
  artist-albums)     cmd_artist_albums "$@" ;;
  artist-top)        cmd_artist_top "$@" ;;
  artist-detail)     cmd_artist_detail "$@" ;;
  album-tracks)      cmd_album_tracks "$@" ;;
  song-detail)       cmd_song_detail "$@" ;;
  genres)            cmd_genres "$@" ;;
  library-playlists) cmd_library_playlists "$@" ;;
  playlist-tracks)   cmd_playlist_tracks "$@" ;;
  create-playlist)   cmd_create_playlist "$@" ;;
  add-to-playlist)   cmd_add_to_playlist "$@" ;;
  remove-from-playlist) cmd_remove_from_playlist "$@" ;;
  help|*)
    cat <<'EOF'
Apple Music DJ — API Wrapper

Usage: apple_music_api.sh <command> [args...]

Personalized (require both tokens):
  verify                              Validate tokens
  user-storefront                     Detect user's storefront
  recent-tracks                       Recently played (up to 50 tracks)
  recent-played                       Recently played resources
  heavy-rotation                      Heavy rotation albums/playlists
  ratings [type]                      Loved/disliked (songs|albums|playlists)
  library-artists [limit]             Library artists
  library-songs [limit]               Library songs (with catalog IDs)
  library-playlists [limit]           Library playlists
  recommendations                     Personalized recommendations
  replay-summary [year]               Replay / Music Summaries
  replay-milestones [year]            Replay milestones
  playlist-tracks <playlist_id>       Tracks in a library playlist
  create-playlist <json_file>         Create playlist from JSON spec
  add-to-playlist <id> <json_file>    Add tracks to existing playlist
  remove-from-playlist <id> <json>    Remove tracks from playlist

Catalog (require dev token only):
  search <storefront> <query> [types] Search catalog
  charts <storefront> [genre_id]      Top charts
  artist-albums <storefront> <id>     Artist discography
  artist-top <storefront> <id>        Artist top songs
  artist-detail <storefront> <id>     Artist info with albums & genres
  album-tracks <storefront> <id>      Album with track listing
  song-detail <storefront> <id>       Song with artist & album info
  genres <storefront>                  List all genre categories
EOF
    ;;
esac
