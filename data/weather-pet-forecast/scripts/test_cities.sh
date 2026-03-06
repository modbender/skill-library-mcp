#!/bin/bash
# Test weather analysis for multiple cities

SCRIPT="/home/app/.openclaw/workspace/weather-forecast-analysis/scripts/weather_analysis.py"

# Function to test a city with retry
test_city() {
    local city="$1"
    local retry=0
    local max_retries=2
    
    echo "Testing: $city"
    
    while [ $retry -lt $max_retries ]; do
        result=$(curl -s --max-time 15 "wttr.in/$city?format=j1" 2>&1)
        
        if [ $? -eq 0 ] && [ -n "$result" ]; then
            echo "$result" | python3 "$SCRIPT" "$city" 2>&1
            return 0
        fi
        
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            sleep 1
        fi
    done
    
    echo "Error: Failed to fetch data for $city after $max_retries attempts"
    return 1
}

# Test cities by country
echo "========================================="
echo "Testing China Cities"
echo "========================================="
for city in Beijing Shanghai Guangzhou Shenzhen Chengdu; do
    test_city "$city"
    echo ""
done

echo "========================================="
echo "Testing Japan Cities"
echo "========================================="
for city in Tokyo Osaka Kyoto Yokohama; do
    test_city "$city"
    echo ""
done

echo "========================================="
echo "Testing US Cities"
echo "========================================="
for city in "New+York" "Los+Angeles" "San+Francisco" Seattle Miami; do
    test_city "$city"
    echo ""
done

echo "========================================="
echo "Testing Canada Cities"
echo "========================================="
for city in Toronto Vancouver Montreal Calgary; do
    test_city "$city"
    echo ""
done

echo "========================================="
echo "Testing UK Cities"
echo "========================================="
for city in London Manchester Edinburgh Birmingham; do
    test_city "$city"
    echo ""
done

echo "========================================="
echo "All tests completed"
echo "========================================="
