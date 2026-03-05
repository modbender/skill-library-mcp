#!/bin/bash
# Intelligent Ramadan Times Script

# Get coords for city
get_coords() {
    case "$1" in
        istanbul) echo "41.0082,28.9784" ;;
        ankara) echo "39.9334,32.8597" ;;
        izmir) echo "38.4192,27.1287" ;;
        london) echo "51.5074,-0.1278" ;;
        newyork|NewYork) echo "40.7128,-74.0060" ;;
        losangeles|LosAngeles) echo "34.0522,-118.2437" ;;
        dubai) echo "25.2048,55.2708" ;;
        cairo) echo "30.0444,31.2357" ;;
        paris) echo "48.8566,2.3522" ;;
        berlin) echo "52.5200,13.4050" ;;
        moscow) echo "55.7558,37.6173" ;;
        tokyo) echo "35.6762,139.6503" ;;
        *) echo "41.0082,28.9784" ;;
    esac
}

city="${1:-istanbul}"
coords=$(get_coords "$city")
lat=$(echo "$coords" | cut -d',' -f1)
lng=$(echo "$coords" | cut -d',' -f2)

result=$(curl -s "https://api.sunrise-sunset.org/json?lat=$lat&lng=$lng&formatted=0" 2>/dev/null)
sunset=$(echo "$result" | jq -r '.results.sunset' 2>/dev/null)

if [ -z "$sunset" ] || [ "$sunset" = "null" ]; then
    sunset_unix=$(date -d "today 18:47" +%s)
else
    sunset_unix=$(date -d "$sunset" +%s 2>/dev/null)
    [ $? -ne 0 ] && sunset_unix=$(date -d "today 18:47" +%s)
fi

iftar_unix=$((sunset_unix + 1200))
sahur_unix=$((iftar_unix - 43200))
now=$(date +%s)
diff=$((iftar_unix - now))
hours=$((diff / 3600))
minutes=$(((diff % 3600) / 60))

echo ""
echo "🌙 RAMADAN TIMES"
echo "📍 $(echo $city | sed 's/.*/\u&/')"
echo "📅 $(date +'%d %B %Y')"
echo ""
echo "🌅 Sahur:   $(date -d @$sahur_unix +'%H:%M')"
echo "🌅 İftar:   $(date -d @$iftar_unix +'%H:%M')"
echo ""

if [ $diff -gt 0 ]; then
    echo "⏰ İftara kaldı: $hours saat $minutes dakika"
else
    echo "⏰ İFTAR VAKTİ! 🌙 Herkese afiyet olsun!"
fi
