#!/usr/bin/env bash
set -euo pipefail

# ===================== CONSTANTS =====================

GEOCODING_API="https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API="https://api.open-meteo.com/v1/forecast"

DEFAULT_FORECAST_DAYS=7
DEFAULT_CURRENT_PARAMS="temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,cloud_cover,is_day"
DEFAULT_HOURLY_PARAMS="temperature_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,wind_speed_10m"
DEFAULT_DAILY_PARAMS="temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code,wind_speed_10m_max"

# WMO weather interpretation codes -> description
WMO_TEXT='{"0":"Clear sky","1":"Mainly clear","2":"Partly cloudy","3":"Overcast","45":"Fog","48":"Rime fog","51":"Light drizzle","53":"Moderate drizzle","55":"Dense drizzle","56":"Light freezing drizzle","57":"Dense freezing drizzle","61":"Slight rain","63":"Moderate rain","65":"Heavy rain","66":"Light freezing rain","67":"Heavy freezing rain","71":"Slight snow","73":"Moderate snow","75":"Heavy snow","77":"Snow grains","80":"Slight rain showers","81":"Moderate rain showers","82":"Violent rain showers","85":"Slight snow showers","86":"Heavy snow showers","95":"Thunderstorm","96":"Thunderstorm+hail","99":"Thunderstorm+heavy hail"}'

# WMO weather interpretation codes -> emoji
WMO_EMOJI='{"0":"☀️","1":"🌤","2":"⛅","3":"☁️","45":"🌫","48":"🌫","51":"🌦","53":"🌦","55":"🌦","56":"🌦","57":"🌦","61":"🌧","63":"🌧","65":"🌧","66":"🌧","67":"🌧","71":"🌨","73":"🌨","75":"🌨","77":"🌨","80":"🌧","81":"🌧","82":"🌧","85":"🌨","86":"🌨","95":"⛈","96":"⛈","99":"⛈"}'

# ===================== HELPERS =====================

die() { echo "error: $*" >&2; exit 2; }

usage() {
  cat <<'USAGE'
weather - current conditions & forecast via Open-Meteo API

Usage:
  weather.sh --current --city=Minsk --country=BY
  weather.sh --current --lat=53.9 --lon=27.56667
  weather.sh --forecast --city=London --country=GB
  weather.sh --forecast-days=3 --city=Minsk --country=BY
  weather.sh --current --forecast-days=2 --city=Minsk --country=BY

Location (one of):
  --city=NAME         City name (geocoded via Open-Meteo)
  --country=CC        ISO country code (improves geocoding)
  --lat=FLOAT         Latitude  (skips geocoding)
  --lon=FLOAT         Longitude (skips geocoding)

Mode (at least one required):
  --current           Fetch current conditions
  --forecast          Fetch hourly + daily forecast
  --forecast-days=N   Forecast length 1-16 (default: 7; implies --forecast)

Override API variables:
  --current-params=…  Current weather variables (comma-separated)
  --hourly-params=…   Hourly forecast variables
  --daily-params=…    Daily forecast variables

Output format:
  --porcelain         Compact labeled text for AI (default)
  --human             Emoji-rich format for humans
USAGE
}

urlencode() { jq -rn --arg s "$1" '$s | @uri'; }

# ===================== ARG PARSING =====================

parse_args() {
  MODE_CURRENT=false
  MODE_FORECAST=false
  CITY="" COUNTRY="" LAT="" LON=""
  FORECAST_DAYS=""
  CURRENT_PARAMS="" HOURLY_PARAMS="" DAILY_PARAMS=""
  FORMAT="porcelain"

  for arg in "$@"; do
    case "$arg" in
      --current)          MODE_CURRENT=true ;;
      --forecast)         MODE_FORECAST=true ;;
      --forecast-days=*)  FORECAST_DAYS="${arg#*=}"; MODE_FORECAST=true ;;
      --city=*)           CITY="${arg#*=}" ;;
      --country=*)        COUNTRY="${arg#*=}" ;;
      --lat=*)            LAT="${arg#*=}" ;;
      --lon=*)            LON="${arg#*=}" ;;
      --current-params=*) CURRENT_PARAMS="${arg#*=}" ;;
      --hourly-params=*)  HOURLY_PARAMS="${arg#*=}" ;;
      --daily-params=*)   DAILY_PARAMS="${arg#*=}" ;;
      --porcelain)        FORMAT="porcelain" ;;
      --human)            FORMAT="human" ;;
      -h|--help|help)     usage; exit 0 ;;
      *)                  die "unknown argument: $arg" ;;
    esac
  done

  # validate mode
  [[ "$MODE_CURRENT" == true || "$MODE_FORECAST" == true ]] \
    || die "specify --current and/or --forecast (or --forecast-days=N)"

  # validate location
  if [[ -n "$LAT" && -n "$LON" ]]; then
    : # direct coordinates
  elif [[ -n "$CITY" ]]; then
    : # needs geocoding
  else
    die "location required: --lat=X --lon=Y or --city=NAME [--country=CC]"
  fi

  # apply defaults
  FORECAST_DAYS="${FORECAST_DAYS:-$DEFAULT_FORECAST_DAYS}"
  CURRENT_PARAMS="${CURRENT_PARAMS:-$DEFAULT_CURRENT_PARAMS}"
  HOURLY_PARAMS="${HOURLY_PARAMS:-$DEFAULT_HOURLY_PARAMS}"
  DAILY_PARAMS="${DAILY_PARAMS:-$DEFAULT_DAILY_PARAMS}"
}

# ===================== GEOCODING =====================

geocode() {
  local url="${GEOCODING_API}?name=$(urlencode "$CITY")&count=1&language=en&format=json"
  [[ -z "$COUNTRY" ]] || url="${url}&country=${COUNTRY}"

  local resp
  resp="$(curl -sSf "$url" 2>&1)" || die "geocoding request failed: $resp"

  local count
  count="$(printf '%s' "$resp" | jq '.results | length // 0')"
  [[ "$count" -gt 0 ]] || die "no geocoding results for city=\"$CITY\" country=\"$COUNTRY\""

  LAT="$(printf '%s' "$resp" | jq -r '.results[0].latitude')"
  LON="$(printf '%s' "$resp" | jq -r '.results[0].longitude')"
  GEO_CITY="$(printf '%s' "$resp" | jq -r '.results[0].name')"
  GEO_COUNTRY="$(printf '%s' "$resp" | jq -r '.results[0].country')"
}

# ===================== FETCH =====================

fetch_weather() {
  local url="${FORECAST_API}?latitude=${LAT}&longitude=${LON}&timezone=auto"
  [[ "$MODE_CURRENT"  == false ]] || url="${url}&current=${CURRENT_PARAMS}"
  [[ "$MODE_FORECAST" == false ]] || url="${url}&hourly=${HOURLY_PARAMS}&daily=${DAILY_PARAMS}&forecast_days=${FORECAST_DAYS}"

  WEATHER="$(curl -sSf "$url" 2>&1)" || die "forecast request failed: $WEATHER"
}

# ===================== PORCELAIN OUTPUT =====================

print_header_porcelain() {
  [[ -z "${GEO_CITY:-}" ]] || echo "location: ${GEO_CITY}, ${GEO_COUNTRY}"
  echo "coordinates: ${LAT}, ${LON}"
  echo "timezone: $(printf '%s' "$WEATHER" | jq -r '.timezone')"
  echo ""
}

porcelain_current() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" -r '
    def w: if . == null then "n/a" else ($wmo[tostring] // "Unknown(\(.))") end;
    .current as $c | .current_units as $u |
    "=== CURRENT ===",
    "time: \($c.time)",
    (if $c.weather_code       != null then "conditions: \($c.weather_code | w)"                                          else empty end),
    (if $c.temperature_2m     != null then "temperature: \($c.temperature_2m)\($u.temperature_2m)"                       else empty end),
    (if $c.apparent_temperature != null then "feels_like: \($c.apparent_temperature)\($u.apparent_temperature)"           else empty end),
    (if $c.relative_humidity_2m != null then "humidity: \($c.relative_humidity_2m)%"                                      else empty end),
    (if $c.precipitation      != null then "precipitation: \($c.precipitation)mm"                                         else empty end),
    (if $c.wind_speed_10m     != null then "wind: \($c.wind_speed_10m)km/h"                                              else empty end),
    (if $c.wind_gusts_10m     != null then "gusts: \($c.wind_gusts_10m)km/h"                                             else empty end),
    (if $c.cloud_cover        != null then "cloud_cover: \($c.cloud_cover)%"                                              else empty end),
    (if $c.is_day             != null then "is_day: \(if $c.is_day == 1 then "yes" else "no" end)"                        else empty end),
    ""
  '
}

porcelain_daily() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" -r '
    def w: if . == null then "n/a" else ($wmo[tostring] // "Unknown(\(.))") end;
    "=== DAILY FORECAST ===",
    (.daily as $d | range($d.time | length) | . as $i |
      [
        $d.time[$i],
        (if $d.temperature_2m_max then "\($d.temperature_2m_max[$i])/\($d.temperature_2m_min[$i])°C" else null end),
        (if $d.weather_code then ($d.weather_code[$i] | w) else null end),
        (if $d.precipitation_sum then "precip:\($d.precipitation_sum[$i])mm(\($d.precipitation_probability_max[$i] // "?")%)" else null end),
        (if $d.wind_speed_10m_max then "wind_max:\($d.wind_speed_10m_max[$i])km/h" else null end)
      ] | map(select(. != null)) | join(" | ")
    ),
    ""
  '
}

porcelain_hourly() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" -r '
    def w: if . == null then "n/a" else ($wmo[tostring] // "Unknown(\(.))") end;
    "=== HOURLY FORECAST ===",
    (.hourly as $h | range($h.time | length) | . as $i |
      [
        $h.time[$i],
        (if $h.temperature_2m then "\($h.temperature_2m[$i])°C" else null end),
        (if $h.apparent_temperature then "feels:\($h.apparent_temperature[$i])°C" else null end),
        (if $h.weather_code then ($h.weather_code[$i] | w) else null end),
        (if $h.precipitation then "precip:\($h.precipitation[$i])mm(\($h.precipitation_probability[$i] // "?")%)" else null end),
        (if $h.wind_speed_10m then "wind:\($h.wind_speed_10m[$i])km/h" else null end)
      ] | map(select(. != null)) | join(" | ")
    ),
    ""
  '
}

# ===================== HUMAN OUTPUT =====================

print_header_human() {
  if [[ -n "${GEO_CITY:-}" ]]; then
    echo "📍 ${GEO_CITY}, ${GEO_COUNTRY}"
  else
    echo "📍 ${LAT}, ${LON}"
  fi
  echo "🕐 $(printf '%s' "$WEATHER" | jq -r '.timezone')"
  echo ""
}

human_current() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" --argjson emj "$WMO_EMOJI" -r '
    def w: if . == null then "?" else ($wmo[tostring] // "Unknown") end;
    def e: if . == null then "❓" else ($emj[tostring] // "❓") end;
    .current as $c | .current_units as $u |
    "━━━ Current Weather ━━━",
    "\($c.weather_code | e) \($c.weather_code | w)  \($c.temperature_2m // "?")\($u.temperature_2m // "°C")",
    (if $c.apparent_temperature != null then "🌡 Feels like \($c.apparent_temperature)\($u.apparent_temperature // "°C")" else empty end),
    (if $c.relative_humidity_2m != null then "💧 Humidity \($c.relative_humidity_2m)%" else empty end),
    (if $c.precipitation != null and $c.precipitation > 0 then "🌧 Precipitation \($c.precipitation)mm" else empty end),
    (if $c.wind_speed_10m != null then
      "💨 Wind \($c.wind_speed_10m)km/h" + (if $c.wind_gusts_10m != null then " (gusts \($c.wind_gusts_10m)km/h)" else "" end)
    else empty end),
    (if $c.cloud_cover != null then "☁️  Clouds \($c.cloud_cover)%" else empty end),
    ""
  '
}

human_daily() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" --argjson emj "$WMO_EMOJI" -r '
    def w: if . == null then "?" else ($wmo[tostring] // "?") end;
    def e: if . == null then "❓" else ($emj[tostring] // "❓") end;
    "━━━ Daily Forecast ━━━",
    (.daily as $d | range($d.time | length) | . as $i |
      "\($d.weather_code[$i] | e) \($d.time[$i])  \($d.temperature_2m_max[$i] // "?")/\($d.temperature_2m_min[$i] // "?")°C  \($d.weather_code[$i] | w)  💧\($d.precipitation_sum[$i] // "?")mm (\($d.precipitation_probability_max[$i] // "?")%)"
    ),
    ""
  '
}

human_hourly() {
  printf '%s' "$WEATHER" | jq --argjson wmo "$WMO_TEXT" --argjson emj "$WMO_EMOJI" -r '
    def w: if . == null then "?" else ($wmo[tostring] // "?") end;
    def e: if . == null then "❓" else ($emj[tostring] // "❓") end;
    "━━━ Hourly Forecast ━━━",
    (.hourly as $h | range($h.time | length) | . as $i |
      (if $i == 0 or ($h.time[$i][0:10] != $h.time[$i-1][0:10])
       then "── \($h.time[$i][0:10]) ──" else empty end),
      "  \($h.time[$i][11:16])  \($h.temperature_2m[$i] // "?")°C  \($h.weather_code[$i] | e) \($h.weather_code[$i] | w)  💧\($h.precipitation[$i] // "?")mm(\($h.precipitation_probability[$i] // "?")%)  💨\($h.wind_speed_10m[$i] // "?")km/h"
    ),
    ""
  '
}

# ===================== MAIN =====================

main() {
  command -v curl >/dev/null 2>&1 || die "curl not found"
  command -v jq   >/dev/null 2>&1 || die "jq not found"

  [[ $# -gt 0 ]] || { usage; exit 0; }

  parse_args "$@"

  # resolve coordinates if needed
  GEO_CITY="" GEO_COUNTRY=""
  [[ -n "$LAT" && -n "$LON" ]] || geocode

  fetch_weather

  case "$FORMAT" in
    porcelain)
      print_header_porcelain
      [[ "$MODE_CURRENT"  == false ]] || porcelain_current
      if [[ "$MODE_FORECAST" == true ]]; then
        porcelain_daily
        porcelain_hourly
      fi
      ;;
    human)
      print_header_human
      [[ "$MODE_CURRENT"  == false ]] || human_current
      if [[ "$MODE_FORECAST" == true ]]; then
        human_daily
        human_hourly
      fi
      ;;
  esac
}

main "$@"
