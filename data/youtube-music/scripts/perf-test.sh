#!/usr/bin/env bash
# Performance test for YouTube Music Skill v2.0

echo "🎵 YouTube Music Skill - Performance Test v2.0"
echo "=============================================="
echo ""

# Test 1: Cold start
echo "Test 1: Cold Start (First Play)"
echo "--------------------------------"
start_time=$(date +%s.%N)
./scripts/youtube-music.sh play "Dildara Ra One" >/dev/null 2>&1
end_time=$(date +%s.%N)
cold_time=$(echo "$end_time - $start_time" | bc)
echo "Time: ${cold_time}s"
echo ""

# Test 2: Warm start (cached)
echo "Test 2: Warm Start (Cached)"
echo "---------------------------"
start_time=$(date +%s.%N)
./scripts/youtube-music.sh play "Dildara Ra One" >/dev/null 2>&1
end_time=$(date +%s.%N)
warm_time=$(echo "$end_time - $start_time" | bc)
echo "Time: ${warm_time}s"
echo ""

# Test 3: Fast play (no cache)
echo "Test 3: Fast Play (No Cache Check)"
echo "-----------------------------------"
start_time=$(date +%s.%N)
./scripts/youtube-music.sh play-fast "Dildara Ra One" >/dev/null 2>&1
end_time=$(date +%s.%N)
fast_time=$(echo "$end_time - $start_time" | bc)
echo "Time: ${fast_time}s"
echo ""

# Summary
echo "=============================================="
echo "Summary:"
echo "  Cold Start:  ${cold_time}s"
echo "  Warm (Cached): ${warm_time}s"
echo "  Fast Play:   ${fast_time}s"
echo ""

# Calculate improvement
if (( $(echo "$cold_time > 0" | bc -l) )); then
  improvement=$(echo "scale=2; (1 - $warm_time/$cold_time) * 100" | bc)
  echo "Cache Improvement: ${improvement}%"
fi

echo ""
echo "✅ Test complete!"
