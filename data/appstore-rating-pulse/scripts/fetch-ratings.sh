#!/bin/bash
# AppStore Rating Pulse
# Fetches current overall App Store ratings via Apple's free iTunes Lookup API
# No API key or paid subscription needed.
#
# CONFIGURATION: Add your apps below
# Format: "App Display Name|AppStoreID|CC1,CC2,CC3"
# Country codes: US GB JP KR RU ES FR DE CA AU IT BR MX TR NL SE NO DK FI

APPS=(
  "My App|1234567890|US,GB,DE"
)

# ─────────────────────────────────────────────────────────────────────────────

DATE_DISPLAY=$(TZ="${TZ:-UTC}" date +%d.%m.%Y)

country_name() {
  case "$1" in
    US) echo "USA";;       GB) echo "UK";;       JP) echo "JAPAN";;
    KR) echo "KOREA";;     RU) echo "RUSSIA";;   ES) echo "SPAIN";;
    FR) echo "FRANCE";;    DE) echo "GERMANY";;  CA) echo "CANADA";;
    AU) echo "AUSTRALIA";; IT) echo "ITALY";;    BR) echo "BRAZIL";;
    MX) echo "MEXICO";;    TR) echo "TURKEY";;   NL) echo "NETHERLANDS";;
    SE) echo "SWEDEN";;    NO) echo "NORWAY";;   DK) echo "DENMARK";;
    FI) echo "FINLAND";;   *) echo "$1";;
  esac
}

fetch_rating() {
  local appName="$1" appId="$2" region="$3"
  local countryName
  countryName=$(country_name "$region")
  local result
  result=$(curl -s --max-time 10 "https://itunes.apple.com/lookup?id=${appId}&country=${region}" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d['resultCount'] == 0:
        print('N/A')
    else:
        r = d['results'][0]
        rating = r.get('averageUserRating', 0)
        if rating:
            print(f'{rating:.2f}'.replace('.', ','))
        else:
            print('N/A')
except:
    print('N/A')
" 2>/dev/null)
  echo "overall rating for ${appName}(${appId}) ${DATE_DISPLAY} - ${result} - ${countryName}"
}

for entry in "${APPS[@]}"; do
  IFS='|' read -r appName appId regions <<< "$entry"
  IFS=',' read -ra regionList <<< "$regions"
  for region in "${regionList[@]}"; do
    fetch_rating "$appName" "$appId" "$region"
  done
done
