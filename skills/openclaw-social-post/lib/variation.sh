#!/bin/bash
# Text variation library - introduce subtle differences to avoid duplicate content detection

# Vary text with random subtle changes
vary_text() {
  local text="$1"
  local varied="$text"
  local original="$text"
  local attempts=0
  local max_attempts=10
  
  # Keep trying until we get a variation that's different from original
  while [ "$varied" = "$original" ] && [ $attempts -lt $max_attempts ]; do
    varied="$original"
    
    # Apply 2-3 random variations
    local variations=(
      "punctuation"
      "emoji"
      "spacing"
      "wording"
    )
    
    # Shuffle and pick 2-3 variations
    local num_variations=$((2 + RANDOM % 2))  # 2 or 3
    local applied=0
    
    # Shuffle variations array
    local shuffled=($(shuf -e "${variations[@]}"))
    
    for variation in "${shuffled[@]}"; do
      if [ $applied -ge $num_variations ]; then
        break
      fi
      
      case "$variation" in
        punctuation)
          varied=$(vary_punctuation "$varied")
          ;;
        emoji)
          varied=$(vary_emoji "$varied")
          ;;
        spacing)
          varied=$(vary_spacing "$varied")
          ;;
        wording)
          varied=$(vary_wording "$varied")
          ;;
      esac
      
      applied=$((applied + 1))
    done
    
    attempts=$((attempts + 1))
  done
  
  # If still no change, force an emoji addition
  if [ "$varied" = "$original" ]; then
    local emojis=("🚀" "✨" "🔥" "💪" "🎯" "⚡")
    local random_emoji="${emojis[$((RANDOM % ${#emojis[@]}))]}"
    varied="$varied $random_emoji"
  fi
  
  echo "$varied"
}

# Vary punctuation (! → . or vice versa, add/remove) - only at end of sentences
vary_punctuation() {
  local text="$1"
  local result="$text"
  
  # Random choice
  local choice=$((RANDOM % 3))
  
  case $choice in
    0)
      # Change sentence-ending ! to .
      if [[ "$result" == *"!"* ]]; then
        # Only change ! that's followed by newline or end of string
        result=$(echo "$result" | sed 's/!$/./; s/!\n/.\n/g')
      fi
      ;;
    1)
      # Change sentence-ending . to ! (avoid URLs)
      # Only if there's a period at end of line (not in URLs)
      if echo "$result" | grep -qE '\.$' && [[ "$result" != *"github"* ]] && [[ "$result" != *"http"* ]]; then
        result=$(echo "$result" | sed 's/\.$/!/')
      fi
      ;;
    2)
      # Add trailing period if none exists
      if ! echo "$result" | grep -qE '[.!]$'; then
        result="$result."
      fi
      ;;
  esac
  
  echo "$result"
}

# Vary emoji (add, remove, or change position)
vary_emoji() {
  local text="$1"
  local result="$text"
  
  local emojis=("🚀" "✨" "🔥" "💪" "🎯" "⚡" "🛠️" "🔧" "👀" "💯")
  local random_emoji="${emojis[$((RANDOM % ${#emojis[@]}))]}"
  
  # Check if text already has emojis
  if echo "$result" | grep -qE '[🚀✨🔥💪🎯⚡🛠️🔧👀💯]'; then
    # Remove existing emoji
    result=$(echo "$result" | sed 's/ [🚀✨🔥💪🎯⚡🛠️🔧👀💯]//g')
  else
    # Add emoji at end
    result="$result $random_emoji"
  fi
  
  echo "$result"
}

# Vary spacing (add/remove line breaks)
vary_spacing() {
  local text="$1"
  local result="$text"
  
  local choice=$((RANDOM % 2))
  
  case $choice in
    0)
      # Add extra line break before last line
      result=$(echo "$result" | sed '$ s/^/\n/')
      ;;
    1)
      # Remove one line break if multiple exist
      if [ $(echo "$result" | grep -c "^$") -gt 1 ]; then
        result=$(echo "$result" | sed '/^$/{ N; s/\n$//; }' | head -20)
      fi
      ;;
  esac
  
  echo "$result"
}

# Vary wording (subtle synonym swaps)
vary_wording() {
  local text="$1"
  local result="$text"
  
  # Simple word swaps (only if word exists)
  local swaps=(
    "just:now"
    "now:just"
    "new:latest"
    "check:see"
    "see:check"
    "live:available"
    "available:live"
    "published:released"
    "released:published"
  )
  
  local swap="${swaps[$((RANDOM % ${#swaps[@]}))]}"
  local from="${swap%:*}"
  local to="${swap#*:}"
  
  # Only swap if the word exists (case insensitive, whole word) and preserve the full text
  if echo "$result" | grep -qiw "$from"; then
    result=$(echo "$result" | sed "s/\b$from\b/$to/gi")
  fi
  
  echo "$result"
}
