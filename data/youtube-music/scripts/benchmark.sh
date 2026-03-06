#!/usr/bin/env bash
# Performance Benchmark - YouTube Music Skill
# Compares v1.0 vs v2.0 vs v3.0

echo "🎵 YouTube Music Performance Benchmark"
echo "======================================"
echo ""

# Test query
QUERY="Despacito Luis Fonsi"
DIRECT_ID="kJQP7kiw5Fk"

echo "Test Query: $QUERY"
echo "Direct ID: $DIRECT_ID"
echo ""

# v1.0 Simulation (original slow way)
echo "📊 v1.0 (Original - Simulated)"
echo "  Steps: 7 (browser check, start, open, wait, search, wait, click)"
echo "  Estimated: 8-10 seconds"
echo ""

# v2.0 Test
echo "⚡ v2.0 (Optimized)"
start=$(date +%s%N)
./scripts/youtube-music.sh play "$QUERY" >/dev/null 2>&1
v2_time=$(( ($(date +%s%N) - start) / 1000000 ))
echo "  Steps: 3 (browser warm, direct URL, auto-play)"
echo "  Actual: ${v2_time}ms"
echo ""

# v3.0 Test  
echo "🚀 v3.0 (ULTRA FAST)"
start=$(date +%s%N)
./scripts/youtube-music-v3.sh play "$QUERY" >/dev/null 2>&1
v3_time=$(( ($(date +%s%N) - start) / 1000000 ))
echo "  Steps: 2 (atomic play, smart cache)"
echo "  Actual: ${v3_time}ms"
echo ""

# Direct ID Test
echo "🎯 Direct Video ID"
start=$(date +%s%N)
./scripts/youtube-music-v3.sh direct "$DIRECT_ID" >/dev/null 2>&1
direct_time=$(( ($(date +%s%N) - start) / 1000000 ))
echo "  Steps: 1 (direct URL)"
echo "  Actual: ${direct_time}ms"
echo ""

# Summary
echo "======================================"
echo "Summary:"
echo "  v1.0 (Original):  ~8000-10000ms (estimated)"
echo "  v2.0 (Optimized): ${v2_time}ms"
echo "  v3.0 (ULTRA):     ${v3_time}ms"
echo "  Direct ID:        ${direct_time}ms"
echo ""

# Calculate improvement
if [[ $v3_time -gt 0 && $v2_time -gt 0 ]]; then
  improvement=$(( (v2_time - v3_time) * 100 / v2_time ))
  echo "v3.0 is ${improvement}% faster than v2.0"
fi

echo ""
echo "✅ Benchmark complete!"
