#!/bin/sh
# Philips Hue Skill - Robust Control Script
# Usage: ./hue.sh light <id> [on|off] [bri 0-100] [color name] [color #hex] [hue 0-65535] [sat 0-254] [ct 153-500]

set -e

SCRIPT_DIR="$(dirname "$0")"
SCRIPT_DIR="$(cd "$SCRIPT_DIR" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.env"

if [ -f "$CONFIG_FILE" ]; then
  . "$CONFIG_FILE"
fi

BRIDGE_IP=${BRIDGE_IP:-""}
USERNAME=${USERNAME:-""}

call_api() {
  path="$1"
  data="$2"
  method="${3:-PUT}"
  
  if [ -z "$BRIDGE_IP" ] || [ -z "$USERNAME" ]; then
    echo "❌ Missing config (BRIDGE_IP/USERNAME). Please run setup or check .env."
    exit 1
  fi

  url="http://$BRIDGE_IP/api/$USERNAME$path"
  
  if [ "$method" = "GET" ]; then
    curl -s -H "Connection: close" "$url"
  else
    curl -s -H "Connection: close" -X "$method" -d "$data" "$url"
  fi
}

# Helper to convert Hex to Hue/Sat/Bri via Python
hex_to_hsb() {
  hex=$(echo "$1" | sed 's/#//')
  python3 - <<EOF
import colorsys
hex_color = "$hex"
r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
h, s, v = colorsys.rgb_to_hsv(r, g, b)
# Hue is 0-65535, Sat is 0-254, Bri is 0-254
print(f"\"on\":true,\"hue\":{int(h * 65535)},\"sat\":{int(s * 254)},\"bri\":{int(v * 254)}")
EOF
}

case "$1" in
  status|st)
    call_api "/lights" "" "GET"
    ;;

  light|l)
    shift
    ID="$1"
    shift
    STATE="{"
    FIRST=1
    
    while [ $# -gt 0 ]; do
      [ $FIRST -eq 0 ] && STATE="$STATE,"
      case "$1" in
        on) STATE="${STATE}\"on\":true" ;;
        off) STATE="${STATE}\"on\":false" ;;
        bri) shift; val=$(($1 * 254 / 100)); STATE="${STATE}\"bri\":$val" ;;
        sat) shift; STATE="${STATE}\"sat\":$1" ;;
        hue) shift; STATE="${STATE}\"hue\":$1" ;;
        ct)  shift; STATE="${STATE}\"ct\":$1" ;;
        color)
          shift
          case "$1" in
            red)    HEX="#FF0000" ;;
            blue)   HEX="#0000FF" ;;
            green)  HEX="#00FF00" ;;
            yellow) HEX="#FFFF00" ;;
            orange) HEX="#FFA500" ;;
            pink)   HEX="#FFC0CB" ;;
            purple) HEX="#800080" ;;
            white)  HEX="#FFFFFF" ;;
            # Use hex for white and colors, but keep specialized CT for warm/cold
            warm)   HSB="\"on\":true,\"sat\":0,\"bri\":254,\"ct\":450" ;;
            cold)   HSB="\"on\":true,\"sat\":0,\"bri\":254,\"ct\":153" ;;
            \#*)    HEX="$1" ;;
            *)      echo "Unknown color: $1" ; exit 1 ;;
          esac
          
          if [ -n "$HEX" ]; then
            HSB=$(hex_to_hsb "$HEX")
            unset HEX
          fi
          STATE="${STATE}${HSB}"
          ;;
      esac
      FIRST=0
      shift
    done
    STATE="$STATE}"
    
    call_api "/lights/$ID/state" "$STATE"
    echo "Light $ID updated: $STATE"
    ;;

  *)
    echo "Usage: $0 light <id> [on|off] [bri %] [color name|#hex]"
    ;;
esac
