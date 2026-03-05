#!/bin/bash

# Unified Calendar for arr-all

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/lib/common.sh"

DAYS=${1:-7}
START_DATE=$(date -I)
if [[ "$OSTYPE" == "darwin"* ]]; then
    END_DATE=$(date -v+${DAYS}d +%Y-%m-%d)
else
    END_DATE=$(date -d "+$DAYS days" +%Y-%m-%d)
fi

echo "Upcoming Releases (Next $DAYS Days)"
echo ""

# Temp file for aggregating results
TMP_CAL="/tmp/arr-all-calendar-$$.json"
echo "[]" > "$TMP_CAL"

# RADARR
if load_config "radarr"; then
    res=$(api_request "radarr" "GET" "/api/v3/calendar?start=$START_DATE&end=$END_DATE")
    # Normalize: {date, type: "movie", title, hasFile}
    echo "$res" | jq '[.[] | {date: (.inCinemas // .physicalRelease // .digitalRelease // .status), type: "[M]", title: "\(.title) (\(.year))", hasFile: .hasFile, sortKey: (.inCinemas // .physicalRelease // .digitalRelease // .status)}]' > "${TMP_CAL}.radarr"
    # Merge
    jq -s '.[0] + .[1]' "$TMP_CAL" "${TMP_CAL}.radarr" > "${TMP_CAL}.tmp" && mv "${TMP_CAL}.tmp" "$TMP_CAL"
    rm "${TMP_CAL}.radarr"
fi

# SONARR
if load_config "sonarr"; then
    res=$(api_request "sonarr" "GET" "/api/v3/calendar?start=$START_DATE&end=$END_DATE&includeSeries=true")
    # Normalize - includeSeries=true ensures .series.title is available
    echo "$res" | jq '[.[] | {date: .airDate, type: "[TV]", title: "\(.series.title // "Unknown") S\(.seasonNumber)E\(.episodeNumber) - \(.title // "TBA")", hasFile: .hasFile, sortKey: .airDate}]' > "${TMP_CAL}.sonarr"
     # Merge
    jq -s '.[0] + .[1]' "$TMP_CAL" "${TMP_CAL}.sonarr" > "${TMP_CAL}.tmp" && mv "${TMP_CAL}.tmp" "$TMP_CAL"
    rm "${TMP_CAL}.sonarr"
fi

# LIDARR
if load_config "lidarr"; then
    res=$(api_request "lidarr" "GET" "/api/v1/calendar?start=$START_DATE&end=$END_DATE")
    # Normalize
    echo "$res" | jq '[.[] | {date: .releaseDate, type: "[Music]", title: "\(.artist.artistName) - \(.title)", hasFile: (.grabbed or .hasFile), sortKey: .releaseDate}]' > "${TMP_CAL}.lidarr"
     # Merge
    jq -s '.[0] + .[1]' "$TMP_CAL" "${TMP_CAL}.lidarr" > "${TMP_CAL}.tmp" && mv "${TMP_CAL}.tmp" "$TMP_CAL"
     rm "${TMP_CAL}.lidarr"
fi

# Sort and Display
# We want to group by date
cat "$TMP_CAL" | jq -r '
  sort_by(.sortKey) | .[] | 
  "\(.sortKey | split("T")[0])|\(.type)| \(.title)|\(.hasFile)"
' | while IFS="|" read -r date type title hasFile; do
    if [ "$date" != "$prev_date" ]; then
        echo ""
        # Format date nicely if available, otherwise just YYYY-MM-DD
        formatted_date=$(date -d "$date" +"%a %b %d" 2>/dev/null || echo "$date")
        echo "$formatted_date:"
        prev_date="$date"
    fi
    
    status=""
    if [ "$hasFile" = "true" ]; then status="[DOWNLOADED]"; fi
    
    echo "  $type $title $status"
done

echo ""
rm "$TMP_CAL"
