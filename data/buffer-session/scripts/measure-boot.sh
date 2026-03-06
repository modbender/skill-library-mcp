#!/bin/bash
# Measure boot payload: files, sizes, token estimates, skill counts
set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
echo "=== BOOT FILE SIZES ==="
total=0
for f in AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md; do
  path="$WORKSPACE/$f"
  if [ -f "$path" ]; then
    size=$(wc -c < "$path")
    lines=$(wc -l < "$path")
    tokens=$((size / 4))
    total=$((total + size))
    printf "  %-15s %6d bytes  %4d lines  ~%5d tokens\n" "$f" "$size" "$lines" "$tokens"
  fi
done
echo "  ---"
printf "  %-15s %6d bytes              ~%5d tokens\n" "TOTAL" "$total" "$((total / 4))"

echo ""
echo "=== MEMORY FILES ==="
mem_count=$(ls "$WORKSPACE"/memory/*.md 2>/dev/null | wc -l | tr -d ' ')
mem_bytes=$(wc -c "$WORKSPACE"/memory/*.md 2>/dev/null | tail -1 | awk '{print $1}')
echo "  Files: $mem_count"
echo "  Total: ${mem_bytes:-0} bytes"
echo "  Loaded in boot (recent):"
# Show the 5 most recent
ls -t "$WORKSPACE"/memory/*.md 2>/dev/null | head -5 | while read f; do
  size=$(wc -c < "$f")
  printf "    %-50s %6d bytes\n" "$(basename "$f")" "$size"
done

echo ""
echo "=== SKILLS ==="
builtin_dir="/opt/homebrew/lib/node_modules/openclaw/skills"
custom_dir="$WORKSPACE/skills"
builtin_count=$(ls "$builtin_dir" 2>/dev/null | wc -l | tr -d ' ')
custom_count=$(ls "$custom_dir" 2>/dev/null | wc -l | tr -d ' ')
echo "  Built-in: $builtin_count"
echo "  Custom: $custom_count"
echo "  Total: $((builtin_count + custom_count))"

echo ""
echo "=== GHOST FILE CHECK ==="
recognized="AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md"
for f in "$WORKSPACE"/*.md; do
  name=$(basename "$f")
  if ! echo "$recognized" | grep -qw "$name"; then
    echo "  ⚠️  $name — NOT auto-loaded by OpenClaw"
  fi
done

echo ""
echo "=== THRESHOLDS ==="
check() {
  local name="$1" size="$2" limit="$3"
  if [ "$size" -gt "$limit" ]; then
    echo "  🔴 $name: ${size}B > ${limit}B limit"
  else
    echo "  ✅ $name: ${size}B (under ${limit}B)"
  fi
}
for f in AGENTS.md SOUL.md USER.md MEMORY.md HANDOFF.md IDENTITY.md; do
  path="$WORKSPACE/$f"
  [ -f "$path" ] || continue
  size=$(wc -c < "$path")
  case "$f" in
    AGENTS.md) check "$f" "$size" 4000 ;;
    MEMORY.md) check "$f" "$size" 1500 ;;
    HANDOFF.md) check "$f" "$size" 2000 ;;
    *) check "$f" "$size" 1500 ;;
  esac
done
check "Total boot" "$total" 12000
echo "  Skills: $((builtin_count + custom_count)) (target: <20, danger: >40)"
